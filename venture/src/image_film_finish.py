"""objekt camera finish: make a generated image read like a photograph.

Calibrated on Sabry's five references (11 Nov 2026, plan/HOUSE-STYLE.md section 7). Measured there:
- grain is monochrome (R, G, B noise equal; colour noise almost nil) and clumped, about 2-3 px at
  2000 px tall; high-pass strength on plain walls 1.9 to 3.4 (0-255 scale, blur radius 3)
- highlights never pure white: 99th percentile 200 to 238, cream (R > G > B by 10 to 30)
- blacks deep but soft: 1st percentile 11 to 28; shadows warm brown, never blue
- saturation low to moderate (0.14 to 0.27), warm overall

Usage:
  python image_film_finish.py in.png out.jpg [studio|editorial]   # finish (default editorial)
  python image_film_finish.py --measure image.jpg [...]            # print the same numbers
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

PRESETS = {
    # grain = target high-pass std on flat areas; warm = shadow/highlight warmth; white = highlight cap
    "studio":    dict(grain=2.2, white=0.925, black=0.018, warm_sh=0.035, warm_hi=0.018, soft=0.35, vignette=0.04),
    "editorial": dict(grain=2.4, white=0.900, black=0.025, warm_sh=0.055, warm_hi=0.025, soft=0.45, vignette=0.08),
}


def measure(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    g = im.convert("L")
    blur = np.asarray(g.filter(ImageFilter.GaussianBlur(3))).astype(float)
    hp = np.asarray(g).astype(float) - blur
    H, W = blur.shape
    bs = 32
    blocks = sorted((blur[y:y + bs, x:x + bs].std(), hp[y:y + bs, x:x + bs].std())
                    for y in range(0, H - bs, bs) for x in range(0, W - bs, bs))
    flat = blocks[:max(5, len(blocks) // 5)]
    grain = float(np.mean([b[1] for b in flat]))
    sat = np.asarray(im.convert("HSV"))[..., 1].mean() / 255
    sh = a[L < np.percentile(L, 10)].mean(0)
    hi = a[L > np.percentile(L, 90)].mean(0)
    p = np.percentile(L, [1, 50, 99])
    ok = lambda v, lo, hi_: "ok" if lo <= v <= hi_ else "OUT"
    print(f"{path.split('/')[-1]}: grain {grain:.2f} [{ok(grain, 1.9, 3.5)}]  "
          f"black p1 {p[0]:.0f} [{ok(p[0], 8, 32)}]  median {p[1]:.0f}  white p99 {p[2]:.0f} [{ok(p[2], 195, 240)}]  "
          f"sat {sat:.2f} [{ok(sat, 0.10, 0.30)}]  shadow R-B {sh[0] - sh[2]:+.0f} [{ok(sh[0] - sh[2], 0, 35)}]  "
          f"highlight R-B {hi[0] - hi[2]:+.0f} [{ok(hi[0] - hi[2], 4, 35)}]")


def finish(src, out, preset="editorial", seed=7):
    P = PRESETS[preset]
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(float) / 255
    h, w, _ = a.shape
    # 1. tone: soft shoulder to a cream white, slightly lifted warm black
    a = P["black"] + a * (P["white"] - P["black"])          # cream white; black lifted only slightly
    a = a + 0.04 * np.sin(np.pi * a) * (a < 0.5)            # open the low mids a little
    lum = a.mean(2, keepdims=True)
    sh_w = np.clip(1 - lum / 0.45, 0, 1)                    # shadow weight
    hi_w = np.clip((lum - 0.6) / 0.4, 0, 1)                 # highlight weight
    warm = np.array([1.0, 0.25, -1.0])                      # add red, a little green, remove blue
    a = a + sh_w * P["warm_sh"] * warm * 0.5 + hi_w * P["warm_hi"] * warm * 0.5
    # 2. gentle lens softness and vignette
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(P["soft"]))
    a = np.asarray(img).astype(float) / 255
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - P["vignette"] * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None]
    # 3. grain: monochrome, clumped (2-3 px at 2000 px tall), strongest in the mid-tones
    scale = max(h, w) / 2000
    n = np.random.default_rng(seed).normal(0, 1, (h, w)).astype(np.float32)
    ni = Image.fromarray(((n * 30) + 128).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.9 * scale))
    n = (np.asarray(ni).astype(float) - 128)
    n /= n.std() + 1e-6
    lum = a.mean(2)
    mid = 0.55 + 0.45 * (1 - np.abs(lum - 0.5) * 2)          # midtones carry the most grain
    amp = P["grain"] * 1.55 / 255                            # 1.55: blur-3 high-pass keeps about 65 percent
    a = a + (n * amp * mid)[..., None]
    Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8")).save(out, quality=94, subsampling=0)


if __name__ == "__main__":
    if sys.argv[1] == "--measure":
        for f in sys.argv[2:]:
            measure(f)
    else:
        finish(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "editorial")
