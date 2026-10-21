# Half-size layers for /colours/, for screens that show the map at up to about 1700 device pixels:
# the page loads it there and the full-size layers only on larger screens (user, 2026-10-21).
# Usage: python3 images/colours2/make_layers_half.py images/colours2/F007-inos-layers.png images/colours2/F007-inos-layers-half.png
# Each 2 x 2 block of the full layers gives one pixel: the fill share is the block's mean (the ink
# is the same for the whole block), the class is that of the block's pixel with the most fill,
# and the text flag is set where any pixel of the block is text ink.
# Needs: pillow, numpy.
import sys
from PIL import Image; import numpy as np
a=np.array(Image.open(sys.argv[1]).convert('RGB'))
h,w=a.shape[0]//2*2,a.shape[1]//2*2
a=a[:h,:w]
def blocks(x): return x.reshape(h//2,2,w//2,2).transpose(0,2,1,3).reshape(h//2,w//2,4)
cls=blocks(np.round(a[...,0]/24).astype(np.uint8)); T=blocks(a[...,1].astype(float)); txt=blocks(a[...,2]>127)
pick=T.argmax(-1)[...,None]
Ts=np.round(T.mean(-1))
out=np.zeros((h//2,w//2,3),np.uint8)
out[...,0]=np.take_along_axis(cls,pick,-1)[...,0]*24
out[...,1]=Ts
out[...,2]=(txt.any(-1)&(Ts<255))*255
Image.fromarray(out).save(sys.argv[2],optimize=True)
print(out.shape[1],'x',out.shape[0])
