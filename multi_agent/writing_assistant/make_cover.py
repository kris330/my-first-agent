"""
生成《多 Agent 写作助手》公众号封面
尺寸：1280 × 720，风格与进阶篇系列一致。

运行：
  cd multi_agent/writing_assistant
  python make_cover.py
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
OUT  = os.path.join(os.path.dirname(__file__), "cover.png")

# 金色系 —— "最终项目"完成感
ACCENT = (234, 179, 8)
BG     = (18, 14, 4)

_HIRA  = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_M = (_HIRA, 1)
FONT_L = (_HIRA, 0)


# ── 通用工具 ─────────────────────────────────────────────────

def fnt(spec, size: int):
    try:
        if isinstance(spec, tuple):
            path, idx = spec
            return ImageFont.truetype(path, size, index=idx)
        return ImageFont.truetype(spec, size)
    except Exception:
        return ImageFont.load_default()


def make_base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img  = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    a    = ACCENT

    # 渐变背景
    for y in range(H):
        t = y / H
        c = tuple(max(0, int(BG[i] * (1.0 - t * 0.22))) for i in range(3))
        draw.line([(0, y), (W, y)], fill=(*c, 255))

    # 点阵网格
    for x in range(28, W, 52):
        for y in range(160, H - 50, 52):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(*a, 22))

    # 暗角
    for i in range(60, 0, -1):
        alpha = int((1 - i / 60) ** 2 * 55)
        bx, by = i * 2, int(i * 1.2)
        draw.rectangle([0, 0, W, by],       fill=(0, 0, 0, alpha))
        draw.rectangle([0, H-by, W, H],     fill=(0, 0, 0, alpha))
        draw.rectangle([0, 0, bx, H],       fill=(0, 0, 0, alpha))
        draw.rectangle([W-bx, 0, W, H],     fill=(0, 0, 0, alpha))

    return img, draw


def box(draw, x, y, w, h, text, fill_a=130, border_a=200, fs=22, r=10, bold=False):
    a = ACCENT
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=(*a, fill_a), outline=(*a, border_a), width=2)
    f  = fnt(FONT_M, fs + (2 if bold else 0))
    tc = (255, 255, 255, 235)
    lines = text.split("\n")
    lh = fs + 5
    ty = y + (h - len(lines) * lh) // 2
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=f)
        tx = x + (w - (bb[2] - bb[0])) // 2
        draw.text((tx, ty), line, font=f, fill=tc)
        ty += lh


def ghost_box(draw, x, y, w, h, r=8):
    a = ACCENT
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=(*a, 16), outline=(*a, 75), width=1)


def arr(draw, x1, y1, x2, y2, w=2, head=9):
    a = ACCENT
    c = (*a, 195)
    draw.line([(x1, y1), (x2, y2)], fill=c, width=w)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (-0.42, 0.42):
        ax = x2 - head * math.cos(ang + da)
        ay = y2 - head * math.sin(ang + da)
        draw.line([(x2, y2), (int(ax), int(ay))], fill=c, width=w)


def title_strip(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    SC  = 3
    s_w, s_h = W * SC, 168 * SC
    surf = Image.new("RGBA", (s_w, s_h), (0, 0, 0, 0))
    sd   = ImageDraw.Draw(surf, "RGBA")
    a    = ACCENT

    tag  = "进阶 Final"
    title = "多 Agent 写作助手"
    sub  = "Researcher · Writer · Editor  三 Agent 协作"

    # Tag 徽章
    tf  = fnt(FONT_L, 20 * SC)
    tb  = sd.textbbox((0, 0), tag, font=tf)
    bw_ = tb[2] - tb[0] + 28 * SC
    bh_ = tb[3] - tb[1] + 12 * SC
    sd.rounded_rectangle([52*SC, 36*SC, 52*SC+bw_, 36*SC+bh_],
                          radius=5*SC, fill=(*a, 200))
    sd.text((66*SC, 36*SC+6*SC), tag, font=tf, fill=(255, 255, 255, 245))

    # 主标题
    tf2 = fnt(FONT_L, 40 * SC)
    ty  = 36*SC + bh_ + 10*SC
    sd.text((52*SC, ty), title, font=tf2, fill=(255, 255, 255, 240))
    bb  = sd.textbbox((0, 0), title, font=tf2)
    ty += bb[3] - bb[1] + 2*SC

    # 副标题
    sd.text((52*SC, ty+6*SC), sub,
            font=fnt(FONT_L, 19*SC), fill=(*a, 190))

    small = surf.resize((W, 168), Image.LANCZOS)
    img.alpha_composite(small, (0, 0))


def brand_bar(draw: ImageDraw.ImageDraw) -> None:
    a = ACCENT
    y = H - 46
    draw.rectangle([0, y, W, H], fill=(*a, 18))
    draw.line([(0, y), (W, y)], fill=(*a, 70), width=1)
    f = fnt(FONT_L, 18)
    draw.text((52, y+13), "《AI Agent 进阶：手搓 Multi-Agent 系统》",
              font=f, fill=(255, 255, 255, 120))
    url = "github.com/kris330/my-first-agent"
    bb  = draw.textbbox((0, 0), url, font=f)
    draw.text((W-(bb[2]-bb[0])-56, y+13), url, font=f, fill=(*ACCENT, 110))


# ── 主图表：写作助手完整流水线 ────────────────────────────────

def draw_diagram(draw: ImageDraw.ImageDraw) -> None:
    a   = ACCENT
    f_s = fnt(FONT_L, 16)

    # ── 左半：流水线 ──────────────────────────────────────────
    cx_pipe = 420   # 流水线中心 x
    bw_pipe = 260   # 流水线框宽

    # 用户输入
    uy, uh = 192, 48
    box(draw, cx_pipe - bw_pipe//2, uy, bw_pipe, uh, "用户写作需求",
        fill_a=110, fs=20)

    # Orchestrator
    oy, oh = 282, 68
    box(draw, cx_pipe - bw_pipe//2 - 30, oy, bw_pipe + 60, oh,
        "Orchestrator（调度员）", fill_a=185, fs=20, bold=True)
    arr(draw, cx_pipe, uy+uh+2, cx_pipe, oy-2)

    # 注解：调度 · 传递 · 重试
    draw.text((cx_pipe - bw_pipe//2 - 30 + bw_pipe + 60 + 12, oy+20),
              "调度 · 传递上下文", font=f_s, fill=(*a, 145))
    draw.text((cx_pipe - bw_pipe//2 - 30 + bw_pipe + 60 + 12, oy+40),
              "失败时自动重试", font=f_s, fill=(*a, 125))

    # 三个 Worker（串行流水线）
    workers = [
        ("Researcher",   "分析主题 · 整理研究要点"),
        ("Writer",       "根据研究报告 · 写文章初稿"),
        ("Editor",       "审核润色 · 输出最终版本"),
    ]
    wh, wg = 58, 14
    worker_tops = []
    prev_bottom = oy + oh

    for i, (name, desc) in enumerate(workers):
        wy = prev_bottom + wg
        worker_tops.append(wy)

        # Task 下发标注（左侧）
        draw.text((cx_pipe - bw_pipe//2 - 72, wy + wh//2 - 9),
                  "Task ↓", font=f_s, fill=(*a, 125))

        # Worker 框
        box(draw, cx_pipe - bw_pipe//2, wy, bw_pipe, wh,
            name, fill_a=80 + i*30, fs=21, bold=True)

        # 功能描述（右侧）
        draw.text((cx_pipe + bw_pipe//2 + 14, wy + wh//2 - 9),
                  desc, font=f_s, fill=(*a, 150))

        # 箭头（从上一步底部到这一框）
        arr(draw, cx_pipe, prev_bottom+2, cx_pipe, wy-2)
        prev_bottom = wy + wh

    # TaskResult 返回竖线（左侧）
    ret_x = cx_pipe - bw_pipe//2 - 48
    draw.line([(ret_x, oy+oh//2), (ret_x, prev_bottom)],
              fill=(*a, 55), width=1)
    mid_y = (oy + oh//2 + prev_bottom) // 2
    draw.text((ret_x - 2, mid_y - 9), "↑", font=fnt(FONT_L, 18), fill=(*a, 90))
    draw.text((ret_x - 66, mid_y + 6), "TaskResult",
              font=fnt(FONT_L, 14), fill=(*a, 90))

    # 最终文章（底部）
    fy, fh = prev_bottom + wg, 48
    box(draw, cx_pipe - bw_pipe//2, fy, bw_pipe, fh,
        "最终文章", fill_a=165, fs=22, bold=True)
    arr(draw, cx_pipe, prev_bottom+2, cx_pipe, fy-2)

    # ── 右半：功能说明框 ──────────────────────────────────────
    rx, ry, rw = 760, 285, 468
    ghost_box(draw, rx, ry, rw, 250, r=10)

    f_title = fnt(FONT_M, 18)
    draw.text((rx+18, ry+12), "整合了进阶篇所有核心概念", font=f_title,
              fill=(255, 255, 255, 215))

    items = [
        ("进阶 Day 2", "Orchestrator 调度员模式"),
        ("进阶 Day 3", "Task / TaskResult 通信协议"),
        ("进阶 Day 4", "串行流水线（有依赖顺序）"),
        ("进阶 Day 5", "重试装饰器 + 局部失败容忍"),
    ]
    for i, (day, desc) in enumerate(items):
        iy = ry + 50 + i * 46
        # Day 标签
        draw.rounded_rectangle([rx+18, iy, rx+108, iy+28],
                                radius=5, fill=(*a, 130), outline=(*a, 180), width=1)
        draw.text((rx+28, iy+6), day, font=fnt(FONT_L, 14),
                  fill=(255, 255, 255, 230))
        # 描述
        draw.text((rx+120, iy+6), desc, font=fnt(FONT_L, 15),
                  fill=(255, 255, 255, 190))

    # 运行命令框
    cmd_y = ry + 260 + 12
    ghost_box(draw, rx, cmd_y, rw, 90, r=8)
    draw.text((rx+18, cmd_y+8), "运行方式", font=fnt(FONT_M, 16),
              fill=(255, 255, 255, 200))
    cmd_lines = [
        "cd multi_agent/writing_assistant",
        'python main.py "写一篇关于AI的科普文章"',
    ]
    for i, line in enumerate(cmd_lines):
        draw.text((rx+18, cmd_y+34+i*26), line, font=fnt(FONT_L, 15),
                  fill=(255, 255, 255, 200))


# ── 主入口 ────────────────────────────────────────────────────

if __name__ == "__main__":
    img, draw = make_base()
    draw_diagram(draw)
    title_strip(img, draw)
    brand_bar(draw)

    img.convert("RGB").save(OUT, "PNG")
    print(f"✓  封面已生成：{OUT}")
