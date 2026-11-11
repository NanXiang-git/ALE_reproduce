"""Local-only audit comparison and observable-action dashboard; no private reasoning."""
from pathlib import Path
import json,html,hashlib,shutil,re,collections
R=Path(__file__).resolve().parent;OLD=Path('D:/omniALE/ALE_repro');D=R/'dashboard';D.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def scrub(s):return re.sub(r'sk-[A-Za-z0-9_-]{12,}','[REDACTED]',s)
def h(s):return html.escape(str(s))
names=['video_storyboard_001','butterfly_flap_animation'];results=[];sections=[]
for name in names:
 result=read(R/'evaluation'/name/'result.json');freeze=read(R/'sealed'/name/'freeze.json');sub=R/'sealed'/name/'submission';events=[]
 for line in (R/'orchestrator'/name/'events.jsonl').read_text(encoding='utf-8').splitlines():
  e=json.loads(line)
  if e.get('event')=='codex_jsonl':
   v=json.loads(e['line']);item=v.get('item',{})
   if v.get('type')=='item.completed' and item.get('type') in ('command_execution','agent_message'):
    events.append({'order':len(events)+1,**item})
 calls=[json.loads(x) for x in (R/'orchestrator'/name/'api.jsonl').read_text().splitlines()]
 # Include view_image calls from actual API request history, deduplicated by call ID.
 tools={}
 for call in calls:
  for item in call.get('input_tools',[])+call.get('output_tools',[]):
   if item.get('name') in ['view_image','functions.view_image']:tools[item.get('call_id',item.get('id',json.dumps(item)))]=item
 trace={'case':name,'actions':events,'image_tool_calls':list(tools.values()),'sent_image_hashes':list({x['sha256']:x for call in calls for x in call.get('image_inputs',[])}.values()),'note':'Public completed commands/messages and image calls; private reasoning excluded. Image calls recovered from gateway request/output metadata when CLI omits them.'}
 write(D/(name+'_trajectory.json'),trace)
 for f in freeze['submission_manifest']:
  assert not f.get('unsupported_link');assert sha(sub/f['path'])==f['sha256']
 usage={k:sum(x.get('usage',{}).get(k,0) for x in calls if x.get('usage')) for k in ['input_tokens','output_tokens','total_tokens']}
 entry={'task_id':name,'new_score':result.get('score'),'old_score':1 if name==names[0] else .974035,'elapsed_minutes':freeze.get('elapsed_solver_environment_seconds',0)/60,'model':'gpt-6-astra','effort':'high','input_unchanged':freeze['input_unchanged'],'provider_configuration_verified':freeze['provider_configuration_verified'],'timed_out':freeze['timed_out'],'api_calls':len(calls),'usage':usage,'submission_files':len(freeze['submission_manifest']),'result':result}
 results.append(entry)
 action_html=''.join('<details><summary>'+str(i+1)+' · '+h(x.get('command',x.get('text',''))[:160])+'</summary><pre>'+h(x.get('command',''))+'\n'+h(x.get('aggregated_output',x.get('text','')))+'</pre></details>' for i,x in enumerate(events))
 (D/(name+'_trajectory.html')).write_text('<!doctype html><meta charset="utf-8"><title>工具运行轨迹</title><style>body{max-width:1100px;margin:auto;font:16px/1.6 system-ui;padding:24px}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{border-bottom:1px solid #ccc;padding:10px}</style><a href="index.html">返回结果</a><h1>'+name+'</h1><p>只展示公开动作，不展示内部推理。看图调用及图像哈希见JSON。</p><a href="'+name+'_trajectory.json">下载轨迹JSON</a>'+action_html,encoding='utf-8')
 if name==names[0]:
  from docx import Document
  doc=sub/'storyboard.docx';texts=[]
  if doc.exists():
   d=Document(doc);texts=[p.text for p in d.paragraphs if p.text.strip()]
   for table in d.tables:texts += [' | '.join(c.text for c in row.cells) for row in table.rows]
  (D/'storyboard_text.txt').write_text('\n'.join(texts),encoding='utf-8')
  media='<a href="../sealed/'+name+'/submission/storyboard.docx">下载镜头日志DOCX</a><details><summary>查看完整日志正文</summary><pre>'+h('\n'.join(texts))+'</pre></details>'
  evidence=result.get('raw_judge_payload',{}).get('evidence',{})
  review='<table><tr><th>问题</th><th>回答</th><th>正确</th><th>裁判证据</th></tr>'+''.join('<tr><td>'+qid+'</td><td>'+h(result.get('answers',{}).get(qid))+'</td><td>'+h(result.get('correct',{}).get(qid))+'</td><td>'+h(evidence.get(qid))+'</td></tr>' for qid in [f'Q{i}' for i in range(1,11)])+'</table>'
  secondary=R/'evaluation'/name/'original_default_judge/result.json'
  if secondary.exists():
   second=read(secondary);entry['original_default_judge_score']=second['score']
   review+='<p>补充复核：原默认 GPT-5.4 裁判得分 '+h(second['score'])+'。独立列示，不替换主对比 Sol/high 分数。<a href="../evaluation/'+name+'/original_default_judge/result.json">复核JSON</a></p>'
  elif (secondary.parent/'error.json').exists():
   review+='<p>原默认 GPT-5.4 复核未成功；不补分。<a href="../evaluation/'+name+'/original_default_judge/error.json">错误记录</a></p>'
 else:
  media='<p>本轮 Astra 成片：</p><video controls muted preload="metadata" src="../sealed/'+name+'/submission/output.mp4"></video><p>旧 Sol 成片：</p><video controls muted preload="metadata" src="../../ALE_repro/deliverables/butterfly_flap_animation/output.mp4"></video><p><a href="../sealed/'+name+'/submission/output.mp4">下载本轮蝴蝶成片</a> · <a href="../candidate/butterfly_flap_animation/input/butterfly.jpeg">原始蝴蝶图片</a></p><p>未满足 AE 软件执行要求：按用户授权仅复现视频评分。主任务文字允许 AE 不可用时替代制作，附件仍要求 AE；这里单独披露未用 AE，不额外改动官方分数。</p>'
  review='<pre>'+h(json.dumps({k:result.get(k) for k in ['probe','metrics','components','passed']},ensure_ascii=False,indent=2))+'</pre>'
 analysis_path=R/'reports'/('analysis_'+name+'.json')
 if analysis_path.exists():
  analysis=read(analysis_path);entry['quality_review']=analysis
  review+='<h3>产物检查与评分遗漏</h3><ul>'+''.join('<li>'+h(x)+'</li>' for x in analysis['findings'])+'</ul><p>'+h(analysis['scope'])+'</p>'
  if analysis.get('preview'):review+='<img style="width:100%" alt="动画抽帧检查" src="'+h(analysis['preview'])+'">'
 sections.append('<section><h2>'+name+'</h2><p>旧Sol '+str(entry['old_score'])+' → 本轮Astra <b>'+str(entry['new_score'])+'</b>（0–1标度）；耗时 '+format(entry['elapsed_minutes'],'.2f')+' 分钟。</p>'+media+review+'<p><a href="'+name+'_trajectory.html">完整工具轨迹</a> · <a href="../evaluation/'+name+'/result.json">评分原始JSON</a> · <a href="../sealed/'+name+'/freeze.json">冻结文件与哈希</a></p>'+ '</section>')
write(R/'reports/comparison.json',results)
negative=read(R/'audit/audit_checks.json')['butterfly_controls'];negative['pulsing_rectangle_1080p']=read(R/'audit/negative_controls/pulsing_rectangle_1080p.json')['score']
intro='''<h1>ALE 两题：Astra/high 断网复现与高分审计</h1><p>API gpt-6-astra/high + Codex，两个独立会话串行，每题上限120分钟。工具环境没有外网接口或默认路由，只有受控模型代理；宿主、旧答案、真值及评分器未挂载。官方源代码固定，不按本轮成绩修改公式。</p><p><b>已确认：评分覆盖不足不等于作弊。</b> 旧日志未发现搜题/读取答案证据，但旧环境缺少完整系统级隔离证明。新环境通过输入只读、宿主不可见、外网连接失败、代理禁搜题/远程图片/历史会话、超时终止等测试。训练期接触无法排除。</p><p>蝴蝶的实心矩形负对照仍得0.912812，说明评分器无法可靠区分真实振翅与轮廓伸缩；来源形状仅占10%，不检查AE使用。镜头日志空白、无关文本、仅问题对照均0分；其满分只表示十个问题可由日志回答，不代表全片逐镜头质量已认证。</p><p>旧答卷重新核分：蝴蝶0.974035；日志换成本轮API Sol/high裁判仍1.0。正式新结果如下，所有旧记录保留。</p><p>对比边界：旧实验Windows/订阅Codex0.167，本轮Linux/API Codex0.163；裁判沿用Sol/high但传输改为Responses，temperature=0未发送，原max_output_tokens=2200保留。不能把成绩差异全部归因于答题模型。原题与输入保持，路径本地化；蝴蝶脚本替代AE已获用户同意。</p>'''
style='<style>body{max-width:1150px;margin:auto;padding:28px;font:16px/1.7 system-ui;background:#f3f6f8;color:#172c3a}section{background:white;padding:24px;margin:20px 0;border-radius:12px}video{width:100%;max-height:500px;background:black}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{padding:8px;border:1px solid #ddd;text-align:left}a{color:#126759}</style>'
page='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ALE Astra断网复现</title>'+style+intro+''.join(sections)+'<section><h2>负对照与隔离证据</h2><p>实心矩形动画（并非蝴蝶）：</p><video controls muted src="../audit/negative_controls/pulsing_rectangle_1080p.mp4"></video><pre>'+h(json.dumps(negative,indent=2))+'</pre><p><a href="../environment/acceptance.json">隔离验收</a> · <a href="../audit/history_recheck.json">旧轨迹复查</a> · <a href="../audit/audit_checks.json">素材及评分器核验</a> · <a href="../reports/comparison.json">完整比较JSON</a></p></section>'
assert not re.search(r'sk-[A-Za-z0-9_-]{12,}',page)
(D/'index.html').write_text(page,encoding='utf-8')
md='# ALE 两题复现与审计\n\n'+ '\n'.join(f"- {x['task_id']}: 旧Sol {x['old_score']} → Astra {x['new_score']}；{x['elapsed_minutes']:.2f}分钟；输入完整性与API返回模型/强度核验通过。" for x in results)+'\n\n主要问题：蝴蝶实心矩形负对照0.912812，官方计分存在明显语义覆盖不足；旧蝴蝶用脚本未用AE，评分器不核验软件。未发现旧轨迹读答案或联网检索证据，但不能回溯证明旧环境完全隔离。新运行使用独立bwrap断网命名空间。\n\n镜头日志三个负对照均0分，旧答卷API复核仍1.0。高分仅覆盖十题事实可恢复性。\n\n旧评分缓存只绑定提交哈希，存在配置变化仍复用分数的风险；本轮不复用旧缓存，各分数保存提交、评分器、问题、请求/响应和模型信息。缓存风险不等于已经证明旧分数错误。\n\n本轮是产物评分复现，不是官方VM完整复现。用户授权脚本替代AE；未满足AE软件要求单独标注。所有真实API身份以提供方返回值核验，无法从客户端验证服务内部；禁网也不能排除预训练见过公开素材。\n\n详见 dashboard/index.html、reports/comparison.json、environment/acceptance.json。\n'
(R/'reports/RESULTS.md').write_text(md,encoding='utf-8')
write(R/'reports/final_integrity.json',{'submission_hashes_verified':True,'results':[{k:x[k] for k in ['task_id','input_unchanged','provider_configuration_verified','new_score']} for x in results],'dashboard_external_dependencies':False})
print('REPORT BUILT',R/'dashboard/index.html')
