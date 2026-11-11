from PIL import Image,ImageDraw
from pathlib import Path
fs=list(Path('work').glob('frame_*.jpg'))
for s in range(0,len(fs),30):
 out=Image.new('RGB',(1600,6*325),'white'); d=ImageDraw.Draw(out)
 for j,f in enumerate(fs[s:s+30]):
  im=Image.open(f); x=j%4*400; y=j//4*325
  # 4 columns, 8 rows
  if j==0: pass
 # rebuild
 out=Image.new('RGB',(1600,8*325),'white'); d=ImageDraw.Draw(out)
 for j,f in enumerate(fs[s:s+30]):
  t=(int(f.stem.split('_')[1])-1)*3; x=j%4*400;y=j//4*325
  out.paste(Image.open(f),(x,y));d.text((x+5,y+302),f'{t//60:02}:{t%60:02}',fill='black')
 out.save(f'work/sheet_{s//30:02}.jpg')
