# Decompose a yEd PNG export into (fill class, ink mix, text flag) per pixel for /colours/.
# Usage: python3 make_layers.py downloads/F007-inos.png images/colours2/F007-inos-layers.png
# Fill order must match the cls numbers of ROLES in colours2.js; class 7 is the page margin.
# Needs: pillow, numpy, scipy.
import sys
from PIL import Image; import numpy as np; from scipy import ndimage
a=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(float)
fills=['F7F6F3','FFFFFF','C8D8EB','E0E7EF','DBEBDB','EDD1CB','E2ACA3']
F=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in fills],float)
best=None
for k,f in enumerate(F):
    t=np.clip((a@f)/(f@f),0,1)
    res=((a-t[...,None]*f)**2).sum(-1)
    if best is None: best=res;cls=np.zeros(res.shape,int);T=t
    else:
        m=res<best; best[m]=res[m]; cls[m]=k; T[m]=t[m]
# anti-aliased pixels take the class of the nearest solid fill pixel
solid=(T>0.97)
_,(iy,ix)=ndimage.distance_transform_edt(~solid,return_indices=True)
soft=~solid
cls[soft]=cls[iy[soft],ix[soft]]
f=F[cls]; T=np.clip((a*f).sum(-1)/(f*f).sum(-1),0,1)
best=((a-T[...,None]*f)**2).sum(-1)
# page margin: white region connected to the image border -> class 7
lab,_=ndimage.label(cls==1)
edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
cls[np.isin(lab,list(edge))]=7
print('max residual',np.sqrt(best.max()), 'p99.9',np.percentile(np.sqrt(best),99.9))
# text: ink components of glyph size that do not enclose another component
# (that rules out small boxes such as stoichiometry labels); every other ink
# pixel, anti-aliasing included, takes the flag of the nearest core ink pixel
core=(1-T)>0.35
lab,n=ndimage.label(core,structure=np.ones((3,3)))
boxes=ndimage.find_objects(lab)
def encloses(i):
    y,x=boxes[i]
    return any(j!=i and b[0].start>y.start and b[0].stop<y.stop and b[1].start>x.start and b[1].stop<x.stop
               for j,b in enumerate(boxes))
glyph=np.zeros(n+1,bool)
for i,(y,x) in enumerate(boxes):
    h,w=y.stop-y.start,x.stop-x.start
    glyph[i+1]=h<=30 and w<=80 and not encloses(i)
_,(iy,ix)=ndimage.distance_transform_edt(~core,return_indices=True)
text=glyph[lab[iy,ix]]&(T<1)
print('text components',glyph.sum(),'of',n)
out=np.zeros(a.shape[:2]+(3,),np.uint8)
out[...,0]=cls*32; out[...,1]=np.round(T*255); out[...,2]=text*255
Image.fromarray(out).save(sys.argv[2],optimize=True)
# reconstruction check
F2=np.vstack([F,[[255,255,255]]])
rec=T[...,None]*F2[cls]
print('mean abs err',np.abs(rec-a).mean())
