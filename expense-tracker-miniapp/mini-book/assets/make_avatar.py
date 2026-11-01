# -*- coding: utf-8 -*-
"""
生成记账小程序头像
设计：深靛紫渐变圆角底 + 白色账本 + 金色 ¥
无政治、色情等敏感元素，纯工具类图形。
"""
import os
import math
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))

# 画布放大 4 倍绘制，最后缩回目标尺寸（超采样抗锯齿）
SS = 4
SIZE = 144
CANVAS = SIZE * SS


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def gradient_background(size, top=(99, 91, 255), bottom=(124, 58, 237)):
    """竖向渐变"""
    img = Image.new("RGB", (1, size), top)
    px = img.load()
    for y in range(size):
        t = y / max(1, size - 1)
        px[0, y] = lerp(top, bottom, t)
    return img.resize((size, size), Image.NEAREST)


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def draw_icon(canvas, book_scale=1.0, mono=False):
    """在画布上画一本账本 + ¥ 符号。
    book_scale: 账本相对大小，便于做不同版本。
    mono: True 时画纯白（用于深色/浅色底变体）。
    """
    d = ImageDraw.Draw(canvas, "RGBA")
    S = canvas.size[0]

    # ---------- 账本主体 ----------
    # 尺寸参数（按 144 基准设计，乘以超采样）
    k = S / 144.0 * book_scale
    bw, bh = 74 * k, 88 * k            # 账本宽高
    cx, cy = S / 2, S / 2 + 2 * k      # 中心
    x0, y0 = cx - bw / 2, cy - bh / 2
    x1, y1 = cx + bw / 2, cy + bh / 2
    r = 12 * k

    # 账本阴影（柔和）
    sh_off = 3 * k
    d.rounded_rectangle(
        [x0 + sh_off, y0 + sh_off, x1 + sh_off, y1 + sh_off],
        radius=r, fill=(30, 20, 80, 60),
    )

    # 账本白底
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=(255, 255, 255, 255))

    # ---------- 顶部两条“账目线”（从 3 条减到 2 条，小尺寸更清爽） ----------
    # 注意：只放在钱币上方，避免被金色圆压住造成脏边
    line_h = 7 * k
    line_gap = 12 * k
    lx0 = x0 + 14 * k
    lx1_long = x1 - 14 * k
    ly = y0 + 13 * k
    for i, ratio in enumerate((0.8, 0.55)):
        ly_i = ly + i * line_gap
        w = (lx1_long - lx0) * ratio
        color = (99, 91, 255, 255) if i == 0 else (208, 211, 238, 255)
        if mono:
            color = (255, 255, 255, 255) if i == 0 else (255, 255, 255, 130)
        d.rounded_rectangle(
            [lx0, ly_i, lx0 + w, ly_i + line_h],
            radius=line_h / 2, fill=color,
        )

    # ---------- ¥ 符号 ----------
    my = y0 + bh * 0.655               # 钱币中心（下移，与线条分开）
    mcx = cx
    mr = 23 * k                        # 钱币半径

    # 金色圆底
    coin_fill = (255, 255, 255, 255) if mono else (255, 197, 61, 255)
    d.ellipse([mcx - mr, my - mr, mcx + mr, my + mr], fill=coin_fill)

    sym_color = (99, 91, 255, 255) if mono else (109, 40, 217, 255)
    lw = 5.4 * k

    def stroke(p, q, width=lw, color=sym_color):
        d.line([p, q], fill=color, width=int(round(width)))
        rad = width / 2
        for pt in (p, q):
            d.ellipse([pt[0] - rad, pt[1] - rad, pt[0] + rad, pt[1] + rad], fill=color)

    # 关键：把 V 和竖笔分开，横杠放在竖笔下段，且比 V 更窄
    v_top = my - mr * 0.66             # V 起笔高
    v_join = my - mr * 0.18            # V 汇合点
    v_spread = mr * 0.36               # V 半宽（收窄，给横杠留空间）
    stem_bot = my + mr * 0.62          # 竖笔底

    stroke((mcx - v_spread, v_top), (mcx, v_join))
    stroke((mcx + v_spread, v_top), (mcx, v_join))
    stroke((mcx, v_join), (mcx, stem_bot))

    # 两道横杠：位于竖笔下段，宽度小于 V 的口子
    bar_hw = mr * 0.34
    for by in (my + mr * 0.14, my + mr * 0.40):
        stroke((mcx - bar_hw, by), (mcx + bar_hw, by), width=lw * 0.88)


def build(on_gradient=True, mono=False):
    """生成一张完整图标"""
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    if on_gradient:
        bg = gradient_background(CANVAS)
        canvas.paste(bg, (0, 0), rounded_mask(CANVAS, int(CANVAS * 0.22)))
    draw_icon(canvas, book_scale=0.94 if on_gradient else 0.96, mono=mono)
    return canvas


def save(img, name, size=SIZE, quality=95):
    out = img.resize((size, size), Image.LANCZOS)
    path = os.path.join(OUT, name)
    out.save(path, format="PNG", optimize=True)
    kb = os.path.getsize(path) / 1024
    print(f"  {name:26s} {size}x{size}  {kb:6.1f} KB")
    return path


if __name__ == "__main__":
    print("生成头像：")
    main = build()

    # 主图标：144（微信建议尺寸）+ 512（高清备用）
    save(main, "avatar-144.png", 144)
    save(main, "avatar-512.png", 512)

    # 分类页/关于页用的大图
    save(main, "avatar-1024.png", 1024)

    # 预览图：带几种尺寸的对比
    print("完成。")
