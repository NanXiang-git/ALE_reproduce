"""Host-only audit, official grading and negative controls. Never mounted for solver."""
from pathlib import Path
import sys,types,importlib.util,json,hashlib,asyncio,time,subprocess,re,zipfile
import numpy as np,cv2
from docx import Document
R=Path(__file__).resolve().parent;OLD=Path('D:/omniALE/ALE_repro');REPO=OLD/'sources/official-v1/agents-last-exam-d9abc0734b56ea34116c5bfcbdd0b808269ab9e2'
sys.path.insert(0,str(R/'orchestrator'));import run_serial as host
def write(p,x):host.write(p,x)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
stub=types.ModuleType('tasks.utils.evaluation');stub.llm_multimodal_json=None;stub.resolve_llm_judge_model=lambda **kw:kw.get('default') or 'gpt-6.1-sol';sys.modules['tasks.utils.evaluation']=stub
SFILE=REPO/'tasks/visual_media/video_storyboard_001/scripts/evaluate_storyboard.py'
BFILE=REPO/'tasks/visual_media/butterfly_flap_animation/scripts/score_outputs.py'
S=module('official_storyboard',SFILE);B=module('official_butterfly',BFILE)
Q=R/'candidate/video_storyboard_001/input/video_storyboard_qa_set.docx';SOURCE=R/'candidate/butterfly_flap_animation/input/butterfly.jpeg'

def do_judge(folder,deadline):
 async def call(content,model,max_tokens,temperature,**kwargs):
  assert time.time()<deadline,'judge budget exhausted'
  prompt='\n'.join(x['text'] for x in content)
  folder.mkdir(parents=True,exist_ok=True)
  assert not (folder/'request.json').exists(),'No retries or cached-score reuse'
  body={'model':model,'reasoning':{'effort':'high'},'input':[{'role':'user','content':[{'type':'input_text','text':prompt}]}],'store':False,'max_output_tokens':max_tokens,'text':{'format':{'type':'json_object'}}}
  write(folder/'request.json',body)
  meta={'model':model,'effort':'high','original_temperature':temperature,'temperature_sent':False,'transport':'Responses API; not prior subscription Codex judge','deadline':deadline}
  start=time.time()
  try:
   res=host.SESSION.post(host.BASE+'/responses',headers={'Authorization':'Bearer '+host.KEY},json=body,timeout=(15,min(300,max(1,deadline-time.time()))))
   meta['http_status']=res.status_code
   if not res.ok:raise RuntimeError('Judge HTTP '+str(res.status_code))
   d=res.json();write(folder/'response.json',d)
   assert d.get('model')==model and d.get('reasoning',{}).get('effort')=='high','wrong model or effort'
   assert d.get('status')=='completed','incomplete response'
   text=''.join(x.get('text','') for item in d.get('output',[]) for x in item.get('content',[]) if x.get('type')=='output_text')
   parsed=json.loads(text);assert isinstance(parsed.get('answers'),dict)
   assert time.time()<=deadline,'judge returned after budget'
   meta.update(status='completed',usage=d.get('usage'));return parsed
  except Exception as e:meta.update(status='failed',error=str(e).replace(host.KEY,'[REDACTED]'));raise
  finally:meta['elapsed_seconds']=time.time()-start;write(folder/'call.json',meta)
 return call

def judge_doc(doc,folder,model='gpt-6.1-sol',deadline=None):
 deadline=deadline or time.time()+1800;S.llm_multimodal_json=do_judge(folder/'judge',deadline)
 r=asyncio.run(S.score_storyboard_docx(storyboard_docx=doc,question_docx=Q.read_bytes(),model=model))
 r.update(submission_sha256=hashlib.sha256(doc).hexdigest(),questions_sha256=sha(Q),evaluator_sha256=sha(SFILE),model=model,effort='high',temperature_difference='official0 not sent with high reasoning; recorded not equivalent',score_scale='0..1')
 write(folder/'result.json',r);return r

def docbytes(text):
 import io
 d=Document();d.add_paragraph(text);b=io.BytesIO();d.save(b);return b.getvalue()

def render_control(dest,kind):
 w,h=640,360;n=144
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','640x360','-r','30','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(dest)],stdin=subprocess.PIPE)
 for i in range(n):
  u=i/(n-1);im=np.zeros((h,w,3),np.uint8)
  cx=int(320+150*np.sin(2*np.pi*u)) if kind!='static' else 320
  cy=int(180+60*np.sin(4*np.pi*u)) if kind!='static' else 180
  width=int(120+90*(.5+.5*np.cos(8*np.pi*u))) if kind=='pulsing_rectangle' else 160
  cv2.rectangle(im,(cx-width//2,cy-38),(cx+width//2,cy+38),(80,160,220),-1)
  proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0

def audit():
 out=R/'audit';checks={}
 with zipfile.ZipFile(Q) as z:
  text=S.extract_docx_text(Q.read_bytes()).text
  (out/'qc_visible_text.txt').write_text(text,encoding='utf-8')
  checks['qc_document']={'members':z.namelist(),'visible_text_chars':len(text),'answer_marker_matches':re.findall(r'(?i)answer\s*key|correct\s*answer|答案|正确答案',text),'comments_or_embeddings':[x for x in z.namelist() if any(y in x for y in ['comments','embeddings','customXml'])],'public_by_official_task':True}
 oldexp=json.loads((OLD/'experiment.json').read_text());checks['input_hashes']={}
 for c in oldexp['cases']:
  name=c['task_id'].split('/')[-1];checks['input_hashes'][name]={rel:sha(R/'candidate'/name/rel)==h for rel,h in c['input_sha256'].items()}
 checks['source_hashes']={'storyboard':sha(SFILE),'butterfly':sha(BFILE)}
 # Verify the full retained action history structure and identify evidence candidates for manual review.
 for name in ['video_storyboard_001','butterfly_flap_animation']:
  p=OLD/'dashboard/data'/(name+'-actions.json');d=json.loads(p.read_text());checks[name+'_history']={'sha256':sha(p),'structure':type(d).__name__,'top_keys':list(d)[:20] if isinstance(d,dict) else None}
 checks['old_butterfly_script']={'path':'runs/butterfly_flap_animation/attempt_002/work/render.py','sha256':sha(OLD/'runs/butterfly_flap_animation/attempt_002/work/render.py'),'uses_opencv_ffmpeg':True,'after_effects_evidence':False}
 # Audit-only artifact scoring cannot feed anything back to the new solver.
 prior=OLD/'deliverables/butterfly_flap_animation/output.mp4'
 r=B.score_video(prior,SOURCE).to_dict();write(out/'old_butterfly_recomputed.json',r);checks['old_butterfly_recomputed']=r['score']
 controls=out/'negative_controls';controls.mkdir(exist_ok=True)
 for kind in ['static','moving_rectangle','pulsing_rectangle']:
  dest=controls/(kind+'.mp4');render_control(dest,kind);r=B.score_video(dest,SOURCE).to_dict();write(controls/(kind+'.json'),r);print('BUTTERFLY_CONTROL',kind,r['score'],flush=True)
 checks['butterfly_controls']={kind:json.loads((controls/(kind+'.json')).read_text())['score'] for kind in ['static','moving_rectangle','pulsing_rectangle']}
 write(out/'audit_checks.json',checks)
 # Exact official prompt with unsupported document content, not a rewritten strict judge.
 for label,text in [('empty',''),('unrelated','00:00–00:10: A blue square is shown on a white background. No animals or narrative events are visible.'),('questions_only',S.extract_docx_text(Q.read_bytes()).text)]:
  folder=controls/label;folder.mkdir(exist_ok=True);b=docbytes(text);(folder/'storyboard.docx').write_bytes(b)
  try:r=judge_doc(b,folder);print('STORY_CONTROL',label,r['score'],flush=True)
  except Exception as e:write(folder/'error.json',{'error':str(e)});print('STORY_CONTROL',label,'ERROR',flush=True)

def evaluate(name):
 folder=R/'evaluation'/name;folder.mkdir(exist_ok=True);assert not (folder/'result.json').exists(),'Already graded'
 start=time.time();sub=R/'sealed'/name/'submission'
 freeze=json.loads((R/'sealed'/name/'freeze.json').read_text())
 assert freeze['input_unchanged'] and freeze['provider_configuration_verified'],'run integrity or model identity not verified'
 if any(x.get('unsupported_link') for x in freeze['submission_manifest']):raise RuntimeError('Unsafe submission link')
 for item in freeze['submission_manifest']:assert sha(sub/item['path'])==item['sha256']
 if name=='video_storyboard_001':
  p=sub/'storyboard.docx'
  if not p.exists():r={'score':0,'error':'missing required output'}
  else:r=judge_doc(p.read_bytes(),folder,deadline=start+1800)
 else:
  p=sub/'output.mp4';r=B.score_video(p,SOURCE).to_dict();r.update(evaluator_sha256=sha(BFILE),submission_sha256=sha(p) if p.exists() else None,software_compliant=False,software_note='User authorized non-AE artifact-score reproduction. No claim of AE compliance.')
 r.update(elapsed_seconds=time.time()-start,solver_model='gpt-6-astra',solver_effort='high',scope='local artifact-score replication; not exact official VM/harness replication')
 write(folder/'result.json',r);print('GRADED',name,r['score'],flush=True)
if __name__=='__main__':
 if sys.argv[1]=='audit':audit()
 else:evaluate(sys.argv[1])
