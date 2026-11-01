# -*- coding: utf-8 -*-
"""生成 Chrome 扩展图标：深紫圆角 + 白色方框对准符号（“采集”的意象）"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
SS = 8
BASE = 128


def draw(size):
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角底
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=(79, 70, 229, 255))

    # 白色取景框（四角括号）
    pad = S * 0.24
    L = S * 0.16          # 角臂长
    w = max(2, int(S * 0.055))
    x0, y0, x1, y1 = pad, pad, S - pad, S - pad
    # 左上
    d.line([(x0, y0 + L), (x0, y0), (x0 + L, y0)], fill="white", width=w, joint="curve")
    # 右上
    d.line([(x1 - L, y0), (x1, y0), (x1, y0 + L)], fill="white", width=w, joint="curve")
    # 左下
    d.line([(x0, y1 - L), (x0, y1), (x0 + L, y1)], fill="white", width=w, joint="curve")
    # 右下
    d.line([(x1 - L, y1), (x1, y1), (x1, y1 - L)], fill="white", width=w, joint="curve")

    # 中心圆点
    r = S * 0.09
    cx = cy = S / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white")

    return img.resize((size, size), Image.LANCZOS)


for s in (16, 48, 128):
    p = os.path.join(OUT, f"icon{s}.png")
    draw(s).save(p, "PNG", optimize=True)
    print(f"  icons/icon{s}.png  {os.path.getsize(p)} B")
