from PIL import Image,ImageDraw
from pathlib import Path
fs=sorted(Path('work').glob('sec_*.jpg'))
for s in range(0,len(fs),32):
 out=Image.new('RGB',(1600,8*322),'white'); d=ImageDraw.Draw(out)
 for j,f in enumerate(fs[s:s+32]):
  t=int(f.stem.split('_')[1])-1;x=j%4*400;y=j//4*322
  out.paste(Image.open(f),(x,y));d.text((x+5,y+301),f'{t//60:02}:{t%60:02}',fill='black')
 out.save(f'work/dense_{s//32:02}.jpg')
