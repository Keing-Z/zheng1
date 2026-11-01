# -*- coding: utf-8 -*-
"""生成个人简历（DOCX），用于 TalentsAI 资质申请上传（平台支持 DOC/DOCX/PDF）。"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(OUT, "resume.docx")

INK = RGBColor(0x1F, 0x23, 0x33)
MUTED = RGBColor(0x5B, 0x61, 0x78)
ACCENT = RGBColor(0x4F, 0x46, 0xE5)

doc = Document()

# ---- 页面与默认字体 ----
sec = doc.sections[0]
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(2.0)
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.8)

style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10)
style.font.color.rgb = INK
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
style.paragraph_format.space_after = Pt(2)
style.paragraph_format.line_spacing = 1.25


def para(text="", size=10, bold=False, color=INK, space_before=0, space_after=2,
         align=None, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    r.font.color.rgb = color
    r.font.name = "微软雅黑"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    return p


def rich(parts, size=9.5, indent=0, space_after=2, space_before=0):
    """parts: [(text, bold, color), ...]"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.3
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    for text, bold, color in parts:
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        r.font.color.rgb = color
        r.font.name = "微软雅黑"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    return p


def bullet(text, size=9.5):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.55)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run("· " + text)
    r.font.size = Pt(size)
    r.font.color.rgb = INK
    r.font.name = "微软雅黑"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    return p


def section_title(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = "微软雅黑"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    # 下边框
    pPr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "D9DCE8")
    borders.append(bottom)
    pPr.append(borders)


# ================= 头部 =================
para("Keing", size=22, bold=True, space_after=2)
para("数据科学与大数据技术 · 本科在读 · 专业排名前 20%", size=10.5, color=MUTED, space_after=2)
para("福建农林大学　|　邮箱：2776599149@qq.com　|　GitHub：github.com/Keing-Z",
     size=9, color=MUTED, space_after=4)

# ================= 教育背景 =================
section_title("教育背景")
rich([("福建农林大学", True, INK),
      ("　·　数据科学与大数据技术　·　学士　·　2025.09 – 2029.06（在读）", False, INK)], size=10)
bullet("专业排名前 20%")
bullet("核心课程：数据结构与算法、数据库原理、Python 程序设计、机器学习基础、统计学")

# ================= 专业技能 =================
section_title("专业技能")
rich([("编程语言　", True, INK), ("Python、JavaScript、HTML/CSS、SQL", False, INK)], indent=0.3)
rich([("数据科学　", True, INK),
      ("pandas、NumPy、scikit-learn、Matplotlib、Seaborn；特征工程与模型评估", False, INK)], indent=0.3)
rich([("前端与工具　", True, INK),
      ("原生 JavaScript、WeChat 小程序、Chrome 扩展开发、Chart.js", False, INK)], indent=0.3)
rich([("工程实践　", True, INK),
      ("Git、单元测试与集成测试、技术文档撰写（中英文）", False, INK)], indent=0.3)

# ================= 项目经历 =================
section_title("项目经历")

rich([("蘑菇毒性分类 · 机器学习全流程分析", True, INK), ("　|　个人项目", False, MUTED)],
     size=10, space_after=1)
bullet("基于 UCI Mushroom 数据集（8124 条样本、22 个分类特征）完成数据清洗、探索性分析、"
       "特征工程到模型评估的完整流程")
bullet("在统一预处理下对比 Logistic Regression、Random Forest、Gradient Boosting、SVM、KNN、"
       "Decision Tree 六种模型，以 5 折交叉验证评估稳定性")
bullet("以随机森林重要性、卡方检验、互信息三种独立方法交叉验证特征贡献，结论一致指向 odor "
       "为决定性特征（互信息 = 1.0）；据此解释树模型普遍达到 100% 准确率的成因在于数据集"
       "本身的易分性，而非模型优劣")
bullet("产出 11 张可视化图表、完整分析报告与基于 Chart.js 的交互式数据看板")

rich([("笨蛋记账 · 离线优先微信小程序", True, INK), ("　|　个人项目", False, MUTED)],
     size=10, space_before=4, space_after=1)
bullet("以“记一笔不超过 3 秒”为唯一设计约束：自绘数字键盘替代系统输入法，保存后自动清空"
       "以支持连续记账，备注字段设为可选")
bullet("金额以整数分存储规避浮点误差；日期使用本地时区构造规避 UTC 偏移；统计环形图以 "
       "CSS conic-gradient 实现，减少约 30 KB 运行时依赖")
bullet("建立单元、集成、静态三层自动化测试共 82 项断言，并据此发现并修复 3 个真实缺陷："
       "CSV 导出丢列、HTML 文本提取顺序反转、备份恢复导致数据翻倍")

rich([("零依赖网页数据采集工具", True, INK), ("　|　个人项目", False, MUTED)],
     size=10, space_before=4, space_after=1)
bullet("仅使用 Python 标准库（urllib + html.parser）实现完整采集链路，解决客户环境中"
       "第三方依赖无法安装导致脚本无法运行的问题")
bullet("自实现轻量 DOM 树与 CSS 选择器子集，支持分页、指数退避重试、请求限速，"
       "输出带 UTF-8 BOM 的 CSV 以保证 Excel 直接打开不乱码")
bullet("26 项离线单元测试全部通过，另完成端到端实跑验证")

rich([("Quick Capture · Chrome 浏览器扩展", True, INK), ("　|　个人项目", False, MUTED)],
     size=10, space_before=4, space_after=1)
bullet("一键采集当前网页的结构化数据，支持导出为文本 / JSON / CSV 三种格式")
bullet("将采集逻辑与浏览器 API 分层解耦，使核心逻辑无需启动浏览器即可在 Node 环境中单元测试")
bullet("按最小权限原则仅申请 activeTab、scripting、clipboardWrite、storage 四项权限，"
       "不申请任何网络权限")

# ================= 语言与其他 =================
section_title("语言与其他")
rich([("中文　", True, INK), ("母语　　　", False, INK),
      ("英语　", True, INK), ("可流畅阅读技术文档，具备英文项目说明与技术文档撰写能力", False, INK)],
     indent=0.3)

# ================= 说明 =================
section_title("补充说明")
para("项目源代码与详细文档见 GitHub 仓库：github.com/Keing-Z/zheng1。各项目 README 均完整记录了设计取舍、"
     "技术权衡与已知限制。", size=9, color=MUTED)

doc.save(DOCX)
print(f"已生成：{DOCX}  ({os.path.getsize(DOCX) / 1024:.1f} KB)")
