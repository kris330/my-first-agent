#!/usr/bin/env python3
"""Generate PNG diagrams for harness_engineering_article.md"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "article_diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

_HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def fnt(size: int, idx: int = 1) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(_HIRA, size, index=idx)
    except Exception:
        return ImageFont.load_default()


# ── Palette ──────────────────────────────────────────────────────────────────
BG     = (12,  12,  28)
SURF   = (22,  24,  48)
SURF2  = (32,  34,  64)
SURF3  = (44,  46,  84)
BORDER = (55,  60, 105)
ACCENT = (129, 140, 248)
ACCD   = (79,  90, 198)
TEXT   = (230, 232, 245)
DIM    = (150, 155, 200)
TACC   = (167, 169, 255)
GREEN  = (52,  211, 153)
YELLOW = (251, 191,  36)
RED    = (248, 113, 113)
PURPLE = (192, 132, 252)
TEAL   = (45,  212, 191)
ORANGE = (251, 146,  60)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _bb(d: ImageDraw.Draw, t: str, f):
    return d.textbbox((0, 0), t, font=f)


def tw(d, t, f) -> int:
    b = _bb(d, t, f); return b[2] - b[0]


def th(d, t, f) -> int:
    b = _bb(d, t, f); return b[3] - b[1]


def ct(d, cx, cy, t, f, fill):
    """Draw text centered at (cx, cy)."""
    b = _bb(d, t, f)
    d.text((cx - (b[2]-b[0])//2 - b[0], cy - (b[3]-b[1])//2 - b[1]),
           t, font=f, fill=fill)


def make_bg(w: int, h: int) -> tuple[Image.Image, ImageDraw.Draw]:
    img = Image.new("RGBA", (w, h), (*BG, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(h):
        t = y / h
        c = tuple(max(0, int(BG[i] * (1 - t * 0.15))) for i in range(3))
        d.line([(0, y), (w, y)], fill=(*c, 255))
    for x in range(40, w, 60):
        for yy in range(40, h, 60):
            d.ellipse([x-1, yy-1, x+1, yy+1], fill=(*ACCENT, 14))
    for i in range(40, 0, -1):
        a = int((1 - i/40)**2 * 42)
        bx, by = i*2, int(i*1.5)
        d.rectangle([0, 0, w, by], fill=(0, 0, 0, a))
        d.rectangle([0, h-by, w, h], fill=(0, 0, 0, a))
        d.rectangle([0, 0, bx, h], fill=(0, 0, 0, a))
        d.rectangle([w-bx, 0, w, h], fill=(0, 0, 0, a))
    return img, d


def adown(d, x, y1, y2, col=ACCENT, lw=2, hs=10):
    """Draw a downward arrow."""
    c = (*col, 210)
    d.line([(x, y1), (x, y2)], fill=c, width=lw)
    for da in (-0.42, 0.42):
        d.line([(x, y2), (int(x - hs*math.sin(da)), int(y2 - hs*math.cos(da)))],
               fill=c, width=lw)


def aright(d, x1, x2, y, col=ACCENT, lw=2, hs=10):
    """Draw a rightward arrow."""
    c = (*col, 210)
    d.line([(x1, y), (x2, y)], fill=c, width=lw)
    for da in (-0.42, 0.42):
        d.line([(x2, y), (int(x2 - hs*math.cos(da)), int(y - hs*math.sin(da)))],
               fill=c, width=lw)


def rr(d, x1, y1, x2, y2, fill=None, outline=None, r=8, ow=1):
    """Draw a rounded rectangle."""
    kw: dict = {"radius": r}
    if fill is not None:
        kw["fill"] = (*fill[:3], fill[3] if len(fill) == 4 else 255)
    if outline is not None:
        kw["outline"] = (*outline, 200); kw["width"] = ow
    d.rounded_rectangle([x1, y1, x2, y2], **kw)


# ── Diagram 1: Evolution Table ─────────────────────────────────────────────
def diagram_evolution() -> None:
    W, H = 1200, 600
    SC = 2
    surf = Image.new("RGBA", (W*SC, H*SC), (0, 0, 0, 0))
    sd = ImageDraw.Draw(surf, "RGBA")

    def _bg(img, d, w, h):
        for y in range(h):
            t = y / h
            c = tuple(max(0, int(BG[i] * (1 - t * 0.15))) for i in range(3))
            d.line([(0, y), (w, y)], fill=(*c, 255))
        for x in range(40, w, 60):
            for yy in range(40, h, 60):
                d.ellipse([x-1, yy-1, x+1, yy+1], fill=(*ACCENT, 14))
        for i in range(40, 0, -1):
            a = int((1 - i/40)**2 * 42)
            bx, by = i*2, int(i*1.5)
            d.rectangle([0, 0, w, by], fill=(0, 0, 0, a))
            d.rectangle([0, h-by, w, h], fill=(0, 0, 0, a))
            d.rectangle([0, 0, bx, h], fill=(0, 0, 0, a))
            d.rectangle([w-bx, 0, w, h], fill=(0, 0, 0, a))

    base = Image.new("RGBA", (W, H), (*BG, 255))
    bd = ImageDraw.Draw(base, "RGBA")
    _bg(base, bd, W, H)

    # work on 2× surface
    s = SC
    fw = W * s
    fh = H * s

    cols_x = [60*s, 260*s, 540*s, 820*s, 1160*s]
    rows_y = [80*s, 148*s, 250*s, 352*s, 454*s, 554*s]

    col_colors = [SURF2, SURF3, SURF3, SURF3]
    header_fills = [(*ACCD, 180), (*ACCD, 200), (*ACCD, 200), (*ACCENT, 200)]

    fhdr  = fnt(22*s, 1)
    fcell = fnt(19*s, 1)
    ftag  = fnt(16*s, 0)
    ftitle = fnt(26*s, 1)

    # title
    title_text = "AI 工程方法论演进路线"
    sd.text((60*s, 22*s), title_text, font=ftitle, fill=(*TEXT, 220))
    # accent underline
    tw_ = tw(sd, title_text, ftitle)
    sd.rectangle([60*s, 62*s, 60*s + tw_ + 4*s, 65*s], fill=(*ACCENT, 200))

    # draw cells
    labels = ["", "Prompt Eng.\n2023", "Context Eng.\n2024–2025", "Harness Eng.\n2026"]
    row_labels = ["核心问题", "作用范围", "关注点", "类比"]
    data = [
        ["核心问题", '怎么「问」AI', '给 AI\n什么「信息」', '怎么搭\n「系统」'],
        ["作用范围", "单次交互", "单个\n上下文窗口", "跨多次交互\n整个生命周期"],
        ["关注点",   "指令质量", "信息质量", "系统可靠性"],
        ["类比",     "怎么写\n需求文档", "给员工备齐\n背景资料", "搭一套\n公司管理制度"],
    ]

    def cell_rect(col, row):
        return cols_x[col], rows_y[row], cols_x[col+1]-4*s, rows_y[row+1]-4*s

    # header row
    for ci, (label, hfill) in enumerate(zip(labels, header_fills)):
        x1, y1, x2, y2 = cell_rect(ci, 0)
        sd.rounded_rectangle([x1, y1, x2, y2], radius=6*s, fill=hfill)
        if label:
            lines = label.split('\n')
            cy = (y1+y2)//2
            if len(lines) == 2:
                h0 = th(sd, lines[0], fhdr)
                h1 = th(sd, lines[1], ftag)
                gap = 8*s
                total = h0 + gap + h1
                y0 = cy - total//2
                ct(sd, (x1+x2)//2, y0 + h0//2, lines[0], fhdr, (*TEXT, 230))
                ct(sd, (x1+x2)//2, y0 + h0 + gap + h1//2, lines[1], ftag, (*TACC, 200))
            else:
                ct(sd, (x1+x2)//2, cy, label, fhdr, (*TEXT, 230))

    # data rows
    row_accent_fills = [
        (*SURF, 200),
        (*SURF2, 200),
        (*SURF, 200),
        (*SURF2, 200),
    ]
    row_label_fills = [
        (*ACCD, 140),
        (*ACCD, 140),
        (*ACCD, 140),
        (*ACCD, 140),
    ]
    data_col_accents = [GREEN, YELLOW, RED]

    for ri, row in enumerate(data):
        for ci in range(4):
            x1, y1, x2, y2 = cell_rect(ci, ri+1)
            fill = row_label_fills[ri] if ci == 0 else row_accent_fills[ri]
            sd.rounded_rectangle([x1, y1, x2, y2], radius=6*s, fill=fill)
            txt = row[ci]
            lines = txt.split('\n')
            cx_cell = (x1+x2)//2
            cy_cell = (y1+y2)//2
            text_color = (*TACC, 220) if ci == 0 else (*TEXT, 210)
            if ci == 3:
                text_color = (*GREEN, 230)
            elif ci == 1:
                text_color = (*DIM, 220)
            elif ci == 2:
                text_color = (*DIM, 220)
            if len(lines) == 1:
                ct(sd, cx_cell, cy_cell, txt, fcell, text_color)
            else:
                total_h = sum(th(sd, ln, fcell) for ln in lines) + (len(lines)-1)*8*s
                y_cur = cy_cell - total_h//2
                for ln in lines:
                    lh = th(sd, ln, fcell)
                    ct(sd, cx_cell, y_cur + lh//2, ln, fcell, text_color)
                    y_cur += lh + 8*s

    # grid lines
    for rx in cols_x[1:-1]:
        sd.line([(rx-2*s, rows_y[0]), (rx-2*s, rows_y[-1])], fill=(*BORDER, 60), width=s)
    for ry in rows_y[1:-1]:
        sd.line([(cols_x[0], ry-2*s), (cols_x[-1], ry-2*s)], fill=(*BORDER, 60), width=s)

    small = surf.resize((W, H), Image.LANCZOS)
    base.alpha_composite(small, (0, 0))
    base.convert("RGB").save(os.path.join(OUT_DIR, "diagram_evolution.png"))
    print("✓ diagram_evolution.png")


# ── Diagram 2: Harness Architecture ───────────────────────────────────────
def diagram_arch() -> None:
    W, H = 960, 720
    img, d = make_bg(W, H)

    f_title  = fnt(15, 0)
    f_main   = fnt(18, 1)
    f_sub    = fnt(14, 0)
    f_label  = fnt(13, 0)
    f_tag    = fnt(12, 0)

    cx = W // 2

    # Title
    title = "Harness 完整架构"
    d.text((40, 22), title, font=fnt(20, 1), fill=(*TEXT, 210))
    d.rectangle([40, 52, 40 + tw(d, title, fnt(20,1)) + 4, 55], fill=(*ACCENT, 190))

    # ── 用户/任务输入 box ──
    y0 = 76
    bw, bh = 240, 48
    rr(d, cx-bw//2, y0, cx+bw//2, y0+bh, SURF2, ACCENT, r=10, ow=1)
    ct(d, cx, y0+bh//2, "用户 / 任务输入", f_main, (*TEXT, 220))

    # Arrow down
    adown(d, cx, y0+bh, y0+bh+26, ACCENT, lw=2, hs=8)

    # ── HARNESS 层 outer box ──
    har_y1 = y0 + bh + 26
    har_y2 = har_y1 + 212
    har_pad = 20
    rr(d, 40, har_y1, W-40, har_y2, (*ACCD, 22), ACCENT, r=12, ow=1)
    d.text((60, har_y1 + 10), "HARNESS 层", font=fnt(14, 1), fill=(*TACC, 210))

    # 4 inner boxes
    inner_data = [
        ("规则文件\nAGENTS.md", PURPLE),
        ("上下文管理\n历史 / 检索", TEAL),
        ("工具 & API\nMCP 协议", GREEN),
        ("控制流 &\n人工审批门", ORANGE),
    ]
    n = len(inner_data)
    box_y1 = har_y1 + 36
    box_y2 = har_y2 - 14
    bw_each = (W - 80 - (n-1)*12 - 2*har_pad) // n
    for i, (label, col) in enumerate(inner_data):
        bx1 = 40 + har_pad + i * (bw_each + 12)
        bx2 = bx1 + bw_each
        rr(d, bx1, box_y1, bx2, box_y2, (*col[:3], 28), col, r=8, ow=1)
        lines = label.split('\n')
        by_c = (box_y1 + box_y2) // 2
        total_h = th(d, lines[0], f_main) + 8 + th(d, lines[1], f_sub) if len(lines)==2 else th(d, lines[0], f_main)
        yy = by_c - total_h//2
        ct(d, (bx1+bx2)//2, yy + th(d, lines[0], f_main)//2, lines[0], f_main, (*col[:3], 240))
        if len(lines) == 2:
            yy2 = yy + th(d, lines[0], f_main) + 8
            ct(d, (bx1+bx2)//2, yy2 + th(d, lines[1], f_sub)//2, lines[1], f_sub, (*col[:3], 180))

    # Arrow down
    adown(d, cx, har_y2, har_y2+28, ACCENT, lw=2, hs=8)

    # ── MODEL 层 ──
    mod_y1 = har_y2 + 28
    mod_y2 = mod_y1 + 56
    rr(d, 100, mod_y1, W-100, mod_y2, (*ACCENT[:3], 30), ACCENT, r=10, ow=1)
    ct(d, cx, mod_y1+14, "MODEL 层（推理核心）", f_main, (*TEXT, 220))
    ct(d, cx, mod_y1+38, "GPT-4o  /  Claude  /  Gemini", f_sub, (*DIM, 200))

    # Arrow down
    adown(d, cx, mod_y2, mod_y2+28, ACCENT, lw=2, hs=8)

    # ── Safety 层 ──
    saf_y1 = mod_y2 + 28
    saf_y2 = saf_y1 + 56
    rr(d, 100, saf_y1, W-100, saf_y2, (*YELLOW[:3], 20), YELLOW, r=10, ow=1)
    ct(d, cx, saf_y1+14, "Safety & 可观测性", f_main, (*TEXT, 220))
    ct(d, cx, saf_y1+38, "guardrail  /  权限检查  /  行为追踪", f_sub, (*DIM, 200))

    # Arrow down
    adown(d, cx, saf_y2, saf_y2+28, ACCENT, lw=2, hs=8)

    # ── 质量门控 ──
    out_y1 = saf_y2 + 28
    out_y2 = out_y1 + 56
    rr(d, 100, out_y1, W-100, out_y2, (*GREEN[:3], 20), GREEN, r=10, ow=1)
    ct(d, cx, out_y1+14, "输出 / CI 质量门控", f_main, (*TEXT, 220))
    ct(d, cx, out_y1+38, "linter  /  测试  /  安全扫描", f_sub, (*DIM, 200))

    img.convert("RGB").save(os.path.join(OUT_DIR, "diagram_arch.png"))
    print("✓ diagram_arch.png")


# ── Diagram 3: Harness Workflow ────────────────────────────────────────────
def diagram_workflow() -> None:
    W, H = 840, 720
    img, d = make_bg(W, H)

    f_main  = fnt(17, 1)
    f_sub   = fnt(13, 0)
    f_label = fnt(12, 0)

    cx = 220  # center of main flow boxes
    note_x = 460  # left edge of annotation text

    title = "Harness 工作流"
    d.text((40, 22), title, font=fnt(20, 1), fill=(*TEXT, 210))
    d.rectangle([40, 52, 40 + tw(d, title, fnt(20,1)) + 4, 55], fill=(*ACCENT, 190))

    boxes = [
        (70,  "任务输入",  SURF2,  BORDER, None,   None),
        (170, "约束前馈",  (*PURPLE[:3], 35), PURPLE, "← AGENTS.md 规则注入", "AI 生成前就知道边界在哪"),
        (310, "AI 生成内容", SURF2, BORDER, None,   None),
        (410, "反馈回路",  (*TEAL[:3], 35), TEAL, "← linter 报错 → 结构化发给 AI", "AI 自我修正"),
        (550, "质量门控",  (*GREEN[:3], 35), GREEN, None,   None),
        (660, "合并代码库", (*ACCENT[:3], 30), ACCENT, None,  None),
    ]

    bw, bh = 300, 56

    for i, (y, label, fill, border, note1, note2) in enumerate(boxes):
        x1, x2 = cx - bw//2, cx + bw//2
        rr(d, x1, y, x2, y+bh, fill, border, r=10, ow=1)
        ct(d, cx, y+bh//2, label, f_main, (*TEXT, 230))

        if note1:
            d.text((note_x, y + 8), note1, font=f_sub, fill=(*DIM, 200))
        if note2:
            d.text((note_x, y + 28), note2, font=f_sub, fill=(*DIM, 180))

        # Arrow to next (except last)
        if i < len(boxes) - 1:
            next_y = boxes[i+1][0]
            if i == 4:  # 质量门控 → branch
                adown(d, cx, y+bh, next_y, ACCENT, lw=2, hs=8)
                # label "通过"
                d.text((cx+8, y+bh+4), "通过", font=f_label, fill=(*GREEN, 200))
            else:
                adown(d, cx, y+bh, next_y, ACCENT, lw=2, hs=8)

    # "不通过" side arrow from 质量门控
    qc_y = boxes[4][0]
    block_x = W - 100
    block_y = qc_y + 12
    aright(d, cx + bw//2, block_x - 120, qc_y + bh//2, RED, lw=2, hs=8)
    rr(d, block_x - 120, block_y, block_x + 20, block_y + 40, (*RED[:3], 30), RED, r=8, ow=1)
    ct(d, block_x - 50, block_y + 20, "阻断/审核", f_sub, (*RED, 230))
    d.text((cx + bw//2 + 8, qc_y + bh//2 - 16), "不通过", font=f_label, fill=(*RED, 200))

    img.convert("RGB").save(os.path.join(OUT_DIR, "diagram_workflow.png"))
    print("✓ diagram_workflow.png")


# ── Diagram 4: PEV Flow ────────────────────────────────────────────────────
def diagram_pev() -> None:
    W, H = 780, 680
    img, d = make_bg(W, H)

    f_tag  = fnt(14, 0)
    f_main = fnt(17, 1)
    f_body = fnt(14, 0)
    f_item = fnt(13, 0)

    cx = W // 2

    title = "Plan → Review → Execute（三段式流程）"
    d.text((40, 22), title, font=fnt(18, 1), fill=(*TEXT, 210))
    d.rectangle([40, 52, 40 + tw(d, title, fnt(18,1)) + 4, 55], fill=(*ACCENT, 190))

    # Input box at top
    rr(d, cx-120, 66, cx+120, 110, SURF2, BORDER, r=10, ow=1)
    ct(d, cx, 88, "你的需求", f_main, (*TEXT, 220))
    adown(d, cx, 110, 140, ACCENT, lw=2, hs=8)

    phases = [
        {
            "y": 140,
            "tag": "Phase 1",
            "title": "Plan（规划）",
            "color": PURPLE,
            "lines": [
                '你说：「先不要写代码，',
                '告诉我你打算改哪些文件、',
                '每个文件改什么、有什么风险」',
            ],
        },
        {
            "y": 330,
            "tag": "Phase 2",
            "title": "Review（你来审）",
            "color": YELLOW,
            "lines": [
                "✓ 影响范围是否合理？",
                "✓ 有没有遗漏关键文件？",
                "✓ 有没有你不想动的地方？",
            ],
        },
        {
            "y": 510,
            "tag": "Phase 3",
            "title": "Execute（执行）",
            "color": GREEN,
            "lines": [
                '你说：「按计划执行，',
                '每完成一个文件告诉我」',
            ],
        },
    ]

    bw, ph = W - 120, 150

    for i, ph_data in enumerate(phases):
        y = ph_data["y"]
        col = ph_data["color"]
        x1, x2 = 60, W-60

        rr(d, x1, y, x2, y+ph, (*col[:3], 28), col, r=12, ow=1)

        # tag chip
        tag_text = ph_data["tag"]
        chip_w = tw(d, tag_text, f_tag) + 20
        chip_h = 26
        rr(d, x1+16, y+14, x1+16+chip_w, y+14+chip_h, (*col[:3], 120), None, r=6)
        ct(d, x1+16+chip_w//2, y+14+chip_h//2, tag_text, f_tag, (*col, 255))

        # title
        d.text((x1+16+chip_w+14, y+16), ph_data["title"], font=f_main, fill=(*TEXT, 220))

        # body lines
        for j, line in enumerate(ph_data["lines"]):
            d.text((x1+26, y+52+j*26), line, font=f_body, fill=(*DIM, 210))

        # arrow between phases
        if i < len(phases) - 1:
            next_y = phases[i+1]["y"]
            label = "AI 输出计划" if i == 0 else "确认 / 修改计划"
            adown(d, cx, y+ph, next_y, ACCENT, lw=2, hs=8)
            lw_ = tw(d, label, f_item)
            d.text((cx - lw_//2, y+ph+4), label, font=f_item, fill=(*DIM, 180))

    img.convert("RGB").save(os.path.join(OUT_DIR, "diagram_pev.png"))
    print("✓ diagram_pev.png")


# ── Diagram 5: Constraint Priority ────────────────────────────────────────
def diagram_constraint() -> None:
    W, H = 1080, 220
    img, d = make_bg(W, H)

    f_title = fnt(17, 1)
    f_main  = fnt(18, 1)
    f_sub   = fnt(13, 0)
    f_gt    = fnt(22, 1)

    d.text((40, 18), "约束强度优先级", font=f_title, fill=(*TEXT, 210))
    d.rectangle([40, 46, 40+tw(d, "约束强度优先级", f_title)+4, 49], fill=(*ACCENT, 190))

    items = [
        ("CI 拦截",       GREEN,  "最强 · 结构性"),
        ("AGENTS.md 规则", ACCENT, "持久 · 文件级"),
        ("Prompt 提醒",   YELLOW, "单次 · 易失效"),
        ("事后 review",   RED,    "最弱 · 被动补救"),
    ]

    n = len(items)
    pad = 50
    gap = 36
    box_w = (W - 2*pad - (n-1)*gap) // n
    box_y1, box_y2 = 62, 166

    for i, (label, col, sub) in enumerate(items):
        x1 = pad + i * (box_w + gap)
        x2 = x1 + box_w
        alpha = max(35, 60 - i*10)
        rr(d, x1, box_y1, x2, box_y2, (*col[:3], alpha), col, r=10, ow=1)
        cy_box = (box_y1 + box_y2) // 2
        ct(d, (x1+x2)//2, cy_box - 12, label, f_main, (*col, 235))
        ct(d, (x1+x2)//2, cy_box + 16, sub,   f_sub,  (*col, 180))

        # ">" arrow between items
        if i < n - 1:
            ax = x2 + gap//2
            ct(d, ax, (box_y1+box_y2)//2, ">", f_gt, (*BORDER, 200))

    # reliability bar at bottom
    bar_y = 178
    d.text((pad, bar_y), "可靠性递减  →", font=fnt(12, 0), fill=(*DIM, 170))

    img.convert("RGB").save(os.path.join(OUT_DIR, "diagram_constraint.png"))
    print("✓ diagram_constraint.png")


if __name__ == "__main__":
    print("Generating article diagrams…")
    diagram_evolution()
    diagram_arch()
    diagram_workflow()
    diagram_pev()
    diagram_constraint()
    print("\nAll diagrams saved to:", OUT_DIR)
