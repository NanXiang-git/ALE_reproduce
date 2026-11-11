from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from pathlib import Path
import json, re

segments=[]
def add(start,end,title,visual,text=''):
    segments.append(dict(id=f'S{len(segments)+1:02d}',start=start,end=end,title=title,visual=visual,text=text))

add('00:00','00:06','Modern identification card',
    'White Japanese and English lettering on black, followed by black leader.',
    'Visible English: “A Wolf is a Wolf” and “(1931, Yasuji Murata, 11 min)”.')
add('00:06','00:22','Original opening cards',
    'A framed Japanese production card fades in and out. An illustrated title shows a large black wolf above smaller animal silhouettes; a short Japanese animator credit follows. The boxed NFC mark appears at lower right and remains through most of the print.',
    'Japanese cards identify a production credit, the title A Wolf is a Wolf, and the animator Murata Yasuji.')
add('00:22','00:29','Village establishing view',
    'Thatched roofs, a fence, and a spreading tree against a pale sky. Dissolve to a road outside a white-walled house with an open window, hedge, and bare tree.')
add('00:29','00:45','Two animals outside the house',
    'A slender, horned goat faces a round-bellied raccoon dog with dark eye patches and a thick tail. They gesture and bow toward one another, then walk off left, the goat ahead.')
add('00:45','01:10','Woodland walk and transformation',
    'The pair walk left among bare trunks. The raccoon dog leaps and changes into a bald-headed, dark-robed figure. The goat falls backward with stars around its head, then gets up. The figure changes back; the two gesture at one another. A circular iris isolates the raccoon dog.')
add('01:10','01:15','Apology intertitle and iris return',
    'Japanese dialogue card on black, then the raccoon dog reappears in a circular iris.',
    'The speaker asks to be forgiven and says he will not frighten the other again.')
add('01:15','01:30','Walking together again',
    'The goat approaches the raccoon dog from the right. They bow and gesture. The raccoon dog turns left and walks ahead, with the goat following through the trees.')

add('01:30','01:47','Fruit tree',
    'Close view of round fruit on branches dissolves to the two animals below the trunk. The raccoon dog jumps against the tree and fruit falls around them. The goat kicks the trunk, sits down, and more fruit falls. Both collect fruit from the ground.')
add('01:47','02:00','Wolf in the woods',
    'A black wolf with pointed ears, long muzzle, pale eyes, and a long tail emerges from behind trunks. It walks right on all fours across the woodland floor, passing behind foreground trees.')
add('02:00','02:06','Eating beneath the tree',
    'The raccoon dog and goat sit on opposite sides of the trunk, bringing fruit to their mouths. Fruit, skins, and small pieces litter the ground.')
add('02:06','02:14','Wolf reaches a rocky edge',
    'The wolf continues right through bare woodland to a projecting rock ledge. It stops, lifts its muzzle, then leans over the edge and looks downward.')
add('02:14','02:23','Return to the fruit tree; flight',
    'The goat stands, drops backward, and stretches flat along the ground at the trunk. The wolf bounds in from the left. The raccoon dog jumps away to the right and runs through the trees; the wolf bends near the flattened goat, then runs after the raccoon dog.')
add('02:23','02:37','Pursuit and curled animal',
    'The wolf runs right behind the raccoon dog. At a group of rocks the raccoon dog curls into a ball. The wolf stands upright, raises a hind leg, and kicks the ball away to the right.')
add('02:37','02:50','Rolling down the slope',
    'The curled raccoon dog rolls down a sloping, rocky path, its face and tail rotating into view. It strikes a tree, with stars at the impact, then uncurls at the base. Cut back to the upright wolf gesturing beside the rocks.')
add('02:50','03:00','Wolf passes the fruit tree',
    'The flattened goat remains beside the trunk amid fruit debris. The wolf enters from the right, bends down by the trunk, then passes to the left and leaves. The tree view fades to black.')

add('03:00','03:08','Meeting announced',
    'A vertical Japanese intertitle appears on black.',
    'The card says that a village meeting was held that night to discuss measures against the violent wolf.')
add('03:08','03:30','Animals seated indoors',
    'A hanging lamp lights animals seated in a circle on the floor. Closer views move across a floppy-eared dog, horned goats, a pig, and the round raccoon dog; several rest their heads on their hands. The raccoon dog straightens and stands.')
add('03:30','03:41','Raccoon dog addresses the meeting',
    'After a dialogue card, the standing raccoon dog gestures broadly and raises both arms while the others remain seated. A second dialogue card follows.',
    'First card: he has a good idea and asks the others to leave it to him. Second card: he introduces a demonstration—doing it “like this”.')
add('03:41','03:52','Transformation demonstration',
    'The raccoon dog changes into a tall, pale, octopus-like figure with a bulbous head and long tentacles. The goat beside it recoils onto all fours. The figure changes back to the round raccoon dog, followed by a dialogue card.',
    'The card says he will frighten the wolf in this way and then show the others the wolf captured alive.')
add('03:52','04:01','Iris close and next-morning card',
    'A circular iris holds on the raccoon dog and closes to black. A short vertical Japanese time card fades in and out.',
    'Next morning.')
add('04:01','04:10','Raccoon dog sets out',
    'Wearing a neck cloth, short trousers, and dark shoes, the raccoon dog marches through the bare forest. A wide view shows it continuing across open ground with distant hills.')
add('04:10','04:30','Wolf on high rocks; approach below',
    'The wolf sits atop a jagged rock outcrop. Cuts alternate with the raccoon dog marching beneath steep mountain walls and appearing small on an open mountainside. The wolf rises, watches, and leaps off the outcrop; it then appears among large rock slabs.')

add('04:30','04:45','Encounter among rock faces',
    'The raccoon dog continues along the cliff base, stops, and turns. The wolf appears beside a tall rock, followed by a close view of its pale eyes and exposed teeth. An iris close-up shows the raccoon dog facing toward it and gesturing.')
add('04:45','04:47','Call to the wolf',
    'Large vertical Japanese lettering on black.',
    '“Hey, wolf!”')
add('04:47','05:00','Successive transformations',
    'The raccoon dog changes into an upright, pale bear-shaped figure. Intercuts show the black wolf walking closer across the rocky ground. The bear-shaped figure changes back; the raccoon dog bends down and becomes the tall, tentacled figure seen at the meeting.')
add('05:00','05:13','Wolf and tentacled figure',
    'The wolf walks past the tentacled figure, turns back, bares its teeth, and crouches. The figure bends its head down. A brief dialogue card interrupts; the wolf then leaps toward the figure.',
    'Brief card at about 05:11: “Oh no!” / “I’ve made a mistake!”')
add('05:13','05:32','Return toward the village',
    'The raccoon dog is again in its round form and clothing, walking with head and shoulders lowered along the rocks and through the forest. Intercut views show a group of animals waiting by a bare tree. It enters their view from the left and approaches.')
add('05:32','05:47','Facing the waiting group',
    'A circular close-up shows the dog and other waiting animals. Another iris isolates the raccoon dog from behind and in profile as it turns its head and gestures. In the wider view it bends low before the group; the image fades out.')
add('05:47','06:06','Season card and mountain landscape',
    'A Japanese intertitle dissolves into a wide mountain valley with a few buildings. Successive dissolves cover the hills and valley with snow. The snowy view fades to black.',
    'Autumn has passed and winter has arrived.')

add('06:06','06:23','Squirrel lookout above the courtyard',
    'A squirrel with a large bushy tail sits in a fork of a bare tree overlooking a building and an animal gathering. Rabbits hold hands and move in a circle, shown closer through a circular mask. The squirrel holds a telescope to its eye, lowers it, turns, and looks toward the mountains.')
add('06:23','06:37','Circular view across snowy mountains',
    'Within the telescope-like circular field, the view moves over snowy peaks, gullies, and a track. Near the end, the dark wolf appears at the lower right, moving along the snowy slope. Cut back to the squirrel looking through the telescope.')
add('06:37','06:44','Lookout descends and calls out',
    'The squirrel drops from the tree, lands, straightens, and opens its mouth. A Japanese warning card intervenes, then the squirrel leans forward again.',
    '“The wolf has come down the mountain!”')
add('06:44','06:48','Animals scatter in the courtyard',
    'The rabbits break their linked circle and run, some tumbling. A wider view shows pigs, horned goats, and other animals hurrying across the open space in front of the building.')
add('06:48','06:55','Wolf on snowy woodland slope',
    'The black wolf walks right on all fours at the foot of a snow-covered, wooded hillside. A trail of dark footprints remains behind it.')
add('06:55','07:01','Squirrel climbs the house ladder',
    'Against a plain building wall, the bushy-tailed squirrel climbs a fixed vertical wooden ladder using its forepaws and feet. It reaches a projecting rung/platform beneath a small suspended alarm fixture and repeatedly reaches upward to operate it.')
add('07:01','07:12','Warning spreads among houses',
    'Two round animals hurry past thatched houses, raising their arms toward windows and doors; goats and other animals join the movement along the street. A brief return shot shows the squirrel still at the top of the wall-mounted ladder, working the alarm fixture.')

add('07:12','07:20','Interior scramble and doorway',
    'Inside a house, a pig jumps beside a square recessed hearth in a raised floor. A large smoke-like cloud billows up; the pig tumbles off the platform, gets up, and runs outside. In a separate dark lane, a small dark, pointed-eared animal runs into a doorway.')
add('07:20','07:30','Houses and a barrel',
    'A rabbit and a pig hurry along house fronts and turn toward entrances. The pig moves into a narrow lane, approaches an open barrel beside leaning boards, and jumps into it, leaving its upper body above the rim.')
add('07:30','07:35','Wolf continues through the woods',
    'The wolf walks right between bare trunks across pale ground, its long muzzle forward and tail trailing.')
add('07:35','07:41','Barrel overturned',
    'The pig remains in the barrel. Three smaller pigs approach; the barrel tips over. The large pig gets out beside it with dark liquid coating its head and upper body.')
add('07:41','07:52','Rabbit and dark monkey silhouette',
    'A rabbit runs across open ground and stops beside a house. At about 07:47 a black, shadow-like silhouette of a long-tailed monkey drops into view beside it and tumbles low. The monkey rises, faces the rabbit, and gestures; pale facial details show against its dark body.')
add('07:52','08:03','Monkey and rabbit travel together',
    'The monkey moves left with the rabbit immediately behind it across a bare landscape. After a brief view of villagers disappearing into a house, the pair continue along the village street.')
add('08:03','08:16','At a closed house door',
    'The rabbit and monkey stop at a plank door beneath a thatched roof. The rabbit knocks or pushes at the door. A horned goat opens it; the rabbit enters, followed by the monkey, and the door closes.')

add('08:16','08:26','Conversation inside the house',
    'The goat sits on the edge of a raised room while the rabbit and dark monkey stand below. Sliding panels with landscape designs, a round hanging object, hanging strips, and stacked boards are visible. An iris close-up isolates the monkey, which folds its arms and then puts its hands at its waist.')
add('08:26','08:32','Monkey’s dialogue card',
    'Vertical Japanese dialogue on black, followed by the monkey in the circular close-up.',
    'The speaker says he has an idea and asks that everything be left to him.')
add('08:32','08:44','Monkey leaves the house',
    'The goat gets up; all three gesture. Outside, the monkey comes through the doorway first. The goat and rabbit follow to the threshold and wave as the monkey gestures back, then walks right. Fade to black and into rocks.')
add('08:44','08:54','Monkeys at the cliff base',
    'A dark monkey enters among angular boulders below a steep rock face and climbs onto a stone. Another approaches from the right. They look and gesture upward; additional dark figures are visible among the rocks.')
add('08:54','09:07','Wolf above the chasm',
    'The wolf reaches a high projecting cliff beside a bare tree and looks across. A reverse wide view shows several small pale animals, including horned goats, on the opposite rocky rim. Back at the wolf, the view tilts down the sheer cliff to a monkey below.')
add('09:07','09:15','Monkey climbs to the wolf',
    'The monkey bounds upward over rocks, with another monkey below. It reaches the lip beside the tree where the wolf waits. In a circular close-up it grips the edge with one hand and lifts the other in greeting.')
add('09:15','09:25','Greeting and wolf’s response',
    'A greeting card is followed by an iris close-up of the wolf leaning forward with its teeth showing. A second dialogue card appears; the monkey is then shown hanging at the edge and raising one hand.',
    'First card: “Hello, General Wolf!” Second card: the wolf remarks that a monkey has arrived at a convenient moment and orders it not to move.')

add('09:25','09:42','Offer to take the wolf across',
    'A longer Japanese dialogue card is followed by close-ups of the monkey and wolf, then a short reply card.',
    'The monkey’s card calls him the wolf’s subject and says the monkeys have come to take the wolf across to where the goats are. The reply tells him to lead the way immediately.')
add('09:42','09:55','Monkeys summoned upward',
    'The wolf stands upright beside the tree. The monkey pulls itself onto the ledge and signals downward and upward with its arms. Many monkeys gather among the boulders below, climb the cliff, reach the ledge, and begin ascending the tree while the wolf watches.')
add('09:55','10:05','Linked monkeys up cliff and tree',
    'Alternating views show monkeys stretched in a line up the rock face and clustered along the tree trunk. Circular close views show successive monkeys climbing past and joining the others, their bodies linked end to end.')
add('10:05','10:13','Living bridge lowered across the gap',
    'Wide view: two sheer rock cliffs are separated by a deep, open ravine. A long chain of linked monkeys extends along a branch on the left. Its free end swings down and reaches the right cliff; the left end lowers along the tree. The joined bodies hang in a shallow curve across the gap, forming a living bridge.')
add('10:13','10:20','Monkey steps onto the living bridge',
    'With the wolf still beside the tree on the left ledge, the single monkey gestures, steps onto the linked bodies, and walks right across them. Mid-span it stops, bends down, and addresses a monkey in the chain.')
add('10:20','10:22','Instruction on the bridge',
    'Short vertical Japanese dialogue card on black.',
    'The speaker urges the others to hold firm / says he is counting on them.')
add('10:22','10:28','Monkey completes the crossing',
    'The monkey straightens and continues right along the chain. It steps onto the far rock ledge, turns back toward the wolf, and extends an arm in a beckoning gesture. The linked monkeys remain stretched between the cliffs.')

add('10:28','10:32','Wolf follows onto the bridge',
    'Cut to the wolf still at the tree-side cliff. It rises on its hind legs, approaches the edge, and steps from the rock onto the chain of monkeys, proceeding right in the direction the monkey has just taken.')
add('10:32','10:42','Wolf over the ravine',
    'The wolf walks upright along the linked bodies, then bends and crouches on them. A downward-looking insert shows a rocky slope and boulders far below. Back on the bridge, pale concentric circles surround the hunched wolf as it looks down and clings close to the chain.')
add('10:42','10:45','Signal from the far ledge',
    'The monkey on the right cliff gestures toward the bridge, crouches, and then raises both arms overhead. The monkey anchoring that end remains at the edge; monkeys along the chain begin raising their limbs.')
add('10:45','10:48','Chain parts; wolf falls',
    'Back at mid-span, the linked bodies separate beneath the wolf. In the wide ravine view, the two ends swing down beside the cliffs while the wolf drops through the open center, limbs spread. It falls out of the lower frame; a pale burst rises from below. The wolf is not shown returning to either ledge.')
add('10:48','10:53','Animals at the rim',
    'A row of rabbits, horned goats, and round-faced animals peers over a rocky edge, then raises forelegs and bobs up and down. The view fades to black.')
add('10:53','11:02','Closing narrative card',
    'Vertical Japanese intertitle fades in and out on black.',
    'The card says that happy days returned once more to the village at the foot of the mountain.')
add('11:02','11:16.22','End title, black, and modern closing credit',
    'The original Japanese title and an end character appear, followed by black from about 11:06 to 11:10. A modern bilingual credit fades in and remains to the end of the file.',
    'Original card: A Wolf is a Wolf / End. The English closing credit identifies the National Project for the Sustainability of Born-Digital Cinema, support by Japan’s Agency for Cultural Affairs in fiscal 2016, January 2017, and the National Film Center, The Museum of Modern Art, Tokyo.')

Path('/workspace/scratch/log_segments.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))

# Readable fixed page groups, with each continuity segment kept together.
doc=Document()
sec=doc.sections[0]
sec.page_width=Inches(8.27); sec.page_height=Inches(11.69)
sec.top_margin=Inches(.62); sec.bottom_margin=Inches(.62)
sec.left_margin=Inches(.65); sec.right_margin=Inches(.65)
sec.header_distance=Inches(.25); sec.footer_distance=Inches(.25)
normal=doc.styles['Normal']
normal.font.name='Calibri'; normal.font.size=Pt(10.5)
normal.paragraph_format.space_after=Pt(3)
normal.paragraph_format.line_spacing=1.03
for name in ['Title','Subtitle','Heading 1','Heading 2']:
    doc.styles[name].font.name='Calibri'
header=sec.header.paragraphs[0]
header.text='ARCHIVAL SHOT LOG  /  A WOLF IS A WOLF'
header.runs[0].font.size=Pt(8)
header.runs[0].font.color.rgb=RGBColor.from_string('526171')
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=footer.add_run('Source elapsed time  •  ');r.font.size=Pt(8)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

p=doc.add_paragraph();p.paragraph_format.space_after=Pt(2)
r=p.add_run('Archival shot log');r.bold=True;r.font.size=Pt(23);r.font.color.rgb=RGBColor.from_string('243747')
p=doc.add_paragraph('A Wolf is a Wolf (1931)  |  Source-print continuity report')
p.paragraph_format.space_after=Pt(8);p.runs[0].font.size=Pt(12)
p=doc.add_paragraph()
r=p.add_run('Source: ');r.bold=True
p.add_run('Yasuji_Murata-_A_Wolf_is_a_Wolf_(1931).ogv')
for r in p.runs:r.font.size=Pt(9)
p=doc.add_paragraph('Coverage: 00:00–11:16.22, including opening and closing cards. Times are elapsed from the first source frame, rounded to the nearest second except the file end. Adjacent shots may be grouped into continuity segments; ranges are contiguous, not frame-accurate edit points.')
for r in p.runs:r.font.size=Pt(9)
p=doc.add_paragraph('Records describe visible action. “Text — English sense” summarizes Japanese intertitles; quoted English on the modern cards is identified separately. Dialogue claims remain attributed to the cards. The round, masked-faced animal is called the raccoon dog for continuity.')
p.paragraph_format.space_after=Pt(9)
for r in p.runs:r.font.size=Pt(9)

page_groups=[segments[:7],segments[7:15],segments[15:22],segments[22:29],segments[29:36],segments[36:43],segments[43:50],segments[50:57],segments[57:]]

for pg,group in enumerate(page_groups):
    if pg:
        doc.add_page_break()
        p=doc.add_paragraph()
        p.paragraph_format.space_after=Pt(7)
        r=p.add_run(f'{group[0]["start"]}–{group[-1]["end"]}  |  Continuity segments')
        r.bold=True;r.font.size=Pt(13);r.font.color.rgb=RGBColor.from_string('243747')
    table=doc.add_table(rows=1,cols=2)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    table.autofit=False
    table.columns[0].width=Inches(1.02)
    table.columns[1].width=Inches(5.95)
    table.rows[0].cells[0].text='SEGMENT\nSTART / END'
    table.rows[0].cells[1].text='VISUAL RECORD / ACTION / ON-SCREEN TEXT'
    repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
    for cell in table.rows[0].cells:
        shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'243747');cell._tc.get_or_add_tcPr().append(shd)
        for r in cell.paragraphs[0].runs:
            r.bold=True;r.font.size=Pt(8);r.font.color.rgb=RGBColor(255,255,255)
    for s in group:
        cells=table.add_row().cells
        cells[0].width=Inches(1.02);cells[1].width=Inches(5.95)
        p=cells[0].paragraphs[0]
        r=p.add_run(s['id']);r.bold=True;r.font.size=Pt(11);r.font.color.rgb=RGBColor.from_string('243747')
        p=cells[0].add_paragraph(s['start']+'\n– '+s['end'])
        p.paragraph_format.space_after=Pt(0)
        for r in p.runs:r.font.size=Pt(9)
        p=cells[1].paragraphs[0]
        r=p.add_run(s['title']);r.bold=True
        p.paragraph_format.space_after=Pt(2)
        p=cells[1].add_paragraph(s['visual'])
        p.paragraph_format.space_after=Pt(2 if s['text'] else 0)
        if s['text']:
            p=cells[1].add_paragraph()
            is_modern=s['id'] in ['S01']
            label='Text — ' if is_modern else 'Text — English sense: '
            r=p.add_run(label);r.italic=True;r.font.color.rgb=RGBColor.from_string('45545F')
            p.add_run(s['text'])
            p.paragraph_format.space_after=Pt(0)
            for r in p.runs:r.font.size=Pt(9.5)
        for cell in cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
            tcPr=cell._tc.get_or_add_tcPr()
            mar=OxmlElement('w:tcMar')
            for side,val in [('top',85),('bottom',85),('left',100),('right',100)]:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),str(val));e.set(qn('w:type'),'dxa');mar.append(e)
            tcPr.append(mar)
            borders=OxmlElement('w:tcBorders');bottom=OxmlElement('w:bottom');bottom.set(qn('w:val'),'single');bottom.set(qn('w:sz'),'4');bottom.set(qn('w:color'),'D6DEE4');borders.append(bottom);tcPr.append(borders)
            for p in cell.paragraphs:
                p.paragraph_format.keep_together=True
                p.paragraph_format.widow_control=True
        no_split=OxmlElement('w:cantSplit');cells[0]._tc.getparent().get_or_add_trPr().append(no_split)
    # No extra paragraph text after the table; a normal page break follows.

props=doc.core_properties
props.title='A Wolf is a Wolf — Archival shot log / continuity report'
props.subject='Temporal visual record of the supplied source print'
props.author='Archival assistant editor'
props.keywords='shot log, continuity report, source print'
props.comments='Prepared locally with Python and python-docx from the supplied OGV and QC brief.'
output=Path('/workspace/submission/storyboard.docx')
doc.save(output)
print('Segments:',len(segments))
print('Words:',sum(len((s['title']+' '+s['visual']+' '+s['text']).split()) for s in segments))
print('Page groups:',[(g[0]['id'],g[-1]['id'],sum(len((s['title']+' '+s['visual']+' '+s['text']).split()) for s in g)) for g in page_groups])
print('Saved:',output,output.stat().st_size)
