import numpy as np, json
from PIL import Image, ImageFilter, ImageDraw
exec(open('overlay.py').read().split("# cloth grain taken")[0])   # reuse helpers: base, B, meta, warp, spine_art, cover_art, lum, median_img, coeffs
C = {'Bone':(233,228,216),'Carbon':(34,34,34),'Oxblood':(90,31,37),'Objekt Green':(55,97,63)}
rng = np.random.default_rng(5)
Bf = B.copy()
def poly_mask(q):
    im = Image.new('L',(BW,BH),0); ImageDraw.Draw(im).polygon([tuple(p) for p in q], fill=255); return np.asarray(im).astype(np.float32)/255
def blurf(a, r): return np.asarray(Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255
def maxf(a, s): return np.asarray(Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(s))).astype(np.float32)/255
def med3(a, s):
    return np.stack([np.asarray(Image.fromarray((np.clip(a[...,i],0,1)*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(s))).astype(np.float32)/255 for i in range(3)],-1)
def surface(quad, art, vis, pol, target, letter, thr=.035, extra_erase=None, noise_boost=1.0, only=None, force=None, gain_pow=1.0, feather=1.2, ex_thr=.02, keep=None):
    global Bf
    lpx = (dist(quad[0],quad[1])+dist(quad[3],quad[2]))/2; sc = min(1.0, 2.2*lpx/art.width)
    if sc < 1: art = art.resize((int(art.width*sc), int(art.height*sc)), Image.LANCZOS)
    m0 = poly_mask(quad)*(vis if force is None else np.maximum(vis, force.astype(np.float32)))
    L = lum(Bf); Mm = med3(Bf, 15); Lm = lum(Mm); diff = L-Lm
    text = ((diff*pol > thr) if pol!=0 else (np.abs(diff) > thr)) & (m0>.5)
    if only is not None: text &= only
    if extra_erase is not None: text |= (extra_erase & (np.abs(diff)>ex_thr))
    if keep is not None: text &= ~keep
    text = maxf(text.astype(np.float32), 11) > .5
    text &= (m0>.3)
    clean_px = (m0>.5)&(~text)
    resid = (L - blurf(L,2))[clean_px]; sig = float(resid.std())
    sig = min(sig, .018)
    tx_ = (text & extra_erase) if extra_erase is not None else np.zeros_like(text)
    Mm41 = med3(Bf, 41) if tx_.any() else Mm
    cl = np.where((text & ~tx_)[...,None], Mm + rng.normal(0,sig*noise_boost,(BH,BW,1)), Bf)
    cl = np.where(tx_[...,None], Mm41 + rng.normal(0,sig*noise_boost,(BH,BW,1)), cl)
    gain = np.array(target,np.float32)/255/np.maximum(cl[clean_px].mean(0),1e-3); gain = np.clip(gain,.6,1.7)**gain_pow
    graded = np.clip(cl*gain,0,1)
    f = blurf(m0, feather)[...,None]
    Bf = Bf*(1-f) + graded*f
    # exact lettering from the artwork: alpha from how far the art differs from the plain cover colour
    A = np.asarray(art).astype(np.float32); c0 = A[A.shape[0]//2, 2]
    dd = np.sqrt(((A-c0)**2).sum(-1)); amask = Image.fromarray((np.clip((dd-25)/70,0,1)*255).astype(np.uint8))
    aw = np.asarray(warp(amask, quad, Image.BICUBIC)).astype(np.float32)/255*m0
    aw = blurf(aw, .55)
    Lg = blurf(lum(Bf), 2.2); shade = np.clip(Lg/ max(Lg[m0>.5].mean(),1e-3), .4, 1.6)[...,None]
    ink = np.array(letter,np.float32)/255*shade
    tn = np.clip(1 + rng.normal(0, .06, (BH,BW,1)),.8,1.2)
    Bf = Bf*(1-aw[...,None]*.97) + np.clip(ink*tn + rng.normal(0,sig*.7,(BH,BW,1)),0,1)*aw[...,None]*.97
    return sig, gain
q_cover = [(395,661),(730,550),(1069,802),(710,945)]
q_mid   = [(364,839),(880,1018),(880,1084),(365,905)]
q_bot   = [(365,905),(880,1084),(873,1152),(369,975)]
R_,G_,B_ = B[...,0],B[...,1],B[...,2]
oxb = ((R_-G_)>.10)&(R_<.7)
neutral_white = (np.minimum(np.minimum(R_,G_),B_) > .88) & ((R_-B_) < .06)
occ_keep = maxf(oxb.astype(np.float32), 9) > .5
occ_keep |= maxf(neutral_white.astype(np.float32), 5) > .5
occ_keep = np.asarray(occ_keep)
occl = oxb | neutral_white
vis_mid = 1-maxf(occl.astype(np.float32),7)
# (PA)PIERRE stays out of the exact-lettering zone but is erased too
pap = np.zeros((BH,BW),bool); pap[985:1060, 700:900] = True
old_mid = np.zeros((BH,BW),bool); old_mid[850:945, 395:650] = True
old_bot = np.zeros((BH,BW),bool); old_bot[920:1040, 372:610] = True
logo_bot = np.zeros((BH,BW),bool); logo_bot[920:985, 372:450] = True
surface(q_bot, spine_art(3,q_bot), np.ones((BH,BW),np.float32), +1, C['Carbon'], C['Bone'], extra_erase=logo_bot|old_bot, noise_boost=.5, ex_thr=.05)
sg, gain_mid = surface(q_mid, spine_art(1,q_mid), vis_mid, -1, C['Bone'], C['Objekt Green'], extra_erase=pap|old_mid, force=pap, gain_pow=.6, feather=2.5, ex_thr=.03, keep=occ_keep)
# the same cream book: bring its top surface to the same Bone so the book reads as one object
Rr,Gg,Bb = Bf[...,0],Bf[...,1],Bf[...,2]
key = ((Rr-Bb)>.07)&(np.abs(Rr-Gg)<.03)&(lum(Bf)>.7)&(Rr>.75)
box = np.zeros((BH,BW),bool); box[690:905, 340:720] = True
keym = blurf(maxf((key&box&(poly_mask(q_mid)<.5)).astype(np.float32),3),1.5)[...,None]
Bf = Bf*(1-keym) + np.clip(Bf*gain_mid,0,1)*keym
title_box = np.zeros((BH,BW),bool); title_box[585:665, 480:710] = True
surface(q_cover, cover_art(5), np.ones((BH,BW),np.float32), +1, C['Oxblood'], C['Bone'], only=title_box)
Image.fromarray((np.clip(Bf,0,1)*255).astype(np.uint8)).save('couch_overlay2.png')
