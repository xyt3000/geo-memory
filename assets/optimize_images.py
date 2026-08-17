# -*- coding: utf-8 -*-
"""图片优化：JPG → WebP 降采样，并生成 og 分享封面"""
from pathlib import Path
from PIL import Image

IMG = Path(__file__).parent / "img"

SPECS = {
    "hero_contour.jpg": 1600,
    "cross_section.jpg": 1600,
    "strat_column.jpg": 1400,
    "locator_map.jpg": 1600,
    "photo_colliery.jpg": 1600,
    "photo_rail.jpg": 1400,
    "photo_pond.jpg": 1400,
}

for name, maxw in SPECS.items():
    src = IMG / name
    dst = src.with_suffix(".webp")
    im = Image.open(src).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)),
                       Image.LANCZOS)
    im.save(dst, "WEBP", quality=82, method=6)
    print(f"{name}: {src.stat().st_size//1024}KB -> {dst.stat().st_size//1024}KB ({im.width}x{im.height})")

# og 封面：hero 中心裁 1200×630
hero = Image.open(IMG / "hero_contour.jpg").convert("RGB")
w, h = hero.size
target = 1200 / 630
cw, ch = (w, int(w / target)) if w / h > target else (int(h * target), h)
x, y = (w - cw) // 2, int((h - ch) * 0.45)
og = hero.crop((x, y, x + cw, y + ch)).resize((1200, 630), Image.LANCZOS)
og.save(IMG / "og_cover.jpg", "JPEG", quality=85)
print("og_cover.jpg:", (IMG / 'og_cover.jpg').stat().st_size // 1024, "KB")
