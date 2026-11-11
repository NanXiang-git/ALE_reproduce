"""Trusted WSL launcher with an external wall-clock watchdog."""
import argparse, json, os, pathlib, signal, subprocess, threading, time
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--case',required=True);p.add_argument('--mode',default='official');p.add_argument('--seconds',type=int,default=3000);a=p.parse_args()
root=pathlib.Path(a.root); work=root/'solver'/a.case; runtime=pathlib.Path('/mnt/d/omniALE/runs_11_14_gpt61sol_high_50m/run_20261102_002748/environment/runtime')
source_case=a.case.split('_retry')[0]
candidate=root/'candidate'/source_case if a.mode=='official' else root/'environment/smoke_candidate'
for name in ('submission','scratch','home','.cache','tmp','codex_home'):(work/name).mkdir(parents=True,exist_ok=True)
started=time.time(); deadline=started+a.seconds
(work/'DEADLINE.json').write_text(json.dumps({'start_unix':started,'deadline_unix':deadline,'wall_clock_seconds':a.seconds,'mode':a.mode}))
cmd=['bwrap','--unshare-all','--unshare-user','--die-with-parent','--disable-userns','--cap-drop','ALL','--clearenv',
 '--ro-bind','/usr/bin','/usr/bin','--ro-bind','/usr/lib','/usr/lib','--ro-bind','/usr/share','/usr/share',
 '--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64',
 '--ro-bind-try','/usr/lib64','/usr/lib64','--ro-bind','/etc/fonts','/etc/fonts',
 '--ro-bind','/etc/ssl','/etc/ssl','--ro-bind','/etc/alternatives','/etc/alternatives','--ro-bind-try','/etc/ld.so.cache','/etc/ld.so.cache',
 '--proc','/proc','--dev','/dev','--ro-bind',str(root/'environment/deps'),'/runtime/deps','--ro-bind',str(root/'environment/bin'),'/runtime/bin','--ro-bind',str(runtime/'codex_dist'),'/runtime/codex_dist','--ro-bind',str(runtime/'fonts'),'/runtime/fonts','--ro-bind',str(runtime/'fonts.conf'),'/runtime/fonts.conf','--ro-bind',str(root/'environment/runtime/inside.py'),'/runtime/inside.py','--ro-bind',str(root/'environment/runtime/prompt.txt'),'/runtime/prompt.txt','--ro-bind',str(candidate),'/candidate',
 '--bind',str(work),'/workspace','--bind',str(work/'tmp'),'/tmp','--chdir','/workspace']
env={'PATH':'/runtime/bin:/runtime/codex_dist/package/vendor/x86_64-unknown-linux-musl/bin:/usr/bin:/bin',
 'HOME':'/workspace/home','CODEX_HOME':'/workspace/codex_home','LANG':'C.UTF-8',
 'TMPDIR':'/workspace/tmp','TMP':'/workspace/tmp','TEMP':'/workspace/tmp',
 'XDG_CACHE_HOME':'/workspace/.cache','PYTHONPATH':'/runtime/deps','PYTHONDONTWRITEBYTECODE':'1',
 'HF_HUB_OFFLINE':'1','HF_HOME':'/workspace/.cache/huggingface','FONTCONFIG_FILE':'/runtime/fonts.conf',
 'OMP_NUM_THREADS':'6','OPENBLAS_NUM_THREADS':'6','TOKENIZERS_PARALLELISM':'false'}
for k,v in env.items():cmd+=['--setenv',k,v]
cmd+=['/usr/bin/python3','/runtime/inside.py','killcheck' if a.mode=='wallcheck' else a.mode]
print(json.dumps({'op':'event','event':'namespace_start','utc':started,'deadline_unix':deadline,'case':a.case,'mode':a.mode}),flush=True)
proc=subprocess.Popen(cmd,start_new_session=True)
print(json.dumps({'op':'event','event':'watchdog_target','bwrap_pid':proc.pid,'deadline_unix':deadline}),flush=True)
timed_out=threading.Event()
def timeout():
    timed_out.set()
    # Killing the namespace init/launcher destroys every process inside, even setsid children.
    try:os.killpg(proc.pid,signal.SIGKILL)
    except ProcessLookupError:pass
done=threading.Event();mono_start=time.monotonic()
def watchdog():
    while not done.wait(.05):
        now=time.time()
        if a.mode=='wallcheck' and time.monotonic()-mono_start>=2:now=deadline+1
        if now>=deadline or time.monotonic()-mono_start>=a.seconds:
            timeout();return
timer=threading.Thread(target=watchdog,daemon=True);timer.start()
code=proc.wait();done.set()
result={'op':'event','event':'namespace_exit','case':a.case,'returncode':code,'timed_out':timed_out.is_set(),'utc':time.time(),'elapsed_seconds':time.time()-started}
(root/'orchestrator'/f'{a.case}_termination.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
raise SystemExit(0 if timed_out.is_set() else code)
