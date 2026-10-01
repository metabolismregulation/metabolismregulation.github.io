# Decompose a yEd PNG export into (fill class, ink mix) per pixel for /colours2/.
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
out=np.zeros(a.shape[:2]+(3,),np.uint8)
out[...,0]=cls*32; out[...,1]=np.round(T*255); 
Image.fromarray(out).save(sys.argv[2],optimize=True)
# reconstruction check
F2=np.vstack([F,[[255,255,255]]])
rec=T[...,None]*F2[cls]
print('mean abs err',np.abs(rec-a).mean())
