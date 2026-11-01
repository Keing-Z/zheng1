# -*- coding: utf-8 -*-
"""校验头像文件是否符合微信后台上传规格"""
import os
from PIL import Image

ALLOWED = {"PNG", "BMP", "JPEG", "GIF"}
LIMIT_KB = 2 * 1024
RECOMMEND = (144, 144)

base = os.path.dirname(os.path.abspath(__file__))
files = ["avatar-144.png", "avatar-512.png", "avatar-1024.png"]

print("微信小程序头像规格校验")
print("-" * 58)
all_ok = True
for name in files:
    path = os.path.join(base, name)
    im = Image.open(path)
    kb = os.path.getsize(path) / 1024
    fmt_ok = im.format in ALLOWED
    size_ok = kb <= LIMIT_KB
    square = im.size[0] == im.size[1]
    ok = fmt_ok and size_ok and square
    all_ok &= ok
    status = "OK" if ok else "FAIL"
    print(f"{name:18s} {im.format:4s} {im.size[0]}x{im.size[1]:<5d} {kb:7.1f} KB   [{status}]")

print("-" * 58)
print(f"要求: 格式 png/bmp/jpeg/jpg/gif，≤2MB，建议 {RECOMMEND[0]}x{RECOMMEND[1]}")
print("结论:", "全部符合上传要求" if all_ok else "存在不符合项")
