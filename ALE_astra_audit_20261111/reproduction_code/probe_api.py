from pathlib import Path
import sys,json,time
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'orchestrator'))
import run_serial as host
results=[]
for model in ['gpt-6-astra','gpt-6.1-sol']:
 t=time.monotonic()
 r=host.SESSION.post(host.BASE+'/responses',headers={'Authorization':'Bearer '+host.KEY},json={'model':model,'reasoning':{'effort':'high'},'input':'Reply with exactly ALE_PROBE_OK.','max_output_tokens':512,'store':False},timeout=(20,120))
 d=r.json();record={'requested_model':model,'http_status':r.status_code,'model':d.get('model'),'status':d.get('status'),'reasoning':d.get('reasoning'),'elapsed':time.monotonic()-t,'usage':d.get('usage')}
 record['text']=''.join(c.get('text','') for i in d.get('output',[]) for c in i.get('content',[]) if c.get('type')=='output_text')
 if not r.ok:record['error']=str(d)[:600].replace(host.KEY,'[REDACTED]')
 results.append(record);host.write(R/'environment/api_probe.json',results);print(json.dumps(record),flush=True)
 assert r.ok and d.get('model')==model and d.get('reasoning',{}).get('effort')=='high' and record['text'].strip()=='ALE_PROBE_OK'
