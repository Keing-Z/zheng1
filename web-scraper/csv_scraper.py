#!/usr/bin/env python3
"""
csv_scraper.py — 网页列表页 → CSV 抓取工具（零依赖版）

特点：
· 只依赖 Python 标准库（urllib + html.parser），装都不用装
· 支持 CSS 简写选择器：tag、.class、#id、[attr=value] 以及空格后代组合
· 支持分页、自动重试、请求限速
· 把相对链接自动补成绝对链接

用法：
    python csv_scraper.py --url "https://example.com/list" \
        --row "div.item" \
        --field "title=h2" --field "price=.price" --field "link=a@href" \
        --out result.csv

    翻 3 页：
        --pages 3
    有权限要求的站点：
        --cookie "sessionid=xxx"
"""

import argparse
import csv
import re
import sys
import time
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ============================ 极简 DOM ============================
class Element:
    __slots__ = ("tag", "attrs", "children", "parent", "parts")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = parent
        # parts 按文档顺序保存文本片段和子元素，保证 <div>a<b>x</b>c</div> → "a x c"
        self.parts = []

    # --- 取文本：按文档顺序递归拼接，压缩空白 ---
    @property
    def text(self):
        out = []
        for p in self.parts:
            if isinstance(p, str):
                out.append(p)
            else:
                t = p.text
                if t:
                    out.append(t)
        return re.sub(r"\s+", " ", " ".join(out)).strip()

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    # --- 后代遍历 ---
    def iter(self):
        for c in self.children:
            yield c
            yield from c.iter()

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"


class DomBuilder(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}
    SKIP_TEXT_IN = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1]
        el = Element(tag.lower(), {k.lower(): (v or "") for k, v in attrs}, parent)
        parent.children.append(el)
        parent.parts.append(el)          # 保持文档顺序
        if tag.lower() not in self.VOID:
            self.stack.append(el)

    def handle_endtag(self, tag):
        tag = tag.lower()
        # 容错：向上找最近的同名标签再弹出
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not data.strip():
            return
        cur = self.stack[-1]
        if cur.tag in self.SKIP_TEXT_IN:
            return
        cur.parts.append(data)


def parse_html(html):
    b = DomBuilder()
    b.feed(html)
    b.close()
    return b.root


# ============================ 选择器 ============================
SIMPLE_RE = re.compile(
    r"^(?P<tag>[a-zA-Z][\w-]*|\*)?"
    r"(?P<id>#[\w-]+)?"
    r"(?P<cls>(?:\.[\w-]+)*)"
    r"(?P<attr>\[[\w-]+(?:[~^$*|]?=['\"]?[^\]'\"]*['\"]?)?\])?$"
)


def parse_compound(part):
    """解析单个复合选择器，如 div.item[data-x='1']"""
    m = SIMPLE_RE.match(part)
    if not m:
        raise ValueError(f"不支持的选择器：{part}")
    tag = m.group("tag")
    el_id = (m.group("id") or "")[1:] or None
    classes = [c for c in (m.group("cls") or "").split(".") if c]
    attr = m.group("attr")
    attr_name = attr_value = None
    if attr:
        inner = attr[1:-1]
        if "=" in inner:
            k, v = inner.split("=", 1)
            attr_name = k.strip()
            attr_value = v.strip().strip("'\"")
        else:
            attr_name = inner.strip()
    return {
        "tag": None if tag in (None, "*") else tag.lower(),
        "id": el_id,
        "classes": classes,
        "attr_name": attr_name,
        "attr_value": attr_value,
    }


def parse_selector(selector):
    """把 'div.item a' 解析成 [复合1, 复合2]（后代关系）"""
    parts = [p for p in selector.strip().split() if p]
    if not parts:
        raise ValueError("选择器为空")
    return [parse_compound(p) for p in parts]


def matches(el, comp):
    if comp["tag"] and el.tag != comp["tag"]:
        return False
    if comp["id"] and el.get("id") != comp["id"]:
        return False
    if comp["classes"]:
        el_classes = set((el.get("class") or "").split())
        if not all(c in el_classes for c in comp["classes"]):
            return False
    if comp["attr_name"]:
        if comp["attr_name"] not in el.attrs:
            return False
        if comp["attr_value"] is not None and el.attrs[comp["attr_name"]] != comp["attr_value"]:
            return False
    return True


def select(root, selector):
    """返回匹配元素的列表（支持后代组合，不支持 > + ~ 等）"""
    comps = parse_selector(selector)
    results = []

    def walk(node, idx):
        for child in node.children:
            if matches(child, comps[idx]):
                if idx == len(comps) - 1:
                    results.append(child)
                else:
                    walk(child, idx + 1)
            walk(child, idx)   # 中间元素也可能作为后续根继续匹配

    walk(root, 0)
    return results


# ============================ 抓取 ============================
def fetch(url, retries=3, delay=1.0, timeout=20, cookie=None):
    headers = dict(DEFAULT_HEADERS)
    if cookie:
        headers["Cookie"] = cookie

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                charset = resp.headers.get_content_charset() or "utf-8"
            try:
                return raw.decode(charset, errors="replace")
            except LookupError:
                return raw.decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < retries:
                wait = delay * attempt
                print(f"  请求失败（第 {attempt} 次）：{e}；{wait:.1f}s 后重试", file=sys.stderr)
                time.sleep(wait)
    raise RuntimeError(f"抓取失败：{url}（{last_err}）")


def parse_field(spec):
    """name=selector 或 name=selector@attr"""
    if "=" not in spec:
        raise ValueError(f"字段格式错误：{spec}（应为 name=selector[@attr]）")
    name, rest = spec.split("=", 1)
    attr = None
    if "@" in rest:
        rest, attr = rest.rsplit("@", 1)
    return name.strip(), rest.strip(), (attr.strip() if attr else None)


def extract_rows(html, row_selector, fields, base_url=""):
    root = parse_html(html)
    rows = select(root, row_selector)
    out = []
    for node in rows:
        record = {}
        for name, sel, attr in fields:
            hit = select(node, sel) if sel else [node]
            target = hit[0] if hit else None
            if target is None:
                record[name] = ""
                continue
            if attr:
                val = target.get(attr, "") or ""
                if attr in ("href", "src") and val and base_url:
                    val = urljoin(base_url, val)
            else:
                val = target.text
            record[name] = val
        out.append(record)
    return out


def build_page_urls(url, pages, page_param="page", start=1):
    if pages <= 1:
        return [url]
    sep = "&" if "?" in url else "?"
    return [f"{url}{sep}{page_param}={i}" for i in range(start, start + pages)]


def main():
    ap = argparse.ArgumentParser(description="网页列表页 → CSV 抓取工具（零依赖）")
    ap.add_argument("--url", required=True)
    ap.add_argument("--row", required=True, help="每行的选择器，如 div.item")
    ap.add_argument("--field", action="append", required=True,
                    help="name=selector[@attr]，可重复")
    ap.add_argument("--out", default="output.csv")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--page-param", default="page")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--cookie", default=None, help="需要登录时传入 Cookie 字符串")
    args = ap.parse_args()

    fields = [parse_field(f) for f in args.field]
    names = [f[0] for f in fields]

    all_rows = []
    urls = build_page_urls(args.url, args.pages, args.page_param)
    for idx, page_url in enumerate(urls, 1):
        print(f"抓取第 {idx}/{len(urls)} 页：{page_url}")
        html = fetch(page_url, cookie=args.cookie)
        rows = extract_rows(html, args.row, fields, base_url=args.url)
        print(f"  找到 {len(rows)} 条")
        all_rows.extend(rows)
        if idx < len(urls):
            time.sleep(args.delay)

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n完成：共 {len(all_rows)} 条，已保存到 {args.out}")


if __name__ == "__main__":
    main()
