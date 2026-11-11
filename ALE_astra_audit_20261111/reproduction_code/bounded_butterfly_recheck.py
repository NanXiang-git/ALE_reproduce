"""Recheck the same frozen output after an over-budget evaluator incident."""
from pathlib import Path
import subprocess,sys,time,json,ctypes,os
R=Path(__file__).resolve().parent;folder=R/'evaluation/butterfly_flap_animation'
original=folder/'result.json';archived=folder/'result_over_budget.json'
assert original.exists() and not archived.exists()
old=json.loads(original.read_text());assert old['elapsed_seconds']>1800
original.rename(archived)
start=time.time();mono=time.perf_counter();deadline=start+1800
ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',TEMP=str(R/'environment/tmp'),TMP=str(R/'environment/tmp'))
try:
    with (folder/'recheck_stdout.log').open('w',encoding='utf-8') as log:
        p=subprocess.Popen([sys.executable,str(R/'audit_evaluate.py'),'butterfly_flap_animation'],env=env,stdout=log,stderr=subprocess.STDOUT)
        while p.poll() is None:
            if time.time()>=deadline or time.perf_counter()-mono>=1800:
                subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True);raise TimeoutError('30 minute evaluator cap exceeded')
            time.sleep(.2)
        assert p.returncode==0
    elapsed=time.time()-start;assert elapsed<1800
    result=json.loads(original.read_text());assert result['submission_sha256']==old['submission_sha256']
    meta={'reason':'Prior deterministic evaluator returned after 6505 seconds wall time; original result retained, excluded from in-budget result. Possible host clock/suspension incident; precise cause not established.','same_frozen_submission':True,'solver_rerun':False,'quality_feedback':False,'prior_score':old['score'],'new_score':result['score'],'wall_seconds':elapsed,'monotonic_seconds':time.perf_counter()-mono,'within_30_minutes':True}
    (folder/'recheck_provenance.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta),flush=True)
finally:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
