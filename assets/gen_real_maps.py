# -*- coding: utf-8 -*-
"""
真实地图生成：下载 Esri 公开瓦片并拼接标注
1. hero_contour.jpg → 潘安湖采煤沉陷湖区卫星影像（Esri World Imagery）
2. locator_map.jpg  → 调研区真实地形位置图（Esri World Topo Map）+ 点位标注
"""
import sys, math, time, io
from pathlib import Path

sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import urllib.request
from PIL import Image

OUT = Path(__file__).parent / "img"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "CUGB-Fieldwork-Site/1.0 (student practice project)"}

INK = "#232a32"; SUB = "#67727e"; AMBER = "#a86a24"; TEAL = "#2a8f8c"


def lonlat_to_global_px(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n * 256
    lat_r = math.radians(lat)
    y = (1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n * 256
    return x, y


def fetch_tile(base, z, x, y, retries=3):
    url = base.format(z=z, x=x, y=y)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return Image.open(io.BytesIO(r.read())).convert("RGB")
        except Exception as e:
            print("  retry", i + 1, url, e)
            time.sleep(2)
    raise RuntimeError("tile failed: " + url)


def build_mosaic(base, z, lon0, lat1, lon1, lat0):
    """lon0/lat1 左上, lon1/lat0 右下；返回 (mosaic, origin_px)"""
    x0f, y0f = lonlat_to_global_px(lon0, lat1, z)
    x1f, y1f = lonlat_to_global_px(lon1, lat0, z)
    tx0, ty0 = int(x0f // 256), int(y0f // 256)
    tx1, ty1 = int(x1f // 256), int(y1f // 256)
    W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
    mosaic = Image.new("RGB", (W, H))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            t = fetch_tile(base, z, tx, ty)
            mosaic.paste(t, ((tx - tx0) * 256, (ty - ty0) * 256))
            time.sleep(0.25)
            print(f"  tile {tx},{ty} ok")
    return mosaic, (tx0 * 256, ty0 * 256), (x0f, y0f, x1f, y1f)


def scale_bar(ax, z, lat, img_frac=0.18):
    """左下角比例尺，长度取整公里"""
    m_per_px = math.cos(math.radians(lat)) * 2 * math.pi * 6378137 / (256 * 2 ** z)
    return m_per_px


# ============================================================
# 1. 潘安湖沉陷湖区 卫星影像（Hero 背景）
#    湖盆约 11.6–12.6 km²，中心约 34.36N, 117.40E
# ============================================================
def hero():
    print("== hero: Esri World Imagery ==")
    base = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    z = 13
    lon0, lat1, lon1, lat0 = 117.300, 34.400, 117.430, 34.310
    mosaic, origin, _ = build_mosaic(base, z, lon0, lat1, lon1, lat0)

    fig = plt.figure(figsize=(16, 9), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.imshow(mosaic)
    ax.text(mosaic.width - 18, mosaic.height - 16,
            "潘安湖采煤沉陷湖区 · 卫星影像", fontsize=13, color="white",
            ha="right", fontweight="bold",
            bbox=dict(facecolor="black", alpha=0.45, pad=6, edgecolor="none"))
    ax.text(mosaic.width - 18, mosaic.height - 52,
            "影像 © Esri — Source: Esri, Maxar, Earthstar Geographics",
            fontsize=7.5, color="white", ha="right", alpha=0.85,
            bbox=dict(facecolor="black", alpha=0.35, pad=3, edgecolor="none"))
    fig.savefig(OUT / "hero_contour.jpg", dpi=200, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("hero_contour.jpg (real imagery) done", mosaic.size)


# ============================================================
# 2. 调研区真实地形位置图 + 点位标注
# ============================================================
def locator():
    print("== locator: Esri World Topo Map ==")
    base = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
    z = 11
    lon0, lat1, lon1, lat0 = 117.18, 34.52, 117.54, 34.20
    mosaic, origin, _ = build_mosaic(base, z, lon0, lat1, lon1, lat0)

    fig = plt.figure(figsize=(12, 8), dpi=220)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.imshow(mosaic)

    def to_px(lon, lat):
        gx, gy = lonlat_to_global_px(lon, lat, z)
        return gx - origin[0], gy - origin[1]

    pts = [  # (名称, lon, lat, 颜色, 标签方向)
        ("贾汪区消防支队 · 集结驻地", 117.4525, 34.4370, "#5c6670", (-20, -40)),
        ("大吴街道（未修复塌陷区）", 117.352, 34.331, AMBER, (16, -6)),
        ("潘安湖国家湿地公园", 117.378, 34.367, TEAL, (-20, -34)),
        ("权台煤矿遗址创意园", 117.415, 34.360, "#5c6670", (16, 26)),
        ("贾汪城区", 117.458, 34.442, "#5c6670", (16, -8)),
    ]
    for name, lon, lat, col, (dx, dy) in pts:
        px, py = to_px(lon, lat)
        ax.scatter([px], [py], s=130, color=col, zorder=5,
                   edgecolors="white", linewidths=2)
        ha = "right" if dx < 0 else "left"
        ax.annotate(name, xy=(px, py), xytext=(px + dx, py + dy),
                    fontsize=10.5, color="white", fontweight="bold", zorder=6,
                    ha=ha,
                    bbox=dict(facecolor="black", alpha=0.42, pad=3.5,
                              edgecolor="none"))

    # 调研路线
    rx, ry = zip(*[to_px(lon, lat) for _, lon, lat, _, _ in pts[:3]])
    ax.plot(rx, ry, color=AMBER, lw=2.2, linestyle=(0, (6, 4)), alpha=0.95,
            zorder=4)

    # 指北针
    ax.annotate("", xy=(mosaic.width - 46, 46), xytext=(mosaic.width - 46, 96),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2))
    ax.text(mosaic.width - 46, 30, "N", fontsize=12, color=INK, ha="center",
            fontweight="bold", family="serif")

    # 比例尺
    mpp = math.cos(math.radians(34.36)) * 2 * math.pi * 6378137 / (256 * 2 ** z)
    bar_km = 5; bar_px = bar_km * 1000 / mpp
    bx, by = 40, mosaic.height - 40
    ax.plot([bx, bx + bar_px], [by, by], color="white", lw=6,
            solid_capstyle="butt")
    ax.plot([bx, bx + bar_px], [by, by], color=INK, lw=2.4,
            solid_capstyle="butt")
    ax.text(bx + bar_px / 2, by - 14, f"{bar_km} km", fontsize=9, color=INK,
            ha="center", fontweight="bold")

    ax.text(26, 34, "徐州 · 贾汪", fontsize=19, color="white",
            fontweight="bold",
            bbox=dict(facecolor="black", alpha=0.45, pad=5, edgecolor="none"))
    ax.text(26, 64, "XUZHOU · JIAWANG FIELD AREA", fontsize=8, color="white",
            family="monospace",
            bbox=dict(facecolor="black", alpha=0.35, pad=3, edgecolor="none"))
    ax.text(mosaic.width - 14, mosaic.height - 10,
            "底图：Esri World Topo Map © Esri, USGS, NOAA · 点位为公开资料近似坐标",
            fontsize=7, color="white", ha="right", alpha=0.9,
            bbox=dict(facecolor="black", alpha=0.35, pad=3, edgecolor="none"))

    fig.savefig(OUT / "locator_map.jpg", dpi=220, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("locator_map.jpg (real map) done", mosaic.size)


if __name__ == "__main__":
    hero()
    locator()
    print("ALL DONE ->", OUT)
