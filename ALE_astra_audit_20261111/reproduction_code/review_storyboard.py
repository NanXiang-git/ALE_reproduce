from pathlib import Path
from docx import Document
import re,json,zipfile
R=Path(__file__).resolve().parent
p=R/'sealed/video_storyboard_001/submission/storyboard.docx'
d=Document(p);rows=[r for t in d.tables for r in t.rows[1:]]
def sec(s):
    m,s=s.split(':');return int(m)*60+float(s)
segments=[]
for row in rows:
    times=re.findall(r'\d{2}:\d{2}(?:\.\d+)?',row.cells[0].text)
    assert len(times)==2
    segments.append({'id':row.cells[0].text.split()[0],'start':sec(times[0]),'end':sec(times[1])})
assert len({x['id'] for x in segments})==len(segments)==64
assert segments[0]['start']==0 and segments[-1]['end']==676.22
assert all(x['end']>x['start'] for x in segments)
assert all(a['end']==b['start'] for a,b in zip(segments,segments[1:]))
with zipfile.ZipFile(p) as z:assert z.testzip() is None
data={'scope':'独立解析冻结DOCX并抽查原片6帧；不是全片逐帧人工标注，也未做Word页面渲染验收。以下检查不改变官方分数。',
      'findings':[
        'Sol/high 根据日志回答10个QC问题，10/10正确，官方分数1.0；没有观察到这10项上的判错。',
        '独立解析确认64个唯一编号段落，时间从00:00连续到11:16.22，均有起止时间和描述；DOCX压缩包及python-docx解析有效。',
        '抽查原片06:56、07:49、08:29、10:12、10:38、10:45六帧，核对了梯子、兔旁猴影、对话卡、猴桥和桥边动作等画面；抽查不能证明其余叙述全部准确。',
        '日志主动说明采用连续分段、秒级约略时间；部分段落合并多个镜头，不能把满分解读为逐帧切点或全片镜头边界准确率100%。',
        '日志的完整性、全部日文翻译、版式与未被10个问题覆盖的叙述没有被官方分数全面检验。',
        '验证脚本曾因变量名复用出现AttributeError，随后修正并通过；属运行轨迹中的工具错误，不是最终DOCX损坏。',
        '模型最终回复附带了不适用于本题的AE说明；AE要求仅属于蝴蝶题，本题允许任意DOCX工作流，不据此扣分。',
        '原默认GPT-5.4补充复核收到HTTP 429，没有产生可用评分；主比较仍为指定的Sol/high。'
      ],'segments':segments,'preview':'../audit/storyboard_source_spotcheck.jpg'}
(R/'reports/analysis_video_storyboard_001.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('STORYBOARD STRUCTURE VERIFIED',len(segments))
