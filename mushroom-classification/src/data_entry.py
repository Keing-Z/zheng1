#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蘑菇数据录入工具
支持逐条录入蘑菇特征数据，保存为 CSV 格式
"""

import csv
import os

# 特征定义：(英文列名, 中文说明, {选项: 中文描述})
FEATURES = [
    ("类别", "类别", {
        "可食用": "可食用",
        "有毒": "有毒"
    }),
    ("cap-shape", "菌盖形状", {
        "b": "钟形(bell)",
        "c": "圆锥形(conical)",
        "f": "平坦(flat)",
        "k": "凸出(knobbed)",
        "s": "凹陷(sunken)",
        "x": "凸形(convex)"
    }),
    ("cap-surface", "菌盖表面", {
        "f": "纤维状(fibrous)",
        "g": "凹槽状(grooves)",
        "s": "光滑(smooth)",
        "y": "鳞片状(scaly)"
    }),
    ("cap-color", "菌盖颜色", {
        "b": "棕色(brown)",
        "c": "肉桂色(cinnamon)",
        "e": "红色(red)",
        "g": "灰色(gray)",
        "n": "棕色(brown)",
        "p": "粉色(pink)",
        "r": "绿色(green)",
        "u": "紫色(purple)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("bruises", "是否有瘀伤", {
        "t": "有瘀伤(bruises)",
        "f": "无瘀伤(no bruises)"
    }),
    ("odor", "气味", {
        "a": "杏仁味(almond)",
        "c": "杂酚油味(creosote)",
        "f": "恶臭(foul)",
        "l": "茴香味(anise)",
        "m": "霉味(musty)",
        "n": "无味(none)",
        "p": "刺鼻味(pungent)",
        "s": "辛辣味(spicy)",
        "y": "鱼腥味(fishy)"
    }),
    ("gill-attachment", "菌褶附着方式", {
        "a": "贴生(attached)",
        "d": "下垂(descending)",
        "f": "自由(free)",
        "n": "有缺口(notched)"
    }),
    ("gill-spacing", "菌褶间距", {
        "c": "紧密(close)",
        "w": "拥挤(crowded)",
        "d": "疏远(distant)"
    }),
    ("gill-size", "菌褶大小", {
        "b": "宽(broad)",
        "n": "窄(narrow)"
    }),
    ("gill-color", "菌褶颜色", {
        "b": "棕色(brown)",
        "e": "红色(red)",
        "g": "灰色(gray)",
        "h": "巧克力色(chocolate)",
        "k": "黑色(black)",
        "n": "棕色(brown)",
        "o": "橙色(orange)",
        "p": "粉色(pink)",
        "r": "绿色(green)",
        "u": "紫色(purple)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("stalk-shape", "菌柄形状", {
        "e": "变细(enlarging)",
        "t": "变细(tapering)"
    }),
    ("stalk-root", "菌柄根部", {
        "b": "球形(bulbous)",
        "c": "棒形(club)",
        "e": "等宽(equal)",
        "r": "根状(rhizomorphs)",
        "u": "未知(unknown)",
        "z": "根状(rooted)",
        "?": "缺失(missing)"
    }),
    ("stalk-surface-above-ring", "菌柄表面(环上)", {
        "f": "纤维状(fibrous)",
        "k": "鳞片状(silky)",
        "s": "光滑(smooth)",
        "y": "鳞片状(scaly)"
    }),
    ("stalk-surface-below-ring", "菌柄表面(环下)", {
        "f": "纤维状(fibrous)",
        "k": "鳞片状(silky)",
        "s": "光滑(smooth)",
        "y": "鳞片状(scaly)"
    }),
    ("stalk-color-above-ring", "菌柄颜色(环上)", {
        "b": "棕色(brown)",
        "c": "肉桂色(cinnamon)",
        "e": "红色(red)",
        "g": "灰色(gray)",
        "n": "棕色(brown)",
        "o": "橙色(orange)",
        "p": "粉色(pink)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("stalk-color-below-ring", "菌柄颜色(环下)", {
        "b": "棕色(brown)",
        "c": "肉桂色(cinnamon)",
        "e": "红色(red)",
        "g": "灰色(gray)",
        "n": "棕色(brown)",
        "o": "橙色(orange)",
        "p": "粉色(pink)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("veil-type", "菌幕类型", {
        "p": "部分(partial)",
        "u": "通用(universal)"
    }),
    ("veil-color", "菌幕颜色", {
        "n": "棕色(brown)",
        "o": "橙色(orange)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("ring-number", "菌环数量", {
        "n": "无(none)",
        "o": "一个(one)",
        "t": "两个(two)"
    }),
    ("ring-type", "菌环类型", {
        "e": "消失(evanescent)",
        "f": "火焰形(flaring)",
        "l": "大型(large)",
        "n": "无(none)",
        "p": "垂落(pendant)",
        "s": "鞘形(sheathing)",
        "z": "有毛(zone)"
    }),
    ("spore-print-color", "孢子印颜色", {
        "b": "棕色(brown)",
        "h": "巧克力色(chocolate)",
        "k": "黑色(black)",
        "n": "棕色(brown)",
        "o": "橙色(orange)",
        "r": "绿色(green)",
        "u": "紫色(purple)",
        "w": "白色(white)",
        "y": "黄色(yellow)"
    }),
    ("population", "种群分布", {
        "a": "丰富(abundant)",
        "c": "聚集群(clustered)",
        "n": "众多(numerous)",
        "s": "分散(scattered)",
        "v": "几个(several)",
        "y": "独居(solitary)"
    }),
    ("habitat", "栖息地", {
        "g": "草地(grasses)",
        "l": "叶子(leaves)",
        "m": "草地(meadows)",
        "p": "小路(paths)",
        "u": "城市(urban)",
        "w": "废物(waste)",
        "d": "树林(woods)"
    })
]

CSV_FILE = "mushroom_data.csv"


def get_column_names():
    return [f[0] for f in FEATURES]


def show_menu(feature_name, feature_desc, options):
    """显示选项菜单，返回用户选择的代码"""
    print(f"\n{'─' * 50}")
    print(f"  {feature_name}: {feature_desc}")
    print(f"{'─' * 50}")
    keys = list(options.keys())
    for i, key in enumerate(keys, 1):
        print(f"  {i}. {key} - {options[key]}")
    print(f"{'─' * 50}")

    while True:
        raw = input(f"  请输入选项编号 (1-{len(keys)}) 或直接输入代码: ").strip()
        # 输入数字
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        # 直接输入代码
        if raw.lower() in options:
            return raw.lower()
        print(f"  [错误] 无效输入，请重试")


def load_existing_data():
    """加载已有数据，返回行数"""
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        # 减去表头
        return max(0, len(rows) - 1)


def ensure_csv_header():
    """确保 CSV 文件有表头"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(get_column_names())
        print(f"[新建文件] {CSV_FILE}")
    else:
        print(f"[追加模式] 已有 {load_existing_data()} 条记录")


def enter_one_record(record_num):
    """录入一条记录"""
    print(f"\n{'=' * 50}")
    print(f"  开始录入第 {record_num} 条数据")
    print(f"{'=' * 50}")

    values = []
    for col_name, desc, options in FEATURES:
        value = show_menu(col_name, desc, options)
        values.append(value)
        # 显示已选摘要
        selected_desc = options.get(value, value)
        print(f"  -> 已选: {value} ({selected_desc})")

    return values


def confirm_record(values):
    """确认录入的记录"""
    print(f"\n{'=' * 50}")
    print("  请确认录入数据:")
    print(f"{'=' * 50}")
    for i, (col_name, desc, options) in enumerate(FEATURES):
        code = values[i]
        label = options.get(code, code)
        print(f"  {desc}: {code} ({label})")
    print(f"{'=' * 50}")

    while True:
        choice = input("  确认保存? (y=保存 / n=重新录入 / q=放弃): ").strip().lower()
        if choice in ("y", "n", "q"):
            return choice
        print("  请输入 y/n/q")


def save_record(values):
    """保存一条记录到 CSV"""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(values)
    print(f"  [已保存] 记录已写入 {CSV_FILE}")


def main():
    print()
    print("=" * 50)
    print("  蘑菇数据录入工具")
    print("  按提示逐项选择特征值，录入纸质数据")
    print("=" * 50)

    ensure_csv_header()

    count = 0
    while True:
        record_num = load_existing_data() + 1
        values = enter_one_record(record_num)
        result = confirm_record(values)

        if result == "y":
            save_record(values)
            count += 1
            total = load_existing_data()
            print(f"\n  本次已录入 {count} 条，文件中共 {total} 条记录")
        elif result == "n":
            print("\n  [重新录入] 请重新填写...")
            continue
        else:
            print("\n  [已放弃] 本条记录未保存")

        cont = input("\n  继续录入下一条? (y/n): ").strip().lower()
        if cont != "y":
            break

    total = load_existing_data()
    print(f"\n{'=' * 50}")
    print(f"  录入结束！本次录入 {count} 条，文件中共 {total} 条记录")
    print(f"  数据已保存到: {os.path.abspath(CSV_FILE)}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
