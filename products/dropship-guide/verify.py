#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「위탁판매 시작 체크리스트 가이드」 PDF 검수 스크립트.

    python3 verify.py

검사 항목
  1. 파일 실측     쪽수, 바이트, 페이지 크기
  2. 폰트          한글 폰트 임베드 여부, 실제로 글자를 그리는 데 쓰인 서체
  3. 한글 렌더     텍스트 추출 후 한글 포함 확인, 두부(빈 사각형) 문자 검사
  4. 글리프        본문에 쓰인 모든 문자가 두 서체 cmap 에 있는지
  5. 구조          목차 항목의 페이지 번호, PDF 북마크, 러닝 헤더
  6. 금지 문구     표시광고 금지 표현 + 수익 보장류 표현. 적발 위치를 함께 출력

추정 없이 실측만 출력합니다. 판정은 마지막 줄에 요약합니다.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PDF = os.path.join(HERE, "위탁판매_시작_체크리스트_가이드.pdf")

# 두부로 보일 수 있는 사각형·대체 문자. 본문에서 의도적으로 쓰지 않았으므로
# 하나라도 나오면 글리프 사고입니다. (체크박스는 벡터 도형으로 그립니다.)
TOFU = ["□", "■", "☐", "☑", "�", "▯", "▮", "〓"]

# 검사어. (표현 유형, 정규식)
BANNED = [
    ("최저가", r"최저가"),
    ("보장", r"보장"),
    ("100%", r"100\s*%"),
    ("무조건", r"무조건"),
    ("완벽/완전무결", r"완벽|완전무결"),
    ("최고/최상", r"최고급|최고의|최상의"),
    ("1위/베스트/인기순위", r"1위|베스트|인기\s*순위"),
    ("효능/치료/완치/특효", r"효능|치료|완치|특효"),
    ("후기/판매량 암시", r"구매\s*후기|판매량|누적\s*판매"),
    ("수익·매출 증대 서술", r"수익이\s*늘|매출이\s*늘|수익\s*창출|확실한\s*수익|"
                            r"월\s*\d+\s*만\s*원|돈을\s*번|벌\s*수\s*있|벌었"),
    ("수익 인증", r"수익\s*인증|정산\s*인증|실적\s*공개"),
]

# 이 문장 안에서 발견된 검사어는 '금지어를 나열·부정하는 문장'이므로 사용례가 아닙니다.
# 근거를 남기기 위해 패턴으로 명시합니다.
ALLOWED_CONTEXTS = [
    r"수익을\s*보장하지\s*않",      # 표지·서문·맺으며의 면책 문장
    r"쓰지\s*않는\s*표현",           # 4.5절 표 머리글
    r"쓰지\s*않을\s*말",             # 4.5절 도입 문장
    r"단정",                          # 4.5절 표의 유형 이름 (가격 우위 단정 등)
    r"신규\s*스토어에서는\s*쓰지\s*않",
    r"표현을\s*쓰지\s*않습니다",       # 4.4절 원칙 3 (금지 서술)
    r"싣지\s*않았습니다",               # 서문 면책 문장
    r"자사\s*상품의\s*사양만",
    r"측정\s*조건과\s*함께",
    r"용도와\s*사용\s*상황만",
    r"가격은\s*숫자로만",
    r"~하도록\s*만들었습니다",
    r"구체적\s*사양을\s*숫자로",
]


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def main():
    ok = True
    print("=" * 78)
    print("「위탁판매 시작 체크리스트 가이드」 검수 결과")
    print("=" * 78)

    # ---------------------------------------------------------- 1. 파일 실측
    from pypdf import PdfReader
    reader = PdfReader(PDF)
    pages = len(reader.pages)
    size = os.path.getsize(PDF)
    box = reader.pages[0].mediabox
    print("\n[1] 파일 실측")
    print("    파일        : %s" % os.path.basename(PDF))
    print("    쪽수        : %d쪽" % pages)
    print("    크기        : %s bytes (%.1f KB)" % (format(size, ","), size / 1024.0))
    print("    페이지 크기 : %.1f x %.1f pt (A4 = 595.3 x 841.9)"
          % (float(box.width), float(box.height)))
    sizes = {(round(float(p.mediabox.width)), round(float(p.mediabox.height)))
             for p in reader.pages}
    print("    전 쪽 동일  : %s" % ("예" if len(sizes) == 1 else "아니오 %s" % sizes))
    if len(sizes) != 1:
        ok = False

    # ---------------------------------------------------------- 2. 폰트
    print("\n[2] 폰트")
    fonts = sh("pdffonts", PDF)
    embedded, base14 = [], []
    for line in fonts.splitlines()[2:]:
        if not line.strip():
            continue
        cols = line.split()
        name, emb = cols[0], cols[-4]
        (embedded if emb == "yes" else base14).append(name)
    for n in embedded:
        print("    임베드      : %s" % n)
    for n in base14:
        print("    비임베드    : %s (리소스 선언만 — 아래에서 실사용 확인)" % n)
    if not any("Nanum" in n for n in embedded):
        print("    !! 한글 폰트가 임베드되지 않았습니다")
        ok = False

    # 비임베드 서체로 실제 글자를 그리는지 콘텐츠 스트림에서 확인
    used = 0
    for pg in reader.pages:
        fdict = pg["/Resources"].get("/Font", {})
        b14 = {n for n, ref in fdict.items()
               if any(k in str(ref.get_object().get("/BaseFont", ""))
                      for k in ("Helvetica", "Courier", "Times"))}
        if not b14:
            continue
        data = pg.get_contents().get_data().decode("latin-1")
        for nm in b14:
            pat = re.compile(re.escape(nm) + r"\s+[\d.]+\s+Tf(.{0,400}?)"
                             r"(?:ET|/[\w+]+\s+[\d.]+\s+Tf)", re.S)
            for m in pat.finditer(data):
                if re.search(r"\)\s*Tj|\]\s*TJ", m.group(1)):
                    used += 1
    print("    비임베드 서체로 그린 글자 : %d건 %s"
          % (used, "(정상)" if used == 0 else "(!! 확인 필요)"))
    if used:
        ok = False

    # ---------------------------------------------------------- 3. 한글 렌더
    print("\n[3] 한글 렌더 / 두부 검사")
    txt = sh("pdftotext", "-layout", PDF, "-")
    hangul = len(re.findall(r"[가-힣]", txt))
    print("    추출 문자 수      : %s자" % format(len(txt), ","))
    print("    한글 음절 수      : %s자" % format(hangul, ","))
    tofu_hits = {c: txt.count(c) for c in TOFU if txt.count(c)}
    print("    두부·대체 문자    : %s" % (tofu_hits if tofu_hits else "0건"))
    if tofu_hits or hangul < 5000:
        ok = False
    # 쪽마다 한글이 나오는지 (표지 포함 전 쪽)
    empty = []
    for i in range(1, pages + 1):
        pt = sh("pdftotext", "-f", str(i), "-l", str(i), PDF, "-")
        if not re.search(r"[가-힣]", pt):
            empty.append(i)
    print("    한글 없는 쪽      : %s" % (empty if empty else "없음"))
    if empty:
        ok = False

    # ---------------------------------------------------------- 4. 글리프
    print("\n[4] 글리프 커버리지 (본문에 쓰인 모든 문자)")
    import guide_layout as L
    src = open(os.path.join(HERE, "content.py"), encoding="utf-8").read()
    body = re.findall(r'"((?:[^"\\]|\\.)*)"', src)
    chars = {c for chunk in body for c in chunk}
    chars |= set(re.sub(r"\s", "", txt))
    missing = sorted({c for c in chars if ord(c) > 31 and ord(c) not in L._CMAP})
    print("    검사 문자 종류    : %d종" % len(chars))
    print("    폰트에 없는 문자  : %s"
          % (", ".join("U+%04X %r" % (ord(c), c) for c in missing) if missing else "0건"))
    if missing:
        ok = False

    # ---------------------------------------------------------- 5. 구조
    print("\n[5] 구조")
    outlines = reader.outline
    def count_outline(o):
        n = 0
        for item in o:
            if isinstance(item, list):
                n += count_outline(item)
            else:
                n += 1
        return n
    n_out = count_outline(outlines)
    toc_txt = sh("pdftotext", "-layout", "-f", "3", "-l", "4", PDF, "-")
    toc_lines = [l for l in toc_txt.splitlines() if re.search(r"\.\s*\.\s*\.", l)]
    unresolved = [l for l in toc_lines if re.search(r"\.\s+0\s*$", l)]
    placeholder = "Placeholder for table of contents" in toc_txt
    print("    PDF 북마크        : %d개" % n_out)
    print("    목차 항목         : %d개" % len(toc_lines))
    print("    목차 미해결(0쪽)  : %d개" % len(unresolved))
    print("    목차 플레이스홀더 : %s" % ("있음 (!!)" if placeholder else "없음"))
    heads = []
    for i in (2, 3, 5, 12, 20, pages):
        first = sh("pdftotext", "-layout", "-f", str(i), "-l", str(i), PDF, "-")
        heads.append((i, first.splitlines()[0].strip() if first.strip() else ""))
    for i, h in heads:
        print("    러닝 헤더 p.%-2d    : %s" % (i, re.sub(r"\s{2,}", " | ", h)))
    if placeholder or unresolved or n_out < 10:
        ok = False

    # ---------------------------------------------------------- 6. 금지 문구
    print("\n[6] 금지 문구 검사 (고객에게 보이는 PDF 본문 전체)")
    page_texts = [sh("pdftotext", "-f", str(i), "-l", str(i), PDF, "-")
                  for i in range(1, pages + 1)]
    total_hits = 0
    real_hits = 0
    for label, pat in BANNED:
        hits = []
        for pno, pt in enumerate(page_texts, 1):
            flat = re.sub(r"\s+", " ", pt)
            for m in re.finditer(pat, flat):
                s = max(0, m.start() - 45)
                ctx = flat[s:m.end() + 45]
                allowed = any(re.search(a, ctx) for a in ALLOWED_CONTEXTS)
                hits.append((pno, ctx.strip(), allowed))
        total_hits += len(hits)
        bad = [h for h in hits if not h[2]]
        real_hits += len(bad)
        status = "0건" if not hits else (
            "%d건 (전부 규칙 서술·면책 문장)" % len(hits) if not bad
            else "%d건 중 실사용 %d건 (!!)" % (len(hits), len(bad)))
        print("    %-22s: %s" % (label, status))
        for pno, ctx, allowed in hits:
            mark = "  ·" if allowed else "  !!"
            print("      %s p.%-2d %s" % (mark, pno, ctx))
    print("    ----")
    print("    적발 합계         : %d건" % total_hits)
    print("    실제 사용         : %d건" % real_hits)
    if real_hits:
        ok = False

    print("\n" + "=" * 78)
    print("판정: %s" % ("통과" if ok else "확인 필요 항목 있음"))
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
