#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Capture a bounded reload in an existing ego-browser TaskSpace."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--doctor',action='store_true');p.add_argument('--space',type=int);p.add_argument('--page',default='p1')
    p.add_argument('--seconds',type=int,default=25);p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.doctor:
        print('ego-browser: '+('available' if shutil.which('ego-browser') else 'missing; use existing trace files instead'))
        return
    if not shutil.which('ego-browser'):p.exit(2,'ego-browser not found; use an existing Chrome trace with analyze.py.\n')
    if a.space is None or a.out is None or not 5<=a.seconds<=60:p.error('--space, --out and --seconds between 5 and 60 are required')
    a.out.mkdir(parents=True,exist_ok=True)
    config=json.dumps({'space':a.space,'page':a.page,'seconds':a.seconds,'out':str(a.out.resolve())})
    script='const cfg='+config+';'+r'''
const task=await taskSpace(cfg.space),page=task.page(cfg.page),fs=await import('node:fs/promises'),path=await import('node:path');
await page.cdp('Tracing.start',{categories:'devtools.timeline,loading,blink.user_timing,disabled-by-default-devtools.timeline',transferMode:'ReportEvents'});
let perf;
try {
 await page.cdp('Page.reload');
 await new Promise(r=>setTimeout(r,cfg.seconds*1000));
 perf=await page.evaluate(async()=>{
  const lcp=[];const observer=new PerformanceObserver(list=>lcp.push(...list.getEntries().map(e=>({startTime:e.startTime,url:e.url,size:e.size}))));
  observer.observe({type:'largest-contentful-paint',buffered:true});await new Promise(r=>setTimeout(r,100));observer.disconnect();
  return {url:location.href,now:performance.now(),timeOrigin:performance.timeOrigin,viewport:{width:innerWidth,height:innerHeight},navigation:performance.getEntriesByType('navigation').map(e=>e.toJSON()),resources:performance.getEntriesByType('resource').map(e=>e.toJSON()),lcp};
 });
} finally {await page.cdp('Tracing.end');}
const events=[];let complete=false;
for(let i=0;i<80;i++){const batch=await page.events();events.push(...batch);if(batch.some(e=>e.method==='Tracing.tracingComplete')){complete=true;break;}await new Promise(r=>setTimeout(r,250));}
if(!complete)throw new Error('Trace did not complete within 20 seconds; do not treat this capture as complete.');
// Persist tracing events only, never raw network request/response headers.
await fs.writeFile(path.join(cfg.out,'trace.json'),JSON.stringify({traceEvents:events.filter(e=>e.method==='Tracing.dataCollected').flatMap(e=>e.params.value)}));
await fs.writeFile(path.join(cfg.out,'perf.json'),JSON.stringify(perf));
console.log(JSON.stringify({output:cfg.out,url:perf.url,lcp:perf.lcp.at(-1)?.startTime}));
'''
    result=subprocess.run(['ego-browser','nodejs'],input=script,text=True)
    if result.returncode:p.exit(result.returncode,'Capture failed; inspect browser state before retrying.\n')

if __name__=='__main__':main()
