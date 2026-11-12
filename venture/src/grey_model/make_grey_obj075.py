"""OBJ-075 grey geometry model (plain untextured grey, soft studio light) from the approved drawing rev 1, exact dimensions.
Numpy ray tracer, no 3D library. Sizes from venture/src/drawings/make_obj075_rev1.py: wall 2 mm, foot ring 12 high set in 10, base disc inside wall bottom.
Run: python3 make_grey_obj075.py <repo root>. Output venture/grey-models/OBJ-075/ (kept out of git while the repo is public)."""
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/grey-models/OBJ-075'; os.makedirs(OUT, exist_ok=True)
T, RH, SET = 2.0, 12.0, 10.0
SIZES = [('S', 300, 360), ('M', 400, 500), ('L', 520, 650)]
GAP = 100.0
def layout(sel):
    x = 0.0; ps = []
    for k, D, H in SIZES:
        if k in sel: ps.append(dict(k=k, R=D/2, H=H, cx=x+D/2)); x += D+GAP
    mid = (ps[0]['cx']-ps[0]['R'] + ps[-1]['cx']+ps[-1]['R'])/2
    for p in ps: p['cx'] -= mid
    return ps
def hit_cyl(o, d, cx, r, y0, y1, cut):
    ox, oz = o[..., 0]-cx, o[..., 2]; dx, dz = d[..., 0], d[..., 2]
    a = dx*dx+dz*dz; b = ox*dx+oz*dz; c = ox*ox+oz*oz-r*r
    disc = b*b-a*c; ok = disc > 0; sq = np.sqrt(np.where(ok, disc, 0)); a = np.where(a == 0, 1e-12, a)
    best_t = np.full(a.shape, np.inf); 
    for s in (-1, 1):
        t = (-b+s*sq)/a; y = o[..., 1]+t*d[..., 1]; z = o[..., 2]+t*d[..., 2]
        v = ok & (t > 1e-3) & (y >= y0) & (y <= y1) & ((not cut) | (z <= 0)); best_t = np.where(v & (t < best_t), t, best_t)
    return best_t
def hit_plane(o, d, y, cx, rin, rout, cut):
    dy = np.where(d[..., 1] == 0, 1e-12, d[..., 1]); t = (y-o[..., 1])/dy
    x = o[..., 0]+t*d[..., 0]-cx; z = o[..., 2]+t*d[..., 2]; rr = np.hypot(x, z)
    v = (t > 1e-3) & (rr >= rin) & (rr <= rout) & ((not cut) | (z <= 0)); return np.where(v, t, np.inf)
def trace(o, d, ps, cut=False, shadow=True):
    sh = d.shape[:-1]; best = np.full(sh, np.inf); nrm = np.zeros(d.shape); kind = np.zeros(sh, int)
    def upd(t, n_fn, k):
        nonlocal best, nrm, kind
        m = t < best; best = np.where(m, t, best); kind = np.where(m, k, kind)
        if n_fn is not None:
            n = n_fn(t); nrm = np.where(m[..., None], n, nrm)
    t = (0-o[..., 1])/np.where(d[..., 1] == 0, 1e-12, d[..., 1]); t = np.where((t > 1e-3) & (t < 1e5), t, np.inf); upd(t, lambda t: np.broadcast_to([0, 1, 0.], d.shape), 0)
    def radial(cx, sign):
        return lambda t: sign*np.stack([o[..., 0]+t*d[..., 0]-cx, np.zeros(sh), o[..., 2]+t*d[..., 2]], -1)
    def norm(n): return n/np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    for p in ps:
        cx, R, H = p['cx'], p['R'], p['H']
        for (r, y0, y1, sg) in [(R, RH, H, 1), (R-T, RH+T, H, -1), (R-SET, 0, RH, 1)]:
            t = hit_cyl(o, d, cx, r, y0, y1, cut); upd(t, (lambda t, cx=cx, sg=sg: norm(radial(cx, sg)(t))), 1)
        for (y, ri, ro) in [(H, R-T, R), (RH+T, 0, R-T)]:
            t = hit_plane(o, d, y, cx, ri, ro, cut); upd(t, lambda t: np.broadcast_to([0, 1, 0.], d.shape), 1)
    return best, nrm, kind
LIGHT = np.array([-0.45, 0.85, 0.55]); LIGHT /= np.linalg.norm(LIGHT)
def shade(o, d, ps, cut):
    t, n, kind = trace(o, d, ps, cut); hit = np.isfinite(t); p = o+d*np.where(hit, t, 0)[..., None]
    lam = np.clip((n*LIGHT).sum(-1), 0, 1)
    rng = np.random.default_rng(1); vis = np.zeros(t.shape)
    NS = 10
    for i in range(NS):
        L = LIGHT+rng.normal(0, .06, 3); L /= np.linalg.norm(L)
        Ls = np.broadcast_to(L, p.shape); ts, _, ks = trace(p+n*0.5, Ls, ps, cut); vis += ~np.isfinite(ts)
    vis /= NS
    base = np.where(kind == 0, 0.86, 0.60)
    amb = 0.38 + 0.12*np.clip(n[..., 1], 0, 1)
    c = base*(amb+0.62*lam*vis)
    c = np.where(hit, c, 0.93)
    return np.clip(c, 0, 1)
def cam_rays(W, Hh, fwd, up, scale, centre, persp=None, dist=6000.0):
    fwd = np.array(fwd, float); fwd /= np.linalg.norm(fwd); right = np.cross(fwd, up); right /= np.linalg.norm(right); upv = np.cross(right, fwd)
    xs = (np.arange(W)-W/2+.5)/scale; ys = (Hh/2-np.arange(Hh)-.5)/scale; U, V = np.meshgrid(xs, ys)
    centre = np.array(centre, float)
    if persp is None:
        o = centre-fwd*dist + right*U[..., None] + upv*V[..., None]; d = np.broadcast_to(fwd, o.shape).copy()
    else:
        o = np.broadcast_to(centre-fwd*persp, (Hh, W, 3)).copy(); f = persp  # pixel scale at the centre plane
        d = fwd*persp + right*U[..., None] + upv*V[..., None]; d /= np.linalg.norm(d, axis=-1, keepdims=True)
    return o, d
def label(img, text, ps, y=None):
    im = Image.fromarray((img*255).astype('uint8')).convert('RGB'); dr = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    except Exception: f = None
    dr.text((30, 24), text, fill=(60, 60, 60), font=f); return im
def render(name, ps, W, Hh, fwd, scale, centre, persp=None, cut=False, title=''):
    o, d = cam_rays(W, Hh, fwd, (0, 1, 0), scale, centre, persp); c = shade(o, d, ps, cut)
    im = label(c, title, ps); im.save(f'{OUT}/{name}'); print(name); return im
if __name__ == '__main__':
    ps = layout('SML'); span = ps[-1]['cx']+ps[-1]['R']-(ps[0]['cx']-ps[0]['R'])
    W, Hh = 1800, 1100; sc = (W*0.9)/span
    ims = []
    ims.append(render('OBJ-075_grey_front_all_rev1.png', ps, W, Hh, (0, 0, -1), sc, (0, 330, 0), title='OBJ-075 grey model, rev 1: FRONT (orthographic), S 300x360, M 400x500, L 520x650 mm'))
    ims.append(render('OBJ-075_grey_section_all_rev1.png', ps, W, Hh, (0, 0, -1), sc, (0, 330, 0), cut=True, title='SECTION (front half removed): 2 mm wall, base disc inside, 12 mm foot ring set in 10, no drain hole'))
    ims.append(render('OBJ-075_grey_3q_all_rev1.png', ps, W, Hh, (0.55, -0.32, -0.77), 1.0, (0, 300, 0), persp=int(2.4*span), title='THREE-QUARTER (long lens)'))
    ims.append(render('OBJ-075_grey_top_all_rev1.png', ps, W, 700, (0, -1, -0.0001), sc*1.0, (0, 0, 0), title='TOP (orthographic)'))
    render('OBJ-075_grey_M_section3q_rev1.png', layout('M'), 1000, 1200, (0.45, -0.55, -0.7), 1.0, (0, 240, 0), persp=2600, cut=True, title='size M: section, three-quarter from above, base disc and no drain hole')
    for k in 'SML':
        q = layout(k); R = q[0]['R']; Hq = q[0]['H']
        render(f'OBJ-075_grey_{k}_3q_rev1.png', q, 1000, 1200, (0.55, -0.32, -0.77), 1.0, (0, Hq*0.48, 0), persp=int(5.2*max(Hq, 2*R)), title=f'size {k}: D{int(2*R)} x H{int(Hq)}, three-quarter')
