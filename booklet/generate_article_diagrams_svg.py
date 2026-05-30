#!/usr/bin/env python3
"""Generate SVG diagrams for harness_engineering_article.md"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "article_diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# Palette
BG     = "#0c0c1c"
SURF   = "#161830"
SURF2  = "#202240"
SURF3  = "#2c2e54"
BORDER = "#373c69"
ACCENT = "#818cf8"
ACCD   = "#4f5ac6"
TEXT   = "#e6e8f5"
DIM    = "#969bc8"
TACC   = "#a7a9ff"
GREEN  = "#34d399"
YELLOW = "#fbbf24"
RED    = "#f87171"
PURPLE = "#c084fc"
TEAL   = "#2dd4bf"
ORANGE = "#fb923c"

FONT = "'Hiragino Sans GB', 'PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif"


def x(s: str) -> str:
    """Escape XML special characters in text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── SVG primitives ───────────────────────────────────────────────────────────

def start(w: int, h: int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="bgG" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="100%" stop-color="#070710"/>
  </linearGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#bgG)"/>'''


def dots(w: int, h: int) -> str:
    out = []
    for x in range(40, w, 60):
        for y in range(40, h, 60):
            out.append(f'<circle cx="{x}" cy="{y}" r="1.2" fill="{ACCENT}" opacity="0.07"/>')
    return ''.join(out)


def end() -> str:
    return '</svg>'


def R(x1, y1, x2, y2, fill, stroke=None, rx=10, fo=1.0, sw=1.5, so=0.75) -> str:
    s = (f'stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{so}"'
         if stroke else 'stroke="none"')
    return (f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" '
            f'rx="{rx}" fill="{fill}" fill-opacity="{fo}" {s}/>')


def T(px, py, text, size, color, weight="normal", anchor="middle", fo=1.0) -> str:
    return (f'<text x="{px}" y="{py}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" fill-opacity="{fo}" '
            f'text-anchor="{anchor}" dominant-baseline="central">'
            f'{x(text)}</text>')


def adown(x, y1, y2, col=ACCENT, lw=2, hs=10) -> str:
    hw = hs * 0.55
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - hs}" '
            f'stroke="{col}" stroke-width="{lw}" stroke-linecap="round" opacity="0.85"/>'
            f'<polygon points="{x},{y2} {x-hw:.1f},{y2-hs} {x+hw:.1f},{y2-hs}" '
            f'fill="{col}" opacity="0.85"/>')


def aright(x1, x2, y, col=ACCENT, lw=2, hs=10) -> str:
    hw = hs * 0.55
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 - hs}" y2="{y}" '
            f'stroke="{col}" stroke-width="{lw}" stroke-linecap="round" opacity="0.85"/>'
            f'<polygon points="{x2},{y} {x2-hs},{y-hw:.1f} {x2-hs},{y+hw:.1f}" '
            f'fill="{col}" opacity="0.85"/>')


def title_el(tx, ty, text, size=20, col=TEXT) -> str:
    # Rough underline width: each Chinese char ≈ size px, Latin ≈ size*0.6 px
    w_est = sum(size if ord(c) > 0x4E00 else size * 0.62 for c in text)
    t = T(tx, ty, text, size, col, weight="600", anchor="start")
    ul = f'<rect x="{tx}" y="{ty + size * 0.72:.0f}" width="{w_est:.0f}" height="3" rx="1.5" fill="{ACCENT}" opacity="0.8"/>'
    return t + ul


# ── Diagram 1 : Evolution Table ───────────────────────────────────────────
def d1_evolution() -> None:
    W, H = 1200, 628

    # columns: (x_start, width)
    cols = [(40, 196), (240, 276), (520, 276), (800, 360)]
    # rows (header + 4 data): (y_start, height)
    rows = [(68, 64), (136, 96), (236, 96), (336, 96), (436, 96)]

    def cx(ci): return cols[ci][0] + cols[ci][1] // 2
    def cy(ri): return rows[ri][0] + rows[ri][1] // 2

    p = [start(W, H), dots(W, H), title_el(40, 34, "AI 工程方法论演进路线", size=22)]

    # ── Header row ──
    hdr_fills   = [SURF3, ACCD,  ACCD,  ACCENT]
    hdr_alphas  = [0.55,  0.72,  0.72,  0.88]
    hdr_labels  = [None,
                   ("Prompt Eng.",   "2023"),
                   ("Context Eng.",  "2024–2025"),
                   ("Harness Eng.",  "2026")]
    hdr_colors  = [None, DIM, TACC, TEXT]   # year label colors: dim → tacc → bright
    for ci in range(4):
        x, w = cols[ci]
        y, h = rows[0]
        p.append(R(x, y, x+w, y+h, hdr_fills[ci], rx=8, fo=hdr_alphas[ci]))
        lbl = hdr_labels[ci]
        if lbl:
            name, year = lbl
            ycol = hdr_colors[ci]
            p.append(T(cx(ci), cy(0) - 12, name, 18, TEXT, weight="700"))
            p.append(T(cx(ci), cy(0) + 13, year, 14, ycol, weight="700"))

    # ── Small forward arrows between column headers ──
    hdr_mid_y = cy(0)
    for gap_x in [518, 798]:   # midpoints of the 4-px gaps between col2/3 and col3/4
        p.append(f'<polygon points="{gap_x+7},{hdr_mid_y} '
                 f'{gap_x-4},{hdr_mid_y-7} {gap_x-4},{hdr_mid_y+7}" '
                 f'fill="{ACCENT}" opacity="0.55"/>')

    # ── Data rows ──
    data = [
        ["核心问题", "怎么「问」AI",    "给 AI 什么「信息」",  "怎么搭「系统」"],
        ["作用范围", "单次交互",        "单个上下文窗口",       "跨多次交互\n整个生命周期"],
        ["关注点",   "指令质量",        "信息质量",            "系统可靠性"],
        ["类比",     "怎么写需求文档",  "给员工备齐\n背景资料", "搭一套公司\n管理制度"],
    ]
    row_fills  = [SURF3, SURF2, SURF3, SURF2]
    row_alphas = [0.50,  0.50,  0.50,  0.50]
    col_colors = [TACC,  DIM,   DIM,   GREEN]

    for ri, row in enumerate(data):
        ri_r = ri + 1
        for ci in range(4):
            x, w = cols[ci]
            y, h = rows[ri_r]
            if ci == 0:
                p.append(R(x, y, x+w, y+h, ACCD, rx=8, fo=0.45))
            else:
                p.append(R(x, y, x+w, y+h, row_fills[ri], rx=8, fo=row_alphas[ri]))

            cell_text = row[ci]
            color = TACC if ci == 0 else col_colors[ci]
            fw = "700" if ci == 0 else "500"
            if '\n' in cell_text:
                lines = cell_text.split('\n')
                gap = 26
                for j, line in enumerate(lines):
                    yy = cy(ri_r) + (j - (len(lines) - 1) / 2) * gap
                    p.append(T(cx(ci), yy, line, 17, color, weight=fw))
            else:
                p.append(T(cx(ci), cy(ri_r), cell_text, 17, color, weight=fw))

    # ── Grid lines ──
    for ci in range(1, 4):
        gx = cols[ci][0] - 2
        y1 = rows[0][0]; y2 = rows[-1][0] + rows[-1][1]
        p.append(f'<line x1="{gx}" y1="{y1}" x2="{gx}" y2="{y2}" '
                 f'stroke="{BORDER}" stroke-opacity="0.35" stroke-width="1"/>')
    for ri in range(1, 5):
        gy = rows[ri][0] - 2
        x1 = cols[0][0]; x2 = cols[-1][0] + cols[-1][1]
        p.append(f'<line x1="{x1}" y1="{gy}" x2="{x2}" y2="{gy}" '
                 f'stroke="{BORDER}" stroke-opacity="0.35" stroke-width="1"/>')

    # ── Timeline strip ────────────────────────────────────────────────────
    table_btm = rows[-1][0] + rows[-1][1]   # 532
    tl_y      = table_btm + 44              # 576  — timeline centre
    tl_x1     = cols[1][0]                  # 240
    tl_x2     = cols[-1][0] + cols[-1][1]   # 1160

    # "演进时间轴" label on the left
    p.append(T(tl_x1 - 12, tl_y, "演进时间轴", 11, DIM, anchor="end", fo=0.55))

    # Horizontal arrow (main line + arrowhead)
    hw = 9
    p.append(f'<line x1="{tl_x1}" y1="{tl_y}" x2="{tl_x2 - hw}" y2="{tl_y}" '
             f'stroke="{ACCENT}" stroke-width="2" stroke-opacity="0.45"/>')
    p.append(f'<polygon points="{tl_x2},{tl_y} '
             f'{tl_x2 - hw},{tl_y - 6} {tl_x2 - hw},{tl_y + 6}" '
             f'fill="{ACCENT}" opacity="0.45"/>')

    # Milestone dots + vertical connectors + year labels
    milestones = [
        (cx(1), "2023",      ACCD,   DIM),
        (cx(2), "2024–2025", TACC,   TACC),
        (cx(3), "2026",      ACCENT, ACCENT),
    ]
    for mx, year, dot_col, lbl_col in milestones:
        # Vertical dashed connector from table bottom to timeline
        p.append(f'<line x1="{mx}" y1="{table_btm + 4}" x2="{mx}" y2="{tl_y - 9}" '
                 f'stroke="{dot_col}" stroke-width="1.2" '
                 f'stroke-dasharray="4,3" stroke-opacity="0.40"/>')
        # Dot
        p.append(f'<circle cx="{mx}" cy="{tl_y}" r="5.5" '
                 f'fill="{dot_col}" opacity="0.88"/>')
        # Year label below dot
        p.append(T(mx, tl_y + 22, year, 13, lbl_col, weight="700", fo=0.88))

    p.append(end())
    _save("diagram_evolution.svg", p)


# ── Diagram 2 : Harness Architecture ──────────────────────────────────────
def d2_arch() -> None:
    W, H = 1040, 1010
    cx = W // 2  # 520

    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 28, "Harness 完整架构", size=20))

    # ── 用户 / 任务输入 ──
    p.append(R(cx - 172, 60, cx + 172, 112, SURF2, stroke=ACCENT, rx=10, fo=0.90, sw=1.5))
    p.append(T(cx, 80, "用户 / 任务输入", 20, TEXT, weight="700"))
    p.append(T(cx, 101, "自然语言指令  /  自动触发事件  /  外部调用", 13, DIM, fo=0.80))
    p.append(adown(cx, 112, 150, ACCENT))

    # ── Outer AGENT container ──
    # "Agent = Model + Harness" label lives HERE, not inside HARNESS.
    # CI 质量门控 is Harness component ③ (质量门控), so it sits INSIDE Agent.
    agent_y1, agent_y2 = 150, 660
    p.append(R(36, agent_y1, W - 36, agent_y2,
               ACCENT, stroke=ACCENT, rx=14, fo=0.07, sw=1.8, so=0.50))
    p.append(T(62, agent_y1 + 18, "Agent", 14, ACCENT, weight="700",
               anchor="start", fo=0.90))
    p.append(T(62 + 54, agent_y1 + 18, "=  Model  +  Harness", 12, DIM,
               anchor="start", fo=0.55))

    # ── HARNESS container (inside Agent) ──
    # Safety & 可观测性 IS part of Harness — included as 5th component
    h_y1 = agent_y1 + 34   # 184
    h_y2 = h_y1 + 256       # 440
    p.append(R(52, h_y1, W - 52, h_y2,
               ACCD, stroke=ACCENT, rx=12, fo=0.17, sw=1.4, so=0.60))
    p.append(title_el(72, h_y1 + 20, "HARNESS 层", size=14, col=TACC))

    # ── 5 Harness component boxes ──
    cw_c, ch_c = 172, 192
    cgap_c     = 12
    c_x0       = 66          # (52 + 14 inner margin)
    c_y0       = h_y1 + 42   # 226

    components = [
        ("规则文件",      "AGENTS.md",         "定义 AI 行为边界",
         ["personas / red-lines", "工作流规则文件", "权限范围声明"],       PURPLE),
        ("上下文管理",    "历史 · 检索 · RAG", "控制 AI 看到的信息",
         ["对话历史滚动压缩", "向量检索按需注入", "Token 预算管理"],       TEAL),
        ("工具 & API",   "MCP 协议",          "赋予操作外部系统能力",
         ["文件读写 / 代码执行", "数据库 / HTTP 调用", "搜索 / 计算工具"], GREEN),
        ("控制流 & 审批", "人工审批门",         "编排节点 · 管控风险",
         ["危险操作强制拦截", "分支路由 / 循环", "完成条件判断"],           ORANGE),
        ("Safety & 观测", "guardrail · 追踪",  "护栏 · 可观测性",
         ["输出实时 guardrail", "权限越界检查", "行为追踪日志"],            YELLOW),
    ]

    for i, (title_c, tech, desc, bullets, col) in enumerate(components):
        bx  = c_x0 + i * (cw_c + cgap_c)
        by  = c_y0
        bcx = bx + cw_c // 2

        p.append(R(bx, by, bx + cw_c, by + ch_c, col, stroke=col, rx=10, fo=0.15, sw=1.2))
        # Top band
        p.append(R(bx, by, bx + cw_c, by + 46, col, stroke=None, rx=10, fo=0.55))
        p.append(f'<rect x="{bx}" y="{by+36}" width="{cw_c}" height="10" '
                 f'fill="{col}" fill-opacity="0.55"/>')
        p.append(T(bcx, by + 23, title_c, 15, TEXT, weight="700"))
        p.append(T(bcx, by + 60, tech, 12, col, weight="600", fo=0.90))
        p.append(f'<line x1="{bx+10}" y1="{by+72}" x2="{bx+cw_c-10}" y2="{by+72}" '
                 f'stroke="{col}" stroke-width="0.8" stroke-opacity="0.25"/>')
        p.append(T(bcx, by + 87, desc, 12, DIM, fo=0.85))
        for j, bullet in enumerate(bullets):
            ey = by + 108 + j * 26
            p.append(f'<circle cx="{bx+14}" cy="{ey}" r="3" fill="{col}" opacity="0.65"/>')
            p.append(T(bx + 23, ey, bullet, 11, DIM, anchor="start", fo=0.80))

    # ── Bidirectional arrows: Harness ↔ Model ──
    arr_y1 = h_y2           # 440
    arr_y2 = h_y2 + 36      # 476  (MODEL starts here)
    arr_mid = (arr_y1 + arr_y2) // 2   # 458
    dn_x, up_x, hw_a = cx - 16, cx + 16, 7

    # Solid down arrow (Harness → Model: instruction)
    p.append(f'<line x1="{dn_x}" y1="{arr_y1}" x2="{dn_x}" y2="{arr_y2 - hw_a}" '
             f'stroke="{ACCENT}" stroke-width="2.0" opacity="0.85"/>')
    p.append(f'<polygon points="{dn_x},{arr_y2} {dn_x-hw_a},{arr_y2-hw_a} {dn_x+hw_a},{arr_y2-hw_a}" '
             f'fill="{ACCENT}" opacity="0.85"/>')
    # Dashed up arrow (Model → Harness: response)
    p.append(f'<line x1="{up_x}" y1="{arr_y2}" x2="{up_x}" y2="{arr_y1 + hw_a}" '
             f'stroke="{TEAL}" stroke-width="2.0" stroke-dasharray="5,3" opacity="0.75"/>')
    p.append(f'<polygon points="{up_x},{arr_y1} {up_x-hw_a},{arr_y1+hw_a} {up_x+hw_a},{arr_y1+hw_a}" '
             f'fill="{TEAL}" opacity="0.75"/>')
    p.append(T(cx + 24, arr_mid - 8,  "指令下发", 11, ACCENT, anchor="start", fo=0.82))
    p.append(T(cx + 24, arr_mid + 8,  "结果返回", 11, TEAL,   anchor="start", fo=0.80))

    # ── MODEL layer (inside Agent, sibling of Harness) ──
    m_y1 = arr_y2           # 476
    m_y2 = m_y1 + 68        # 544
    p.append(R(64, m_y1, W - 64, m_y2, ACCENT, stroke=ACCENT, rx=10, fo=0.20, sw=1.5))
    p.append(T(cx, (m_y1 + m_y2) // 2 - 13,
               "MODEL 层（推理核心）", 18, TEXT, weight="700"))
    p.append(T(cx, (m_y1 + m_y2) // 2 + 13,
               "GPT-4o  /  Claude  /  Gemini  /  本地开源模型", 13, DIM, fo=0.82))
    # m_y2=544; CI will follow below inside Agent

    # ── Arrow: Model → CI 质量门控 (both inside Agent) ──
    ci_y1 = m_y2 + 28       # 572
    ci_y2 = ci_y1 + 68      # 640
    p.append(adown(cx, m_y2, ci_y1, ACCENT))
    p.append(T(cx + 10, m_y2 + 14, "AI 输出", 11, DIM, anchor="start", fo=0.72))

    # ── 质量门控 — INSIDE Agent, Harness 三大核心之③ ──
    p.append(R(64, ci_y1, W - 64, ci_y2, GREEN, stroke=GREEN, rx=10, fo=0.18, sw=1.5))
    p.append(T(cx, (ci_y1 + ci_y2) // 2 - 13,
               "质量门控（Harness 三大核心之③）", 17, TEXT, weight="700"))
    p.append(T(cx, (ci_y1 + ci_y2) // 2 + 13,
               "结构性强制验证  /  终态检查  /  不依赖 AI 理解", 13, DIM, fo=0.82))
    # ci_y2=640, agent_y2=660 → 20 px bottom margin inside Agent ✓

    # ── Arrow: Agent → 最终输出 ──
    p.append(adown(cx, agent_y2, agent_y2 + 40, ACCENT))
    p.append(T(cx + 10, agent_y2 + 20, "最终输出", 11, DIM, anchor="start", fo=0.72))

    # ══════════════════════════════════════════════════════════════
    # ── Explanation section ──
    # ══════════════════════════════════════════════════════════════
    div_y = agent_y2 + 40 + 18   # 718
    p.append(f'<line x1="40" y1="{div_y}" x2="{W-40}" y2="{div_y}" '
             f'stroke="{BORDER}" stroke-width="1" stroke-opacity="0.45"/>')
    p.append(title_el(40, div_y + 18, "图解说明", size=15, col=TACC))

    # 2-column layout: 4 entries left, 3 entries right
    LC, RC  = 40, 538       # column x starts
    EY0     = div_y + 46    # 744  (first entry top)
    E_STEP  = 62            # vertical step per entry

    left_entries = [
        (PURPLE, "① 规则文件（AGENTS.md）",
         ["以文件形式持久化 AI 的 personas、禁止操作清单和工作流规则；",
          "每次推理前自动注入，AI 生成内容之前就已锁定约束边界。"]),
        (TEAL, "② 上下文管理",
         ["控制 AI 每次推理看到的信息质量：历史滚动压缩、",
          "RAG 按需注入相关知识、Token 预算管理防止超窗。"]),
        (GREEN, "③ 工具 & API（MCP 协议）",
         ["通过 MCP 协议赋予 AI 调用外部系统能力：文件读写、代码执行、",
          "数据库 / HTTP。Harness 负责注册、鉴权和结果结构化处理。"]),
        (ORANGE, "④ 控制流 & 审批",
         ["执行编排层：分支路由、循环控制、子任务分发；",
          "内置人工审批门，危险操作前强制暂停等人确认。"]),
    ]
    right_entries = [
        (YELLOW, "⑤ Safety & 可观测性（Harness 内部）",
         ["Safety 和可观测性是 Harness 的组成部分，非独立层级。",
          "含 guardrail 实时过滤、权限越界检查、全量行为追踪日志。"]),
        (ACCENT, "⑥ MODEL 层（Agent 内，与 Harness 并列）",
         ["推理核心。Harness 构建 Prompt 后调用 Model；",
          "Model 输出经 Safety 过滤，再进入质量门控。二者合称 Agent。"]),
        (GREEN, "⑦ 质量门控（Harness 三大核心之③）",
         ["与约束前馈、反馈回路并列，是 Harness 的第三大核心。",
          "结构性强制验证，不依赖 AI 理解；失败则阻断，触发修复。"]),
    ]

    for j, (col, label, lines) in enumerate(left_entries):
        ey = EY0 + j * E_STEP
        p.append(f'<circle cx="{LC+7}" cy="{ey+7}" r="5" fill="{col}" opacity="0.82"/>')
        p.append(T(LC + 18, ey + 7,  label,   13, col, weight="700", anchor="start"))
        for k, line in enumerate(lines):
            p.append(T(LC + 18, ey + 24 + k * 17, line, 12, DIM,
                       anchor="start", fo=0.80))

    for j, (col, label, lines) in enumerate(right_entries):
        ey = EY0 + j * E_STEP
        p.append(f'<circle cx="{RC+7}" cy="{ey+7}" r="5" fill="{col}" opacity="0.82"/>')
        p.append(T(RC + 18, ey + 7,  label,   13, col, weight="700", anchor="start"))
        for k, line in enumerate(lines):
            p.append(T(RC + 18, ey + 24 + k * 17, line, 12, DIM,
                       anchor="start", fo=0.80))

    p.append(end())
    _save("diagram_arch.svg", p)


# ── Diagram 3 : Harness Workflow ───────────────────────────────────────────
def d3_workflow() -> None:
    W, H = 960, 780
    cx = W // 2          # 480
    bw, bh = 480, 72
    bx1 = cx - bw // 2  # 240
    bx2 = cx + bw // 2  # 720

    p = [start(W, H), dots(W, H), title_el(40, 28, "Harness 工作流", size=20)]
    # Badge: "以 Coding Agent 为例"
    p.append(R(762, 14, 950, 44, ACCENT, stroke=ACCENT, rx=14, fo=0.15, sw=1.0, so=0.55))
    p.append(T(856, 29, "以 Coding Agent 为例", 12, ACCENT, fo=0.95))

    # (y1, step_num, title, subtitle, accent_col, is_harness)
    steps = [
        (60,  "①", "任务输入",    "用户指令 / 需求描述",                           SURF2,  False),
        (168, "②", "约束前馈",    "AGENTS.md 规则注入 — AI 生成前就锁定边界",      PURPLE, True),
        (276, "③", "AI 生成内容", "模型依据约束与上下文生成代码 / 文本",             SURF2,  False),
        (384, "④", "反馈回路",    "linter / 测试报错 → 结构化后发回 → AI 自我修正", TEAL,   True),
        (520, "⑤", "质量门控",    "CI 全绿 · 安全扫描通过 · linter 零警告",         GREEN,  True),
        (628, "⑥", "合并代码库",  "代码入库，任务完成",                              ACCENT, False),
    ]

    for i, (y1, num, title, subtitle, col, is_harness) in enumerate(steps):
        y2 = y1 + bh

        # Box
        if col == SURF2:
            p.append(R(bx1, y1, bx2, y2, SURF2, stroke=BORDER, rx=12, fo=0.85, sw=1.0))
        else:
            p.append(R(bx1, y1, bx2, y2, col, stroke=col, rx=12, fo=0.18, sw=1.5))

        # Left accent stripe
        stripe_col = col if col != SURF2 else BORDER
        p.append(f'<rect x="{bx1}" y="{y1+8}" width="4" height="{bh-16}" '
                 f'rx="2" fill="{stripe_col}" opacity="0.90"/>')

        # Step number badge
        nc = bx1 + 32
        ncy = y1 + bh // 2
        badge_col = col if col != SURF2 else SURF3
        p.append(f'<circle cx="{nc}" cy="{ncy}" r="15" fill="{badge_col}" opacity="0.75"/>')
        p.append(T(nc, ncy, num, 14, TEXT, weight="700"))

        # Title + subtitle
        tx = bx1 + 60
        title_col = col if col != SURF2 else TEXT
        p.append(T(tx, y1 + bh // 2 - 13, title,    18, title_col, weight="700", anchor="start"))
        p.append(T(tx, y1 + bh // 2 + 14, subtitle, 13, DIM,       anchor="start", fo=0.82))

        # "Harness" tag chip (right side)
        if is_harness:
            tag_x2 = bx2 - 12
            tag_x1_t = tag_x2 - 80
            tag_cy   = y1 + bh // 2
            p.append(R(tag_x1_t, tag_cy - 11, tag_x2, tag_cy + 11, col, rx=5, fo=0.35))
            p.append(T((tag_x1_t + tag_x2) // 2, tag_cy, "Harness", 11, col, weight="700", fo=0.95))

        # Arrow to next step
        if i < len(steps) - 1:
            next_y1 = steps[i + 1][0]
            p.append(adown(cx, y2, next_y1, ACCENT))
            if i == 4:  # 质量门控 → 合并 : "通过" label
                p.append(T(cx + 8, y2 + 8, "通过", 12, GREEN, anchor="start"))

    # ── Feedback loop: ④ → ③  (L-shaped arrow on the left) ──
    s3_y1, s4_y1 = steps[2][0], steps[3][0]
    s3_cy = s3_y1 + bh // 2  # center of step ③
    s4_cy = s4_y1 + bh // 2  # center of step ④
    loop_x = bx1 - 56

    # Path: left edge of ④ → leftward → up → rightward → left edge of ③
    p.append(f'<path d="M {bx1},{s4_cy} H {loop_x} V {s3_cy} H {bx1}" '
             f'fill="none" stroke="{TEAL}" stroke-width="2.0" '
             f'stroke-dasharray="6,4" opacity="0.80"/>')
    # Arrowhead into step ③
    hw = 6
    arr_up = s3_cy - hw
    arr_dn = s3_cy + hw
    p.append(f'<polygon points="{bx1},{s3_cy} {bx1-10},{arr_up} {bx1-10},{arr_dn}" '
             f'fill="{TEAL}" opacity="0.85"/>')
    # Label beside the loop
    mid_loop_y = (s3_cy + s4_cy) // 2
    p.append(T(loop_x - 8, mid_loop_y, "自我", 11, TEAL, anchor="end", fo=0.85))
    p.append(T(loop_x - 8, mid_loop_y + 16, "修正", 11, TEAL, anchor="end", fo=0.85))

    # ── 不通过 branch from ⑤ ──
    s5_y1 = steps[4][0]
    qc_cy  = s5_y1 + bh // 2
    blk_x1_b = bx2 + 28
    blk_x2_b = blk_x1_b + 180
    blk_y1_b = s5_y1 + 14
    blk_y2_b = s5_y1 + bh - 14

    p.append(aright(bx2, blk_x1_b, qc_cy, RED))
    p.append(T(bx2 + 14, qc_cy - 16, "不通过", 12, RED, anchor="start"))
    p.append(R(blk_x1_b, blk_y1_b, blk_x2_b, blk_y2_b, RED, stroke=RED, rx=8, fo=0.22, sw=1.2))
    p.append(T((blk_x1_b + blk_x2_b) // 2, (blk_y1_b + blk_y2_b) // 2,
               "阻断 / 人工审核", 14, RED, weight="700"))

    p.append(end())
    _save("diagram_workflow.svg", p)


# ── Diagram 4 : PEV Flow ──────────────────────────────────────────────────
def d4_pre() -> None:
    W, H   = 1040, 860
    cx     = W // 2          # 520
    CX1, CX2 = 56, W - 56   # card left/right edges  (56 … 984)
    CH     = 200             # card height
    BADGE_W = 80             # left badge column width  → badge_x2 = 136

    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 28, "Plan → Review → Execute（三段式工作法）", size=18))

    # ── Input box ──
    p.append(R(cx - 172, 60, cx + 172, 110, SURF2, stroke=BORDER, rx=10, fo=0.90, sw=1.0))
    p.append(T(cx, 79, "你的需求", 20, TEXT, weight="700"))
    p.append(T(cx, 99, "功能需求 / Bug 报告 / 重构请求", 12, DIM, fo=0.78))
    p.append(adown(cx, 110, 152, ACCENT))

    # Phase gap = 44 px
    PHASE_STEP = CH + 44
    phases = [
        {
            "y1":  152,
            "num": "01", "role": "你 → AI",
            "title":     "Plan  规划",
            "principle": "强制 AI 先出方案，不允许直接写代码",
            "color":     PURPLE,
            "you": ["「先不要写代码，告诉我打算改哪些文件、每个文件改什么、有什么风险」"],
            "ai":  ["输出：文件改动清单 · 每条改动理由 · 潜在风险 · 预计影响范围"],
            "out": "→  AI 规划文档",
        },
        {
            "y1":  152 + PHASE_STEP,
            "num": "02", "role": "你  ✓",
            "title":     "Review  审查",
            "principle": "人工把关——你是唯一决策者，改完计划再执行",
            "color":     YELLOW,
            "you": [
                "✓ 影响范围合理？  ✓ 有无遗漏关键文件？  ✓ 有不想动的地方？",
                "有问题就修改计划；没问题才放行——AI 在等，不会自行动手",
            ],
            "ai":  ["等待你确认，不执行任何代码操作，直到收到明确「执行」指令"],
            "out": "→  确认后的计划",
        },
        {
            "y1":  152 + 2 * PHASE_STEP,
            "num": "03", "role": "你 → AI",
            "title":     "Execute  执行",
            "principle": "按步骤执行、逐文件汇报——可随时叫停",
            "color":     GREEN,
            "you": ["「按计划执行，每完成一个文件告诉我，等我确认再继续」"],
            "ai":  ["逐文件执行并汇报进度；遇到意外主动暂停，不自行决策"],
            "out": "→  可审计的执行记录",
        },
    ]

    for i, ph in enumerate(phases):
        y1  = ph["y1"]
        y2  = y1 + CH
        col = ph["color"]
        badge_x2  = CX1 + BADGE_W   # 136
        content_x = badge_x2 + 16   # 152

        # ── Card background ──
        p.append(R(CX1, y1, CX2, y2, col, stroke=col, rx=12, fo=0.14, sw=1.5))

        # ── Badge column: clipped solid panel ──
        clip_id = f"pc{i}"
        p.append(f'<defs><clipPath id="{clip_id}">'
                 f'<rect x="{CX1}" y="{y1}" width="{CX2-CX1}" height="{CH}" rx="12"/>'
                 f'</clipPath></defs>')
        p.append(f'<g clip-path="url(#{clip_id})">')
        p.append(R(CX1, y1, badge_x2, y2, col, stroke=None, rx=0, fo=0.55))
        p.append('</g>')

        # Phase number + role inside badge
        p.append(T(CX1 + BADGE_W // 2, y1 + CH // 2 - 14, ph["num"], 26, TEXT, weight="800"))
        p.append(T(CX1 + BADGE_W // 2, y1 + CH // 2 + 16, ph["role"], 11, TEXT, fo=0.80))

        # ── Title + principle ──
        p.append(T(content_x, y1 + 26, ph["title"], 20, col, weight="700", anchor="start"))
        p.append(T(content_x, y1 + 50, ph["principle"], 13, DIM, anchor="start", fo=0.82))

        # Divider
        p.append(f'<line x1="{content_x}" y1="{y1+62}" x2="{CX2-12}" y2="{y1+62}" '
                 f'stroke="{col}" stroke-width="0.8" stroke-opacity="0.28"/>')

        # ── 你 → rows ──
        you_y = y1 + 80
        p.append(T(content_x, you_y, "你 →", 13, col, weight="700", anchor="start", fo=0.92))
        for j, line in enumerate(ph["you"]):
            p.append(T(content_x + 46, you_y + j * 22, line, 13, TEXT,
                       anchor="start", fo=0.85))

        # ── AI → rows ──
        ai_y = you_y + len(ph["you"]) * 22 + 20
        p.append(T(content_x, ai_y, "AI →", 13, col, weight="700", anchor="start", fo=0.92))
        for j, line in enumerate(ph["ai"]):
            p.append(T(content_x + 46, ai_y + j * 22, line, 13, DIM,
                       anchor="start", fo=0.80))

        # ── Output badge (bottom-right) ──
        ob_y1, ob_y2 = y2 - 30, y2 - 8
        ob_x2, ob_x1 = CX2 - 10, CX2 - 10 - 172
        p.append(R(ob_x1, ob_y1, ob_x2, ob_y2, col, rx=6, fo=0.45))
        p.append(T((ob_x1 + ob_x2) // 2, (ob_y1 + ob_y2) // 2,
                   ph["out"], 12, TEXT, weight="600", fo=0.95))

        # ── Arrow to next phase ──
        if i < len(phases) - 1:
            next_y1 = phases[i + 1]["y1"]
            p.append(adown(cx, y2, next_y1, ACCENT))
            labels = ["AI 规划文档传入审查", "确认计划传入执行"]
            p.append(T(cx + 10, y2 + 22, labels[i], 11, DIM, anchor="start", fo=0.70))

    p.append(end())
    _save("diagram_pre.svg", p)


# ── Diagram 5 : Constraint Priority ───────────────────────────────────────
def d5_constraint() -> None:
    W, H = 1080, 220

    p = [start(W, H), dots(W, H), title_el(40, 26, "约束强度优先级", size=18)]

    items = [
        ("CI 拦截",        GREEN,  "最强 · 结构性"),
        ("AGENTS.md 规则", ACCENT, "持久 · 文件级"),
        ("Prompt 提醒",    YELLOW, "单次 · 易失效"),
        ("事后 review",    RED,    "最弱 · 被动补救"),
    ]
    n = len(items)
    pad, gap = 50, 32
    bw = (W - 2 * pad - (n - 1) * gap) // n
    by1, by2 = 60, 164

    for i, (label, col, sub) in enumerate(items):
        x1 = pad + i * (bw + gap)
        x2 = x1 + bw
        bcy = (by1 + by2) // 2
        fo = max(0.18, 0.38 - i * 0.05)
        p.append(R(x1, by1, x2, by2, col, stroke=col, rx=10, fo=fo, sw=1.5))
        p.append(T((x1 + x2) // 2, bcy - 16, label, 19, col, weight="700"))
        p.append(T((x1 + x2) // 2, bcy + 14, sub,   14, col, fo=0.78))

        if i < n - 1:
            gx = x2 + gap // 2
            p.append(T(gx, bcy, ">", 22, BORDER, weight="700", fo=0.75))

    p.append(T(pad, 186, "可靠性递减  →", 12, DIM, anchor="start", fo=0.65))
    p.append(end())
    _save("diagram_constraint.svg", p)


# ── Diagram 6 : Prompt Anatomy ────────────────────────────────────────────
def d6_prompt_anatomy() -> None:
    W, H = 960, 580
    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 32, "Prompt 的六个要素", size=22))

    elements = [
        ("① 角色设定",      PURPLE, "你是一个有 10 年经验的 Python 工程师",    "告诉 AI 用什么身份和知识框架来思考"),
        ("② 任务描述",      ACCENT, "请帮我写一个带权限校验的用户注册接口",     "明确你想要什么结果，越具体越好"),
        ("③ 背景信息",      TEAL,   "项目用 FastAPI，数据库是 PostgreSQL",     "AI 了解你的技术栈，才能给出合适方案"),
        ("④ 输出格式",      YELLOW, "返回 JSON，包含错误处理，加上类型注解",    "控制输出结构，避免 AI 自由发挥"),
        ("⑤ Few-shot 示例", GREEN,  "函数签名示例：def get_user(uid: int)",    "举例子比描述有效 10 倍，模型直接对齐"),
        ("⑥ 约束条件",      RED,    "禁止同步 IO，禁止硬编码任何配置项",        "明确不能做什么，比说能做什么更有效"),
    ]

    rh, gap, y0 = 76, 4, 80
    for i, (label, col, example, desc) in enumerate(elements):
        y = y0 + i * (rh + gap)
        p.append(R(44, y, W - 44, y + rh, col, stroke=col, rx=8, fo=0.10, sw=1.0, so=0.30))
        p.append(f'<rect x="44" y="{y+4}" width="5" height="{rh-8}" rx="2.5" fill="{col}" opacity="0.85"/>')
        p.append(T(82, y + 22, label, 18, col, weight="700", anchor="start"))
        p.append(T(82, y + 52, desc, 13, DIM, anchor="start", fo=0.85))
        p.append(T(360, y + 37, example, 13, col, anchor="start", fo=0.82))

    p.append(end())
    _save("diagram_prompt_anatomy.svg", p)


# ── Diagram 7 : Prompt Limitations ────────────────────────────────────────
def d7_prompt_limits() -> None:
    W, H = 960, 356
    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 26, "Prompt Engineering 的两大局限", size=20))

    # ── Left panel: session amnesia ──
    lx1, lx2, lcx = 44, 450, 247
    p.append(T(lcx, 60, "局限 1：跨会话遗忘", 16, ACCENT, weight="700"))

    # Session 1
    p.append(R(lx1, 76, lx2, 154, TEAL, stroke=TEAL, rx=8, fo=0.15, sw=1.2))
    p.append(T(lx1+14, 90, "第 1 次会话", 13, TEAL, weight="700", anchor="start"))
    p.append(T(lx1+14, 112, "Prompt: 含完整规范 + 安全红线 + 架构约束", 12, DIM, anchor="start"))
    p.append(T(lx2-14, 115, "✓ 符合规范", 14, GREEN, weight="700", anchor="end"))

    # Boundary dashed line
    p.append(f'<line x1="{lx1+8}" y1="162" x2="{lx2-8}" y2="162" stroke="{BORDER}" '
             f'stroke-width="1.5" stroke-dasharray="6,4" opacity="0.7"/>')
    p.append(T(lcx, 162, "  会话结束，记忆全部清空  ", 12, DIM, fo=0.75))

    # Session 2
    p.append(R(lx1, 172, lx2, 250, RED, stroke=RED, rx=8, fo=0.15, sw=1.2))
    p.append(T(lx1+14, 186, "第 2 次会话", 13, RED, weight="700", anchor="start"))
    p.append(T(lx1+14, 208, "Prompt:「帮我写个接口」（之前的规范？全忘了）", 12, DIM, anchor="start"))
    p.append(T(lx2-14, 211, "✗ 规范全忘", 14, RED, weight="700", anchor="end"))

    p.append(T(lcx, 276, "每开新对话，AI 就重置成陌生人", 13, DIM, anchor="middle", fo=0.80))

    # ── Divider ──
    p.append(f'<line x1="480" y1="52" x2="480" y2="300" stroke="{BORDER}" stroke-width="1" stroke-opacity="0.4"/>')

    # ── Right panel: whack-a-mole ──
    rx1, rcx = 500, 718
    p.append(T(rcx, 60, "局限 2：软约束，改不完的地鼠", 16, ACCENT, weight="700"))

    issues = [
        ("SQL 注入",   RED,    "改 Prompt ✓"),
        ("权限缺失",   RED,    "改 Prompt ✓"),
        ("日志泄露",   RED,    "改 Prompt ✓"),
        ("下一个？",   YELLOW, "还要继续改……"),
    ]
    iy0, i_gap = 80, 54
    for j, (issue, col, fix) in enumerate(issues):
        iy = iy0 + j * i_gap
        # Issue box
        p.append(R(rx1, iy, rx1 + 155, iy + 36, col, stroke=col, rx=6, fo=0.18, sw=1))
        p.append(T(rx1 + 78, iy + 18, issue, 13, col, weight="600"))
        # Arrow
        p.append(aright(rx1 + 155, rx1 + 205, iy + 18, ACCENT, lw=1.5, hs=7))
        # Fix box
        fix_col = GREEN if "✓" in fix else YELLOW
        p.append(R(rx1 + 209, iy, rx1 + 367, iy + 36, fix_col, stroke=fix_col, rx=6, fo=0.18, sw=1))
        p.append(T(rx1 + 288, iy + 18, fix, 13, fix_col, weight="600"))

    p.append(T(rcx, 308, "AI 靠「理解」执行规范，不靠「强制」——治标不治本", 13, DIM, anchor="middle", fo=0.78))

    p.append(end())
    _save("diagram_prompt_limits.svg", p)


# ── Diagram 8 : Context Window ────────────────────────────────────────────
def d8_context_window() -> None:
    W, H = 1040, 520
    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 28, "Context Window 的构成", size=20))

    bx1, bx2 = 64, 296    # bar: 232 px wide
    by1, by2 = 62, 488    # bar: 426 px tall
    bar_h = by2 - by1

    sections = [
        ("剩余空间",      SURF3,  0.04, "可用 token 配额"),
        ("Tool 调用结果", GREEN,  0.10, "工具执行返回的数据"),
        ("对话历史",      ACCENT, 0.34, "随任务推进持续增长"),
        ("RAG 检索文档",  ORANGE, 0.24, "按需注入的知识片段"),
        ("Tool Schema",  TEAL,   0.08, "工具定义和参数说明"),
        ("系统 Prompt",   PURPLE, 0.20, "固定规范，每次都在"),
    ]

    # clipPath for bar rounded corners
    p.append(f'<defs><clipPath id="barClip8">'
             f'<rect x="{bx1}" y="{by1}" width="{bx2-bx1}" height="{bar_h}" rx="8"/>'
             f'</clipPath></defs>')

    # Draw sections; record vertical center of each for connectors
    seg_centers: list[int] = []
    p.append('<g clip-path="url(#barClip8)">')
    cur_y = by1
    for name, col, frac, _ in sections:
        h = round(bar_h * frac)
        fo = 0.22 if col == SURF3 else 0.72
        p.append(R(bx1, cur_y, bx2, cur_y + h, col, stroke=None, rx=0, fo=fo))
        seg_centers.append(cur_y + h // 2)
        cur_y += h
    p.append('</g>')

    # Bar border
    p.append(f'<rect x="{bx1}" y="{by1}" width="{bx2-bx1}" height="{bar_h}" '
             f'rx="8" fill="none" stroke="{BORDER}" stroke-width="1.5" stroke-opacity="0.55"/>')

    # Context-limit cap
    p.append(f'<line x1="{bx1-14}" y1="{by1}" x2="{bx2+14}" y2="{by1}" '
             f'stroke="{RED}" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.75"/>')
    p.append(T(bx2 + 20, by1, "← 上限", 11, RED, anchor="start", fo=0.85))

    # Inside labels: show name + % for tall sections, % only for medium sections
    bcx = (bx1 + bx2) // 2
    for (name, col, frac, _), s_cy in zip(sections, seg_centers):
        h = round(bar_h * frac)
        pct = int(frac * 100)
        tc = DIM if col == SURF3 else col
        if h >= 72:
            p.append(T(bcx, s_cy - 11, name, 13, tc, weight="700", fo=0.95))
            p.append(T(bcx, s_cy + 12, f"{pct}%", 17, tc, weight="700", fo=0.88))
        elif h >= 36:
            p.append(T(bcx, s_cy, f"{pct}%", 14, tc, weight="700", fo=0.85))

    # ── Legend ──────────────────────────────────────────────────────────────
    lx = 336
    leg_step = bar_h // len(sections)   # ~71 px per item
    leg_y0 = by1 + leg_step // 2        # first item centre

    for i, (name, col, frac, desc) in enumerate(sections):
        lcy = leg_y0 + i * leg_step
        pct = int(frac * 100)
        s_cy = seg_centers[i]
        vc = DIM if col == SURF3 else col   # legible colour (SURF3 is near-black)

        # Bezier connector: bar right edge → legend item
        ctrl_x = bx2 + 28
        p.append(f'<path d="M {bx2},{s_cy} C {ctrl_x},{s_cy} {lx-32},{lcy} {lx-8},{lcy}" '
                 f'fill="none" stroke="{vc}" stroke-width="1.2" '
                 f'stroke-opacity="0.38" stroke-dasharray="4,3"/>')

        # Dot
        p.append(f'<circle cx="{lx+9}" cy="{lcy}" r="9" fill="{vc}" opacity="0.82"/>')

        # Name + description
        p.append(T(lx + 26, lcy - 11, name, 15, vc, weight="700", anchor="start"))
        p.append(T(lx + 26, lcy + 9, desc, 12, DIM, anchor="start", fo=0.78))

        # Mini proportional bar (shows relative size at a glance)
        mb_x1, mb_x2 = 614, 882
        mb_w = mb_x2 - mb_x1
        p.append(R(mb_x1, lcy - 5, mb_x2, lcy + 5, SURF3, rx=4, fo=0.35))
        fill_w = max(5, round(mb_w * frac))
        p.append(R(mb_x1, lcy - 5, mb_x1 + fill_w, lcy + 5, vc, rx=4, fo=0.82))

        # Percentage badge
        bdg_cx = W - 46
        p.append(R(bdg_cx - 28, lcy - 14, bdg_cx + 28, lcy + 14,
                   vc, stroke=vc, rx=12, fo=0.14, sw=1.0, so=0.50))
        p.append(T(bdg_cx, lcy, f"{pct}%", 14, vc, weight="700", fo=0.95))

    p.append(end())
    _save("diagram_context_window.svg", p)


# ── Diagram 9 : Context Limitations ───────────────────────────────────────
def d9_context_limits() -> None:
    W, H = 960, 436
    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 26, "Context Engineering 的两大局限", size=20))

    # ════════════════════════════════════════════════════════════════════════
    # ── 局限一：信息不等于约束 ────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════
    s1_y1, s1_y2 = 46, 200
    p.append(R(40, s1_y1, W - 40, s1_y2, SURF2, rx=10, fo=0.30))
    p.append(f'<rect x="40" y="{s1_y1}" width="5" height="{s1_y2 - s1_y1}" '
             f'rx="2.5" fill="{ACCENT}" opacity="0.75"/>')
    p.append(T(56, s1_y1 + 14, "局限一：信息不等于约束", 15, ACCENT,
               weight="700", anchor="start"))

    # Three boxes: 规范注入 → AI推理 → 输出违规
    by1, by2 = s1_y1 + 30, s1_y1 + 30 + 88   # 76..164
    box_specs = [
        (54,  278, PURPLE, PURPLE, 0.13, "规范注入上下文",   "系统 Prompt / RAG",    "✓ 规范在上下文里", GREEN),
        (322, 542, SURF3,  BORDER, 0.55, "AI",               "推理 · 生成",           "",                 DIM),
        (586, 908, RED,    RED,    0.13, "输出违规代码",      "SQL 拼接 / 无权限校验", "✗ 规范被无视",     RED),
    ]
    for x1, x2, col, stk, fo, t1, t2, t3, t3col in box_specs:
        p.append(R(x1, by1, x2, by2, col, stroke=stk, rx=8, fo=fo, sw=1.3))
        cx = (x1 + x2) // 2
        if t1 == "AI":
            p.append(T(cx, by1 + 30, t1, 28, TEXT, weight="700"))
            p.append(T(cx, by1 + 62, t2, 13, DIM, fo=0.82))
        else:
            p.append(T(cx, by1 + 22, t1, 14, col if col != SURF3 else TEXT, weight="700"))
            p.append(T(cx, by1 + 48, t2, 12, DIM, fo=0.82))
            if t3:
                p.append(T(cx, by1 + 70, t3, 13, t3col, weight="600",
                           fo=0.90 if t3col == RED else 1.0))

    box_mid_y = (by1 + by2) // 2
    p.append(aright(278 + 4, 322 - 4, box_mid_y, BORDER, lw=1.5, hs=9))
    p.append(aright(542 + 4, 586 - 4, box_mid_y, BORDER, lw=1.5, hs=9))

    # Caption
    p.append(T(W // 2, s1_y2 - 14, "AI 看到了规则  ≠  AI 会执行规则", 15, ACCENT, weight="700"))

    # ════════════════════════════════════════════════════════════════════════
    # ── 局限二：任务越长，早期规范被稀释 ──────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════
    s2_y1 = s1_y2 + 10   # 210
    s2_y2 = H - 8         # 428
    p.append(R(40, s2_y1, W - 40, s2_y2, SURF2, rx=10, fo=0.30))
    p.append(f'<rect x="40" y="{s2_y1}" width="5" height="{s2_y2 - s2_y1}" '
             f'rx="2.5" fill="{YELLOW}" opacity="0.75"/>')
    p.append(T(56, s2_y1 + 14, "局限二：任务越长，早期规范被稀释", 15, YELLOW,
               weight="700", anchor="start"))

    snap_w, snap_h = 168, 128
    snap_y1 = s2_y1 + 34   # 244
    snaps = [
        (58,  "任务初期", "✓ 运转稳定",   GREEN,
         [(PURPLE,0.20),(TEAL,0.08),(ORANGE,0.10),(ACCENT,0.08),(GREEN,0.04),(SURF3,0.50)]),
        (302, "任务中期", "⚠ 开始压缩",  YELLOW,
         [(PURPLE,0.20),(TEAL,0.08),(ORANGE,0.20),(ACCENT,0.32),(GREEN,0.08),(SURF3,0.12)]),
        (546, "任务后期", "✗ 规范被稀释", RED,
         [(PURPLE,0.20),(TEAL,0.08),(ORANGE,0.22),(ACCENT,0.44),(GREEN,0.05),(SURF3,0.01)]),
    ]

    for sx, label, result, rcol, sects in snaps:
        scx = sx + snap_w // 2
        p.append(T(scx, snap_y1 - 12, label, 13, DIM, weight="600"))
        cid = f"clt{sx}"
        p.append(f'<defs><clipPath id="{cid}">'
                 f'<rect x="{sx}" y="{snap_y1}" width="{snap_w}" height="{snap_h}" rx="6"/>'
                 f'</clipPath></defs>')
        p.append(f'<g clip-path="url(#{cid})">')
        ys = snap_y1
        for col, frac in sects:
            h = round(snap_h * frac)
            if h > 0:
                fo = 0.35 if col == SURF3 else 0.70
                p.append(R(sx, ys, sx + snap_w, ys + h, col, rx=0, fo=fo))
            ys += h
        p.append('</g>')
        p.append(f'<rect x="{sx}" y="{snap_y1}" width="{snap_w}" height="{snap_h}" '
                 f'rx="6" fill="none" stroke="{BORDER}" stroke-width="1" stroke-opacity="0.5"/>')
        p.append(T(scx, snap_y1 + snap_h + 15, result, 13, rcol, weight="600"))

    mid_y = snap_y1 + snap_h // 2
    for x1a, x2a in [(58+snap_w+4, 302-4), (302+snap_w+4, 546-4)]:
        p.append(aright(x1a, x2a, mid_y, ACCENT, lw=1.5, hs=8))

    # Mini legend (right side)
    leg_items = [("系统Prompt",PURPLE),("RAG文档",ORANGE),("对话历史",ACCENT),
                 ("Tool结果",GREEN),("剩余空间",SURF3)]
    lx_leg = 748
    for j, (lname, lcol) in enumerate(leg_items):
        ly = snap_y1 + j * 26
        p.append(f'<rect x="{lx_leg}" y="{ly}" width="10" height="10" '
                 f'rx="2" fill="{lcol}" opacity="0.72"/>')
        p.append(T(lx_leg + 14, ly + 5, lname, 11, lcol, anchor="start", fo=0.85))

    p.append(end())
    _save("diagram_context_limits.svg", p)


# ── Diagram 10 : Agent Types Comparison ──────────────────────────────────
def d10_agent_types() -> None:
    W, H = 1200, 720
    p = [start(W, H), dots(W, H)]
    p.append(title_el(40, 30, "不同类型 Agent 的 Harness 三大核心对比", size=22))

    # Table geometry
    tx1, tx2 = 40, 1160
    header_y, header_h = 68, 52
    row_h = 90
    n_rows = 6

    # Column x boundaries (left edge of each col, plus right edge of last col)
    col_x = [40, 235, 543, 851, 1160]
    # widths: 195, 308, 308, 309

    # ── Header ──────────────────────────────────────────────────────────────
    p.append(R(tx1, header_y, tx2, header_y + header_h, SURF3,
               stroke=BORDER, rx=8, fo=0.85, sw=1.5))
    header_labels = ["Agent 类型", "① 约束前馈", "② 反馈回路", "③ 质量门控"]
    header_colors = [DIM, PURPLE, TEAL, GREEN]
    for i, (lbl, hcol) in enumerate(zip(header_labels, header_colors)):
        mid_x = (col_x[i] + col_x[i + 1]) // 2
        p.append(T(mid_x, header_y + header_h // 2, lbl, 16, hcol, weight="700"))

    # ── Row data ─────────────────────────────────────────────────────────────
    rows_data = [
        (ACCENT,  "编码助手",  "Coding",
         "AGENTS.md 代码规范",  "& 安全红线注入",
         "linter / 测试报错",   "→ AI 自我修正",
         "CI 全流程验证",        "linter + 测试 + 安全扫描"),
        (TEAL,    "客服机器人", "Customer Service",
         "回复规范 / 禁忌话题",  "/ 升级规则",
         "情绪检测异常",         "→ 调整语气策略",
         "政策合规检查",         "+ 敏感内容过滤"),
        (PURPLE,  "内容创作",  "Content Creation",
         "品牌语调 / 格式限制",  "/ 事实边界",
         "可读性评分低",         "→ AI 修改润色",
         "抄袭检测",             "+ 品牌一致性核查"),
        (YELLOW,  "研究分析",  "Research",
         "来源白名单",           "/ 置信度门槛",
         "引用验证失败",         "→ 查询替代来源",
         "置信度评分",           "+ 专家评审"),
        (ORANGE,  "数据处理",  "Data Pipeline",
         "数据规范 / 字段映射",  "/ 异常策略",
         "Schema 报错",         "→ 修正处理逻辑",
         "数据质量检查",         "+ 批次对账"),
        (GREEN,   "金融合规",  "Finance",
         "监管规则 / 金额阈值",  "/ 合规红线",
         "风险评分超限",         "→ 重新规划方案",
         "法规审批流程",         "+ 大额人工确认"),
    ]

    for ri, (col, cn, en,
             c1l1, c1l2, c2l1, c2l2, c3l1, c3l2) in enumerate(rows_data):
        ry = header_y + header_h + ri * row_h
        bg, bg_fo = (SURF2, 0.65) if ri % 2 == 0 else (SURF, 0.50)
        p.append(R(tx1, ry, tx2, ry + row_h, bg, stroke=None, rx=0, fo=bg_fo))

        # Left color accent stripe
        p.append(f'<rect x="{tx1}" y="{ry}" width="5" height="{row_h}" '
                 f'fill="{col}" opacity="0.90"/>')

        # Agent type cell
        mid_a = (col_x[0] + col_x[1]) // 2
        rcy = ry + row_h // 2
        p.append(T(mid_a, rcy - 12, cn, 15, col, weight="700"))
        p.append(T(mid_a, rcy + 11, en, 11, col, fo=0.62))

        # Vertical column separators
        for ci in [1, 2, 3]:
            p.append(f'<line x1="{col_x[ci]}" y1="{ry + 10}" '
                     f'x2="{col_x[ci]}" y2="{ry + row_h - 10}" '
                     f'stroke="{BORDER}" stroke-width="1" stroke-opacity="0.40"/>')

        # Content columns
        for col_i, (l1, l2) in enumerate([(c1l1, c1l2), (c2l1, c2l2), (c3l1, c3l2)]):
            mid_x = (col_x[col_i + 1] + col_x[col_i + 2]) // 2
            p.append(T(mid_x, rcy - 12, l1, 13, TEXT, anchor="middle", fo=0.90))
            p.append(T(mid_x, rcy + 10, l2, 13, DIM, anchor="middle", fo=0.75))

    # Horizontal row separators
    for ri in range(1, n_rows + 1):
        ly = header_y + header_h + ri * row_h
        p.append(f'<line x1="{tx1}" y1="{ly}" x2="{tx2}" y2="{ly}" '
                 f'stroke="{BORDER}" stroke-width="1" stroke-opacity="0.30"/>')

    # Outer table border (drawn last)
    tbl_h = header_h + n_rows * row_h
    p.append(f'<rect x="{tx1}" y="{header_y}" width="{tx2 - tx1}" height="{tbl_h}" '
             f'rx="8" fill="none" stroke="{BORDER}" stroke-width="1.5" stroke-opacity="0.65"/>')

    # Footer note
    foot_y = header_y + tbl_h + 24
    p.append(T(tx1, foot_y,
               "* 三大核心原则在所有 Agent 类型中通用；具体实现工具因场景而异，"
               "Coding Agent 的质量门控即为 CI 管道",
               12, DIM, anchor="start", fo=0.68))

    p.append(end())
    _save("diagram_agent_types.svg", p)


# ── Save helper ───────────────────────────────────────────────────────────
def d11_cover() -> None:
    W, H = 1280, 720
    p: list[str] = []

    # ── defs ──────────────────────────────────────────────────────────────────
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}">'
    )
    p.append("<defs>")
    p.append(
        '<pattern id="cov_dots" x="0" y="0" width="48" height="48" patternUnits="userSpaceOnUse">'
        f'<circle cx="24" cy="24" r="1.4" fill="{ACCENT}" opacity="0.09"/>'
        "</pattern>"
    )
    p.append(
        '<radialGradient id="cov_glow" cx="50%" cy="44%" r="56%">'
        f'<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.13"/>'
        f'<stop offset="100%" stop-color="{BG}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    p.append(
        '<radialGradient id="cov_glow2" cx="50%" cy="44%" r="32%">'
        f'<stop offset="0%" stop-color="{PURPLE}" stop-opacity="0.07"/>'
        f'<stop offset="100%" stop-color="{BG}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    p.append("</defs>")

    # ── background ────────────────────────────────────────────────────────────
    p.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#cov_dots)"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#cov_glow)"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#cov_glow2)"/>')

    # Thin horizontal accent lines
    p.append(f'<line x1="0" y1="152" x2="{W}" y2="152" stroke="{ACCENT}" stroke-width="0.6" opacity="0.13"/>')
    p.append(f'<line x1="0" y1="{H - 152}" x2="{W}" y2="{H - 152}" stroke="{ACCENT}" stroke-width="0.6" opacity="0.13"/>')

    # Decorative corner arcs — top-left
    p.append(f'<path d="M 0,130 Q 90,0 240,0" stroke="{ACCENT}" stroke-width="1.5" fill="none" opacity="0.17"/>')
    p.append(f'<path d="M 0,85 Q 65,0 165,0" stroke="{PURPLE}" stroke-width="1" fill="none" opacity="0.12"/>')
    # bottom-right
    p.append(f'<path d="M {W},{H - 130} Q {W - 90},{H} {W - 240},{H}" stroke="{ACCENT}" stroke-width="1.5" fill="none" opacity="0.17"/>')
    p.append(f'<path d="M {W},{H - 85} Q {W - 65},{H} {W - 165},{H}" stroke="{PURPLE}" stroke-width="1" fill="none" opacity="0.12"/>')

    # ── top badge ─────────────────────────────────────────────────────────────
    bx, by = W // 2, 96
    p.append(R(bx - 118, by - 22, bx + 118, by + 22, ACCENT, stroke=ACCENT, rx=22, fo=0.10, sw=1.0, so=0.45))
    p.append(T(bx, by, "Harness  Engineering", 15, ACCENT, weight="600", fo=0.92))

    # ── hero formula ──────────────────────────────────────────────────────────
    # Rendered as inline tspan for multi-color; dominant-baseline="central" on surrounding group
    fy = 282
    p.append(
        f'<text x="{W // 2}" y="{fy}" '
        f'font-family="{FONT}" font-size="80" font-weight="800" letter-spacing="-1" '
        f'text-anchor="middle" dominant-baseline="central">'
        f'<tspan fill="{TEXT}">Agent</tspan>'
        f'<tspan fill="{ACCENT}"> = </tspan>'
        f'<tspan fill="{GREEN}">Model</tspan>'
        f'<tspan fill="{ACCENT}"> + </tspan>'
        f'<tspan fill="{PURPLE}">Harness</tspan>'
        f'</text>'
    )

    # ── tagline ───────────────────────────────────────────────────────────────
    p.append(T(W // 2, 356, "让 AI 的输出，从「提示依赖」变成「结构保障」", 22, DIM, fo=0.85))

    # ── three component cards ─────────────────────────────────────────────────
    cards = [
        (192, 432, 252, 88, ACCENT, "① 约束前馈", "规则文件 · 缩小解空间"),
        (514, 432, 252, 88, TEAL,   "② 反馈回路", "结构化错误 · 自我修正"),
        (836, 432, 252, 88, GREEN,  "③ 质量门控", "硬性检查 · 不依赖理解"),
    ]
    for cx_card, cy_card, cw, ch, col, title, sub in cards:
        x1, y1, x2, y2 = cx_card, cy_card, cx_card + cw, cy_card + ch
        mid_x = cx_card + cw // 2
        p.append(R(x1, y1, x2, y2, col, stroke=col, rx=12, fo=0.10, sw=1.0, so=0.30))
        p.append(f'<rect x="{x1}" y="{y1}" width="5" height="{ch}" rx="2.5" fill="{col}" opacity="0.72"/>')
        p.append(T(mid_x + 4, y1 + ch // 2 - 13, title, 16, col, weight="700"))
        p.append(T(mid_x + 4, y1 + ch // 2 + 14, sub, 13, DIM, fo=0.80))

    # ── bottom attribution ────────────────────────────────────────────────────
    sep_y = H - 110
    p.append(f'<line x1="430" y1="{sep_y}" x2="850" y2="{sep_y}" stroke="{DIM}" stroke-width="0.5" opacity="0.28"/>')
    p.append(T(W // 2, sep_y + 22, "Mitchell Hashimoto · Agent = Model + Harness · 2026", 12, DIM, fo=0.42))

    p.append("</svg>")
    _save("diagram_cover.svg", p)


def _save(name: str, parts: list[str]) -> None:
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write('\n'.join(parts))
    print(f"✓ {name}")


if __name__ == "__main__":
    print("Generating SVG diagrams…")
    d1_evolution()
    d2_arch()
    d3_workflow()
    d4_pre()
    d5_constraint()
    d6_prompt_anatomy()
    d7_prompt_limits()
    d8_context_window()
    d9_context_limits()
    d10_agent_types()
    d11_cover()
    print(f"\nAll SVGs saved to: {OUT_DIR}")
