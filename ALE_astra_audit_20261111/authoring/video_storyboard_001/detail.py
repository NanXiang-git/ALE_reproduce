from PIL import Image, ImageDraw, ImageFont
import subprocess,sys,os
start,end,rate=map(float,sys.argv[1:4])
prefix=sys.argv[4] if len(sys.argv)>4 else 'detail'
os.makedirs(f'/workspace/scratch/{prefix}',exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i','/candidate/input/Yasuji_Murata-_A_Wolf_is_a_Wolf_(1931).ogv','-t',str(end-start),'-vf',f'fps={rate}','-q:v','2',f'/workspace/scratch/{prefix}/%04d.jpg'],check=True)
files=sorted(__import__('glob').glob(f'/workspace/scratch/{prefix}/*.jpg'))
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for j in range(0,len(files),30):
 chunk=files[j:j+30]
 im=Image.new('RGB',(2000,324*((len(chunk)+4)//5)),'#eee');d=ImageDraw.Draw(im)
 for k,path in enumerate(chunk):
  t=start+(j+k)/rate;x=k%5*400;y=k//5*324
  im.paste(Image.open(path),(x,y+24));d.text((x+8,y+1),f'{int(t)//60:02d}:{t%60:05.2f}',font=f,fill='black')
 out=f'/workspace/scratch/sheets/{prefix}_{j//30}.jpg';im.save(out,quality=93); print(out)
