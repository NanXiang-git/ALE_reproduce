from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parent
p=R/'environment/experiment.json';d=json.loads(p.read_text(encoding='utf-8'));d.update(status='complete',final_scores={'video_storyboard_001':1.0,'butterfly_flap_animation':1.0},secondary_judge_status='GPT-5.4 HTTP 429; no score',evaluation_incident='Butterfly first evaluation exceeded wall-clock cap; archived, same frozen submission rechecked in 4.42s with score1.0. Solver not rerun.');p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'audit/AUDIT.md';s=p.read_text(encoding='utf-8').replace('# 复现审计记录（正式新答卷尚在运行）','# 复现审计记录（已完成）');s+='\n## 本轮结果\n\n- Astra/high镜头日志1.0，答题约16.80分钟，主评分8.94秒。\n- Astra/high蝴蝶视频1.0，答题约5.33分钟；未使用AE。首次评分记录6505秒，作为超限异常保留，未计为限时合格；同一冻结答卷重新核分4.42秒（评分函数3.62秒）仍1.0。未修改产物、未重新答题。\n- 主机时间/暂停可能影响墙钟记录，具体原因未确定；不能宣称首次蝴蝶评分满足30分钟。答题阶段日志还存在墙钟与单调时钟的小幅差异，耗时按冻结记录披露，不做精确性能排名。\n- GPT-5.4补充复核返回HTTP429，无有效分数。\n- 两题49次完成调用均返回gpt-6-astra/high，候选输入、隔离配置、冻结答卷哈希通过复核，未复用评分缓存。\n- 本轮正文检查、轨迹和评分遗漏见reports/analysis_*.json及dashboard/index.html。\n';p.write_text(s,encoding='utf-8')
p=R/'reports/RESULTS.md';s=p.read_text(encoding='utf-8');s+='\n## 评分异常及补充复核\n\n蝴蝶首次评分记录6505秒墙钟耗时，超过30分钟，已归档为evaluation/butterfly_flap_animation/result_over_budget.json；同一冻结视频重新限时核分，总计4.42秒，仍为1.0。未重新答题或修改视频。宿主时钟或暂停的具体原因未确定。镜头日志主评分8.94秒；原默认GPT-5.4复核HTTP429，无有效分数。\n\n## 实际产物检查\n\n镜头日志64个连续分段覆盖00:00–11:16.22，DOCX结构可解析，抽查6帧；未逐帧核验全部描述、时间与译文，未做页面渲染验收。蝴蝶150帧全部可解码，1920×1080、30fps、5秒，抽查12帧显示原图纹样、分层透视折叠，无检测到画面边缘裁切。蝴蝶满分较旧分数高2.5965分，全部来自源形状子项的变化。\n\n未满足AE软件执行要求。主任务允许AE缺失时替代制作，附件仍要求AE；此处遵循用户明确授权，只复现产物评分。\n\n[本地结果面板](../dashboard/index.html)包含视频、DOCX、运行轨迹、各题错误与遗漏分析。\n';p.write_text(s,encoding='utf-8')
# Preserve old dashboard and add a local comparison entry; no external publication.
old=Path('D:/omniALE/ALE_repro/dashboard/dist/index.html');s=old.read_text(encoding='utf-8')
if 'id="astra-audit-entry"' not in s:
    (R/'audit/previous_dashboard_index.html').write_text(s,encoding='utf-8')
    link='<a id="astra-audit-entry" href="../../../ALE_astra_audit_20261111/dashboard/index.html" style="position:fixed;right:20px;bottom:20px;z-index:1000;padding:12px 18px;background:#173e64;color:white;border-radius:8px;box-shadow:0 2px 10px #0003">查看 Astra 断网复现与评分审计 →</a>'
    assert '</body>' in s;s=s.replace('</body>',link+'</body>');old.write_text(s,encoding='utf-8')
wrapper=Path('D:/omniALE/ALE_Astra_复现结果.html');wrapper.write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=ALE_astra_audit_20261111/dashboard/index.html"><a href="ALE_astra_audit_20261111/dashboard/index.html">查看ALE Astra复现结果</a>',encoding='utf-8')
assert (old.parent/'../../../ALE_astra_audit_20261111/dashboard/index.html').resolve().exists()
# Inspect actual completed command history for potential external access, distinct from constants/metadata.
review={}
for name in ['video_storyboard_001','butterfly_flap_animation']:
    events=[json.loads(x) for x in (R/'orchestrator'/name/'events.jsonl').read_text(encoding='utf-8').splitlines()];commands=[]
    for e in events:
        if e.get('event')=='codex_jsonl':
            v=json.loads(e['line']);item=v.get('item',{})
            if v.get('type')=='item.completed' and item.get('type')=='command_execution':commands.append(item['command'])
    flags=[]
    for i,c in enumerate(commands):
        terms=re.findall(r'(?i)\b(?:curl|wget|requests|urllib|web_search)\b|/mnt/[cd]/|https?://|evaluator|answer.key',c)
        if terms:flags.append({'command_index':i,'terms':terms})
    review[name]={'commands':len(commands),'potential_access_matches':flags,'note':'Pattern scan is supplemental; enforced namespace and gateway isolation are primary evidence. Matches require context review.'}
(R/'audit/new_action_access_review.json').write_text(json.dumps(review,indent=2),encoding='utf-8');print(json.dumps(review,indent=2))
print('FINALIZED',wrapper)
