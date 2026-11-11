"""Sequential authorized run, independent post-freeze grading. No automatic quality retry."""
from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent
def call(args,timeout=None):
 p=subprocess.Popen([sys.executable,*map(str,args)])
 try:code=p.wait(timeout=timeout)
 except subprocess.TimeoutExpired:
  subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True);p.wait();raise
 if code:raise RuntimeError('Process failed: '+str(code))
if __name__=='__main__':
 status={}
 for name in ['video_storyboard_001','butterfly_flap_animation']:
  status[name]='running';(R/'reports/status.json').write_text(json.dumps(status))
  call([R/'orchestrator/run_serial.py','--mode','official','--case',name,'--seconds','7200'])
  status[name]='frozen';(R/'reports/status.json').write_text(json.dumps(status))
  try:call([R/'audit_evaluate.py',name],timeout=1800);status[name]='graded'
  except Exception as e:status[name]='grading_error';(R/'reports'/f'{name}_grading_error.txt').write_text(str(e))
  (R/'reports/status.json').write_text(json.dumps(status))
 print('SERIAL RUN COMPLETE',json.dumps(status),flush=True)
