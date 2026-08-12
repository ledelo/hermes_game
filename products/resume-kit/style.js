// 공통 스타일 · 조판 헬퍼 — 「깔끔한 국문 이력서·자소서 세트」
// 사용: require('./style.js')  (docx 패키지 필요: npm install docx)
const d = require('docx');

const NAVY = '1F3864'; // 포인트 컬러 1색 (남색)
const NAVY_LIGHT = 'EDF1F7'; // 표 머리행 배경
const GRAY_LINE = 'C9CFD8'; // 표·문단 테두리 (얇은 회색)
const GRAY_TEXT = '808080'; // 안내 문구
const BLACK = '1A1A1A'; // 본문

const FONT = { ascii: '맑은 고딕', eastAsia: '맑은 고딕', hAnsi: '맑은 고딕', cs: '맑은 고딕' };

// A4(11906 x 16838 DXA) 기준 본문 폭
const PAGE = { top: 850, bottom: 800, left: 1000, right: 1000 };
const W = 9906; // 11906 - 2000

const border = (sz = 4, color = GRAY_LINE) => ({ style: d.BorderStyle.SINGLE, size: sz, color });
const cellBorders = (opts = {}) => ({
  top: border(opts.size), bottom: border(opts.size), left: border(opts.size), right: border(opts.size),
});
const NO_BORDERS = {
  top: { style: d.BorderStyle.NONE }, bottom: { style: d.BorderStyle.NONE },
  left: { style: d.BorderStyle.NONE }, right: { style: d.BorderStyle.NONE },
};

// ---- 런(run) 헬퍼 : size 는 half-point ----
const run = (text, o = {}) => new d.TextRun({
  text, font: FONT, size: o.size || 19, bold: !!o.bold, italics: !!o.italics,
  color: o.color || BLACK, characterSpacing: o.spacing,
});

// ---- 문단 헬퍼 ----
const p = (text, o = {}) => new d.Paragraph({
  children: Array.isArray(text) ? text : [run(text, o)],
  alignment: o.align,
  spacing: { before: o.before || 0, after: o.after === undefined ? 60 : o.after, line: o.line || 264, lineRule: 'auto' },
  indent: o.indent,
  border: o.border,
  keepNext: o.keepNext,
});

// 문서 제목 (이력서 / 자기소개서)
const docTitle = (text, o = {}) => new d.Paragraph({
  children: [run(text, { size: o.size || 36, bold: true, color: NAVY, spacing: o.spacing === undefined ? 120 : o.spacing })],
  alignment: d.AlignmentType.CENTER,
  spacing: { after: o.after === undefined ? 160 : o.after, line: 264, lineRule: 'auto' },
  border: { bottom: { style: d.BorderStyle.SINGLE, size: 12, color: NAVY, space: 6 } },
});

// 섹션 제목 (인적사항 / 학력 …)
const sectionTitle = (text, o = {}) => new d.Paragraph({
  children: [run(text, { size: 21, bold: true, color: NAVY, spacing: 20 })],
  spacing: { before: o.before === undefined ? 220 : o.before, after: 70, line: 264, lineRule: 'auto' },
  border: { bottom: { style: d.BorderStyle.SINGLE, size: 6, color: NAVY, space: 3 } },
  keepNext: true,
});

// 회색 안내(작성 팁) 문단 — 왼쪽 얇은 회색 선 + 회색 이탤릭
const tip = (text, o = {}) => new d.Paragraph({
  children: [run(text, { size: 17, italics: true, color: GRAY_TEXT })],
  spacing: { before: o.before || 0, after: o.after === undefined ? 30 : o.after, line: 252, lineRule: 'auto' },
  indent: { left: 260 },
  border: { left: { style: d.BorderStyle.SINGLE, size: 6, color: GRAY_LINE, space: 8 } },
});

// 표 셀
const cell = (children, o = {}) => new d.TableCell({
  width: { size: o.width, type: d.WidthType.DXA },
  columnSpan: o.colSpan, rowSpan: o.rowSpan,
  verticalAlign: o.valign || d.VerticalAlign.CENTER,
  shading: o.fill ? { type: d.ShadingType.CLEAR, color: 'auto', fill: o.fill } : undefined,
  borders: o.borders,
  margins: { top: o.padY === undefined ? 60 : o.padY, bottom: o.padY === undefined ? 60 : o.padY, left: 100, right: 100 },
  children: Array.isArray(children) ? children : [children],
});

// 표 머리행 셀 (연한 남색 배경 + 굵은 남색 글자)
const th = (text, width) => cell(
  p(text, { align: d.AlignmentType.CENTER, after: 0, size: 18, bold: true, color: NAVY }),
  { width, fill: NAVY_LIGHT },
);
// 라벨 셀 (좌측 항목명)
const tl = (text, width) => cell(
  p(text, { align: d.AlignmentType.CENTER, after: 0, size: 18, bold: true, color: NAVY }),
  { width, fill: NAVY_LIGHT },
);
// 값 셀
const td = (text, width, o = {}) => cell(
  Array.isArray(text) ? text : p(text, { align: o.align, after: 0, size: o.size || 18, color: o.color, italics: o.italics }),
  { width, valign: o.valign, fill: o.fill },
);

const table = (rows, columnWidths, o = {}) => new d.Table({
  rows, columnWidths,
  width: { size: columnWidths.reduce((a, b) => a + b, 0), type: d.WidthType.DXA },
  layout: d.TableLayoutType.FIXED,
  borders: o.borders || cellBorders(),
  margins: o.margins,
});

const row = (cells, o = {}) => new d.TableRow({
  children: cells,
  height: o.height ? { value: o.height, rule: o.rule || d.HeightRule.EXACT } : undefined,
  tableHeader: o.header,
  cantSplit: true,
});

const spacer = (h = 80) => new d.Paragraph({ children: [], spacing: { after: h, line: 240, lineRule: 'auto' } });

// 불릿 목록 설정
const bulletNumbering = {
  config: [
    {
      reference: 'kit-bullets',
      levels: [{
        level: 0, format: d.LevelFormat.BULLET, text: '•', alignment: d.AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 320, hanging: 200 } }, run: { color: NAVY, font: FONT } },
      }],
    },
    {
      reference: 'kit-checks',
      levels: [{
        level: 0, format: d.LevelFormat.BULLET, text: '□', alignment: d.AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 460, hanging: 320 } }, run: { color: NAVY, font: FONT } },
      }],
    },
  ],
};

const bullet = (text, o = {}) => new d.Paragraph({
  children: Array.isArray(text) ? text : [run(text, { size: o.size || 18 })],
  numbering: { reference: o.reference || 'kit-bullets', level: 0 },
  spacing: { after: o.after === undefined ? 40 : o.after, line: o.line || 258, lineRule: 'auto' },
});

// 문서 기본 스타일 (모든 문단이 맑은 고딕을 상속)
const defaultStyles = {
  default: {
    document: {
      run: { font: FONT, size: 19, color: BLACK },
      paragraph: { spacing: { line: 264, lineRule: 'auto' } },
    },
  },
};

const makeDoc = (children, o = {}) => new d.Document({
  creator: '이력서·자소서 세트',
  title: o.title,
  description: o.description,
  styles: defaultStyles,
  numbering: bulletNumbering,
  sections: [{
    properties: {
      page: { margin: o.margin || PAGE },
    },
    children,
  }],
});

module.exports = {
  d, NAVY, NAVY_LIGHT, GRAY_LINE, GRAY_TEXT, BLACK, FONT, W, PAGE,
  border, cellBorders, NO_BORDERS, run, p, docTitle, sectionTitle, tip,
  cell, th, tl, td, table, row, spacer, bullet, makeDoc,
};
