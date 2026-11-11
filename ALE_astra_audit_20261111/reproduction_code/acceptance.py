from pathlib import Path
import json,hashlib,time
R=Path(__file__).resolve().parent
def events(name):return [json.loads(x) for x in (R/'orchestrator'/name/'events.jsonl').read_text().splitlines()]
sm=events('smoke_fixed');tool=events('tools');kill=json.loads((R/'orchestrator/killcheck_termination.json').read_text())
assert kill['timed_out']
heartbeat=R/'solver/killcheck/heartbeat';before=heartbeat.read_bytes();time.sleep(1);assert before==heartbeat.read_bytes()
assert any(x.get('event')=='gateway_restrictions_verified' for x in tool)
assert any(x.get('event')=='dependencies_verified' for x in tool)
for es in [sm,tool]:
 checks=next(x['checks'] for x in es if x.get('event')=='isolation_checks');assert all(v for k,v in checks.items() if k!='visible_process_count')
assert any(x.get('event')=='codex_exit' and x['returncode']==0 for x in sm)
text=(R/'solver/smoke_fixed/submission/smoke.txt').read_text();assert '56' in text and 'ALE739' in text
apis=[json.loads(x) for x in (R/'orchestrator/smoke_fixed/api.jsonl').read_text().splitlines()]
assert any(x.get('image_inputs') for x in apis),'No actual image sent to model'
assert all(x.get('model')=='gpt-6-astra' and x.get('reasoning',{}).get('effort')=='high' for x in apis if x.get('status')=='completed')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
config={str(p.relative_to(R)):sha(p) for folder in ['orchestrator','environment/runtime','candidate'] for p in (R/folder).rglob('*') if p.is_file() and (folder=='candidate' or p.suffix in ['.py','.txt']) and not any(x in p.parts for x in ['smoke','smoke_fixed','tools','killcheck'])}
out={'passed':True,'network':'bwrap unshare-all network namespace; no default route; external TCP denied; only host model proxy over stdio','filesystem':'candidate readonly, dedicated workspace, runtime-only libraries; host/evaluator/old answers not mounted','gateway_tests':'wrong model, web search, remote image, prior conversation all rejected before network','watchdog_verified':True,'model_image_input_verified':True,'model':'gpt-6-astra','effort':'high','codex':'0.163.0; differs from old0.167.0-alpha.3.2','initial_smoke':'dependency failure retained; not a benchmark attempt','hashes':config,'limits':['Not official ALE VM/harness','Backend model identity relies on provider response; client cannot inspect server internals','Offline inference tools do not rule out pretraining exposure','No AE; user approved artifact-score reproduction']}
(R/'environment/acceptance.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('ACCEPTANCE PASSED')
