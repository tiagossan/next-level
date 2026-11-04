import sys, cv2, numpy as np
from PIL import Image, ImageOps
src, dst, rot = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
if rot: im = im.rotate(rot, expand=True)
a = np.array(im)
g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
# crop to paper: brightest, low-saturation region
hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
mask = ((hsv[...,2] > 150) & (hsv[...,1] < 60)).astype(np.uint8)*255
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((15,15),np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
if n > 1:
    i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    x,y,w,h = st[i,:4]
    if w*h > 0.15*g.size:
        p=10; g = g[max(0,y-p):y+h+p, max(0,x-p):x+w+p]
# upscale for print
g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
# flatten illumination
bg = cv2.GaussianBlur(cv2.dilate(g, np.ones((9,9),np.uint8)), (0,0), 25)
norm = cv2.divide(g, bg, scale=255)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(norm)
# darken text: gamma
out = np.clip(255*((clahe/255.0)**2.2), 0, 255).astype(np.uint8)
cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 90])
