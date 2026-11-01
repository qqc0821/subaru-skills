#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build a local main-thread report from Chrome trace or ego CDP events."""
import argparse
import collections
import json
from pathlib import Path


def normalize(raw, perf=None, navigation=0):
    events = raw.get('traceEvents', []) if isinstance(raw, dict) else raw
    if events and 'method' in events[0]:
        events = [v for e in events if e.get('method') == 'Tracing.dataCollected' for v in e['params']['value']]
    navs = [e for e in events if e.get('name') == 'navigationStart' and e.get('args', {}).get('data', {}).get('documentLoaderURL') and e['args']['data'].get('isOutermostMainFrame', e['args']['data'].get('isLoadingMainFrame', False))]
    if not navs or navigation >= len(navs) or navigation < 0:
        raise ValueError('No matching top-level navigation. Record a page reload, or choose --navigation INDEX.')
    nav = navs[navigation]
    base, pid, tid = nav['ts'], nav['pid'], nav['tid']
    stop = min((e['ts'] for e in navs if e['ts'] > base and e['args'].get('frame') == nav['args'].get('frame')), default=float('inf'))
    main = [e for e in events if e.get('pid') == pid and e.get('tid') == tid and base <= e.get('ts', -1) < stop]
    duration = max(((e['ts'] + e.get('dur', 0) - base) / 1000 for e in main), default=0)
    candidates = [e for e in main if e['name'] == 'largestContentfulPaint::Candidate']
    lcp = (candidates[-1]['ts'] - base) / 1000 if candidates else None
    if perf:
        if perf['url'] != nav['args']['data']['documentLoaderURL']:
            raise ValueError('Performance snapshot URL does not match selected navigation.')
        duration = perf['now']
        lcp = perf['lcp'][-1]['startTime'] if perf.get('lcp') else lcp
    tasks = [{'start': (e['ts'] - base) / 1000, 'duration': min(e['dur'] / 1000, duration - (e['ts'] - base) / 1000)} for e in main if e.get('ph') == 'X' and e['name'] in ('RunTask', 'ThreadControllerImpl::RunTask') and e.get('dur', 0) >= 1000 and (e['ts'] - base) / 1000 < duration]
    if not tasks:
        raise ValueError('No supported main-thread RunTask events; capture disabled-by-default-devtools.timeline.')
    tasks.sort(key=lambda t: t['start'])
    # Reject nested scheduler wrappers rather than double-counting them.
    outer = []
    for t in tasks:
        if outer and t['start'] < outer[-1]['start'] + outer[-1]['duration'] - .001:
            continue
        outer.append(t)
    resources = []
    breakdown = []
    if perf:
        resources = [{'url': r['name'], 'start': r['startTime'], 'duration': r['duration'], 'cache': r.get('deliveryType') == 'cache'} for r in perf.get('resources', [])]
        last = perf.get('lcp', [])[-1] if perf.get('lcp') else {}
        r = next((r for r in perf.get('resources', []) if r['name'] == last.get('url')), None)
        n = perf.get('navigation', [{}])[0]
        if r and lcp is not None and 0 <= n.get('responseStart', -1) <= r['startTime'] <= r['responseEnd'] <= lcp:
            breakdown = [{'name': k, 'value': v} for k, v in zip(['等待文档首字节', 'LCP 资源开始前', 'LCP 资源加载', '资源完成至 LCP'], [n['responseStart'], r['startTime'] - n['responseStart'], r['duration'], lcp - r['responseEnd']])]
    else:
        pending = {}
        for e in sorted(main, key=lambda x: x['ts']):
            d = e.get('args', {}).get('data', {})
            if e['name'] == 'ResourceSendRequest' and d.get('frame') == nav['args'].get('frame'):
                pending[d['requestId']] = {'url': d.get('url', ''), 'start': (e['ts'] - base) / 1000}
            elif e['name'] == 'ResourceFinish' and d.get('requestId') in pending:
                r = pending.pop(d['requestId']);r['duration'] = (e['ts'] - base) / 1000 - r['start'];resources.append(r)
    data = {'url': nav['args']['data']['documentLoaderURL'], 'duration': duration, 'lcp': lcp, 'tasks': outer, 'resources': resources, 'breakdown': breakdown}
    return data, main, base


def attribute(data, main, base):
    kinds = {'FunctionCall': '脚本', 'EvaluateScript': '脚本', 'CompileScript': '脚本', 'Layout': '布局', 'UpdateLayoutTree': '样式', 'Paint': '绘制', 'ParseHTML': 'HTML'}
    acts = [e for e in main if e.get('ph') == 'X' and e['name'] in kinds and e.get('dur', 0) > 0]
    files = {}
    for idx, task in enumerate(data['tasks']):
        start, end = task['start'], task['start'] + task['duration']
        bounds = [(max(start, (e['ts']-base)/1000), min(end, (e['ts']+e['dur']-base)/1000), e) for e in acts if (e['ts']-base)/1000 < end and (e['ts']+e['dur']-base)/1000 > start]
        points = sorted({start, end, *(v for a,b,e in bounds for v in (a,b))})
        groups = {};segments = []
        for a,b in zip(points, points[1:]):
            active = [e for st,en,e in bounds if st <= a and en >= b]
            leaf = min(active, key=lambda e: e['dur'], default=None)
            script = min((e for e in active if e['name'] in ('FunctionCall','EvaluateScript','CompileScript') and e.get('args',{}).get('data',{}).get('url')), key=lambda e:e['dur'], default=None)
            source = script.get('args',{}).get('data',{}) if script else {}
            url = source.get('url','');kind = kinds[leaf['name']] if leaf else '其他'
            g = groups.setdefault(url, {'busy':0,'tail':0,'kinds':collections.defaultdict(float),'line':source.get('lineNumber')})
            g['busy'] += b-a;g['tail'] += max(0,b-max(a,start+50));g['kinds'][kind] += b-a
            segments.append({'start':a,'duration':b-a,'kind':kind,'url':url})
        for url,g in groups.items():
            f=files.setdefault(url, {'url':url,'busy':0,'tail':0,'tasks':[]})
            f['busy']+=g['busy'];f['tail']+=g['tail'];f['tasks'].append(idx)
        task.update(id=idx,sources=[{'url':u,**g} for u,g in sorted(groups.items(),key=lambda kv:-kv[1]['busy'])],segments=segments)
    data['files']=sorted(files.values(),key=lambda f:-f['tail'])
    assert abs(sum(f['busy'] for f in data['files'])-sum(t['duration'] for t in data['tasks'])) < .1
    return data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('trace',type=Path);p.add_argument('--perf',type=Path,help='Optional same-capture Performance API snapshot')
    p.add_argument('--navigation',type=int,default=0);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    try:
        raw=json.loads(args.trace.read_text());perf=json.loads(args.perf.read_text()) if args.perf else None
        data,events,base=normalize(raw,perf,args.navigation);attribute(data,events,base)
        template=(Path(__file__).resolve().parent.parent/'assets/viewer.html').read_text()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')))
        print(json.dumps({'output':str(args.out),'lcp_ms':data['lcp'],'tasks':len(data['tasks']),'files':len(data['files'])}))
    except (ValueError,OSError,KeyError,TypeError) as e:
        p.exit(2,f'Analysis failed: {e}\n')

if __name__=='__main__':main()
