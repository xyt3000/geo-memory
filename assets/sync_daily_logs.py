# -*- coding: utf-8 -*-
"""
实践动态同步：把 05_实践过程资料/可公开日志/ 中的日志同步进 Wiki 并更新侧边栏
安全边界：只有"可公开日志"文件夹里的文件才会上站；同步时再做一次脱敏扫描。
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent          # 社会实践/
SRC = ROOT / "05_实践过程资料" / "可公开日志"
DST = ROOT / "site" / "wiki" / "docs" / "daily"
SIDEBAR = ROOT / "site" / "wiki" / "docs" / "_sidebar.md"

NAMES = ["夏煜棠", "黄子豪", "覃汉杰", "孟杨", "崔文阳", "邱家宝", "杨添棋",
         "赵博睿", "王玺迪", "郭航", "孙天佑", "顾梣懿", "韩彪", "焦建亭"]

def scrub(text: str) -> str:
    text = re.sub(r"1[3-9]\d{9}", "（联系方式已脱敏）", text)
    for n in NAMES:
        text = text.replace(n, "队员")
    text = text.replace("消防", "有关单位")
    return text

def main():
    if not SRC.exists():
        print("无可公开日志目录，跳过")
        return
    logs = sorted(p for p in SRC.glob("日志_*.md"))
    if not logs:
        print("没有新日志，跳过")
        return

    DST.mkdir(parents=True, exist_ok=True)
    entries = []
    for p in logs:
        text = scrub(p.read_text(encoding="utf-8"))
        m = re.search(r"^#\s+(.+)$", text, re.M)
        title = m.group(1).strip() if m else p.stem
        (DST / p.name).write_text(text, encoding="utf-8")
        entries.append((p.name, title))
        print("synced:", p.name)

    # 动态首页（新的在前）
    lines = ["# 实践动态\n",
             "> 2026 年 8 月下旬 · 徐州贾汪 · 七天现场调研的每日记录\n"]
    for fn, title in reversed(entries):
        lines.append(f"- [{title}](daily/{fn})")
    (DST / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 侧边栏注入实践动态区
    sb = SIDEBAR.read_text(encoding="utf-8")
    block = "<!-- DAILY:BEGIN -->\n- **实践动态**\n- [最新日志](daily/README.md)\n" + \
            "".join(f"- [{t}](daily/{f})" for f, t in reversed(entries)) + \
            "<!-- DAILY:END -->"
    sb = re.sub(r"<!-- DAILY:BEGIN -->.*?<!-- DAILY:END -->", block, sb,
                flags=re.DOTALL)
    SIDEBAR.write_text(sb, encoding="utf-8")
    print(f"侧边栏已更新，共 {len(entries)} 篇日志")

if __name__ == "__main__":
    main()
