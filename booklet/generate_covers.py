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

def brand_bar_adv(draw, accent):
    """进阶篇品牌栏"""
    y = H-46
    draw.rectangle([0,y,W,H], fill=(*accent,18))
    draw.line([(0,y),(W,y)], fill=(*accent,70), width=1)
    f = fnt(FONT_L, 18)
    draw.text((52, y+13), "《AI Agent 进阶：手搓 Multi-Agent 系统》", font=f, fill=(255,255,255,120))
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


def diagram_adv1(draw, a):
    """进阶 Day 1：单 Agent 上下文膨胀 vs 多 Agent 隔离对比"""
    draw.line([(W//2+10, 178), (W//2+10, 618)], fill=(*a, 35), width=1)

    # ── 左侧：单 Agent 上下文逐步增大 ──
    label(draw, 60, 180, "单 Agent 包干所有", a, fs=20)
    steps_data = [
        ("研究阶段", "+384 tokens",  110),
        ("写作阶段", "+947 tokens",  240),
        ("审核阶段", "+1048 tokens", 340),
    ]
    bh_s, bg_s = 56, 12
    for i, (name, tok, bw) in enumerate(steps_data):
        sy = 216 + i * (bh_s + bg_s)
        box(draw, 60, sy, bw, bh_s, name, a, fill_a=80 + i*40, fs=18)
        f2 = fnt(FONT_L, 16)
        draw.text((60 + bw + 12, sy + bh_s//2 - 9), tok, font=f2, fill=(*a, 150))
        if i < 2:
            # 渐长的暗示箭头
            nx = 60 + steps_data[i+1][2]//2
            arr(draw, 60 + bw + 2, sy + bh_s//2, 60 + steps_data[i+1][2] - 2, sy + bh_s + bg_s//2 + bh_s//2, a, w=1, head=6)

    total_sy = 216 + 3*(bh_s + bg_s) + 6
    box(draw, 60, total_sy, 340, 48, "最终：2891 tokens", a, fill_a=55, fs=19, bold=True)
    f3 = fnt(FONT_L, 16)
    draw.text((60, total_sy + 58), "任务越复杂，数字越大，直到超出上限", font=f3, fill=(*a, 130))

    # ── 右侧：三个 Agent 各自上下文很小 ──
    rx = W//2 + 40
    label(draw, rx, 180, "多 Agent 分工", a, fs=20)
    agents_data = [
        ("Researcher",  "~28 tokens"),
        ("Writer",      "~142 tokens"),
        ("Editor",      "~242 tokens"),
    ]
    aw, ah = 220, 56
    for i, (name, tok) in enumerate(agents_data):
        ay = 216 + i * (ah + bg_s)
        box(draw, rx, ay, aw, ah, name, a, fill_a=130, fs=21, bold=True)
        f2 = fnt(FONT_L, 16)
        draw.text((rx + aw + 14, ay + ah//2 - 9), tok, font=f2, fill=(*a, 160))

    total_sy_r = 216 + 3*(ah + bg_s) + 6
    box(draw, rx, total_sy_r, aw, 48, "合计：~412 tokens", a, fill_a=165, fs=19, bold=True)
    draw.text((rx, total_sy_r + 58), "每个 Agent 只看自己需要的，专注度更高", font=f3, fill=(*a, 160))


def diagram_adv2(draw, a):
    """进阶 Day 2：Orchestrator 调度员模式"""
    cx = W // 2

    # 用户请求
    ux, uy, uw, uh = cx - 110, 186, 220, 52
    box(draw, ux, uy, uw, uh, "用户请求", a, fill_a=110, fs=21)

    # Orchestrator
    ox, oy, ow, oh = cx - 150, 288, 300, 76
    box(draw, ox, oy, ow, oh, "Orchestrator\n（调度员·只管调度）", a, fill_a=185, fs=20, bold=True)
    arr(draw, cx, uy+uh+2, cx, oy-2, a, w=2)

    # LLM 规划注释（右侧浮标）
    f2 = fnt(FONT_L, 17)
    draw.text((ox+ow+20, oy+14), "用 LLM 解析意图", font=f2, fill=(*a, 160))
    draw.text((ox+ow+20, oy+38), "→ 规划任务列表", font=f2, fill=(*a, 160))

    # 三个 Worker
    workers = [
        ("Translator\n（翻译）",    cx - 370),
        ("Summarizer\n（摘要）",    cx),
        ("Sentiment\n（情感分析）", cx + 370),
    ]
    wy, ww, wh = 440, 200, 76
    for name, wx in workers:
        box(draw, wx - ww//2, wy, ww, wh, name, a, fill_a=100, fs=20)
        arr(draw, cx, oy+oh+2, wx, wy-2, a, w=2, head=8)

    # Worker 说明文字
    f3 = fnt(FONT_L, 17)
    draw.text((52, 542), "各 Worker 只知道自己的任务，不知道自己是第几步，不关心其他 Worker", font=f3, fill=(*a, 155))

    # 结果汇聚
    ry, rw, rh = 560, 280, 50
    box(draw, cx-rw//2, ry, rw, rh, "汇总结果 → 回复用户", a, fill_a=160, fs=20, bold=True)
    for _, wx in workers:
        arr(draw, wx, wy+wh+2, cx, ry-2, a, w=1, head=5)


def diagram_adv3(draw, a):
    """进阶 Day 3：Task / TaskResult 通信协议"""
    # Task 定义框（左）
    tx, ty, tw, th = 52, 186, 355, 200
    ghost_box(draw, tx, ty, tw, th, a)
    f_h = fnt(FONT_M, 19)
    draw.text((tx+16, ty+10), "Task（任务单）", font=f_h, fill=(255,255,255,220))
    task_fields = [
        ("task_id",     "唯一 ID"),
        ("agent_name",  "目标 Worker"),
        ("instruction", "主要指令"),
        ("context",     "附加数据"),
        ("created_at",  "创建时间戳"),
    ]
    for i, (field, desc) in enumerate(task_fields):
        fy = ty + 42 + i * 29
        draw.text((tx+18, fy), field, font=fnt(FONT_M, 17), fill=(255, 255, 255, 210))
        draw.text((tx+155, fy), f"# {desc}", font=fnt(FONT_L, 16), fill=(*a, 180))

    # Worker 中间框
    wx, wy, ww, wh = 500, 258, 200, 72
    box(draw, wx, wy, ww, wh,
        "Worker.run()\n(task) → TaskResult",
        a, fill_a=165, fs=16, bold=True)
    arr(draw, tx+tw+2, ty+th//2, wx-2, wy+wh//2, a, w=2)

    # TaskResult 定义框（右）
    rx, ry, rw, rh = 786, 186, 388, 200
    ghost_box(draw, rx, ry, rw, rh, a)
    draw.text((rx+16, ry+10), "TaskResult（结果单）", font=f_h, fill=(255,255,255,220))
    result_fields = [
        ("task_id",     "与 Task 对应"),
        ("agent_name",  "执行的 Worker"),
        ("status",      "DONE / FAILED"),
        ("output",      "结果内容"),
        ("duration_ms", "耗时（毫秒）"),
    ]
    for i, (field, desc) in enumerate(result_fields):
        fy = ry + 42 + i * 29
        draw.text((rx+18, fy), field, font=fnt(FONT_M, 17), fill=(255, 255, 255, 210))
        draw.text((rx+158, fy), f"# {desc}", font=fnt(FONT_L, 16), fill=(*a, 180))
    arr(draw, wx+ww+2, wy+wh//2, rx-2, ry+rh//2, a, w=2)

    # ProtocolLogger 日志示例（底部横跨）
    log_y = 430
    ghost_box(draw, 52, log_y, W-104, 120, a)
    draw.text((70, log_y+8), "ProtocolLogger（每次交接都有记录，出 bug 一眼定位）",
              font=fnt(FONT_M, 18), fill=(255,255,255,210))
    log_lines = [
        "  [协议] → 下发任务 a3f8c2d1 给 keyword_extractor",
        "  [协议] ✓ 收到结果 a3f8c2d1 来自 keyword_extractor (1243ms)",
        "  [协议] → 下发任务 b7e1f09a 给 tag_generator",
    ]
    for i, line in enumerate(log_lines):
        draw.text((70, log_y+36+i*26), line, font=fnt(FONT_L, 16), fill=(255, 255, 255, 190))


def diagram_adv4(draw, a):
    """进阶 Day 4：串行 vs 并行任务流"""
    draw.line([(W//2+10, 178), (W//2+10, 610)], fill=(*a, 35), width=1)
    workers_str = ["fact_checker", "tone_analyst", "action_advisor"]
    wh = 56

    # ── 左：串行 ──
    label(draw, 60, 180, "串行执行（一个接一个）", a, fs=19)
    t_labels = ["2341ms", "1876ms", "2103ms"]
    sw = 230
    for i, (name, t) in enumerate(zip(workers_str, t_labels)):
        sy = 216 + i * (wh + 12)
        box(draw, 60, sy, sw, wh, name, a, fill_a=85 + i*22, fs=17)
        f2 = fnt(FONT_L, 16)
        draw.text((60+sw+12, sy+wh//2-9), t, font=f2, fill=(*a, 150))
        if i < 2:
            arr(draw, 60+sw//2, sy+wh+2, 60+sw//2, sy+wh+10, a, w=2, head=5)

    total_sy = 216 + 3*(wh+12) + 8
    box(draw, 60, total_sy, sw, 46, "总耗时：6.32s", a, fill_a=60, fs=19, bold=True)

    # ── 右：并行 ──
    rx = W//2 + 40
    label(draw, rx, 180, "并行执行（同时开干）", a, fs=19)

    pw, pg = 166, 14
    total_pw = 3*pw + 2*pg   # = 526
    px_start = rx + max(0, (W//2 - 40 - total_pw)//2)

    # 同时开始横线 + 箭头
    bar_y = 218
    line_x1 = px_start + pw//2
    line_x2 = px_start + 2*(pw+pg) + pw//2
    draw.line([(line_x1, bar_y), (line_x2, bar_y)], fill=(*a, 160), width=2)
    box(draw, (line_x1+line_x2)//2 - 75, bar_y-42, 150, 36, "同时开始", a, fill_a=60, fs=17)

    for i, name in enumerate(workers_str):
        px = px_start + i*(pw+pg)
        box(draw, px, bar_y+32, pw, wh, name, a, fill_a=85+i*22, fs=15)
        arr(draw, px+pw//2, bar_y+2, px+pw//2, bar_y+30, a, w=2, head=6)

    total_py = bar_y + 32 + wh + 14
    box(draw, px_start, total_py, total_pw, 46,
        "总耗时：2.31s   加速比：2.7x", a, fill_a=165, fs=18, bold=True)

    # Synthesizer
    synth_y = total_py + 46 + 18
    box(draw, px_start + 40, synth_y, total_pw - 80, 50,
        "Synthesizer：汇总三份分析结果", a, fill_a=120, fs=17, bold=True)
    arr(draw, px_start + total_pw//2, total_py+46+2,
        px_start + total_pw//2, synth_y-2, a, w=2, head=6)

    # 底部说明
    label(draw, 40, 610, "有依赖 → 串行   |   无依赖 → 并行   |   并行结果由 Synthesizer 汇总", a, fs=17)


def diagram_adv5(draw, a):
    """进阶 Day 5：三种错误处理策略"""
    gap_col = 20
    col_w = (W - 80 - 2*gap_col) // 3   # ~386

    cols_cfg = [
        {
            "x": 40,
            "title": "策略一：重试装饰器",
            "sub": "指数退避",
            "steps": ["LLM 调用失败", "等 0.3s 重试", "等 0.6s 重试", "等 1.2s 重试", "成功 ✓"],
            "alphas": [100, 72, 82, 92, 185],
        },
        {
            "x": 40 + col_w + gap_col,
            "title": "策略二：JSON 安全提取",
            "sub": "降级而非崩溃",
            "steps": ["LLM 输出文本", "尝试提取JSON", "解析失败？", "返回 fallback", "继续运行 ✓"],
            "alphas": [100, 90, 68, 120, 185],
        },
        {
            "x": 40 + 2*(col_w + gap_col),
            "title": "策略三：局部失败容忍",
            "sub": "流水线不中断",
            "steps": ["步骤 1 成功", "步骤 2 失败！", "→ 用 fallback", "步骤 3 继续", "最终输出 ✓"],
            "alphas": [180, 58, 110, 140, 185],
        },
    ]

    bh, bg = 52, 10
    for col in cols_cfg:
        cx = col["x"]
        bw_box = col_w - 16

        draw.text((cx+8, 186), col["title"], font=fnt(FONT_M, 19), fill=(255,255,255,230))
        draw.text((cx+8, 212), col["sub"],   font=fnt(FONT_L, 16), fill=(*a, 160))

        for i, (step, alpha) in enumerate(zip(col["steps"], col["alphas"])):
            sy = 242 + i * (bh + bg)
            box(draw, cx, sy, bw_box, bh, step, a, fill_a=alpha, fs=17)
            if i < len(col["steps"]) - 1:
                arr(draw, cx+bw_box//2, sy+bh+2, cx+bw_box//2, sy+bh+bg-2, a, w=2, head=5)

    label(draw, 40, 612, "临时错误 → 重试   |   格式错误 → 降级   |   逻辑 Bug → 不要重试，立刻暴露", a, fs=17)


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
    # ── 进阶篇 ──
    dict(file="09_adv1", tag="进阶 Day 1",
         title="上下文隔离", sub="单 Agent 2891 tokens → 多 Agent 412 tokens",
         accent=(14, 165, 233), bg=(4, 14, 22), draw_fn=diagram_adv1, adv=True),
    dict(file="10_adv2", tag="进阶 Day 2",
         title="Orchestrator 调度员模式", sub="调度员只管调度，Worker 各司其职",
         accent=(245, 158, 11), bg=(22, 14, 4), draw_fn=diagram_adv2, adv=True),
    dict(file="11_adv3", tag="进阶 Day 3",
         title="Task / TaskResult 协议", sub="统一接口 · 可观测性 · 方便扩展",
         accent=(34, 197, 94), bg=(4, 18, 8), draw_fn=diagram_adv3, adv=True),
    dict(file="12_adv4", tag="进阶 Day 4",
         title="串行 vs 并行任务流", sub="3个任务：6.32s → 2.31s，加速 2.7x",
         accent=(167, 139, 250), bg=(12, 8, 22), draw_fn=diagram_adv4, adv=True),
    dict(file="13_adv5", tag="进阶 Day 5",
         title="三种错误处理策略", sub="重试 · 降级 · 局部失败容忍",
         accent=(251, 113, 133), bg=(22, 6, 10), draw_fn=diagram_adv5, adv=True),
]


def make_cover(cfg):
    img, draw = make_base(cfg["bg"], cfg["accent"])
    a = cfg["accent"]

    cfg["draw_fn"](draw, a)
    title_strip(img, draw, cfg["tag"], cfg["title"], cfg["sub"], a)
    if cfg.get("adv"):
        brand_bar_adv(draw, a)
    else:
        brand_bar(draw, a)

    out = os.path.join(OUT_DIR, f"{cfg['file']}_cover.png")
    img.convert("RGB").save(out, "PNG")
    print(f"✓  {out}")


if __name__ == "__main__":
    print(f"输出目录：{OUT_DIR}\n")
    for cfg in ARTICLES:
        make_cover(cfg)
    print(f"\n完成，共 {len(ARTICLES)} 张。")
