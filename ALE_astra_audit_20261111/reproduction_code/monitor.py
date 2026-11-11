from pathlib import Path
import json,time
R=Path(__file__).resolve().parent
print((R/'reports/status.json').read_text())
for name in ['video_storyboard_001','butterfly_flap_animation']:
    folder=R/'orchestrator'/name
    if not folder.exists(): continue
    calls=[json.loads(x) for x in (folder/'api.jsonl').read_text(encoding='utf-8').splitlines()]
    events=[json.loads(x) for x in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]
    items=[]
    for e in events:
        if e.get('event')=='codex_jsonl':
            v=json.loads(e['line'])
            if v.get('type')=='item.completed': items.append(v.get('item',{}))
    messages=[x.get('text') for x in items if x.get('type')=='agent_message']
    starts=[x for x in events if x.get('event')=='watchdog_target']
    print(json.dumps({'case':name,'api_calls':len(calls),'image_hashes':len({im['sha256'] for c in calls for im in c.get('image_inputs',[])}),'api_errors':sum(bool(x.get('error')) for x in calls),'commands':sum(x.get('type')=='command_execution' for x in items),'last_public_message':messages[-1] if messages else None,'api_log_age_seconds':round(time.time()-(folder/'api.jsonl').stat().st_mtime)},ensure_ascii=False))
