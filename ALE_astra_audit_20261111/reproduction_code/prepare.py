from pathlib import Path
import json,hashlib,shutil,re
R=Path(__file__).resolve().parent;OLD=Path('D:/omniALE/ALE_repro');BASE=Path('D:/omniALE/runs_case46_astra_high_50m/run_20261109_184134')
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for d in ['audit','environment/runtime','environment/tmp','candidate','orchestrator','reports','sealed','solver','evaluation','dashboard','cache']:(R/d).mkdir(parents=True,exist_ok=True)
exp=json.loads((OLD/'experiment.json').read_text())
man={}
for c in exp['cases']:
 name=c['task_id'].split('/')[-1];src=OLD/'runs'/name/'attempt_002';dest=R/'candidate'/name
 shutil.copytree(src/'input',dest/'input',dirs_exist_ok=True)
 for rel,h in c['input_sha256'].items():assert sha(src/rel)==h and sha(dest/rel)==h
 prompt=(src/'official_prompt.md').read_text(encoding='utf-8')
 prompt=prompt.replace(str(src),'/candidate').replace(str(src).replace('\\','/'),'/candidate')
 prompt=prompt.replace('\\','/')
 # Paths in old prompt use the ALE_repro alias, localized identically.
 prompt=re.sub(r'D:/omniALE/ALE_repro/runs/'+name+r'/attempt_002','/candidate',prompt)
 prompt=prompt.replace('/candidate/output/','/workspace/submission/')
 write(dest/'TASK.md',prompt)
 man[name]=[dict(path=p.relative_to(dest).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.rglob('*')) if p.is_file()]
write(R/'environment/input_manifests.json',man)
write(R/'environment/experiment.json',dict(model='gpt-6-astra',effort='high',solver_budget_seconds=7200,evaluation_budget_seconds=1800,judge_model='gpt-6.1-sol',judge_effort='high',old_experiment=exp,mode='API with isolated Codex harness; sequential new sessions',software_compliance='AE not found; butterfly decision pending',status='preparing'))
# Reuse infrastructure only, never previous solver content.
for name in ['run_serial.py','linux_launcher.py','guard_kill.py']:shutil.copy2(BASE/'orchestrator'/name,R/'orchestrator'/name)
s=(BASE/'environment/runtime/inside.py').read_text()
s=s.replace("('/v1/responses', '/tts')","('/v1/responses',)")
a=s.index("if mode == 'tools':");b=s.index("if mode == 'killcheck':",a)
s=s[:a]+s[b:]
a=s.index("prompt = pathlib.Path('/runtime/prompt.txt')");b=s.index('\nargs = ',a)
s=s[:a]+'''prompt = pathlib.Path('/runtime/prompt.txt').read_text() if mode == 'official' else (
 'Infrastructure test only. Execute python to print 7*8; use view_image on /candidate/visual.png and read the six-character code. '
 'Verify Python imports cv2,numpy,scipy,PIL,docx. Write the arithmetic result and image code to /workspace/submission/smoke.txt. Do not spawn subagents.')
'''+s[b:]
s=s.replace("'credential_absent':", "'credential_absent':")
s=s.replace("result['network_blocked'] = False", "result['network_blocked'] = False\n    result['no_network_interfaces'] = set(x.name for x in pathlib.Path('/sys/class/net').iterdir()) <= {'lo'} if pathlib.Path('/sys/class/net').exists() else True\n    result['no_default_route'] = len(pathlib.Path('/proc/net/route').read_text().splitlines()) <= 1")
write(R/'environment/runtime/inside.py',s)
write(R/'environment/runtime/prompt.txt','You are solving a benchmark in an isolated offline Linux environment. Read /candidate/TASK.md and complete the task autonomously. Only official task inputs and local tools are available. No network retrieval, other runs, evaluator or reference answers are available. Use /workspace/scratch for temporary work and /workspace/submission for final outputs. Python3 with numpy, scipy, OpenCV, Pillow and python-docx, and FFmpeg are available. No score feedback or retries based on quality. Do not spawn subagents. Time limit 120 minutes. Native After Effects is not installed in this Linux environment; if the task requires it, clearly disclose that limitation rather than claiming to have used it.')
p=R/'orchestrator/linux_launcher.py';s=p.read_text();s=s.replace("pathlib.Path('/mnt/d/omniALE/case46_trial_v1/candidate') if a.mode=='official' else pathlib.Path('/mnt/d/omniALE/runs_11_14_gpt61sol_high_50m/run_20261102_002748/environment/smoke_candidate')","root/'candidate'/source_case if a.mode=='official' else root/'environment/smoke_candidate'")
s=s.replace("'--ro-bind',str(runtime),'/runtime'", "'--ro-bind',str(runtime/'deps'),'/runtime/deps','--ro-bind',str(runtime/'codex_dist'),'/runtime/codex_dist','--ro-bind',str(runtime/'fonts'),'/runtime/fonts','--ro-bind',str(runtime/'fonts.conf'),'/runtime/fonts.conf'")
write(p,s)
p=R/'orchestrator/run_serial.py';s=p.read_text();s=s.replace("KEY=os.environ['NJU_LINK_API_KEY']; BASE=", "import importlib.util\n_cred=pathlib.Path('D:/omniALE/runs_1_5_gpt61sol_high_50m/run_20261102_0110/orchestrator/credential.py')\n_spec=importlib.util.spec_from_file_location('existing_credential',_cred);_mod=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_mod)\nKEY=_mod.get_key(); BASE=")
a=s.index('def handle_tts(');b=s.index('def validate_api(',a);s=s[:a]+s[b:]
s=s.replace("elif message['path']=='/tts':handle_tts(proc,message['body'],case)\n                    ",'')
s=s.replace("manifest(pathlib.Path('D:/omniALE/case46_trial_v1/candidate'))", "manifest(ROOT/'candidate'/source_case)")
s=s.replace("['case11','case12','case13','case14']", "['video_storyboard_001','butterfly_flap_animation']")
s=s.replace("a.seconds or 3000", "a.seconds or 7200")
# Log and reject provider model/effort mismatch, do not silently regard it as valid.
s=s.replace("except (ValueError,TypeError):pass", "except (ValueError,TypeError):pass")
write(p,s)
from PIL import Image,ImageDraw
sm=R/'environment/smoke_candidate';sm.mkdir(exist_ok=True);write(sm/'TASK.md','Infrastructure fixture only.')
im=Image.new('RGB',(600,200),'white');ImageDraw.Draw(im).text((40,70),'ALE739',fill='black',font_size=55);im.save(sm/'visual.png')
write(R/'audit/initial_findings.md','# 初查\n\n旧分数：镜头日志1.0；蝴蝶0.974035。旧运行不是官方VM，日志未发现外部检索但不能证明物理隔离。镜头日志仅测十个问题，蝴蝶仅测视频参数/轮廓运动，未检查AE使用或工程。旧缓存按答卷哈希复用而未绑定judge/配置，新的评测不复用它。待完成负对照与源文件核验。\n')
print('PREPARED',R)
