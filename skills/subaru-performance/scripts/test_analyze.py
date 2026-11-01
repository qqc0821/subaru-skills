#!/usr/bin/env python3
"""Offline invariants for attribution and missing metrics."""
import unittest
from analyze import normalize, attribute

class AttributionTests(unittest.TestCase):
    def trace(self):
        return {'traceEvents':[
            {'name':'navigationStart','ts':1000,'pid':1,'tid':2,'args':{'frame':'main','data':{'documentLoaderURL':'https://example.test/','isOutermostMainFrame':True}}},
            {'name':'RunTask','ph':'X','ts':1000,'dur':100000,'pid':1,'tid':2},
            {'name':'FunctionCall','ph':'X','ts':1000,'dur':80000,'pid':1,'tid':2,'args':{'data':{'url':'https://example.test/a.js'}}},
            {'name':'Layout','ph':'X','ts':21000,'dur':40000,'pid':1,'tid':2},
            {'name':'RunTask','ph':'X','ts':1000,'dur':900000,'pid':9,'tid':9},
        ]}
    def test_nested_exclusive_and_unknown(self):
        d,m,b=normalize(self.trace());attribute(d,m,b)
        self.assertIsNone(d['lcp']);self.assertEqual(len(d['tasks']),1)
        f={x['url']:x for x in d['files']}
        self.assertAlmostEqual(f['https://example.test/a.js']['busy'],80)
        self.assertAlmostEqual(f['']['busy'],20)
        self.assertAlmostEqual(sum(x['tail'] for x in d['files']),50)
        s=d['tasks'][0]['sources'][0]
        self.assertAlmostEqual(s['kinds']['布局'],40)
        self.assertAlmostEqual(s['kinds']['脚本'],40)
    def test_lcp_and_invalid_navigation(self):
        t=self.trace();t['traceEvents'].append({'name':'largestContentfulPaint::Candidate','ts':51000,'pid':1,'tid':2})
        d,_,_=normalize(t);self.assertEqual(d['lcp'],50)
        with self.assertRaises(ValueError):normalize(t,navigation=99)
    def test_no_navigation_fails(self):
        with self.assertRaises(ValueError):normalize({'traceEvents':[]})

if __name__=='__main__':unittest.main()
