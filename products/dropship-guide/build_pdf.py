#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「위탁판매 시작 체크리스트 가이드」 PDF 생성 진입점.

    python3 build_pdf.py

파일 구성
  guide_layout.py  폰트·색·스타일·조판 헬퍼·문서 템플릿 (레이아웃 엔진)
  content.py       본문 텍스트와 표 데이터
  build_pdf.py     이 파일. 위 둘을 묶어 PDF 를 만듭니다.

주의: content.py 가 guide_layout 을 import 하므로, 엔진을 직접 실행하지 말고
항상 이 파일을 실행해 주세요. (같은 모듈이 두 이름으로 두 번 적재되면
목차 수집용 isinstance 검사가 어긋나 목차가 빈 채로 생성됩니다.)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import guide_layout as L  # noqa: E402
import content as C  # noqa: E402


def build():
    out_path = os.path.join(HERE, C.OUT_FILENAME)
    meta = {
        "title": C.PDF_TITLE,
        "author": C.PDF_AUTHOR,
        "subject": C.PDF_SUBJECT,
        "creator": C.PDF_CREATOR,
        "running_title": C.RUNNING_TITLE,
    }
    doc = L.make_doc(out_path, meta)
    toc = L.make_toc()
    story = L.clean_story(C.build_story(toc))
    doc.multiBuild(story)
    return out_path


if __name__ == "__main__":
    path = build()
    size = os.path.getsize(path)
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(path).pages)
        print("생성 완료: %s (%d쪽, %,d bytes)".replace("%,d", "{:,}".format(size))
              % (os.path.basename(path), pages))
    except Exception:
        print("생성 완료: %s (%d bytes)" % (os.path.basename(path), size))
