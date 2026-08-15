# -*- coding: utf-8 -*-
"""
沉陷区的地质记忆 · 网站视觉素材生成（浅色图纸版）
全部基于项目公开数据（wiki 04/05/06）绘制的示意性地貌图件：
1. hero_contour.jpg   —— 潘安湖采煤沉陷盆地等高线示意（浅色地质图风）
2. cross_section.jpg  —— 采煤塌陷"上三带"机理地质剖面示意图
3. strat_column.jpg   —— 含煤地层柱状示意图
4. locator_map.jpg    —— 调研区位置与路线示意图
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

OUT = Path(__file__).parent / "img"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 浅色「公开地质图」风格（纯白底） ----------
PAPER   = "#ffffff"   # 纯白
PANEL   = "#eef0f2"   # 浅灰图框
INK     = "#232a32"   # 墨色
SUB     = "#67727e"   # 次要文字
FAINT   = "#ccd2d8"   # 网格/弱化
AMBER   = "#a86a24"   # 计曲线/标注（赭石）
AMBER_D = "#c49a63"   # 首曲线（浅赭）
TEAL    = "#2a8f8c"   # 水域线（青绿）
TEAL_D  = "#b9dbd7"   # 水域填充
TEAL_DD = "#8ec6bf"

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER, "text.color": INK,
    "axes.edgecolor": FAINT, "xtick.color": SUB, "ytick.color": SUB,
})


def smooth2d(Z, k=5, iters=2):
    """纯 numpy 盒式平滑"""
    Z = Z.copy()
    for _ in range(iters):
        P = np.pad(Z, k // 2, mode="edge")
        Z = sum(P[i:i + Z.shape[0], j:j + Z.shape[1]]
                for i in range(k) for j in range(k)) / (k * k)
    return Z


# ============================================================
# 1. HERO：潘安湖沉陷盆地等高线示意（浅色，3888×2208）
#    数据锚点：沉陷盆地约 11.6–12.6 km²，沉降 2–8 m（wiki 06）
# ============================================================
def hero():
    fig = plt.figure(figsize=(16, 9), dpi=240)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8); ax.set_ylim(0, 4.5); ax.axis("off")

    x = np.linspace(0, 8, 1600); y = np.linspace(0, 4.5, 900)
    X, Y = np.meshgrid(x, y)
    rng = np.random.default_rng(42)

    def basin(cx, cy, ax_, ay_, depth, rot=0.0):
        th = np.deg2rad(rot)
        Xr = (X - cx) * np.cos(th) + (Y - cy) * np.sin(th)
        Yr = -(X - cx) * np.sin(th) + (Y - cy) * np.cos(th)
        return depth * np.exp(-((Xr / ax_) ** 2 + (Yr / ay_) ** 2))

    Z = (basin(3.1, 2.3, 1.9, 1.15, 8.0, rot=25)
         + basin(5.9, 2.9, 1.15, 0.8, 5.5, rot=30)
         + basin(6.4, 1.2, 0.8, 0.55, 3.5, rot=-15)
         + 0.35 * np.sin(X * 1.3) * np.cos(Y * 1.7)
         + 0.12 * rng.standard_normal(X.shape))
    Z = smooth2d(Z, k=5, iters=3)

    Zmin = 8.6
    levels = np.arange(0, Zmin, 1.0)
    idx_levels = np.arange(0, Zmin, 4.0)

    # 水域（沉降 >3 m 视为常年积水，呼应平均积水深 4 m+）
    water = np.ma.masked_where(Z < 3.0, Z)
    ax.contourf(X, Y, water, levels=[3.0, Zmin + 1], colors=[TEAL_D],
                alpha=0.95, zorder=2)
    ax.contour(X, Y, Z, levels=[3.0], colors=[TEAL], linewidths=2.4,
               alpha=0.95, zorder=4)

    # 等高线
    ax.contour(X, Y, Z, levels=levels, colors=[AMBER_D], linewidths=0.5,
               alpha=0.9, zorder=3)
    cs2 = ax.contour(X, Y, Z, levels=idx_levels, colors=[AMBER],
                     linewidths=1.2, alpha=0.95, zorder=3)
    ax.clabel(cs2, fmt="-%d m", fontsize=7, colors=[AMBER], inline=True,
              inline_spacing=3)

    # 图廓网格与坐标注记
    for gx in np.arange(0.5, 8, 0.5):
        ax.plot([gx, gx], [0, 4.5], color=FAINT, lw=0.3, alpha=0.55, zorder=1)
    for gy in np.arange(0.5, 4.5, 0.5):
        ax.plot([0, 8], [gy, gy], color=FAINT, lw=0.3, alpha=0.55, zorder=1)
    for i, gx in enumerate(np.arange(0.5, 8, 1.0)):
        ax.text(gx, 4.5 - 0.08, f"117°{20 + i * 5:02d}′E", fontsize=6.5,
                color=SUB, ha="center", va="bottom", family="monospace")
    for i, gy in enumerate(np.arange(0.5, 4.5, 1.0)):
        ax.text(0.06, gy, f"34°{15 + i * 5:02d}′N", fontsize=6.5, color=SUB,
                ha="left", va="center", rotation=90, family="monospace")

    # 比例尺（8 单位 ≈ 6.4 km 示意）
    bx, by = 0.55, 0.42
    ax.plot([bx, bx + 1.25], [by, by], color=INK, lw=2.4, zorder=5)
    for i, lab in enumerate(["0", "1", "2 km"]):
        ax.plot([bx + i * 0.625, bx + i * 0.625], [by - 0.045, by + 0.045],
                color=INK, lw=1.4, zorder=5)
        ax.text(bx + i * 0.625, by + 0.09, lab, fontsize=8, color=INK,
                ha="center")
    # 指北针
    nx, ny = 7.35, 3.85
    ax.annotate("", xy=(nx, ny + 0.28), xytext=(nx, ny - 0.16),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6), zorder=5)
    ax.text(nx, ny + 0.36, "N", fontsize=11, color=INK, ha="center",
            fontweight="bold", family="serif")
    # 图名签
    ax.text(7.92, 0.30, "潘安湖采煤沉陷盆地 · 地貌形态示意", fontsize=10.5,
            color=INK, ha="right", fontweight="bold")
    ax.text(7.92, 0.16, "据项目公开数据绘制（盆地约 11.6–12.6 km²，沉降 2–8 m）· 非实测图件",
            fontsize=6.5, color=SUB, ha="right")

    fig.savefig(OUT / "hero_contour.jpg", dpi=240, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("hero_contour.jpg done")


# ============================================================
# 2. "上三带"机理剖面示意（浅色，2928×1739）
# ============================================================
def cross_section():
    fig = plt.figure(figsize=(12.5, 7.5), dpi=240)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94])
    ax.set_xlim(0, 12.5); ax.set_ylim(-5.6, 1.4); ax.axis("off")

    xs = np.linspace(0, 12.5, 500)
    surf = -0.15 - 1.9 * np.exp(-((xs - 6.2) / 2.6) ** 2)

    # 天空留白即 PAPER；水面
    ax.fill_between(xs, surf, -1.55, where=(surf < -1.55),
                    color=TEAL_D, alpha=0.95, zorder=3)
    ax.plot(xs[surf < -1.55], surf[surf < -1.55], color=TEAL, lw=2.2, zorder=4)
    ax.text(6.2, -1.30, "塌陷积水区", color=TEAL, fontsize=11, ha="center",
            fontweight="bold")

    # 地层
    bounds = [surf,
              surf - 1.55 * np.exp(-((xs - 6.2) / 3.0) ** 2) * 0.55 - 1.15,
              surf - 2.35 * np.exp(-((xs - 6.2) / 3.2) ** 2) * 0.5 - 1.65,
              surf - 3.15 * np.exp(-((xs - 6.2) / 3.4) ** 2) * 0.45 - 2.15,
              np.full_like(xs, -5.6)]
    names = ["第四系松散层", "二叠系 · 下石盒子组", "二叠系 · 山西组", "石炭系 · 太原组（含煤层）"]
    cols  = ["#e9e2d1", "#dcd3bd", "#cfc3a6", "#c2b08d"]
    hatchs = [None, "..", "--", None]
    hcols = ["#9a8f73", "#a39878", "#948a6c", "#6e7a68"]
    for i in range(4):
        ax.fill_between(xs, bounds[i], bounds[i + 1], color=cols[i],
                        zorder=2, hatch=hatchs[i], edgecolor=hcols[i],
                        linewidth=0)
        ax.text(1.05, float(np.mean([bounds[i][30], bounds[i + 1][30]])),
                names[i], color="#4d5661", fontsize=9.5, va="center")


    # 煤层 + 采空区
    coal_y0, coal_y1 = -4.55, -4.35
    ax.add_patch(Rectangle((0.4, coal_y0), 11.7, coal_y1 - coal_y0,
                           color="#3a3f45", zorder=3))
    ax.text(11.9, (coal_y0 + coal_y1) / 2, "煤层", color="#4d5661",
            fontsize=9, va="center", ha="right")
    ax.add_patch(Rectangle((5.2, coal_y0), 2.1, coal_y1 - coal_y0,
                           facecolor=PAPER, edgecolor=AMBER, lw=1.4,
                           linestyle="--", zorder=4))
    ax.text(6.25, coal_y0 - 0.22, "采空区", color=AMBER, fontsize=10,
            ha="center", fontweight="bold")

    # 上三带
    def zone(y0, y1, color, label, hatch=None):
        verts = [(5.35, y0), (7.15, y0), (6.9, y1), (5.6, y1)]
        ax.add_patch(Polygon(verts, closed=True, facecolor=color,
                             edgecolor=AMBER, lw=0.9, alpha=0.9,
                             hatch=hatch, zorder=3))
        ax.text(7.55, (y0 + y1) / 2, label, color=INK, fontsize=11,
                va="center", fontweight="bold")
        ax.plot([7.18, 7.5], [(y0 + y1) / 2, (y0 + y1) / 2],
                color=SUB, lw=0.8, zorder=3)

    zone(-4.35, -3.85, "#e3c9a3", "冒落带", hatch="xx")
    zone(-3.85, -3.05, "#eadfc2", "裂隙带", hatch="//")
    zone(-3.05, -2.15, "#d8e2dd", "弯曲带")

    # 地裂缝
    for fx in (3.65, 8.8):
        ax.plot([fx, fx + 0.12], [float(surf[np.argmin(abs(xs - fx))]),
                float(surf[np.argmin(abs(xs - fx))]) - 0.55],
                color=AMBER, lw=2.4, zorder=4)
    ax.text(3.28, float(surf[np.argmin(abs(xs - 3.65))]) + 0.13, "地裂缝",
            color=AMBER, fontsize=9.5, ha="center")

    # 应力箭头
    for sx_ in (5.6, 6.9):
        ax.annotate("", xy=(sx_, -4.15), xytext=(sx_, -3.35),
                    arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.1,
                                    alpha=0.85), zorder=4)

    ax.text(0.35, 1.05, "采煤塌陷形成机理示意 —— “上三带”",
            fontsize=15, color=INK, fontweight="bold")
    ax.text(0.35, 0.68, "煤炭采出 → 覆岩失稳 → 冒落 / 裂隙 / 弯曲三带发育 → 地表沉陷盆地 · 边缘地裂缝 · 高潜水位区积水成湖",
            fontsize=9, color=SUB)
    ax.text(12.15, -5.35, "示意剖面 · 据项目公开地质资料绘制", fontsize=7,
            color=SUB, ha="right")

    fig.savefig(OUT / "cross_section.jpg", dpi=240, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("cross_section.jpg done")


# ============================================================
# 3. 含煤地层柱状示意（浅色，1544×2465）
# ============================================================
def strat_column():
    fig = plt.figure(figsize=(8, 12), dpi=200)
    ax = fig.add_axes([0.03, 0.02, 0.94, 0.96])
    ax.set_xlim(0, 8); ax.set_ylim(0, 12); ax.axis("off")

    units = [
        ("第四系松散层", "", 12.0, 11.0, "#e9e2d1", []),
        ("二叠系 · 下石盒子组", "180–220 m · 可采煤层 3–5 层", 11.0, 7.6,
         "#dcd3bd", [8.9, 9.5, 10.2]),
        ("二叠系 · 山西组", "60–120 m · 可采煤层 2–6 层", 7.6, 5.2,
         "#cfc3a6", [5.7, 6.5]),
        ("石炭系 · 太原组", "140–190 m · 可采煤层 8–12 层", 5.2, 1.2,
         "#c2b08d", [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.4, 4.8]),
    ]
    for name, thick, top, bot, col, seams in units:
        ax.add_patch(Rectangle((1.0, bot), 3.2, top - bot, facecolor=col,
                               edgecolor="#9aa2ab", lw=1.0))
        ax.text(4.55, top - 0.30, name, fontsize=13, color=INK,
                va="center", fontweight="bold")
        if thick:
            ax.text(4.55, top - 0.72, thick, fontsize=9.5,
                    color=AMBER, va="center")
        for sy in seams:
            ax.add_patch(Rectangle((1.0, sy), 3.2, 0.13, facecolor="#3a3f45",
                                   edgecolor="#7d6a4a", lw=0.6, zorder=3))

    for sy, lab, ty in [(4.8, "1 煤 · 平均 1.5 m", 4.02),
                        (3.0, "3 煤 · 平均 3.42 m", 3.30),
                        (1.5, "9 煤 · 平均 1.89 m", 1.85)]:
        ax.annotate(lab, xy=(4.2, sy + 0.06), xytext=(4.75, ty),
                    fontsize=9.5, color=AMBER,
                    arrowprops=dict(arrowstyle="->", color="#c99a5e", lw=0.9))

    ax.set_title("贾汪含煤地层柱状示意\n可采煤层总厚 5.30–9.17 m · 缓倾斜煤层（倾角 4°–10°）",
                 fontsize=13, color=INK, loc="left", pad=18, fontweight="bold")
    ax.text(1.0, 0.45, "示意柱状图 · 地层厚度据项目公开地质资料", fontsize=8,
            color=SUB)

    fig.savefig(OUT / "strat_column.jpg", dpi=200, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("strat_column.jpg done")


# ============================================================
# 4. 调研区位置与路线示意（浅色，3050×2050）
# ============================================================
def locator():
    fig = plt.figure(figsize=(12, 8), dpi=250)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(117.20, 117.52); ax.set_ylim(34.22, 34.50); ax.axis("off")

    # 背景微地形（浅色等高纹理）
    x = np.linspace(117.20, 117.52, 400); y = np.linspace(34.22, 34.50, 350)
    X, Y = np.meshgrid(x, y)
    rng = np.random.default_rng(7)
    Z = (np.sin((X - 117.2) * 55) * np.cos((Y - 34.2) * 60) * 0.5
         + 0.5 * rng.standard_normal(X.shape))
    Z = smooth2d(Z, k=7, iters=3)
    ax.contour(X, Y, Z, levels=10, colors=[PANEL], linewidths=6, alpha=0.8)

    # 河流
    river_x = [117.225, 117.25, 117.28, 117.31]; river_y = [34.24, 34.27, 34.30, 34.34]
    ax.plot(river_x, river_y, color=TEAL_DD, lw=5, alpha=0.9, solid_capstyle="round")
    ax.text(117.252, 34.252, "京杭大运河", color=TEAL, fontsize=9, rotation=38)
    bulao_x = [117.36, 117.40, 117.44, 117.50]; bulao_y = [34.375, 34.395, 34.43, 34.47]
    ax.plot(bulao_x, bulao_y, color=TEAL_DD, lw=4, alpha=0.9, solid_capstyle="round")
    ax.text(117.455, 34.455, "不牢河", color=TEAL, fontsize=9, rotation=42)

    pts = [
        ("徐州东站 · 集结", 117.287, 34.264, "#67727e", ""),
        ("大吴街道（未修复塌陷区）", 117.350, 34.330, AMBER, ""),
        ("潘安湖国家湿地公园", 117.397, 34.365, TEAL, ""),
        ("权台煤矿遗址创意园", 117.418, 34.352, "#67727e", ""),
        ("贾汪城区", 117.451, 34.436, "#67727e", ""),
    ]
    for name, px, py, col, tag in pts:
        ax.scatter([px], [py], s=110, color=col, zorder=5,
                   edgecolors=PAPER, linewidths=1.5)
        ax.annotate(name, xy=(px, py), xytext=(px + 0.008, py + 0.004),
                    fontsize=10.5, color=INK, fontweight="bold", zorder=6)
        if tag:
            ax.annotate(tag, xy=(px, py), xytext=(px + 0.008, py - 0.008),
                        fontsize=8, color=SUB, zorder=6)

    route_x = [117.287, 117.318, 117.350, 117.375, 117.397]
    route_y = [34.264, 34.295, 34.330, 34.350, 34.365]
    ax.plot(route_x, route_y, color=AMBER, lw=1.8, linestyle=(0, (6, 4)),
            alpha=0.95, zorder=4)

    nx, ny = 117.498, 34.475
    ax.annotate("", xy=(nx, ny + 0.012), xytext=(nx, ny - 0.006),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.text(nx, ny + 0.015, "N", fontsize=10, color=INK, ha="center",
            fontweight="bold", family="serif")
    bx, by = 117.222, 34.236
    ax.plot([bx, bx + 0.045], [by, by], color=INK, lw=2.2)
    for i, lab in enumerate(["0", "约 4 km"]):
        ax.text(bx + i * 0.045, by + 0.0035, lab, fontsize=8, color=INK,
                ha="center")
    ax.text(117.508, 34.228, "调研区位置与路线示意 · 点位为公开地图近似坐标",
            fontsize=7.5, color=SUB, ha="right")
    ax.text(117.212, 34.484, "徐州 · 贾汪", fontsize=17, color=INK,
            fontweight="bold")
    ax.text(117.212, 34.472, "XUZHOU · JIAWANG FIELD AREA", fontsize=8,
            color=SUB, family="monospace")

    fig.savefig(OUT / "locator_map.jpg", dpi=250, bbox_inches="tight",
                pil_kwargs={"quality": 90})
    plt.close(fig)
    print("locator_map.jpg done")


hero()
cross_section()
# 地层柱状图由 gen_strat_pro.py 专业版单独生成，此处不再覆盖
locator()
print("ALL DONE ->", OUT)
