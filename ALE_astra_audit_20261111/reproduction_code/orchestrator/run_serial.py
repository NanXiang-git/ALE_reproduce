"""Trusted Windows gateway/orchestrator. Never executes solver code on the host."""
import argparse, base64, ctypes, datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile, threading, time
import requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
LINUX_ROOT='/mnt/d/'+str(ROOT.relative_to('D:/')).replace('\\','/')
import importlib.util
_cred=pathlib.Path('D:/omniALE/runs_1_5_gpt61sol_high_50m/run_20261102_0110/orchestrator/credential.py')
_spec=importlib.util.spec_from_file_location('existing_credential',_cred);_mod=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_mod)
KEY=_mod.get_key(); BASE='https://api-temporary.nju-link.com/v1'
SESSION=requests.Session();SESSION.trust_env=False
VOICES={'Microsoft Huihui Desktop','Microsoft Kangkang','Microsoft Yaoyao','Microsoft Zira Desktop','Microsoft David Desktop'}
for k in ('TEMP','TMP','TMPDIR'):os.environ[k]=str(ROOT/'environment'/'tmp')
TTS_SCRIPT=ROOT/'orchestrator'/'speak.ps1'

def clean(x):return json.loads(json.dumps(x,ensure_ascii=False).replace(KEY,'[REDACTED]'))
def write(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(clean(x),ensure_ascii=False,indent=2),encoding='utf-8')
def send(proc,x):proc.stdin.write(json.dumps(x,separators=(',',':')).encode()+b'\n');proc.stdin.flush()
def reply(proc,status,data):
    send(proc,{'status':status,'content_type':'application/json'})
    send(proc,{'chunk':base64.b64encode(json.dumps(data).encode()).decode()})
    send(proc,{'done':True})

def validate_api(body):
    if body.get('previous_response_id') or body.get('conversation'):raise ValueError('External conversation history disabled')
    if body.get('model')!='gpt-6-astra':raise ValueError('Only authorized solver model is allowed')
    if body.get('reasoning',{}).get('effort')!='high':raise ValueError('Solver reasoning effort must be high')
    for tool in body.get('tools',[]):
        if tool.get('type') not in ('function','custom','local_shell'):raise ValueError('Remote or additional tools are disabled: '+str(tool.get('type')))
    def walk(obj):
        if isinstance(obj,dict):
            if 'file_id' in obj:raise ValueError('Remote stored files disabled')
            if obj.get('type') in ('input_image','input_file'):
                for k in ('image_url','file_url'):
                    if k in obj and not str(obj[k]).startswith('data:'):raise ValueError('Remote media URLs are disabled')
            for x in obj.values():walk(x)
        elif isinstance(obj,list):
            for x in obj:walk(x)
    walk(body)

def handle_api(proc,body,log,deadline=None):
    start=time.time(); rec={'utc':start,'model_requested':body.get('model'),'reasoning_requested':body.get('reasoning'),
        'request_sha256':hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),
        'input_items':len(body.get('input',[])) if isinstance(body.get('input'),list) else None}
    begun=False
    # Record observable calls and hashes of actual image inputs, never private reasoning.
    rec['input_tools']=[{k:v for k,v in it.items() if k in ('type','name','call_id','arguments','input')} for it in body.get('input',[]) if isinstance(it,dict) and it.get('type') in ('function_call','custom_tool_call','local_shell_call')]
    rec['image_inputs']=[]
    def images(obj):
        if isinstance(obj,dict):
            if obj.get('type')=='input_image':
                u=obj.get('image_url','')
                if u.startswith('data:'):
                    try:
                        raw=base64.b64decode(u.split(',',1)[1]);rec['image_inputs'].append({'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                    except Exception:pass
            for v in obj.values():images(v)
        elif isinstance(obj,list):
            for v in obj:images(v)
    images(body.get('input',[]))
    try:
        if deadline is not None and time.time()>=deadline:raise TimeoutError('Absolute solver deadline passed')
        validate_api(body)
        body['store']=False
        with SESSION.post(BASE+'/responses',json=body,headers={'Authorization':'Bearer '+KEY},timeout=(30,300),stream=True) as r:
            rec['http_status']=r.status_code
            send(proc,{'status':r.status_code,'content_type':r.headers.get('Content-Type','application/json')});begun=True
            pending=b''
            for chunk in r.iter_content(chunk_size=4096):
                if deadline is not None and time.time()>=deadline:raise TimeoutError('Absolute solver deadline passed during response')
                if not chunk:continue
                send(proc,{'chunk':base64.b64encode(chunk).decode()})
                pending+=chunk
                while b'\n' in pending:
                    line,pending=pending.split(b'\n',1)
                    if line.startswith(b'data:'):
                        try:
                            e=json.loads(line[5:].strip())
                            if e.get('type') in ('response.completed','response.failed','response.incomplete'):
                                response=e.get('response',{})
                                rec.update({k:response.get(k) for k in ('id','model','status','usage','reasoning','error')})
                                rec['output_tools']=[it for it in response.get('output',[]) if it.get('type') in ('function_call','custom_tool_call','local_shell_call')]
                                if response.get('model')!='gpt-6-astra' or response.get('reasoning',{}).get('effort')!='high':
                                    rec['configuration_violation']=True
                        except (ValueError,TypeError):pass
                if len(pending)>2_000_000:pending=b''
            if r.status_code>=400:rec['error_body']=pending.decode(errors='replace')[:2000]
            send(proc,{'done':True})
    except Exception as e:
        rec['error']=str(e)
        try:
            if begun:send(proc,{'done':True})
            else:reply(proc,502,{'error':str(e).replace(KEY,'[REDACTED]')})
        except (BrokenPipeError,OSError):pass
    rec['elapsed_seconds']=time.time()-start
    log.write(json.dumps(clean(rec),ensure_ascii=False)+'\n');log.flush()

def manifest(directory):
    rows=[]
    for f in sorted(directory.rglob('*')):
        if f.is_symlink() or (hasattr(f,'is_junction') and f.is_junction()):
            rows.append({'path':str(f.relative_to(directory)),'unsupported_link':True});continue
        if f.is_file():
            h=hashlib.sha256()
            with f.open('rb') as stream:
                for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
            rows.append({'path':str(f.relative_to(directory)),'bytes':f.stat().st_size,'sha256':h.hexdigest()})
    return rows

def run(case,mode,seconds):
    work=ROOT/'solver'/case
    if work.exists():raise RuntimeError('Refusing to overwrite an existing attempt: '+case)
    logs=ROOT/'orchestrator'/case;logs.mkdir(parents=True)
    source_case=case.split('_retry')[0]
    if mode=='official':
        expected=json.loads((ROOT/'environment'/'input_manifests.json').read_text())[source_case]
        actual=manifest(ROOT/'candidate'/source_case)
        normalized=[{**x,'path':x['path'].replace('\\','/')} for x in actual]
        if normalized!=expected:raise RuntimeError('Public input hash changed before launch: '+case)
        write(logs/'input_manifest.json',normalized)
    args=['wsl','-d','Ubuntu','--','env','PYTHONDONTWRITEBYTECODE=1','python3',LINUX_ROOT+'/orchestrator/linux_launcher.py','--root',LINUX_ROOT,'--case',case,'--mode',mode,'--seconds',str(seconds)]
    started=time.time();print(json.dumps({'case':case,'mode':mode,'event':'launch','utc':started}),flush=True)
    target={};watch_done=threading.Event()
    def host_watchdog():
        while not watch_done.wait(.05):
            if target.get('pid') and time.time()>=target['deadline']:
                observed=time.time()
                result=subprocess.run(['wsl','-d','Ubuntu','--','env','PYTHONDONTWRITEBYTECODE=1','python3',LINUX_ROOT+'/orchestrator/guard_kill.py',str(target['pid']),case],capture_output=True,timeout=20)
                write(logs/'host_watchdog.json',{'observed_unix':observed,'deadline_unix':target['deadline'],'returncode':result.returncode,'late_seconds':observed-target['deadline']})
                return
    threading.Thread(target=host_watchdog,daemon=True).start()
    with (logs/'wsl_stderr.log').open('wb') as stderr, (logs/'events.jsonl').open('w',encoding='utf-8') as events, (logs/'api.jsonl').open('w',encoding='utf-8') as api:
        proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
        for line in proc.stdout:
            try:message=json.loads(line)
            except ValueError:
                events.write(json.dumps({'unparsed':line.decode(errors='replace')})+'\n');events.flush();continue
            if message.get('op')=='event':
                if message.get('event')=='watchdog_target':target.update(pid=message['bwrap_pid'],deadline=message['deadline_unix'])
                events.write(json.dumps(clean(message),ensure_ascii=False)+'\n');events.flush()
                if message.get('event') not in ('codex_jsonl','codex_stderr'):print(json.dumps(clean(message),ensure_ascii=False),flush=True)
            elif message.get('op')=='http':
                try:
                    if target.get('deadline') and time.time()>=target['deadline']:reply(proc,408,{'error':'Absolute solver deadline passed'})
                    elif message['path']=='/v1/responses':handle_api(proc,message['body'],api,target.get('deadline'))
                    else:reply(proc,403,{'error':'Unsupported endpoint'})
                except Exception as e:
                    try:reply(proc,500,{'error':str(e).replace(KEY,'[REDACTED]')})
                    except Exception:pass
        code=proc.wait()
    watch_done.set()
    end=time.time()
    result={'case':case,'source_case':source_case,'mode':mode,'host_process_returncode':code,'host_start_unix':started,'host_end_unix':end,'grading':'not_run'}
    term=ROOT/'orchestrator'/f'{case}_termination.json'
    if term.exists():result['termination']=json.loads(term.read_text())
    if mode=='official':
        result['input_unchanged']=[{**x,'path':x['path'].replace('\\','/')} for x in manifest(ROOT/'candidate'/source_case)]==expected
        calls=[json.loads(line) for line in (logs/'api.jsonl').read_text(encoding='utf-8').splitlines()]
        result['provider_configuration_verified']=bool(calls) and all(not x.get('configuration_violation') for x in calls) and any(x.get('model')=='gpt-6-astra' and x.get('reasoning',{}).get('effort')=='high' for x in calls)
        sealed=ROOT/'sealed'/case;sealed.mkdir()
        submission=work/'submission'
        if submission.exists():submission.rename(sealed/'submission')
        else:(sealed/'submission').mkdir()
        result['submission_manifest']=manifest(sealed/'submission')
        result['submission_manifest_sha256']=hashlib.sha256(json.dumps(result['submission_manifest'],sort_keys=True).encode()).hexdigest()
        result['elapsed_solver_environment_seconds']=result.get('termination',{}).get('elapsed_seconds')
        result['timed_out']=result.get('termination',{}).get('timed_out')
        final=work/'final_message.txt'
        if final.exists():shutil.copyfile(final,sealed/'final_message.txt')
        write(sealed/'freeze.json',result)
    write(ROOT/'reports'/f'{case}_run.json',result)
    print(json.dumps({'case':case,'event':'finished','returncode':code,'files':len(result.get('submission_manifest',[]))}),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['smoke','killcheck','wallcheck','tools','official'],required=True);p.add_argument('--case');p.add_argument('--cases',nargs='+');p.add_argument('--seconds',type=int);a=p.parse_args()
    previous=ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    if not previous:raise RuntimeError('Could not prevent idle system sleep during the controlled run')
    try:
        if a.mode=='official':
            gate=json.loads((ROOT/'environment'/'acceptance.json').read_text())
            assert gate.get('passed') is True,'Isolation/tool acceptance must pass before official launch'
            cases=a.cases or ([a.case] if a.case else ['video_storyboard_001','butterfly_flap_animation'])
            for case in cases:run(case,'official',a.seconds or 7200)
        else:run(a.case or a.mode,a.mode,a.seconds or (8 if a.mode=='killcheck' else 180))
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
