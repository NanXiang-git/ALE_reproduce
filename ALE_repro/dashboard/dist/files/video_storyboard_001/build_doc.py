import json,zipfile,html,xml.etree.ElementTree as ET
from pathlib import Path
rows=json.loads(Path('work/log.json').read_text(encoding='utf-8'))
for r in rows:
 if r['title']=='Rabbit and monkey travel': r['text']=''
 if r['title']=='Monkey speaks': r['text']='Japanese dialogue card includes 萬事お委せなさい (“Leave everything to me”).'
# A short excerpt avoids uncertain small characters in the longer dialogue card.
for r in rows:
 if r['title']=='Dialogue across the ledge':
  r['text']='The long card begins 冗談ぢゃありませんよ and includes 貴方を山羊の居る川向へお渡し申さうと思ってやって來たのです. The next card reads さうか 宜しい すぐ案内せい.'
Path('work/log.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def esc(t): return html.escape(t,quote=False)
def p(t,style='Normal',keep=False):
 return '<w:p><w:pPr><w:pStyle w:val="'+style+'"/>'+('<w:keepNext/>' if keep else '')+'</w:pPr><w:r><w:t xml:space="preserve">'+esc(t)+'</w:t></w:r></w:p>'
body=p('ARCHIVAL SHOT LOG / CONTINUITY REPORT','Title')+p('A Wolf is a Wolf · source-print visual record','Subtitle')
body+=p('Source: Yasuji_Murata-_A_Wolf_is_a_Wolf_(1931).ogv | 400 × 300 | running time 11:16.224.','Meta')
body+=p('Elapsed times run from the first source frame, including access titles and closing credits. Boundaries are approximate to the nearest second; fades and closely related cuts are grouped as segments. Japanese excerpts identify visible intertitles; English glosses describe the lettering, not independently verified events. The black-and-white print carries an NFC mark at lower right through most of the film.','Meta')
# Automatic pagination, with each segment kept as a readable block.
for i,r in enumerate(rows,1):
 body+=p(f'S{i:02d}   {r["start"]} – {r["end"]}   |   {r["title"]}','Heading2',True)
 body+=p(r['body'],'Normal',bool(r['text']))
 if r['text']: body+=p('On screen: '+r['text'],'TextNote')
body+='<w:sectPr><w:headerReference w:type="default" r:id="rId2"/><w:footerReference w:type="default" r:id="rId3"/><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1050" w:bottom="1000" w:left="1050" w:header="450" w:footer="450"/></w:sectPr>'
document='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="'+W+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'+body+'</w:body></w:document>'
styles='''<w:styles xmlns:w="'''+W+'''"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Yu Mincho"/><w:sz w:val="21"/><w:lang w:val="en-US" w:eastAsia="ja-JP"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="85" w:line="260" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:spacing w:after="140"/></w:pPr><w:rPr><w:b/><w:color w:val="1D384D"/><w:sz w:val="34"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:sz w:val="27"/><w:color w:val="36596E"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Meta"><w:name w:val="Meta"/><w:rPr><w:sz w:val="19"/><w:color w:val="4C5560"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:pPr><w:keepNext/><w:spacing w:before="150" w:after="55"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:color w:val="1D384D"/><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TextNote"><w:name w:val="On-screen text"/><w:pPr><w:ind w:left="180"/><w:spacing w:after="105"/></w:pPr><w:rPr><w:sz w:val="20"/></w:rPr></w:style></w:styles>'''
header='<w:hdr xmlns:w="'+W+'">'+p('A WOLF IS A WOLF  |  SOURCE-PRINT CONTINUITY','Meta')+'</w:hdr>'
footer='<w:ftr xmlns:w="'+W+'"><w:p><w:pPr><w:jc w:val="right"/></w:pPr><w:r><w:t>Shot log · </w:t></w:r><w:fldSimple w:instr="PAGE"/></w:p></w:ftr>'
rels='''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>'''
rootrels='''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
types='''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>'''
files={'[Content_Types].xml':types,'_rels/.rels':rootrels,'word/document.xml':document,'word/styles.xml':styles,'word/header1.xml':header,'word/footer1.xml':footer,'word/_rels/document.xml.rels':rels}
Path('output').mkdir(exist_ok=True)
with zipfile.ZipFile('output/storyboard.docx','w',zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():
  ET.fromstring(data)
  z.writestr(name,data.encode('utf-8'))
with zipfile.ZipFile('output/storyboard.docx') as z:
 assert z.testzip() is None
 root=ET.fromstring(z.read('word/document.xml'))
 assert sum(1 for p0 in root.findall('.//{'+W+'}p') if p0.find('{'+W+'}pPr/{'+W+'}pStyle').get('{'+W+'}val')=='Heading2')==60
print('Validated DOCX package:',Path('output/storyboard.docx').stat().st_size,'bytes; 60 segments')
