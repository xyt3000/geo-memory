# -*- coding: utf-8 -*-
"""潘安湖卫星近景（Esri World Imagery zoom 15，含节点标注）→ wiki/img/pananhu_sat.webp"""
import sys, math, time, io
from pathlib import Path

sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import urllib.request
from PIL import Image

UA = {"User-Agent": "CUGB-Fieldwork-Site/1.0 (student practice project)"}
OUT = Path(__file__).parent.parent / "wiki" / "img"
OUT.mkdir(parents=True, exist_ok=True)

def gpx(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n * 256
    r = math.radians(lat)
    y = (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * n * 256
    return x, y

z = 15
lon0, lat1, lon1, lat0 = 117.348, 34.392, 117.422, 34.344
x0f, y0f = gpx(lon0, lat1, z); x1f, y1f = gpx(lon1, lat0, z)
tx0, ty0, tx1, ty1 = int(x0f // 256), int(y0f // 256), int(x1f // 256), int(y1f // 256)
W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
mosaic = Image.new("RGB", (W, H))
base = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        for i in range(3):
            try:
                req = urllib.request.Request(base.format(z=z, x=tx, y=ty), headers=UA)
                with urllib.request.urlopen(req, timeout=30) as r:
                    mosaic.paste(Image.open(io.BytesIO(r.read())).convert("RGB"),
                                 ((tx - tx0) * 256, (ty - ty0) * 256))
                break
            except Exception as e:
                print("retry", tx, ty, e); time.sleep(2)
        time.sleep(0.25)
print("mosaic", mosaic.size)

fig = plt.figure(figsize=(12, 9), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.imshow(mosaic)

def to_px(lon, lat):
    gx, gy = gpx(lon, lat, z)
    return gx - tx0 * 256, gy - ty0 * 256

# 节点近似坐标（公开地图判读）
nodes = [
    ("湿地科普馆（G1/G2）", 117.3685, 34.3790),
    ("观鸟塔（G3）", 117.3725, 34.3760),
    ("主岛池杉林（G4）", 117.3690, 34.3710),
    ("神农码头", 117.3730, 34.3825),
]
for name, lon, lat in nodes:
    px, py = to_px(lon, lat)
    ax.scatter([px], [py], s=90, color="#d8a35a", edgecolors="white",
               linewidths=1.8, zorder=5)
    ax.annotate(name, xy=(px, py), xytext=(px + 12, py - 4), fontsize=10,
                color="white", fontweight="bold", zorder=6,
                bbox=dict(facecolor="black", alpha=0.45, pad=3, edgecolor="none"))

ax.text(W - 16, H - 14, "潘安湖国家湿地公园 · 卫星影像 © Esri, Maxar, Earthstar Geographics · 节点为公开地图近似判读",
        fontsize=8, color="white", ha="right",
        bbox=dict(facecolor="black", alpha=0.4, pad=3, edgecolor="none"))
fig.savefig(OUT / "pananhu_sat.jpg", dpi=200, bbox_inches="tight",
            pil_kwargs={"quality": 88})
print("done", OUT)
