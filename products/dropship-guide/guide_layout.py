#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「위탁판매 시작 체크리스트 가이드」 레이아웃 엔진.

파일 구성
  guide_layout.py  이 파일. 폰트·색·스타일·조판 헬퍼·문서 템플릿.
  content.py       본문 텍스트와 표 데이터.
  build_pdf.py     실행 진입점. `python3 build_pdf.py`

설계 규칙
- 한글 폰트는 NanumGothic / NanumGothicBold 를 PDF에 임베드합니다(서브셋).
- 체크박스는 문자(U+2610, U+25A1)를 쓰지 않고 벡터 사각형으로 그립니다.
  → 추출 텍스트에 사각형 문자가 하나도 없어야 정상이므로, 두부(글리프 누락) 검사가 명확해집니다.
- 글머리 기호도 한글 폰트로 그립니다(bulletFontName). 기본값인 Helvetica 로 그리면
  본문과 서체가 섞이고, 한글 글머리를 쓸 때 글리프가 빠집니다.
- 목차 페이지 번호는 multiBuild 2패스로 실제 페이지에서 채워집니다(수기 입력 없음).
- 장·절 마커(ChapterTitle)는 목차 항목, PDF 북마크, 러닝 헤더를 한 번에 만듭니다.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 폰트 등록

FONT_DIR = "/usr/share/fonts/truetype/nanum"
FONT_REGULAR = os.path.join(FONT_DIR, "NanumGothic.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "NanumGothicBold.ttf")

for _p in (FONT_REGULAR, FONT_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(
            "한글 폰트를 찾지 못했습니다: %s\n"
            "  해결: apt-get install -y fonts-nanum" % _p
        )

pdfmetrics.registerFont(TTFont("Nanum", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("Nanum-Bold", FONT_BOLD))
pdfmetrics.registerFontFamily(
    "Nanum", normal="Nanum", bold="Nanum-Bold", italic="Nanum", boldItalic="Nanum-Bold"
)

BODY = "Nanum"
BOLD = "Nanum-Bold"

# ------------------------------------------------ 글리프 누락 가드 (중요)
#
# 폰트에 없는 글자는 오류 없이 '빈칸'으로 조판됩니다. 눈으로 보기 전에는 알 수 없고,
# 텍스트 추출에서도 잡히지 않습니다. (실제로 U+2212 MINUS SIGN 이 NanumGothic 에
# 없어서 계산식의 빼기 기호가 통째로 사라진 적이 있습니다. ASCII '-' 로 교체함.)
# 그래서 조판 헬퍼를 통과하는 모든 문자열을 두 서체의 cmap 교집합과 대조합니다.

from reportlab.pdfbase.ttfonts import TTFontFile  # noqa: E402
import re as _re  # noqa: E402

_CMAP = (set(TTFontFile(FONT_REGULAR).charToGlyph)
         & set(TTFontFile(FONT_BOLD).charToGlyph))
_TAG_RE = _re.compile(r"<[^>]*>")
_ENT_RE = _re.compile(r"&[a-zA-Z]+;|&#\d+;")
_glyph_checked = set()


def assert_glyphs(text):
    """두 서체 모두에 글리프가 있는지 확인. 없으면 빌드를 중단합니다."""
    if not isinstance(text, str) or text in _glyph_checked:
        return text
    plain = _ENT_RE.sub(" ", _TAG_RE.sub("", text))
    bad = sorted({c for c in plain if ord(c) > 31 and ord(c) not in _CMAP})
    if bad:
        raise ValueError(
            "폰트에 없는 문자가 있어 빈칸으로 조판됩니다: %s\n  문자열: %.80s" % (
                ", ".join("U+%04X %r" % (ord(c), c) for c in bad), text)
        )
    _glyph_checked.add(text)
    return text

# ---------------------------------------------------------------- 색 / 치수

INK = colors.HexColor("#1A1A1A")
INK_SOFT = colors.HexColor("#4A4A4A")
NAVY = colors.HexColor("#1F4E79")
NAVY_LIGHT = colors.HexColor("#2E6DA4")
RULE = colors.HexColor("#C6D2DE")
RULE_SOFT = colors.HexColor("#DEE5EC")
ZEBRA = colors.HexColor("#F3F7FA")
BOXBG = colors.HexColor("#F5F7F9")
WARN_BG = colors.HexColor("#FBF6EC")
WARN_LINE = colors.HexColor("#D8C08A")

PAGE_W, PAGE_H = A4
M_LEFT = 21 * mm
M_RIGHT = 21 * mm
M_TOP = 24 * mm
M_BOTTOM = 20 * mm
CONTENT_W = PAGE_W - M_LEFT - M_RIGHT  # 168mm

# ---------------------------------------------------------------- 스타일

S = {}

S["cover_kicker"] = ParagraphStyle(
    "cover_kicker", fontName=BOLD, fontSize=11, leading=18, textColor=NAVY_LIGHT,
    alignment=TA_CENTER, spaceAfter=0,
)
S["cover_title"] = ParagraphStyle(
    "cover_title", fontName=BOLD, fontSize=30, leading=44, textColor=NAVY,
    alignment=TA_CENTER,
)
S["cover_sub"] = ParagraphStyle(
    "cover_sub", fontName=BODY, fontSize=13.5, leading=24, textColor=INK_SOFT,
    alignment=TA_CENTER,
)
S["cover_meta"] = ParagraphStyle(
    "cover_meta", fontName=BODY, fontSize=9.5, leading=16, textColor=INK_SOFT,
    alignment=TA_CENTER,
)
S["cover_note"] = ParagraphStyle(
    "cover_note", fontName=BODY, fontSize=8.6, leading=14.5, textColor=INK_SOFT,
    alignment=TA_CENTER,
)

S["h1_num"] = ParagraphStyle(
    "h1_num", fontName=BOLD, fontSize=10, leading=14, textColor=NAVY_LIGHT,
    spaceAfter=2,
)
S["h1"] = ParagraphStyle(
    "h1", fontName=BOLD, fontSize=20, leading=29, textColor=NAVY,
    spaceBefore=0, spaceAfter=4,
)
S["h1_lead"] = ParagraphStyle(
    "h1_lead", fontName=BODY, fontSize=10, leading=17, textColor=INK_SOFT,
    spaceBefore=2, spaceAfter=0,
)
S["h2"] = ParagraphStyle(
    "h2", fontName=BOLD, fontSize=12.6, leading=19, textColor=NAVY,
    spaceBefore=11.5, spaceAfter=4.5, keepWithNext=1,
)
S["h3"] = ParagraphStyle(
    "h3", fontName=BOLD, fontSize=10.6, leading=16.5, textColor=INK,
    spaceBefore=9, spaceAfter=3, keepWithNext=1,
)
# 부록 A(인쇄용 1쪽)처럼 한 쪽에 맞춰야 하는 곳에서 쓰는 촘촘한 소제목
S["h3t"] = ParagraphStyle(
    "h3t", parent=S["h3"], fontSize=10.2, leading=14.5,
    spaceBefore=6, spaceAfter=2,
)
S["p"] = ParagraphStyle(
    "p", fontName=BODY, fontSize=10, leading=17.2, textColor=INK,
    alignment=TA_JUSTIFY, spaceAfter=5.5, wordWrap="CJK",
    # 글머리 기호도 한글 폰트로 그려야 기본 Helvetica 가 섞이지 않습니다.
    bulletFontName=BODY, bulletFontSize=10, bulletColor=NAVY_LIGHT,
)
S["p_tight"] = ParagraphStyle("p_tight", parent=S["p"], spaceAfter=2)
S["bullet"] = ParagraphStyle(
    "bullet", parent=S["p"], leftIndent=9.5 * mm, bulletIndent=4.5 * mm,
    spaceAfter=2.8, alignment=TA_LEFT,
)
S["num"] = ParagraphStyle(
    "num", parent=S["p"], leftIndent=10.5 * mm, bulletIndent=4.0 * mm,
    spaceAfter=2.8, alignment=TA_LEFT,
    bulletFontName=BOLD, bulletFontSize=9.4, bulletColor=NAVY,
)
S["cell"] = ParagraphStyle(
    "cell", fontName=BODY, fontSize=8.9, leading=13.6, textColor=INK,
    alignment=TA_LEFT, wordWrap="CJK",
)
S["cell_b"] = ParagraphStyle("cell_b", parent=S["cell"], fontName=BOLD)
S["cell_c"] = ParagraphStyle("cell_c", parent=S["cell"], alignment=TA_CENTER)
S["cell_r"] = ParagraphStyle("cell_r", parent=S["cell"], alignment=TA_RIGHT)
S["cell_h"] = ParagraphStyle(
    "cell_h", fontName=BOLD, fontSize=8.9, leading=13.2, textColor=colors.white,
    alignment=TA_LEFT, wordWrap="CJK",
)
S["cell_hc"] = ParagraphStyle("cell_hc", parent=S["cell_h"], alignment=TA_CENTER)
S["caption"] = ParagraphStyle(
    "caption", fontName=BOLD, fontSize=9.2, leading=14, textColor=NAVY,
    spaceBefore=6, spaceAfter=3.5, keepWithNext=1,
)
S["tnote"] = ParagraphStyle(
    "tnote", fontName=BODY, fontSize=8.3, leading=13, textColor=INK_SOFT,
    spaceBefore=3, spaceAfter=7, wordWrap="CJK",
)
S["box"] = ParagraphStyle(
    "box", fontName=BODY, fontSize=9.3, leading=15.6, textColor=INK,
    alignment=TA_LEFT, wordWrap="CJK",
)
S["box_b"] = ParagraphStyle("box_b", parent=S["box"], fontName=BOLD, textColor=NAVY)
S["formula"] = ParagraphStyle(
    "formula", fontName=BOLD, fontSize=10.6, leading=18, textColor=NAVY,
    alignment=TA_CENTER, wordWrap="CJK",
)
S["check"] = ParagraphStyle(
    "check", fontName=BODY, fontSize=9.5, leading=15, textColor=INK,
    alignment=TA_LEFT, wordWrap="CJK",
)
S["check_sm"] = ParagraphStyle("check_sm", parent=S["check"], fontSize=8.8, leading=13.4)
S["tpl"] = ParagraphStyle(
    "tpl", fontName=BODY, fontSize=9.1, leading=15.4, textColor=INK,
    alignment=TA_LEFT, wordWrap="CJK",
)
S["toc_head"] = ParagraphStyle(
    "toc_head", fontName=BOLD, fontSize=17, leading=26, textColor=NAVY, spaceAfter=10,
)
S["toc0"] = ParagraphStyle(
    "toc0", fontName=BOLD, fontSize=10.4, leading=21, textColor=INK,
)
S["toc1"] = ParagraphStyle(
    "toc1", fontName=BODY, fontSize=9.3, leading=17, textColor=INK_SOFT,
    leftIndent=7 * mm,
)


# ---------------------------------------------------------------- 벡터 도형

class CheckBox(Flowable):
    """문자가 아닌 벡터로 그리는 체크박스."""

    def __init__(self, size=3.3 * mm, line=0.7, color=NAVY_LIGHT):
        Flowable.__init__(self)
        self.size = size
        self.line = line
        self.color = color
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.line)
        c.setLineJoin(0)
        c.rect(0, 0, self.size, self.size, stroke=1, fill=0)
        c.restoreState()


class CenteredRule(Flowable):
    """가운데 정렬 본문 폭 안에서 가운데에 놓이는 짧은 구분선(표지용)."""

    def __init__(self, rule_width, thickness=1.2, color=None, full_width=None):
        Flowable.__init__(self)
        self.rule_width = rule_width
        self.thickness = thickness
        self.color = color or NAVY
        self.width = full_width or CONTENT_W
        self.height = thickness

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        x0 = (self.width - self.rule_width) / 2.0
        c.line(x0, 0, x0 + self.rule_width, 0)
        c.restoreState()


class HRule(Flowable):
    def __init__(self, width, thickness=0.6, color=RULE, space_before=0, space_after=0):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.height = thickness + space_before + space_after
        self._sa = space_after

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        y = self._sa + self.thickness / 2.0
        c.line(0, y, self.width, y)
        c.restoreState()


# ---------------------------------------------------------------- 조판 헬퍼

def P(text, style="p"):
    return Paragraph(assert_glyphs(text), S[style])


def BUL(items, style="bullet"):
    out = []
    for t in items:
        out.append(Paragraph(assert_glyphs(t), S[style], bulletText="·"))
    return out


def NUM(items, style="num"):
    out = []
    for i, t in enumerate(items, 1):
        out.append(Paragraph(assert_glyphs(t), S[style], bulletText="%d." % i))
    return out


def _mk_cell(v, style):
    if isinstance(v, Flowable):
        return v
    return Paragraph(assert_glyphs(str(v)), S[style])


def TBL(header, rows, widths, aligns=None, caption=None, note=None,
        zebra=True, font_size=None, head_align=None, pad=None, gap=7):
    """머리글 + 본문 표. widths 는 mm 비율이 아니라 절대값(포인트) 리스트.

    pad : 셀 상하 여백(기본 4.0/4.2). 한 쪽에 맞춰야 할 때 줄입니다.
    gap : 표 뒤 여백.
    """
    cell_style = "cell"
    if font_size:
        key = "cell_%s" % str(font_size).replace(".", "_")
        if key not in S:
            S[key] = ParagraphStyle(key, parent=S["cell"], fontSize=font_size,
                                    leading=font_size * 1.52)
            S[key + "c"] = ParagraphStyle(key + "c", parent=S[key], alignment=TA_CENTER)
            S[key + "r"] = ParagraphStyle(key + "r", parent=S[key], alignment=TA_RIGHT)
            S[key + "b"] = ParagraphStyle(key + "b", parent=S[key], fontName=BOLD)
        cell_style = key

    aligns = aligns or ["l"] * len(widths)
    head_align = head_align or aligns

    def st(a, base):
        if a == "c":
            return base + "c" if base != "cell" else "cell_c"
        if a == "r":
            return base + "r" if base != "cell" else "cell_r"
        if a == "b":
            return base + "b" if base != "cell" else "cell_b"
        return base

    data = []
    if header:
        data.append([
            _mk_cell(h, "cell_hc" if head_align[i] == "c" else "cell_h")
            for i, h in enumerate(header)
        ])
    for r in rows:
        data.append([_mk_cell(v, st(aligns[i], cell_style)) for i, v in enumerate(r)])

    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4 if pad is None else pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.6 if pad is None else pad),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("LINEBELOW", (0, 0), (-1, 0), 0.7, NAVY),
            ("TOPPADDING", (0, 0), (-1, 0), 5.0),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5.2),
        ]
        if zebra:
            for i in range(2, len(data), 2):
                cmds.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    else:
        if zebra:
            for i in range(1, len(data), 2):
                cmds.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(cmds))

    out = []
    if caption:
        out.append(P(caption, "caption"))
    out.append(t)
    if note:
        out.append(P(note, "tnote"))
    elif gap:
        out.append(Spacer(1, gap))
    return out


def CHECKLIST(items, style="check", col_gap=3.0 * mm, box=3.3 * mm, two_col=False,
              width=None, row_pad=2.6, gap=5):
    """체크박스 + 문구. two_col=True 면 2단으로 배치합니다."""
    width = width or CONTENT_W

    def one(col_w, its, sty):
        data = []
        for t in its:
            data.append([CheckBox(size=box), Paragraph(assert_glyphs(t), S[sty])])
        tb = Table(data, colWidths=[box + col_gap, col_w - box - col_gap], hAlign="LEFT")
        tb.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 1.5),
            ("RIGHTPADDING", (0, 0), (0, -1), 0),
            ("LEFTPADDING", (1, 0), (1, -1), 0),
            ("RIGHTPADDING", (1, 0), (1, -1), 2),
            ("TOPPADDING", (0, 0), (0, -1), 2.6),
            ("TOPPADDING", (1, 0), (1, -1), 1.0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), row_pad),
        ]))
        return tb

    if not two_col:
        return [one(width, items, style), Spacer(1, gap)]

    half = (len(items) + 1) // 2
    left, right = items[:half], items[half:]
    col_w = (width - 6 * mm) / 2.0
    outer = Table(
        [[one(col_w, left, style), one(col_w, right, style)]],
        colWidths=[col_w, col_w + 6 * mm], hAlign="LEFT",
    )
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 6 * mm),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [outer, Spacer(1, gap)]


def BOXNOTE(title, lines, kind="info", width=None):
    """회색(info) 또는 베이지(warn) 박스."""
    width = width or CONTENT_W
    bg = BOXBG if kind == "info" else WARN_BG
    edge = RULE if kind == "info" else WARN_LINE
    inner = []
    if title:
        inner.append([Paragraph(assert_glyphs(title), S["box_b"])])
    for ln in lines:
        inner.append([Paragraph(assert_glyphs(ln), S["box"])])
    it = Table(inner, colWidths=[width - 13 * mm], hAlign="LEFT")
    it.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    outer = Table([[it]], colWidths=[width], hAlign="LEFT")
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, edge),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, NAVY_LIGHT if kind == "info" else WARN_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
    ]))
    return [outer, Spacer(1, 8)]


def FORMULA(text, sub=None, width=None):
    width = width or CONTENT_W
    rows = [[Paragraph(assert_glyphs(text), S["formula"])]]
    if sub:
        rows.append([Paragraph(assert_glyphs(sub), S["cell_c"])])
    t = Table(rows, colWidths=[width], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BOXBG),
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 9)]


def TEMPLATE_BOX(title, body_lines, width=None):
    """CS 답변 템플릿 등 '그대로 복사해 쓰는' 블록."""
    width = width or CONTENT_W
    rows = [[Paragraph(assert_glyphs(title), S["box_b"])]]
    for ln in body_lines:
        rows.append([Paragraph(assert_glyphs(ln) if ln else "&nbsp;", S["tpl"])])
    t = Table(rows, colWidths=[width - 11 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.0),
        ("TOPPADDING", (0, 1), (-1, 1), 4.0),
    ]))
    outer = Table([[t]], colWidths=[width], hAlign="LEFT")
    outer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FCFDFE")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [outer, Spacer(1, 9)]


class ChapterTitle(Flowable):
    """보이지 않는 마커. 목차 항목 + PDF 북마크 + 러닝 헤더를 한 번에 만듭니다.

    toc_text  : 목차와 북마크에 찍히는 문구 ("1장 · 시작 전 체크리스트")
    head_text : 러닝 헤더 오른쪽에 찍히는 문구 (level 0 에서만 사용)
    """

    def __init__(self, key, toc_text, level=0, head_text=None):
        Flowable.__init__(self)
        self.key = key
        self.text = toc_text
        self.head_text = head_text if head_text is not None else toc_text
        self.level = level
        self.width = 0
        self.height = 0

    def draw(self):
        pass


class SetHeader(Flowable):
    """목차에는 넣지 않고 러닝 헤더만 바꾸는 마커."""

    def __init__(self, head_text):
        Flowable.__init__(self)
        self.head_text = head_text
        self.width = 0
        self.height = 0

    def draw(self):
        pass


def CHAPTER(num_label, title, lead, toc_key):
    """장 시작 블록 (새 페이지에서 시작)."""
    out = [
        PageBreak(),
        ChapterTitle(toc_key, "%s · %s" % (num_label, title), 0,
                     head_text="%s %s" % (num_label, title)),
    ]
    out.append(P(num_label, "h1_num"))
    out.append(P(title, "h1"))
    out.append(HRule(CONTENT_W, 1.6, NAVY, space_before=0, space_after=3))
    if lead:
        out.append(P(lead, "h1_lead"))
    out.append(Spacer(1, 9))
    return out


def SECTION(title, toc_key=None):
    out = []
    if toc_key:
        out.append(ChapterTitle(toc_key, title, 1))
    out.append(P(title, "h2"))
    return out


# ---------------------------------------------------------------- 문서 템플릿

class GuideDoc(BaseDocTemplate):
    def __init__(self, filename, running_title="", **kw):
        BaseDocTemplate.__init__(self, filename, **kw)
        self.running_title = running_title
        self.current_chapter = ""

    def afterFlowable(self, flowable):
        if isinstance(flowable, SetHeader):
            self.current_chapter = flowable.head_text
        elif isinstance(flowable, ChapterTitle):
            # 목차 항목이 이 키로 링크를 걸므로 목적지를 반드시 등록해야 합니다.
            self.canv.bookmarkPage(flowable.key)
            self.canv.addOutlineEntry(flowable.text, flowable.key.encode("utf-8"),
                                      level=flowable.level, closed=(flowable.level == 0))
            if flowable.level == 0:
                self.current_chapter = flowable.head_text
            self.notify("TOCEntry", (flowable.level, flowable.text, self.page,
                                     flowable.key))


def _cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, stroke=0, fill=1)
    canvas.setFillColor(NAVY_LIGHT)
    canvas.rect(0, PAGE_H - 15.4 * mm, PAGE_W, 2.4 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.8)
    canvas.line(M_LEFT, 17 * mm, PAGE_W - M_RIGHT, 17 * mm)
    canvas.restoreState()


def _body_page(canvas, doc):
    canvas.saveState()
    # 러닝 헤더
    canvas.setFont(BODY, 8.2)
    canvas.setFillColor(INK_SOFT)
    canvas.drawString(M_LEFT, PAGE_H - 15.5 * mm, getattr(doc, "running_title", ""))
    ch = getattr(doc, "current_chapter", "")
    if ch:
        canvas.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 15.5 * mm, ch)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(M_LEFT, PAGE_H - 18 * mm, PAGE_W - M_RIGHT, PAGE_H - 18 * mm)
    # 푸터 (페이지 번호)
    canvas.setStrokeColor(RULE_SOFT)
    canvas.line(M_LEFT, 14.5 * mm, PAGE_W - M_RIGHT, 14.5 * mm)
    canvas.setFont(BODY, 8.6)
    canvas.setFillColor(INK_SOFT)
    canvas.drawCentredString(PAGE_W / 2.0, 10.2 * mm, "%d" % doc.page)
    canvas.restoreState()


def make_doc(out_path, meta):
    from reportlab.platypus import PageTemplate

    doc = GuideDoc(
        out_path, running_title=meta["running_title"], pagesize=A4,
        leftMargin=M_LEFT, rightMargin=M_RIGHT,
        topMargin=M_TOP, bottomMargin=M_BOTTOM,
        title=meta["title"], author=meta["author"],
        subject=meta["subject"], creator=meta["creator"],
        # 기본 Helvetica 로 그려지는 텍스트가 생기지 않도록 초기 폰트를 한글 폰트로 지정
        initialFontName=BODY, initialFontSize=10,
    )
    frame = Frame(M_LEFT, M_BOTTOM, CONTENT_W, PAGE_H - M_TOP - M_BOTTOM,
                  id="body", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=_cover_page),
        # 러닝 헤더는 페이지가 끝날 때 그립니다. 페이지 시작 시점에 그리면 그 페이지
        # 첫머리에서 장이 바뀌어도 이전 장 이름이 찍힙니다.
        PageTemplate(id="body", frames=[frame], onPageEnd=_body_page),
    ])
    return doc


def make_toc():
    toc = TableOfContents()
    toc.levelStyles = [S["toc0"], S["toc1"]]
    toc.dotsMinLevel = 0
    return toc


def clean_story(story):
    """PageBreak 직전의 Spacer 를 제거합니다.

    블록이 페이지 맨 아래에 딱 맞게 들어가면, 그 블록 뒤에 붙어 있던 Spacer 가
    다음 페이지로 밀려 나갑니다. 그러면 Spacer 하나 때문에 페이지가 하나 열리고,
    바로 뒤의 PageBreak 가 또 한 번 넘겨서 '완전히 빈 페이지'가 생깁니다.
    (2장 끝에서 실제로 발생했습니다.) 조판 전에 걷어냅니다.
    """
    out = []
    for f in story:
        if isinstance(f, PageBreak):
            while out and isinstance(out[-1], Spacer):
                out.pop()
        out.append(f)
    return out
