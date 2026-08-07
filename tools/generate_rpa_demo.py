"""Generate the original, sanitized RPA workflow demo used by the portfolio.

The animation contains no screenshots, client data, account information or
third-party footage. Run from the repository root with:

    python tools/generate_rpa_demo.py
"""

from __future__ import annotations

import math
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
VIDEO_PATH = ASSET_DIR / "rpa-workflow-demo.mp4"
POSTER_PATH = ASSET_DIR / "rpa-workflow-poster.png"

WIDTH, HEIGHT = 960, 540
FPS, DURATION = 24, 12

INK = "#102C3B"
INK_2 = "#173B4A"
TEAL = "#1DB8AE"
TEAL_SOFT = "#8BE2D9"
PAPER = "#F3F1E8"
MUTED = "#9DB8BE"
LINE = "#315563"
WHITE = "#F8FBFA"
AMBER = "#E9B85D"

FONT_REGULAR = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F10 = font(10)
F11 = font(11)
F12 = font(12)
F12B = font(12, True)
F13 = font(13)
F13B = font(13, True)
F14 = font(14)
F14B = font(14, True)
F16B = font(16, True)
F18B = font(18, True)
F24B = font(24, True)
F31B = font(31, True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def fade(t: float, start: float, length: float = 0.45) -> float:
    return ease((t - start) / length)


def blend(hex_a: str, hex_b: str, amount: float) -> tuple[int, int, int]:
    amount = clamp(amount)
    a = tuple(int(hex_a[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(hex_b[i : i + 2], 16) for i in (1, 3, 5))
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def alpha_color(hex_color: str, opacity: float) -> tuple[int, int, int, int]:
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return (*rgb, round(255 * clamp(opacity)))


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    typeface: ImageFont.FreeTypeFont,
    color: str | tuple[int, ...],
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=typeface, fill=color, anchor=anchor)


def check_mark(draw: ImageDraw.ImageDraw, center: tuple[int, int], color: str) -> None:
    x, y = center
    draw.line((x - 5, y, x - 1, y + 4, x + 7, y - 5), fill=color, width=2, joint="curve")


def render_frame(t: float) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), INK)
    draw = ImageDraw.Draw(image, "RGBA")

    # Subtle engineering grid; intentionally restrained so the video remains
    # readable after mobile downscaling.
    for x in range(0, WIDTH, 32):
        draw.line((x, 0, x, HEIGHT), fill=alpha_color(WHITE, 0.026), width=1)
    for y in range(0, HEIGHT, 32):
        draw.line((0, y, WIDTH, y), fill=alpha_color(WHITE, 0.026), width=1)

    # Header.
    draw.rectangle((0, 0, WIDTH, 58), fill=alpha_color("#0C2532", 0.98))
    draw.rectangle((24, 18, 52, 40), fill=TEAL)
    text(draw, (38, 29), "R", F12B, INK, "mm")
    text(draw, (66, 19), "RPA / AUTOMATION RUNBOOK", F12B, WHITE)
    text(draw, (66, 36), "ORIGINAL MOTION DEMO", F10, MUTED)
    draw.rounded_rectangle((789, 17, 936, 41), radius=12, outline=alpha_color(TEAL_SOFT, 0.4), width=1)
    draw.ellipse((802, 25, 808, 31), fill=TEAL_SOFT)
    text(draw, (819, 29), "DEMO · 已脱敏", F10, TEAL_SOFT, "lm")

    # Heading.
    text(draw, (34, 82), "一条售后任务，如何被自动化接住？", F24B, WHITE)
    text(draw, (34, 116), "从触发、识别到跨系统执行与回写，完整保留异常出口。", F12, MUTED)

    stages = [
        ("01", "任务触发"),
        ("02", "字段识别"),
        ("03", "规则匹配"),
        ("04", "系统执行"),
        ("05", "结果回写"),
    ]
    stage_starts = [1.0, 2.7, 4.5, 6.4, 8.4]
    stage_x = [50, 243, 436, 629, 822]
    current = max(0, min(len(stages) - 1, sum(t >= s for s in stage_starts) - 1))

    # Progress rail.
    draw.line((50, 170, 822, 170), fill=LINE, width=2)
    overall = ease((t - 1.0) / 8.9)
    draw.line((50, 170, 50 + 772 * overall, 170), fill=TEAL, width=3)
    for index, ((number, label), x) in enumerate(zip(stages, stage_x)):
        reached = fade(t, stage_starts[index], 0.32)
        active = index == current and t < 10.1
        fill = blend(INK_2, TEAL, reached)
        outline = TEAL_SOFT if reached > 0 else LINE
        draw.ellipse((x - 15, 155, x + 15, 185), fill=fill, outline=outline, width=2)
        if reached > 0.95 and not active:
            check_mark(draw, (x, 170), WHITE)
        else:
            text(draw, (x, 170), number, F10, WHITE if active else MUTED, "mm")
        text(draw, (x, 197), label, F11 if index != current else F12B, WHITE if active else MUTED, "ma")

    # Lower cards.
    left_box = (34, 230, 344, 479)
    right_box = (362, 230, 926, 479)
    draw.rounded_rectangle(left_box, radius=16, fill=alpha_color(INK_2, 0.94), outline=LINE, width=1)
    draw.rounded_rectangle(right_box, radius=16, fill=alpha_color(INK_2, 0.94), outline=LINE, width=1)

    text(draw, (54, 250), "INPUT / 业务任务", F11, TEAL_SOFT)
    draw.line((54, 274, 324, 274), fill=LINE, width=1)
    fields = [
        ("来源", "海外站点 · 售后消息"),
        ("场景", "退货标签申请"),
        ("订单", "CN-26••••81"),
        ("商品", "SKU-7•••-WH"),
        ("安全", "演示字段 · 全部脱敏"),
    ]
    for i, (key, value) in enumerate(fields):
        y = 296 + i * 33
        text(draw, (54, y), key, F11, MUTED)
        text(draw, (112, y), value, F12B if i < 4 else F11, WHITE if i < 4 else TEAL_SOFT)

    text(draw, (384, 250), "RUN LOG / 执行记录", F11, TEAL_SOFT)
    text(draw, (894, 250), f"{int(overall * 100):02d}%", F12B, WHITE, "ra")
    draw.line((384, 274, 904, 274), fill=LINE, width=1)

    logs = [
        (1.0, "接收新任务", "消息内容已进入待处理队列"),
        (2.7, "解析关键字段", "意图、订单号与 SKU 已识别"),
        (4.5, "匹配业务规则", "责任人与处理路径已确认"),
        (6.4, "执行跨系统动作", "ERP 查询、标签生成与文件校验"),
        (8.4, "回写并通知", "状态同步至业务系统与协作平台"),
    ]
    for index, (start, title, detail) in enumerate(logs):
        y = 298 + index * 30
        appeared = fade(t, start, 0.32)
        active = index == current and t < 10.1
        dot = TEAL if appeared > 0.7 else LINE
        draw.ellipse((384, y - 5, 394, y + 5), fill=dot)
        if appeared > 0.96 and not active:
            check_mark(draw, (389, y), INK)
        text(draw, (407, y - 8), title, F12B, WHITE if appeared > 0.2 else MUTED)
        text(draw, (568, y - 7), detail, F11, MUTED if appeared > 0.2 else alpha_color(MUTED, 0.35))

    # A deliberate exception branch is visible throughout the run: this shows
    # the workflow is engineered, not merely a happy-path screen recording.
    branch_alpha = max(0.28, fade(t, 5.3, 0.5))
    draw.rounded_rectangle((384, 443, 904, 467), radius=6, fill=alpha_color("#0C2532", 0.8))
    draw.rectangle((384, 443, 388, 467), fill=AMBER)
    text(draw, (400, 455), "异常出口", F10, AMBER, "lm")
    text(draw, (466, 455), "无匹配 / 页面异常 → 留痕并转人工复核", F11, alpha_color(WHITE, branch_alpha), "lm")

    # Completion overlay at the end of the loop.
    completed = fade(t, 9.65, 0.6)
    if completed > 0:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay, "RGBA")
        od.rounded_rectangle((224, 180, 736, 412), radius=22, fill=alpha_color("#0A222F", 0.96 * completed), outline=alpha_color(TEAL, completed), width=2)
        od.ellipse((438, 215, 522, 299), fill=alpha_color(TEAL, completed))
        if completed > 0.65:
            check_mark(od, (480, 257), WHITE)
        text(od, (480, 325), "流程闭环完成", F31B, alpha_color(WHITE, completed), "ma")
        text(od, (480, 363), "可追踪 · 可恢复 · 可继续迭代", F14, alpha_color(TEAL_SOFT, completed), "ma")
        text(od, (480, 390), "RPA / 智能自动化工程实践", F11, alpha_color(MUTED, completed), "ma")
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(image, "RGBA")

    # Footer status line.
    draw.rectangle((0, 510, WIDTH, HEIGHT), fill=alpha_color("#0C2532", 0.96))
    text(draw, (34, 525), "WORKFLOW", F10, MUTED, "lm")
    text(draw, (106, 525), "读取 → 判断 → 执行 → 校验 → 回写 → 通知", F11, TEAL_SOFT, "lm")
    text(draw, (926, 525), "12 SEC", F10, MUTED, "rm")

    # One-second intro fade and the final half-second loop fade.
    intro = fade(t, 0.0, 0.55)
    outro = 1.0 - ease((t - 11.55) / 0.45)
    visibility = min(intro, outro)
    if visibility < 1:
        cover = Image.new("RGB", (WIDTH, HEIGHT), INK)
        image = Image.blend(cover, image, visibility)
    return image


def generate() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    container = av.open(str(VIDEO_PATH), mode="w", options={"movflags": "+faststart"})
    stream = container.add_stream("libx264", rate=FPS)
    stream.width = WIDTH
    stream.height = HEIGHT
    stream.pix_fmt = "yuv420p"
    stream.bit_rate = 1_150_000
    stream.options = {"preset": "medium", "crf": "26"}

    poster_saved = False
    for frame_index in range(FPS * DURATION):
        t = frame_index / FPS
        image = render_frame(t)
        if not poster_saved and t >= 6.9:
            image.save(POSTER_PATH, optimize=True)
            poster_saved = True
        video_frame = av.VideoFrame.from_image(image)
        for packet in stream.encode(video_frame):
            container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)
    container.close()

    print(f"Generated: {VIDEO_PATH} ({VIDEO_PATH.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"Generated: {POSTER_PATH} ({POSTER_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    generate()
