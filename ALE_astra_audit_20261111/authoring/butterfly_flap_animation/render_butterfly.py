"""Source-image butterfly animation. Linux/OpenCV renderer; no After Effects.
Four open -> closed -> open cycles, 150 frames, 30 fps, 1920 x 1080.
All artwork comes from the supplied JPEG; only white is keyed out.
"""
from pathlib import Path
import json
import subprocess
import math
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = Path('/workspace/scratch')
OUT = Path('/workspace/submission/output.mp4')
W, H, FPS, FRAMES = 1920, 1080, 30, 150
F = 2500.0
cv2.setNumThreads(4)
source = np.asarray(Image.open('/candidate/input/butterfly.jpeg').convert('RGB')).astype(np.float32)
chroma = source[..., 0] - source[..., 2]
seed = (chroma > 60).astype(np.uint8)
count, labels, stats, centers = cv2.connectedComponentsWithStats(seed)
# Assign the separate ornamental islands to their original anatomical layers.
# Antennae and central body stay fixed while the wings rotate independently.
assignment = np.zeros(count, np.uint8)
for k in range(1, count):
    x, y, w, h, area = stats[k]
    if area < 100:
        continue
    cx, cy = centers[k]
    if (y > 380 and 485 <= cx <= 515) or (100 <= y <= 115 and h > 250):
        assignment[k] = 3
    else:
        assignment[k] = 1 if cx < 500 else 2
nearest_dist, nearest = distance_transform_edt(labels == 0, return_indices=True)
region = assignment[labels[nearest[0], nearest[1]]]
alpha = np.clip((chroma - 3.0) / 252.0, 0, 1)
alpha[nearest_dist > 4] = 0
# Remove the white matte in premultiplied space to avoid pale fringes on black.
premult = np.clip(source / 255.0 - (1.0-alpha[..., None]), 0, 1)
premult = np.minimum(premult, alpha[..., None])
layers = []
for k in [1, 2, 3]:
    a = alpha * (region == k)
    p = premult * (region == k)[..., None]
    layers.append(np.dstack([p, a]).astype(np.float32))
combined = sum(layer[..., :3] for layer in layers)
Image.fromarray(np.uint8(np.clip(combined * 255, 0, 255))).save(ROOT/'isolated_artwork.png')

def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]], dtype=np.float64)

def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]], dtype=np.float64)

def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]], dtype=np.float64)

def state(u):
    # One full spatial loop. The vertical sinusoid has four turning points.
    phase = 2 * math.pi * u
    cx = W / 2 + 440 * math.sin(phase)
    cy = H / 2 - 100 * math.sin(2 * phase)
    scale = .76 + .04 * math.cos(phase)
    roll = math.radians(8 * math.sin(phase) + 3 * math.sin(2 * phase))
    # Exactly four smooth full flaps. Zero angular velocity at open and closed.
    fold = math.radians(86) * .5 * (1 - math.cos(4 * phase))
    pitch = math.radians(4 * math.sin(2 * phase))
    return cx, cy, scale, roll, pitch, fold

def homography(u, kind):
    cx, cy, scale, roll, pitch, fold = state(u)
    global_rotation = rz(roll) @ rx(pitch)
    if kind == 0:
        joint, angle = 480., fold
    elif kind == 1:
        joint, angle = 520., -fold
    else:
        joint, angle = 500., 0.
    wing_rotation = ry(angle)
    plane = np.column_stack((wing_rotation[:,0], wing_rotation[:,1],
                             wing_rotation @ np.array([-joint,-410.,0.]) + np.array([joint-500.,0.,0.])))
    plane = global_rotation @ plane
    den = -plane[2].copy()
    den[2] += F
    mat = np.stack((scale*F*plane[0] + cx*den,
                    scale*F*plane[1] + cy*den, den))
    return mat, fold

def render(u):
    canvas = np.zeros((H,W,3), np.float32)
    for kind in range(3):
        mat, fold = homography(u, kind)
        warped = cv2.warpPerspective(layers[kind], mat, (W,H), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # Gentle lighting makes the physical folding visible without recoloring the art.
        light = 1. if kind == 2 else .78 + .22*math.cos(fold)
        canvas *= 1. - warped[...,3,None]
        canvas += light * warped[...,:3]
    return canvas

cmd = ['ffmpeg','-y','-hide_banner','-loglevel','warning',
       '-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
       '-framerate',str(FPS),'-i','pipe:0','-an','-c:v','libx264',
       '-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high',
       '-level','4.1','-movflags','+faststart','-color_primaries','bt709',
       '-color_trc','bt709','-colorspace','bt709',
       '-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709',
       '-metadata','title=Butterfly | Four Wing Flaps',
       '-metadata','comment=Created from the supplied butterfly artwork with local Python and OpenCV; Adobe After Effects was unavailable and was not used.',
       str(OUT)]
process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
# A short, centered shutter adds restrained antialiasing to fast moving edges.
# Endpoint samples wrap so the first and last pictures are identical.
shutter_offsets = [-.16, 0., .16]
preview_indices = {0, 9, 19, 28, 37, 56, 75, 94, 112, 131, 149}
manifest = []
for frame in range(FRAMES):
    u = frame / (FRAMES-1)
    picture = np.zeros((H,W,3), np.float32)
    for offset in shutter_offsets:
        picture += render((u + offset/(FRAMES-1)) % 1.) / len(shutter_offsets)
    pixels = np.clip(picture*255+.5, 0, 255).astype(np.uint8)
    process.stdin.write(pixels.tobytes())
    if frame in preview_indices:
        Image.fromarray(pixels).save(ROOT/f'frame_{frame:03d}.png')
    nonzero = np.any(pixels > 10, axis=2)
    ys, xs = np.where(nonzero)
    manifest.append({'frame': frame, 'center': state(u)[:2],
                     'fold_degrees': math.degrees(state(u)[-1]),
                     'bounds': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]})
    if frame % 15 == 0:
        print(f'Rendered {frame+1}/{FRAMES}', flush=True)
process.stdin.close()
if process.wait() != 0:
    raise RuntimeError('FFmpeg encoding failed')
(ROOT/'render_manifest.json').write_text(json.dumps(manifest, indent=2))
print(f'Completed: {OUT}', flush=True)
