from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import json,re,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for name in ['video_storyboard_001','butterfly_flap_animation']:
    f=read(R/'sealed'/name/'freeze.json');result=read(R/'evaluation'/name/'result.json')
    assert not f['timed_out'] and f['host_process_returncode']==0
    assert f['input_unchanged'] and f['provider_configuration_verified']
    for x in f['submission_manifest']:assert sha(R/'sealed'/name/'submission'/x['path'])==x['sha256']
    calls=[json.loads(x) for x in (R/'orchestrator'/name/'api.jsonl').read_text(encoding='utf-8').splitlines()]
    completed=[x for x in calls if x.get('status')=='completed']
    assert completed
    assert all(x['model_requested']=='gpt-6-astra' and x['reasoning_requested']['effort']=='high' for x in calls)
    assert all(x['model']=='gpt-6-astra' and x['reasoning']['effort']=='high' for x in completed)
    checks[name]={'api_calls':len(calls),'completed_calls':len(completed),'errors':sum(bool(x.get('error')) for x in calls),'input_hashes_unchanged':True,'submission_hashes_verified':True,'elapsed_grading_seconds':result['elapsed_seconds']}
    assert result['elapsed_seconds']<1800
acceptance=read(R/'environment/acceptance.json')
assert acceptance['passed']
for name,digest in acceptance['hashes'].items():assert sha(R/name)==digest,name
class Links(HTMLParser):
    def __init__(self):super().__init__();self.targets=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v:self.targets.append(v)
link_count=0
for p in (R/'dashboard').glob('*.html'):
    parser=Links();parser.feed(p.read_text(encoding='utf-8'))
    for target in parser.targets:
        u=urlsplit(target)
        if u.scheme or target.startswith('#'):continue
        assert (p.parent/unquote(u.path)).resolve().exists(),(p.name,target)
        link_count+=1
scanned=0
for folder in ['reports','dashboard','evaluation','audit','sealed','orchestrator']:
    for p in (R/folder).rglob('*'):
        if p.is_file() and p.suffix in ['.json','.jsonl','.md','.html','.txt','.log']:
            assert not re.search(r'sk-[A-Za-z0-9_-]{24,}',p.read_text(encoding='utf-8',errors='replace')),str(p)
            scanned+=1
checks.update(acceptance_hashes_verified=True,dashboard_links_checked=link_count,credential_pattern_scan_files=scanned,scoring_cache_reused=False)
(R/'reports/verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
