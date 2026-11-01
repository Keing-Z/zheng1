# -*- coding: utf-8 -*-
"""
csv_scraper 离线测试（零外部依赖）
运行：python test_scraper.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import csv_scraper as S

PASS = 0
FAIL = 0


def t(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  OK   {name}")
    except AssertionError as e:
        FAIL += 1
        print(f"  FAIL {name} :: {e}")
    except Exception as e:  # noqa: BLE001
        FAIL += 1
        print(f"  ERR  {name} :: {type(e).__name__}: {e}")


def eq(a, b, msg=""):
    assert a == b, f"{msg} 期望 {b!r}，实际 {a!r}"


SAMPLE = """
<html><body>
  <div class="list">
    <div class="item">
      <h2 class="title">Widget A</h2>
      <span class="price">$10</span>
      <a href="/product/a">detail</a>
    </div>
    <div class="item">
      <h2 class="title">Widget B</h2>
      <span class="price">$20</span>
      <a href="/product/b">detail</a>
    </div>
    <div class="item">
      <h2 class="title">Widget C</h2>
      <a href="/product/c">detail</a>
    </div>
  </div>
</body></html>
"""

print("【HTML 解析】")
t("能解析出元素树", lambda: eq(S.parse_html("<div><p>x</p></div>").children[0].tag, "div"))
t("文本正确提取", lambda: eq(S.parse_html("<h2>Widget A</h2>").children[0].text, "Widget A"))
t("空白被压缩", lambda: eq(S.parse_html("<h2>  A   B  </h2>").children[0].text, "A B"))
t("script 内容被忽略", lambda: eq(
    S.parse_html("<div><script>var a=1</script>ok</div>").children[0].text, "ok"))
t("嵌套文本拼接", lambda: eq(
    S.parse_html("<div><b>X</b> Y</div>").children[0].text, "X Y"))

print("【选择器】")
root = S.parse_html(SAMPLE)
t(".class 选择", lambda: eq(len(S.select(root, ".item")), 3))
t("tag 选择", lambda: eq(len(S.select(root, "h2")), 3))
t("后代组合：div.item h2", lambda: eq(len(S.select(root, "div.item h2")), 3))
t("复合：.item .price", lambda: eq(len(S.select(root, ".item .price")), 2))
t("找不到返回空", lambda: eq(len(S.select(root, ".nothing")), 0))
t("id 选择", lambda: eq(len(S.select(S.parse_html('<i id="z">1</i>'), "#z")), 1))
t("属性选择", lambda: eq(
    len(S.select(S.parse_html('<a data-k="1">x</a><a data-k="2">y</a>'), 'a[data-k="1"]')), 1))

print("【字段定义】")
t("name=selector", lambda: eq(S.parse_field("title=h2"), ("title", "h2", None)))
t("name=selector@attr", lambda: eq(S.parse_field("link=a@href"), ("link", "a", "href")))


def bad_format():
    try:
        S.parse_field("noequals")
    except ValueError:
        return
    raise AssertionError("应抛 ValueError")


t("格式错误抛异常", bad_format)

print("【提取行】")
fields = [S.parse_field("title=.title"), S.parse_field("price=.price"), S.parse_field("link=a@href")]
rows = S.extract_rows(SAMPLE, "div.item", fields, base_url="https://example.com/list")

t("提取 3 行", lambda: eq(len(rows), 3))
t("标题", lambda: eq(rows[0]["title"], "Widget A"))
t("价格", lambda: eq(rows[1]["price"], "$20"))
t("缺失字段为空串", lambda: eq(rows[2]["price"], ""))
t("相对链接补全", lambda: eq(rows[0]["link"], "https://example.com/product/a"))

print("【分页 URL】")
t("单页", lambda: eq(S.build_page_urls("https://a.com/x", 1), ["https://a.com/x"]))
t("无参数用 ?", lambda: eq(S.build_page_urls("https://a.com/x", 2)[1], "https://a.com/x?page=2"))
t("有参数用 &", lambda: eq(S.build_page_urls("https://a.com/x?q=1", 2)[1], "https://a.com/x?q=1&page=2"))

print("【边界】")
t("空页面不报错", lambda: eq(S.extract_rows("<html></html>", "div.item", fields), []))
t("行内无匹配字段不报错", lambda: eq(
    S.extract_rows("<div class='i'></div>", ".i", [S.parse_field("t=h2")])[0]["t"], ""))


def bad_selector():
    try:
        S.select(root, "div >")
    except ValueError:
        return
    raise AssertionError("应抛 ValueError")


t("非法选择器抛异常", bad_selector)

print(f"\n结果：通过 {PASS} 项，失败 {FAIL} 项")
sys.exit(1 if FAIL else 0)
