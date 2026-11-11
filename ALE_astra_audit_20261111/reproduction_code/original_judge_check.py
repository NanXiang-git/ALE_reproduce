"""Secondary official-default judge; not substituted for the Sol/high primary comparison."""
from pathlib import Path
import sys,json,time,asyncio,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));import audit_evaluate as a
async def run():
 folder=R/'evaluation/video_storyboard_001/original_default_judge';folder.mkdir(exist_ok=True)
 main=json.loads((folder.parent/'result.json').read_text());deadline=(folder.parent/'result.json').stat().st_mtime-main.get('elapsed_seconds',0)+1800
 async def adapter(content,model,max_tokens,temperature,**kw):
  assert not (folder/'request.json').exists(),'No repeated judge attempt'
  body={'model':'gpt-5.4','messages':[{'role':'user','content':content}],'max_completion_tokens':max_tokens,'temperature':temperature,'response_format':{'type':'json_object'}}
  a.write(folder/'request.json',body);left=deadline-time.time();assert left>5,'Combined evaluation budget exhausted'
  t=time.time();res=a.host.SESSION.post(a.host.BASE+'/chat/completions',json=body,headers={'Authorization':'Bearer '+a.host.KEY},timeout=(15,min(300,left)))
  a.write(folder/'transport.json',{'http_status':res.status_code,'elapsed_seconds':time.time()-t,'combined_deadline_unix':deadline,'model':'gpt-5.4','temperature':temperature,'max_completion_tokens':max_tokens})
  if not res.ok:raise RuntimeError('Original-default judge HTTP '+str(res.status_code))
  d=res.json();a.write(folder/'response.json',d);assert d.get('model','').startswith('gpt-5.4'),'Unexpected returned model'
  assert d['choices'][0].get('finish_reason')=='stop','incomplete response'
  assert time.time()<deadline,'Combined evaluation time exceeded'
  return json.loads(d['choices'][0]['message']['content'])
 a.S.llm_multimodal_json=adapter
 p=R/'sealed/video_storyboard_001/submission/storyboard.docx'
 try:
  r=await a.S.score_storyboard_docx(storyboard_docx=p.read_bytes(),question_docx=a.Q.read_bytes(),model='gpt-5.4')
  r.update(model_requested='gpt-5.4',scope='Secondary original-default model/formula/prompt/temp0/token2200 via local API; not exact official infrastructure',submission_sha256=a.sha(p),evaluator_sha256=a.sha(a.SFILE));a.write(folder/'result.json',r);print('ORIGINAL DEFAULT JUDGE',r['score'],flush=True)
 except Exception as e:a.write(folder/'error.json',{'error':str(e)});print('ORIGINAL DEFAULT JUDGE UNAVAILABLE',type(e).__name__,flush=True)
if __name__=='__main__':asyncio.run(run())
