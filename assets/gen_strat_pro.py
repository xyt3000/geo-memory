# -*- coding: utf-8 -*-
"""
贾汪含煤地层综合柱状图 · 专业版
遵循地质图件规范（FGDC 岩性花纹惯例）：
- 栏宽随粒级变化（泥岩窄 → 砂岩宽 → 灰岩/煤层全宽）
- 岩性花纹：表土=点+短划 / 泥岩=水平线 / 粉砂岩=密点 / 砂岩=稀点 / 灰岩=砖墙 / 煤层=黑带
- 左侧深度标尺，右侧地层单位（系/统/组 · 代号）、厚度与岩性描述，图例框
数据来源：项目 wiki 06（下石盒子组 180–220m / 山西组 60–120m / 太原组 140–190m，可采煤层总厚 5.30–9.17m）
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
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "img"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = "#ffffff"; INK = "#232a32"; SUB = "#67727e"; FAINT = "#a8b0b8"
AMBER = "#a86a24"; COAL = "#26262a"
LITH = {"soil": "#ece5d3", "mud": "#e3dcc8", "silt": "#d9cfae",
        "sand": "#cfbf99", "lime": "#c9d1c2", "coal": COAL}

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER, "text.color": INK,
})

rng = np.random.default_rng(2026)

# ---------- 岩性花纹 ----------
def pat_soil(ax, x0, x1, y0, y1, lw=0.6, col="#8a7f63", z=3):
    n = max(3, int((y1 - y0) * 14))
    xs = rng.uniform(x0 + 0.06, x1 - 0.06, n)
    ys = rng.uniform(y0 + 0.04, y1 - 0.04, n)
    for sx, sy in zip(xs, ys):
        if rng.random() < 0.5:
            ax.plot([sx - 0.045, sx + 0.045], [sy, sy], color=col, lw=lw,
                    solid_capstyle="round", zorder=z)
        else:
            ax.plot([sx], [sy], marker=".", ms=1.8, color=col, zorder=z)

def pat_mud(ax, x0, x1, y0, y1, lw=0.5, col="#9a8f73", z=3):
    dy = 1.15
    for yy in np.arange(y0 + dy / 2, y1, dy):
        ax.plot([x0 + 0.05, x1 - 0.05], [yy, yy], color=col, lw=lw, zorder=z)

def pat_silt(ax, x0, x1, y0, y1, col="#7d7357", z=3):
    n = max(6, int((y1 - y0) * (x1 - x0) * 16))
    xs = rng.uniform(x0 + 0.05, x1 - 0.05, n)
    ys = rng.uniform(y0 + 0.03, y1 - 0.03, n)
    ax.plot(xs, ys, linestyle="none", marker=".", ms=1.7, color=col, zorder=z)
    for sx, sy in zip(xs[::4], ys[::4]):
        ax.plot([sx - 0.05, sx + 0.05], [sy, sy], color=col, lw=0.5, zorder=z)

def pat_sand(ax, x0, x1, y0, y1, col="#7d7357", z=3):
    n = max(5, int((y1 - y0) * (x1 - x0) * 9))
    xs = rng.uniform(x0 + 0.05, x1 - 0.05, n)
    ys = rng.uniform(y0 + 0.03, y1 - 0.03, n)
    ax.plot(xs, ys, linestyle="none", marker=".", ms=2.2, color=col, zorder=z)

def pat_lime(ax, x0, x1, y0, y1, lw=0.55, col="#6e7a68", z=3):
    dy = 1.25
    rows = np.arange(y0, y1, dy)
    for i, yy in enumerate(rows):
        ax.plot([x0 + 0.04, x1 - 0.04], [yy, yy], color=col, lw=lw, zorder=z)
        for xx in np.arange(x0 + (0.5 if i % 2 else 1.0), x1 - 0.1, 1.05):
            if yy + dy < y1:
                ax.plot([xx, xx], [yy, min(yy + dy, y1)], color=col, lw=lw,
                        zorder=z)

PATTERNS = {"soil": pat_soil, "mud": pat_mud, "silt": pat_silt,
            "sand": pat_sand, "lime": pat_lime}

# ---------- 柱状栏宽（随粒级） ----------
W = {"mud": 1.15, "silt": 1.5, "sand": 1.95, "lime": 1.95, "soil": 1.5,
     "coal": 1.95}

# ---------- 地层数据（厚度 m，按 wiki 06 区间取代表值；顶界在上） ----------
# (岩性, 厚度, 描述)  自上而下
UNITS = [
    ("Q", "第四系", "", [
        ("soil", 20, "表土、粉砂质粘土"),
    ]),
    (r"$\rm P_1x$", "二叠系下统", "下石盒子组 · 180–220 m", [
        ("mud", 42, "泥岩"),
        ("silt", 30, "粉砂岩"),
        ("sand", 38, "中细粒砂岩"),
        ("coal", 1.5, "1 煤"),
        ("mud", 34, "泥岩夹粉砂岩"),
        ("sand", 26, "砂岩"),
        ("coal", 1.2, "煤线"),
        ("silt", 27, "粉砂岩夹泥岩"),
    ]),
    (r"$\rm P_1s$", "二叠系下统", "山西组 · 60–120 m", [
        ("sand", 24, "中粗粒砂岩"),
        ("mud", 20, "泥岩"),
        ("coal", 3.4, "3 煤"),
        ("silt", 22, "粉砂岩"),
        ("coal", 1.1, "煤线"),
        ("sand", 19, "砂岩"),
    ]),
    (r"$\rm C_3t$", "石炭系上统", "太原组 · 140–190 m", [
        ("lime", 16, "灰岩"),
        ("mud", 14, "泥岩"),
        ("coal", 1.0, "煤线"),
        ("sand", 15, "细粒砂岩"),
        ("coal", 1.0, "煤线"),
        ("lime", 13, "灰岩"),
        ("mud", 12, "泥岩"),
        ("coal", 1.2, "煤线"),
        ("silt", 13, "粉砂岩"),
        ("coal", 1.0, "煤线"),
        ("lime", 14, "灰岩"),
        ("mud", 12, "泥岩"),
        ("coal", 1.9, "9 煤"),
        ("sand", 13, "砂岩"),
        ("lime", 12, "灰岩（基底相）"),
    ]),
    ("O", "奥陶系", "灰岩基底", [
        ("lime", 26, "厚层灰岩"),
    ]),
]

def main():
    fig = plt.figure(figsize=(11.5, 13.5), dpi=200)
    ax = fig.add_axes([0.02, 0.015, 0.96, 0.955])
    total = sum(t for _, _, _, beds in UNITS for _, t, _ in beds)
    ax.set_xlim(0, 11.5); ax.set_ylim(-2, total + 16); ax.axis("off")

    X0 = 3.4          # 柱状左缘
    DEPTH_X = 2.9     # 标尺位置
    top = total

    # ---------- 顶栏表头 ----------
    ax.text(X0 + 1.0, top + 2.6, "岩性柱状", fontsize=10, color=SUB,
            ha="center", fontweight="bold")
    ax.text(7.4, top + 2.6, "地层单位与岩性描述", fontsize=10, color=SUB,
            fontweight="bold")

    y = top
    for code, series, group, beds in UNITS:
        unit_top = y
        for lith, thick, desc in beds:
            y1 = y - thick
            w = W[lith]
            x1 = X0 + w
            face = LITH[lith]
            ax.add_patch(Rectangle((X0, y1), w, thick, facecolor=face,
                                   edgecolor="#6b6152", lw=0.9, zorder=2))
            if lith != "coal":
                PATTERNS[lith](ax, X0, x1, y1, y)
            else:
                # 煤层右侧注记
                ax.text(x1 + 0.12, (y + y1) / 2, desc, fontsize=7.5,
                        color=COAL, va="center", fontweight="bold", zorder=4)
            y = y1
        # 地层单位横线与右侧标注
        ax.plot([X0 - 0.12, X0 + 2.2], [unit_top, unit_top], color=INK,
                lw=1.3, zorder=4)
        ax.plot([X0 - 0.12, X0 + 2.2], [y, y], color=INK, lw=1.3, zorder=4)
        # 大括号
        bx = X0 + 2.35
        ax.plot([bx, bx + 0.12, bx + 0.12, bx], [unit_top, unit_top, y, y],
                color=INK, lw=1.0, zorder=4)
        midy = (unit_top + y) / 2
        ax.plot([bx + 0.12, bx + 0.3], [midy, midy], color=INK, lw=1.0)
        # 代号 + 单位名
        ax.text(bx + 0.42, midy + 3.6, code, fontsize=15, color=INK,
                fontweight="bold", va="center")
        gname = group.split(" · ")[0]
        if not gname:                      # 如第四系：系列名直接作单位名
            gname, series = series, ""
        ax.text(bx + 1.5, midy + 3.6, gname, fontsize=12.5, color=INK,
                fontweight="bold", va="center")
        if "·" in group:
            ax.text(bx + 1.5, midy - 1.6, group.split("· ")[1],
                    fontsize=9, color=AMBER, va="center", family="monospace")
        if series:
            ax.text(bx + 1.5, midy - 6.8, series, fontsize=9, color=SUB,
                    va="center")

    # ---------- 深度标尺 ----------
    ax.plot([DEPTH_X, DEPTH_X], [0, top], color=INK, lw=1.0)
    for d in range(0, int(top) + 1, 50):
        yy = top - d
        ax.plot([DEPTH_X - 0.12, DEPTH_X], [yy, yy], color=INK, lw=1.0)
        ax.text(DEPTH_X - 0.2, yy, f"{d}", fontsize=7.5, color=SUB,
                ha="right", va="center", family="monospace")
    ax.text(DEPTH_X, top + 2.6, "深度/m", fontsize=9, color=SUB, ha="center")

    # ---------- 图例 ----------
    lx, ly = 8.35, 96
    ax.add_patch(Rectangle((lx - 0.25, ly - 40), 2.95, 44, facecolor="#ffffff",
                           edgecolor=INK, lw=1.0, zorder=5))
    ax.text(lx + 1.22, ly + 1.6, "图 例", fontsize=10.5, color=INK,
            ha="center", fontweight="bold", zorder=6)
    legend_items = [
        ("soil", "表土"), ("mud", "泥岩"), ("silt", "粉砂岩"),
        ("sand", "砂岩"), ("lime", "灰岩"), ("coal", "煤层"),
    ]
    for i, (lith, name) in enumerate(legend_items):
        ry = ly - 5.5 - i * 5.6
        ax.add_patch(Rectangle((lx, ry - 1.7), 1.15, 3.4,
                               facecolor=LITH[lith], edgecolor="#6b6152",
                               lw=0.7, zorder=6))
        if lith != "coal":
            PATTERNS[lith](ax, lx, lx + 1.15, ry - 1.7, ry + 1.7, z=7)
        ax.text(lx + 1.45, ry, name, fontsize=9.5, color=INK, va="center",
                zorder=6)

    # ---------- 标题与注记 ----------
    ax.text(0.15, top + 13.0, "贾汪含煤地层综合柱状图", fontsize=17,
            color=INK, fontweight="bold")
    ax.text(0.15, top + 8.6, "可采煤层总厚 5.30–9.17 m · 缓倾斜煤层（倾角 4°–10°）· 1/3/9 煤为旗山矿主采煤层",
            fontsize=9, color=SUB)
    ax.text(0.15, -1.6, "示意柱状图 · 栏宽随粒级变化 · 层序与厚度据项目公开地质资料综合，不代表单一钻孔",
            fontsize=7.5, color=SUB)

    fig.savefig(OUT / "strat_column.jpg", dpi=200, bbox_inches="tight",
                pil_kwargs={"quality": 92})
    plt.close(fig)
    print("strat_column.jpg (pro) done")


if __name__ == "__main__":
    main()
