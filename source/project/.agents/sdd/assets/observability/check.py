#!/usr/bin/env python3
"""Read-only local stack preflight and event lookup. No result implies durability."""
import argparse, json, urllib.parse, urllib.request, urllib.error

p=argparse.ArgumentParser()
p.add_argument('--collector',default='http://127.0.0.1:13133')
p.add_argument('--loki',default='http://127.0.0.1:3100')
p.add_argument('--tempo',default='http://127.0.0.1:3200')
p.add_argument('--prometheus',default='http://127.0.0.1:9090')
p.add_argument('--project')
p.add_argument('--event-id')
args=p.parse_args()
if bool(args.project) != bool(args.event_id): p.error('--project and --event-id must be used together')
def get(url):
    with urllib.request.urlopen(url,timeout=3) as r: return r.read().decode('utf-8')
failed=False
for name,url in [('collector',args.collector+'/'),('loki',args.loki+'/ready'),('tempo',args.tempo+'/ready'),('prometheus',args.prometheus+'/-/ready')]:
    try: print(name, 'reachable', get(url)[:120])
    except (OSError,urllib.error.URLError) as e: failed=True; print(name,'UNAVAILABLE',type(e).__name__,str(e))
if args.project:
    # JSON string escaping gives valid quoted LogQL literals and avoids query injection.
    expression='{project='+json.dumps(args.project)+'} |= '+json.dumps(args.event_id)
    url=args.loki+'/loki/api/v1/query_range?'+urllib.parse.urlencode({'query':expression,'limit':100})
    try:
        result=json.loads(get(url))
        print('lookup',json.dumps(result,ensure_ascii=False))
        if not result.get('data',{}).get('result'): failed=True; print('NOT_FOUND: absence is not proof of loss; check time range and ingestion delay')
    except (OSError,ValueError,urllib.error.URLError) as e: failed=True; print('lookup UNAVAILABLE',str(e))
print('Reachability does not prove pipeline health, queue durability, or complete records.')
raise SystemExit(1 if failed else 0)
