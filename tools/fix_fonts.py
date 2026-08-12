# -*- coding: utf-8 -*-
"""LibreOffice 재계산 시 대체된 폰트(WenQuanYi Zen Hei)를 Malgun Gothic으로 원복.

recalc.py 는 컨테이너에 Malgun Gothic 이 없어 폰트를 대체 저장하고,
문자열을 ASCII/한글 경계에서 rich-text run 으로 쪼갠다.
worksheets(수식/캐시값)는 건드리지 않고 styles.xml / sharedStrings.xml / theme1.xml 만 패치한다.
"""
import re
import shutil
import sys
import zipfile

TARGET = "Malgun Gothic"


def patch_styles(xml: str) -> str:
    def fonts_block(m):
        blk = m.group(0)
        return re.sub(r'<name val="[^"]*"/>', f'<name val="{TARGET}"/>', blk)
    return re.sub(r"<fonts\b.*?</fonts>", fonts_block, xml, flags=re.S)


def patch_theme(xml: str) -> str:
    return re.sub(r'typeface="(Calibri|Cambria|WenQuanYi Zen Hei)"',
                  f'typeface="{TARGET}"', xml)


T_RE = re.compile(r"<t(?:\s[^>]*)?>(.*?)</t>|<t\s*/>", re.S)


def patch_shared_strings(xml: str):
    """rich-text run 으로 쪼개진 <si> 를 원래의 단일 <t> 로 복원."""
    collapsed = 0

    def one_si(m):
        nonlocal collapsed
        blk = m.group(0)
        if "<r>" not in blk:
            return blk
        parts = ["" if g is None else g for g in (mm.group(1) for mm in T_RE.finditer(blk))]
        text = "".join(parts)
        collapsed += 1
        return f'<si><t xml:space="preserve">{text}</t></si>'

    out = re.sub(r"<si>.*?</si>", one_si, xml, flags=re.S)
    return out, collapsed


def main(path):
    bak = path + ".prefontfix"
    shutil.copy2(path, bak)

    with zipfile.ZipFile(bak) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]

    stats = {}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            name = info.filename
            if name == "xl/styles.xml":
                s = data.decode("utf-8")
                before = s.count("WenQuanYi Zen Hei")
                s = patch_styles(s)
                stats["styles.xml"] = f"font name 통일 (대체폰트 {before}건 제거)"
                data = s.encode("utf-8")
            elif name == "xl/sharedStrings.xml":
                s = data.decode("utf-8")
                s, n = patch_shared_strings(s)
                stats["sharedStrings.xml"] = f"rich-text run {n}개 <si> 를 평문으로 복원"
                data = s.encode("utf-8")
            elif name == "xl/theme/theme1.xml":
                s = data.decode("utf-8")
                s = patch_theme(s)
                stats["theme1.xml"] = "테마 폰트 Malgun Gothic"
                data = s.encode("utf-8")
            zout.writestr(info, data)

    for k, v in stats.items():
        print(f"  {k}: {v}")

    with zipfile.ZipFile(path) as z:
        for n in ("xl/styles.xml", "xl/sharedStrings.xml", "xl/theme/theme1.xml"):
            body = z.read(n).decode("utf-8")
            assert "WenQuanYi" not in body, n
            assert "Calibri" not in body and "Cambria" not in body and "Arial" not in body, n
    print("  검증: 잔여 대체폰트 문자열 0건")


if __name__ == "__main__":
    main(sys.argv[1])
