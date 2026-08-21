# -*- coding: utf-8 -*-
"""团队成员照片统一处理：4:5 竖版裁剪 + 600×750 WebP"""
from pathlib import Path
from PIL import Image

SRC = Path(r"D:\Desktop\文件\社会实践\05_实践过程资料\团队照片简介\提取")
DST = Path(r"D:\Desktop\文件\社会实践\wiki\img\team")
DST.mkdir(parents=True, exist_ok=True)

# 特殊情况：横向照片的人物位置偏移（x 中心偏移比例）
OFFSETS = {"夏煜棠": 0.36}   # 人物在画面左 1/3 处

TARGET = 4 / 5  # 宽/高
for f in sorted(SRC.glob("*.webp")):
    im = Image.open(f).convert("RGB")
    w, h = im.size
    tw = int(h * TARGET) if h * TARGET <= w else w
    th = int(w / TARGET) if w / TARGET <= h else h
    cx = int(w * OFFSETS.get(f.stem, 0.5))
    x0 = max(0, min(w - tw, cx - tw // 2))
    y0 = max(0, min(h - th, int(h * 0.12)))  # 略偏上保留头部
    crop = im.crop((x0, y0, x0 + tw, y0 + th)).resize((600, 750), Image.LANCZOS)
    out = DST / f"{f.stem}.webp"
    crop.save(out, "WEBP", quality=84, method=6)
    print(f.stem, im.size, "->", crop.size, out.stat().st_size // 1024, "KB")
