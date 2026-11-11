from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys
start,end,step=map(int,sys.argv[1:4]); cols=int(sys.argv[4]) if len(sys.argv)>4 else 5
w,h=400,324
files=list(range(start,end,step))
im=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),'#eee')
d=ImageDraw.Draw(im)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for i,t in enumerate(files):
 p=Path(f'/workspace/scratch/frames/{t+1:04d}.jpg')
 if not p.exists(): continue
 x=i%cols*w; y=i//cols*h
 im.paste(Image.open(p),(x,y+24)); d.text((x+8,y+1),f'{t//60:02d}:{t%60:02d}',fill='black',font=f)
p=f'/workspace/scratch/sheets/{start}_{end}_{step}.jpg'; im.save(p,quality=93); print(p)
