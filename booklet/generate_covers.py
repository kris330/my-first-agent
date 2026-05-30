"""
生成 8 张知乎文章封面图（架构图/流程图版）
尺寸：1280 x 720
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

OUT_DIR = os.path.join(os.path.dirname(__file__), "covers")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1280, 720
_HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_M = (_HIRA, 1)   # W3 中等粗细，用于正文标签
FONT_L = (_HIRA, 0)   # W3 细体，用于说明文字
FONT_B = (_HIRA, 1)   # 同 M，box bold=True 时字号加大替代真粗体

def fnt(spec, size):
    try:
        if isinstance(spec, tuple):
            path, idx = spec
            return ImageFont.truetype(path, size, index=idx)
        return ImageFont.truetype(spec, size)
    except:
        return ImageFont.load_default()

# ─── 通用背景 ──────────────────────────────────────────────────

def make_base(bg, accent):
    img = Image.new("RGBA", (W, H), (*bg, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 渐变：从上到下轻微加深，顶部保留底色亮度
    for y in range(H):
        t = y / H
        c = tuple(max(0, int(bg[i] * (1.0 - t * 0.22))) for i in range(3))
        draw.line([(0, y), (W, y)], fill=(*c, 255))

    # 极细点阵网格（仅图表区）
    for x in range(28, W, 52):
        for y in range(160, H - 50, 52):
            draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(*accent, 22))

    # 暗角（四边向内渐暗，增加视觉深度）
    for i in range(60, 0, -1):
        a = int((1 - i / 60) ** 2 * 55)
        bx = i * 2
        by = int(i * 1.2)
        draw.rectangle([0, 0, W, by],           fill=(0, 0, 0, a))
        draw.rectangle([0, H - by, W, H],       fill=(0, 0, 0, a))
        draw.rectangle([0, 0, bx, H],           fill=(0, 0, 0, a))
        draw.rectangle([W - bx, 0, W, H],       fill=(0, 0, 0, a))

    return img, draw

# ─── 通用元件 ──────────────────────────────────────────────────

def box(draw, x, y, w, h, text, accent, fill_a=150, border_a=220,
        fs=22, r=10, tc=None, bold=False):
    """带文字的圆角矩形"""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=(*accent, fill_a),
                            outline=(*accent, border_a), width=2)
    f  = fnt(FONT_M, fs + (2 if bold else 0))
    tc = tc or (255, 255, 255, 240)
    lines = text.split('\n')
    lh = fs + 5
    ty = y + (h - len(lines) * lh) // 2
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=f)
        tx = x + (w - (bb[2]-bb[0])) // 2
        draw.text((tx, ty), line, font=f, fill=tc)
        ty += lh

def ghost_box(draw, x, y, w, h, accent, r=8):
    """无文字轮廓框"""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r,
                            fill=(*accent, 18),
                            outline=(*accent, 80), width=1)

def arr(draw, x1, y1, x2, y2, accent, w=2, head=10):
    """直线箭头"""
    c = (*accent, 200)
    draw.line([(x1, y1), (x2, y2)], fill=c, width=w)
    ang = math.atan2(y2-y1, x2-x1)
    for da in (-0.42, 0.42):
        ax = x2 - head * math.cos(ang+da)
        ay = y2 - head * math.sin(ang+da)
        draw.line([(x2,y2),(int(ax),int(ay))], fill=c, width=w)

def arr_h(draw, x1, y1, x2, y2, accent, w=2, head=10):
    """折线箭头（先水平再垂直）"""
    c = (*accent, 200)
    draw.line([(x1, y1), (x2, y1)], fill=c, width=w)
    draw.line([(x2, y1), (x2, y2)], fill=c, width=w)
    ang = math.atan2(y2-y1, 0) if y2 != y1 else 0
    for da in (-0.42, 0.42):
        ax = x2 - head * math.cos(ang+da)
        ay = y2 - head * math.sin(ang+da)
        draw.line([(x2,y2),(int(ax),int(ay))], fill=c, width=w)

def arr_v(draw, x1, y1, x2, y2, accent, w=2, head=10):
    """折线箭头（先垂直再水平）"""
    c = (*accent, 200)
    draw.line([(x1, y1), (x1, y2)], fill=c, width=w)
    draw.line([(x1, y2), (x2, y2)], fill=c, width=w)
    ang = math.atan2(0, x2-x1) if x2 != x1 else 0
    for da in (-0.42, 0.42):
        ax = x2 - head * math.cos(ang+da)
        ay = y2 - head * math.sin(ang+da)
        draw.line([(x2,y2),(int(ax),int(ay))], fill=c, width=w)

def label(draw, x, y, text, accent, fs=18, center=False, w=0):
    f  = fnt(FONT_L, fs)
    if center and w:
        bb = draw.textbbox((0,0), text, font=f)
        x  = x + (w - (bb[2]-bb[0])) // 2
    draw.text((x, y), text, font=f, fill=(*accent, 170))

def title_strip(img, draw, tag, title, sub, accent):
    """顶部标题区（3× 超采样 → LANCZOS 缩回，字体精细圆润）"""
    SC   = 3
    s_w, s_h = W * SC, 168 * SC
    surf = Image.new("RGBA", (s_w, s_h), (0, 0, 0, 0))
    sd   = ImageDraw.Draw(surf, "RGBA")

    # Tag 标签徽章
    tf  = fnt(FONT_L, 20 * SC)
    tb  = sd.textbbox((0, 0), tag, font=tf)
    bw_ = tb[2] - tb[0] + 28 * SC
    bh_ = tb[3] - tb[1] + 12 * SC
    sd.rounded_rectangle(
        [52*SC, 36*SC, 52*SC + bw_, 36*SC + bh_],
        radius=5*SC, fill=(*accent, 200)
    )
    sd.text((66*SC, 36*SC + 6*SC), tag, font=tf, fill=(255, 255, 255, 245))

    # 主标题（用 FONT_L 细体，笔画细腻抗锯齿更佳）
    tf2 = fnt(FONT_L, 40 * SC)
    ty  = 36*SC + bh_ + 10*SC
    for line in title.split('\n'):
        sd.text((52*SC, ty), line, font=tf2, fill=(255, 255, 255, 240))
        bb  = sd.textbbox((0, 0), line, font=tf2)
        ty += bb[3] - bb[1] + 2*SC

    # 副标题
    sd.text((52*SC, ty + 6*SC), sub,
            font=fnt(FONT_L, 19 * SC), fill=(*accent, 190))

    # 缩回 1× 并合成到主图
    small = surf.resize((W, 168), Image.LANCZOS)
    img.alpha_composite(small, (0, 0))

def brand_bar(draw, accent):
    y = H-46
    draw.rectangle([0,y,W,H], fill=(*accent,18))
    draw.line([(0,y),(W,y)], fill=(*accent,70), width=1)
    f = fnt(FONT_L, 18)
    draw.text((52, y+13), "《7天从零手搓 AI Agent》", font=f, fill=(255,255,255,120))
    url = "github.com/kris330/my-first-agent"
    bb  = draw.textbbox((0,0), url, font=f)
    draw.text((W-(bb[2]-bb[0])-56, y+13), url, font=f, fill=(*accent,110))

# ══════════════════════════════════════════════════════════════
# 各篇图表绘制
# ══════════════════════════════════════════════════════════════

def diagram_intro(draw, a):
    """00_intro：7天能力成长路线图"""
    # 7个节点水平排列
    days = [
        ("Day1", "最小\nAgent"),
        ("Day2", "真实\n工具"),
        ("Day3", "多工具\n选择"),
        ("Day4", "对话\n记忆"),
        ("Day5", "ReAct\n循环"),
        ("Day6", "任务\n规划"),
        ("Day7", "完整\n项目"),
    ]
    n    = len(days)
    bw, bh = 116, 80
    gap  = (W - 80 - n * bw) // (n - 1)
    y0   = 360
    x0   = 48

    # 进度条背景线
    lx1 = x0 + bw // 2
    lx2 = x0 + (n-1)*(bw+gap) + bw // 2
    draw.line([(lx1, y0+bh//2), (lx2, y0+bh//2)], fill=(*a, 40), width=4)

    for i, (day, cap) in enumerate(days):
        cx = x0 + i * (bw + gap)
        # 渐变色 alpha（越到后面越亮）
        alpha = 100 + int(i / (n-1) * 100)
        box(draw, cx, y0, bw, bh, cap, a, fill_a=alpha, border_a=160+i*10,
            fs=20, bold=(i==6))
        # Day 标签
        label(draw, cx, y0-34, day, a, fs=20, center=True, w=bw)
        # 连接箭头
        if i < n-1:
            nx = cx + bw
            arr(draw, nx+2, y0+bh//2, nx+gap-2, y0+bh//2, a, w=2, head=8)

    # 最终成果说明框
    fx, fy, fw, fh = 350, 490, 580, 72
    box(draw, fx, fy, fw, fh,
        "多工具  ·  对话记忆  ·  ReAct循环  ·  任务规划",
        a, fill_a=60, border_a=130, fs=22)
    # 从最后节点底部 → 先向下 → 再向左到汇总框右边（连续L形）
    last_cx = x0 + (n-1)*(bw+gap) + bw//2
    arr_v(draw, last_cx, y0+bh+2, fx+fw, fy+fh//2, a, w=2, head=8)
    label(draw, fx + fw//2 - 80, fy + fh + 10, "最终项目具备的完整能力", a, fs=18)


def diagram_day1(draw, a):
    """01_day1：最小Agent执行流程（5步线性）"""
    steps = [
        ("用户\n输入",     ""),
        ("System\nPrompt", "约束输出格式"),
        ("AI 决策\nJSON",  '{"action":...}'),
        ("解析\n执行",     "execute_action()"),
        ("输出\n结果",     ""),
    ]
    bw, bh = 148, 76
    gap    = (W - 120 - len(steps)*bw) // (len(steps)-1)
    y0     = 310

    for i, (name, sub_t) in enumerate(steps):
        cx = 60 + i * (bw + gap)
        fill = 180 if i in (2, 3) else 110
        box(draw, cx, y0, bw, bh, name, a, fill_a=fill, fs=22, bold=(i==2))
        if sub_t:
            label(draw, cx, y0+bh+10, sub_t, a, fs=17, center=True, w=bw)
        if i < len(steps)-1:
            arr(draw, cx+bw+2, y0+bh//2, cx+bw+gap-2, y0+bh//2, a, w=2)

    # 核心注释框
    fx, fy, fw, fh = 380, 460, 520, 56
    box(draw, fx, fy, fw, fh, "Agent 核心 = 感知  →  思考  →  行动",
        a, fill_a=40, border_a=110, fs=20)


def diagram_day2(draw, a):
    """02_day2：工具注册表架构"""
    # 用户 → Agent → tool_registry → [tool1, tool2] → 结果 → 用户
    cx = W // 2

    # 列布局
    nodes = [
        (cx, 170,  220, 52, "用户输入",       True),
        (cx, 270,  220, 52, "Agent.py",        True),
        (cx, 370,  260, 58, "tool_registry.py\nTOOLS = {...}", True),
    ]
    for (nx, ny, nw, nh, text, _) in nodes:
        box(draw, nx-nw//2, ny, nw, nh, text, a,
            fill_a=140, fs=21, bold=True)

    arr(draw, cx, 170+52+2, cx, 270-2, a)
    arr(draw, cx, 270+52+2, cx, 370-2, a)

    # 两个工具
    tools = [("web_search\n(真实搜索)", cx-220), ("get_weather\n(mock数据)", cx+220)]
    ty    = 490
    for txt, tx in tools:
        box(draw, tx-110, ty, 220, 60, txt, a, fill_a=100, fs=20)
        # 从注册表引出
        arr(draw, cx + (1 if tx > cx else -1)*20, 370+58+2,
            tx, ty-2, a, w=2)

    # 合并结果
    ry = 610
    box(draw, cx-120, ry, 240, 52, "工具结果 → 回复用户", a, fill_a=160, fs=21, bold=True)
    for _, tx in tools:
        arr(draw, tx, ty+60+2, cx, ry-2, a, w=2)


def diagram_day3(draw, a):
    """03_day3：多工具自动选择流程"""
    # 左: 用户问题示例  中: AI决策  右: 4个工具
    # 左侧问题列
    questions = ["今天几点了？", "1024 × 3 = ?", "上海天气如何？", "GPT-5 新闻？"]
    qx, qy0, qw, qh = 52, 230, 230, 50
    for i, q in enumerate(questions):
        box(draw, qx, qy0 + i*(qh+12), qw, qh, q, a,
            fill_a=80, border_a=120, fs=20)

    # 中间 AI 决策
    mx, my, mw, mh = 380, 310, 240, 96
    box(draw, mx, my, mw, mh,
        "AI 读取\n工具描述\n选择最合适工具",
        a, fill_a=170, fs=21, bold=True)

    # 左→中 汇聚箭头
    for i in range(4):
        y_from = qy0 + i*(qh+12) + qh//2
        arr(draw, qx+qw+2, y_from, mx-2, my+mh//2, a, w=2, head=8)

    # 右侧 4 个工具
    tools = ["get_current_time", "calculate", "get_weather", "web_search"]
    rx, ry0, rw, rh = 760, 210, 250, 52
    for i, t in enumerate(tools):
        box(draw, rx, ry0 + i*(rh+14), rw, rh, t, a,
            fill_a=100 + i*20, fs=20)
        arr(draw, mx+mw+2, my+mh//2, rx-2, ry0 + i*(rh+14) + rh//2, a, w=2, head=8)

    # 底部说明
    label(draw, 340, 590, "工具描述质量  →  选择准确率", a, fs=20)


def diagram_day4(draw, a):
    """04_day4：对话记忆工作原理（3轮渐增）"""
    msg_w, msg_h = 96, 38
    gap  = 6
    api_w, api_h = 100, 120
    api_x = W - 220

    rounds = [
        ["system", "user1"],
        ["system", "user1", "asst1", "user2"],
        ["system", "user1", "asst1", "user2", "asst2", "user3"],
    ]
    colors_map = {
        "system": (160,160,160),
        "user1":  a, "user2": a, "user3": a,
        "asst1":  (100,200,100), "asst2": (100,200,100),
    }
    labels_map = {
        "system": "sys", "user1": "you", "user2": "you",
        "user3":  "you", "asst1": "AI", "asst2": "AI",
    }
    round_labels = ["第 1 轮", "第 2 轮", "第 3 轮"]
    y_starts = [190, 340, 490]

    for ri, (msgs, ys) in enumerate(zip(rounds, y_starts)):
        # 轮次标签
        label(draw, 52, ys+msg_h//2-10, round_labels[ri], a, fs=19)
        # 消息块
        mx0 = 160
        for mi, msg in enumerate(msgs):
            mc = colors_map.get(msg, a)
            is_last = (mi == len(msgs)-1)
            fa = 200 if is_last else 110
            draw.rounded_rectangle(
                [mx0, ys, mx0+msg_w, ys+msg_h],
                radius=6,
                fill=(*mc, fa),
                outline=(*mc, 220), width=2,
            )
            f = fnt(FONT_L, 16)
            txt = labels_map.get(msg, msg)
            bb  = draw.textbbox((0,0), txt, font=f)
            draw.text((mx0+(msg_w-(bb[2]-bb[0]))//2, ys+(msg_h-(bb[3]-bb[1]))//2),
                      txt, font=f, fill=(255,255,255,230))
            mx0 += msg_w + gap

        # 箭头到 API
        arr(draw, mx0+4, ys+msg_h//2, api_x-4, ys+msg_h//2, a, w=2)

    # API 框
    box(draw, api_x, y_starts[0]-10, api_w, y_starts[2]+msg_h-y_starts[0]+20,
        "OpenAI\nAPI", a, fill_a=130, fs=20, bold=True)

    # 底部说明
    label(draw, 130, 590,
          "每轮请求携带完整历史  →  AI 能「记住」之前的对话", a, fs=20)


def diagram_day5(draw, a):
    """05_day5：ReAct循环流程图（环形）"""
    # 中心坐标
    ocx, ocy = W//2 + 20, 400
    R = 170

    # 4个节点（角度：上=270°，右=0°，下=90°，左=180°）
    node_angles = [270, 180, 90, 0]
    node_labels = ["用户任务\n输入", "AI 思考\n(Thought)", "调用工具\n(Action)", "观察结果\n(Observation)"]
    nw, nh = 158, 66

    node_centers = []
    for ang, lbl in zip(node_angles, node_labels):
        rad = math.radians(ang)
        nx  = ocx + R * math.cos(rad)
        ny  = ocy + R * math.sin(rad)
        node_centers.append((int(nx), int(ny)))
        fill = 180 if "AI 思考" in lbl else 110
        box(draw, int(nx)-nw//2, int(ny)-nh//2, nw, nh, lbl,
            a, fill_a=fill, fs=20, bold=("AI" in lbl))

    # 顺时针箭头（上→左→下→右→上）
    order = [0, 1, 2, 3]
    for i in range(len(order)):
        c1 = node_centers[order[i]]
        c2 = node_centers[order[(i+1) % len(order)]]
        # 从节点边缘出发
        dx  = c2[0]-c1[0]; dy = c2[1]-c1[1]
        dist = math.hypot(dx, dy)
        sx  = c1[0] + dx/dist * (nw//2+4)
        sy  = c1[1] + dy/dist * (nh//2+4)
        ex  = c2[0] - dx/dist * (nw//2+6)
        ey  = c2[1] - dy/dist * (nh//2+6)
        arr(draw, int(sx), int(sy), int(ex), int(ey), a, w=2, head=10)

    # 中心 loop 标签
    label(draw, ocx-46, ocy-16, "循环", a, fs=22)

    # 出口箭头（从"AI思考"向右引出最终答案）
    ex_x = ocx - R - nw//2 - 14
    ex_y = ocy
    box(draw, ex_x - 220, ex_y-30, 200, 60,
        "final_answer\n→ 输出给用户", a, fill_a=160, fs=20, bold=True)
    arr(draw, ex_x-20, ex_y, ex_x-200-4, ex_y, a, w=2)
    label(draw, ex_x-215, ex_y-52, "任务完成", a, fs=18)

    # max_steps 标注
    label(draw, ocx+R+nw//2+14, ocy-14,
          "超出 max_steps\n→ 强制结束", a, fs=17)


def diagram_day6(draw, a):
    """06_day6：Plan-and-Execute 架构"""
    # 左: 复杂任务 → Planner → 计划列表 → Executor → 最终答案
    tx, ty, tw, th = 52, 320, 160, 70
    box(draw, tx, ty, tw, th, "复杂任务\n输入", a, fill_a=110, fs=21)

    px, py, pw, ph = 290, 310, 180, 90
    box(draw, px, py, pw, ph, "Planner\n任务拆解", a, fill_a=170, fs=21, bold=True)
    arr(draw, tx+tw+2, ty+th//2, px-2, py+ph//2, a, w=2)

    # 步骤列表
    steps = ["步骤 1\nweb_search", "步骤 2\nweb_search", "步骤 3\n(无工具)", "步骤 4\n汇总整合"]
    sw, sh = 180, 66
    sy0 = 220
    sx0 = 550
    sg  = (H - 46 - sy0 - 4*sh) // 3

    for i, s in enumerate(steps):
        sy = sy0 + i*(sh+sg)
        fill = 160 if i == 3 else 100
        box(draw, sx0, sy, sw, sh, s, a, fill_a=fill, fs=19, bold=(i==3))
        # Planner 到每个步骤
        arr(draw, px+pw+2, py+ph//2, sx0-2, sy+sh//2, a, w=2, head=8)

    # 顺序执行竖线
    for i in range(len(steps)-1):
        sy1 = sy0 + i*(sh+sg) + sh
        sy2 = sy0 + (i+1)*(sh+sg)
        arr(draw, sx0+sw//2, sy1+2, sx0+sw//2, sy2-2, a, w=2, head=6)

    # Executor
    ex, ey, ew, eh = 820, 295, 180, 100
    box(draw, ex, ey, ew, eh, "Executor\n按步执行", a, fill_a=150, fs=21, bold=True)
    # 步骤到 executor
    for i in range(len(steps)):
        sy = sy0 + i*(sh+sg) + sh//2
        arr(draw, sx0+sw+2, sy, ex-2, ey+eh//2, a, w=2, head=8)

    # 最终答案
    fx, fy, fw, fh = 1070, 320, 178, 70
    box(draw, fx, fy, fw, fh, "最终\n答案", a, fill_a=180, fs=22, bold=True)
    arr(draw, ex+ew+2, ey+eh//2, fx-2, fy+fh//2, a, w=2)


def diagram_day7(draw, a):
    """07_day7：完整系统分层架构图"""
    layers = [
        # (label, height, sub_boxes)
        ("main.py  —  CLI 统一入口",              54,  ["直接对话", "/plan 规划", "/clear 重置"]),
        ("ReactAgent  +  Plan-and-Execute",       54,  ["agent_loop.py", "planner.py", "executor.py"]),
        ("tool_registry.py  —  工具注册中心",     54,  ["web_search", "get_weather", "calculate", "get_time"]),
        ("memory / short_term.py  —  对话记忆",   46,  []),
        ("config.py + llm.py  —  配置 & API调用", 46,  ["OpenAI", "DeepSeek", "国内API"]),
    ]

    lx   = 80
    lw   = W - 160
    ly   = 170
    gap  = 10

    for label_text, lh, subs in layers:
        # 大层框
        ghost_box(draw, lx, ly, lw, lh, a, r=8)
        # 层标签（左对齐）
        draw.text((lx+18, ly+(lh-24)//2), label_text,
                  font=fnt(FONT_M, 21), fill=(255,255,255,220))

        # 子模块小块（右侧）
        if subs:
            sbw = min(150, (lw - 300) // len(subs) - 8)
            sbx = lx + lw - 20 - len(subs)*(sbw+8)
            for s in subs:
                sby = ly + (lh-34)//2
                draw.rounded_rectangle([sbx, sby, sbx+sbw, sby+34],
                                        radius=5,
                                        fill=(*a, 120),
                                        outline=(*a, 190), width=1)
                f  = fnt(FONT_L, 16)
                bb = draw.textbbox((0,0), s, font=f)
                draw.text((sbx+(sbw-(bb[2]-bb[0]))//2, sby+(34-(bb[3]-bb[1]))//2),
                          s, font=f, fill=(255,255,255,220))
                sbx += sbw + 8

        ly += lh + gap

    # 连接竖线
    draw.line([(W//2, 170), (W//2, ly-gap)], fill=(*a, 30), width=1)

    # 底部注释
    label(draw, lx+10, ly+8, "独立模块，各司其职  ·  新增工具只需改 tool_registry.py", a, fs=19)


# ══════════════════════════════════════════════════════════════
# 文章配置 & 主循环
# ══════════════════════════════════════════════════════════════

ARTICLES = [
    dict(file="00_intro", tag="系列开篇",
         title="7天成长路线图", sub="从最小 Agent 到完整系统",
         accent=(129, 140, 248), bg=(10, 10, 26), draw_fn=diagram_intro),
    dict(file="01_day1", tag="Day 1",
         title="最小 Agent 执行流程", sub="感知 → 思考(JSON) → 行动",
         accent=(52, 211, 153), bg=(8, 16, 14), draw_fn=diagram_day1),
    dict(file="02_day2", tag="Day 2",
         title="工具注册表架构", sub="Agent 如何发现并调用工具",
         accent=(96, 165, 250), bg=(8, 12, 26), draw_fn=diagram_day2),
    dict(file="03_day3", tag="Day 3",
         title="多工具自动选择流程", sub="工具描述质量 = 选择准确率",
         accent=(251, 191, 36), bg=(20, 16, 6), draw_fn=diagram_day3),
    dict(file="04_day4", tag="Day 4",
         title="对话记忆工作原理", sub="把历史消息带进每次 API 请求",
         accent=(192, 132, 252), bg=(14, 8, 26), draw_fn=diagram_day4),
    dict(file="05_day5", tag="Day 5",
         title="ReAct 循环流程图", sub="Thought → Action → Observation → ...",
         accent=(248, 113, 113), bg=(22, 8, 10), draw_fn=diagram_day5),
    dict(file="06_day6", tag="Day 6",
         title="Plan-and-Execute 架构", sub="先拆解任务，再逐步执行，最后汇总",
         accent=(45, 212, 191), bg=(6, 20, 18), draw_fn=diagram_day6),
    dict(file="07_day7", tag="Day 7",
         title="完整系统分层架构", sub="7个模块，各司其职，自由扩展",
         accent=(251, 146, 60), bg=(22, 12, 6), draw_fn=diagram_day7),
]


def make_cover(cfg):
    img, draw = make_base(cfg["bg"], cfg["accent"])
    a = cfg["accent"]

    cfg["draw_fn"](draw, a)
    title_strip(img, draw, cfg["tag"], cfg["title"], cfg["sub"], a)
    brand_bar(draw, a)

    out = os.path.join(OUT_DIR, f"{cfg['file']}_cover.png")
    img.convert("RGB").save(out, "PNG")
    print(f"✓  {out}")


if __name__ == "__main__":
    print(f"输出目录：{OUT_DIR}\n")
    for cfg in ARTICLES:
        make_cover(cfg)
    print(f"\n完成，共 {len(ARTICLES)} 张。")
