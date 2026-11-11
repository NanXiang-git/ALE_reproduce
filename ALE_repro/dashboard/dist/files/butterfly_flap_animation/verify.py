import cv2, numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
root=Path.cwd()
cap=cv2.VideoCapture(str(root/'output/output.mp4'))
widths=[]
bounds=[]
previews=[]
i=0
while True:
    ok,bgr=cap.read()
    if not ok: break
    mask=bgr[:,:,2]>35
    yy,xx=np.where(mask)
    bounds.append((xx.min(), yy.min(),xx.max(),yy.max()))
    widths.append(int(xx.max()-xx.min()))
    if i in (0,9,18,27,36,45,54,63,72,90,108,143):
        rgb=cv2.cvtColor(cv2.resize(bgr,(480,270)),cv2.COLOR_BGR2RGB)
        previews.append((i,Image.fromarray(rgb)))
    i+=1
cap.release()
minima=[j for j in range(1,len(widths)-1) if widths[j]<=widths[j-1] and widths[j]<widths[j+1]]
print('Decoded frames:',i)
print('Wing width minima:',minima)
print('Bounds of visible artwork:',np.min(np.array(bounds)[:,:2],axis=0),np.max(np.array(bounds)[:,2:],axis=0))
print('Final bytes:',(root/'output/output.mp4').stat().st_size)
sheet=Image.new('RGB',(1920,810))
draw=ImageDraw.Draw(sheet)
for j,(idx,im) in enumerate(previews):
    x=(j%4)*480;y=(j//4)*270
    sheet.paste(im,(x,y));draw.text((x+8,y+8),f'{idx/30:.2f}s',fill='white')
sheet.save(root/'work/contact_sheet.jpg')
