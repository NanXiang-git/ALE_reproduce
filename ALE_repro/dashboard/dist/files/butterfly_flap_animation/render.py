from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import subprocess, math

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'
OUT=ROOT/'output'
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
src=np.array(Image.open(ROOT/'input'/'butterfly.jpeg').convert('RGB')).astype(np.float32)/255
h,w=src.shape[:2]
# Recover orange ink from its white matte, excluding the neutral watermark.
a=1-src[:,:,2]
chroma=np.clip((src[:,:,0]-src[:,:,1])*255/20,0,1)
a*=chroma
a[a<0.025]=0
rgb=np.clip((src-(1-a[:,:,None]))/np.maximum(a[:,:,None],1e-5),0,1)
# Antennae remain with the body while both wings hinge independently.
central=np.zeros((h,w),np.uint8)
cv2.rectangle(central,(487,380),(513,630),255,-1)
cv2.fillPoly(central,[np.array([[320,95],[369,95],[495,392],[480,392],[322,160]],np.int32)],255)
cv2.fillPoly(central,[np.array([[680,95],[631,95],[505,392],[520,392],[678,160]],np.int32)],255)
Y,X=np.mgrid[:h,:w]
bodymask=(central>0)
leftmask=(X<500)&~bodymask
rightmask=(X>=500)&~bodymask
layers=[]
for mask in (leftmask,rightmask,bodymask):
    alpha=a*mask
    rgba=np.concatenate([rgb*alpha[:,:,None],alpha[:,:,None]],axis=2).astype(np.float32)
    layers.append(rgba)
for name,layer in zip(('left','right','body'),layers):
    aa=layer[:,:,3:4]
    straight=np.divide(layer[:,:,:3],np.maximum(aa,1e-6))
    Image.fromarray(np.uint8(np.clip(np.concatenate([straight,aa],axis=2),0,1)*255)).save(WORK/(name+'.png'))

W,H=1920,1080
N=144
fps=30
corners=np.float32([[0,0],[w,0],[w,h],[0,h]])

def geometry(u,side):
    phase=2*math.pi*u
    cx=960-545*math.cos(phase)
    cy=540-148*math.sin(2*phase)
    scale=.625+.045*math.sin(phase)
    bank=math.radians(8*math.sin(phase)+4*math.sin(2*phase))
    # Exactly four full open -> closed -> open cycles.
    fold=math.radians(83)*(.5-.5*math.cos(4*phase))
    hinge=482 if side==0 else 518 if side==1 else 500
    dx=corners[:,0]-hinge
    dy=corners[:,1]-415
    if side<2:
        xx=dx*math.cos(fold)+(hinge-500)
        zz=dx*(-1 if side==0 else 1)*math.sin(fold)
        # Small longitudinal flex supplies an organic perspective cue.
        yy=dy + dx*(-1 if side==0 else 1)*.035*math.sin(fold)
    else:
        xx=dx
        yy=dy
        zz=np.zeros(4)
    factor=2400/(2400-zz)
    xx=xx*factor*scale
    yy=yy*factor*scale
    dest=np.column_stack([cx+xx*math.cos(bank)-yy*math.sin(bank),cy+xx*math.sin(bank)+yy*math.cos(bank)]).astype(np.float32)
    return cv2.getPerspectiveTransform(corners,dest),fold

def frame(u):
    canvas=np.zeros((H,W,3),np.float32)
    for side in range(3):
        matrix,fold=geometry(u,side)
        warped=cv2.warpPerspective(layers[side],matrix,(W,H),flags=cv2.INTER_LINEAR)
        shade=(.72+.28*math.cos(fold)) if side<2 else 1
        canvas=canvas*(1-warped[:,:,3:4])+warped[:,:,:3]*shade
    return np.uint8(np.clip(canvas*255,0,255))

cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'output.mp4')]
with open(WORK/'ffmpeg.log','w') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(N):
        u=i/(N-1)
        img=frame(u)
        if i in (0,18,36,54,72,90,108,126,143):
            Image.fromarray(img).resize((960,540)).save(WORK/f'preview_{i:03d}.jpg')
        p.stdin.write(img.tobytes())
        if i%24==0: print(f'Rendered {i}/{N}',flush=True)
    p.stdin.close()
    code=p.wait()
    if code: raise RuntimeError(f'FFmpeg failed with {code}')
print('Completed',OUT/'output.mp4',flush=True)

