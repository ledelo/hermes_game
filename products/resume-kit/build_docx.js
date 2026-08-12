// 「깔끔한 국문 이력서·자소서 세트」 docx 4종 빌드
// 실행: NODE_PATH=<docx 설치 경로> node build_docx.js
const fs = require('fs');
const path = require('path');
const S = require('./style.js');
const {
  d, NAVY, NAVY_LIGHT, GRAY_LINE, GRAY_TEXT, run, p, docTitle, sectionTitle, tip,
  cell, th, tl, td, table, row, spacer, bullet, makeDoc, cellBorders, NO_BORDERS,
} = S;

const OUT = __dirname;
const A = d.AlignmentType;

// ─────────────────────────────────────────────────────────────
// 1. 이력서_신입형.docx  (1쪽)
// ─────────────────────────────────────────────────────────────
function buildFresh() {
  const CW = [1150, 2550, 1150, 3070, 1986]; // = 9906
  const photo = cell([
    p('사 진', { align: A.CENTER, after: 40, size: 18, color: GRAY_TEXT }),
    p('3.5 × 4.5 cm', { align: A.CENTER, after: 0, size: 15, color: GRAY_TEXT }),
  ], { width: CW[4], rowSpan: 4 });

  const personal = table([
    row([tl('성 명', CW[0]), td('홍 길 동', CW[1]), tl('생 년', CW[2]), td('1999년', CW[3]), photo], { height: 638 }),
    row([tl('연락처', CW[0]), td('010-0000-0000', CW[1]), tl('이메일', CW[2]), td('hong@example.com', CW[3])], { height: 638 }),
    row([tl('주 소', CW[0]), td('서울특별시 ○○구', CW[1]), tl('포트폴리오', CW[2]), td('링크 (없으면 칸을 지웁니다)', CW[3], { color: GRAY_TEXT })], { height: 638 }),
    row([tl('희망 직무', CW[0]), td('마케팅 기획 · 콘텐츠 운영', CW[1]), tl('최종 학력', CW[2]), td('○○대학교 졸업 (2024.02)', CW[3])], { height: 638 }),
  ], CW);

  const EW = [2300, 2400, 3400, 1806];
  const edu = table([
    row([th('재학 기간', EW[0]), th('학교명', EW[1]), th('전공 · 과정', EW[2]), th('졸업 구분', EW[3])], { header: true }),
    row([td('2020.03 ~ 2024.02', EW[0], { align: A.CENTER }), td('○○대학교', EW[1], { align: A.CENTER }),
      td('경영학 전공 / 데이터분석 부전공', EW[2]), td('졸업', EW[3], { align: A.CENTER })]),
    row([td('2017.03 ~ 2020.02', EW[0], { align: A.CENTER }), td('○○고등학교', EW[1], { align: A.CENTER }),
      td('인문계', EW[2]), td('졸업', EW[3], { align: A.CENTER })]),
  ], EW);

  const XW = [2000, 2100, 1300, 4506];
  const exp = table([
    row([th('기간', XW[0]), th('활동처', XW[1]), th('역할', XW[2]), th('한 일과 결과', XW[3])], { header: true }),
    row([td('2023.07 ~ 2023.08', XW[0], { align: A.CENTER }), td('△△주식회사 마케팅팀', XW[1], { align: A.CENTER }), td('인턴', XW[2], { align: A.CENTER }),
      td('SNS 콘텐츠 20건 기획·발행, 게시물 반응 데이터를 주간 리포트로 정리', XW[3])]),
    row([td('2022.09 ~ 2023.06', XW[0], { align: A.CENTER }), td('○○대학교 마케팅 학회', XW[1], { align: A.CENTER }), td('기획팀장', XW[2], { align: A.CENTER }),
      td('팀원 6명과 교내 캠페인 2회 진행, 설문 300건을 분석해 개선안 제안', XW[3])]),
    row([td('2022.03 ~ 2022.08', XW[0], { align: A.CENTER }), td('△△주식회사 서포터즈', XW[1], { align: A.CENTER }), td('활동생', XW[2], { align: A.CENTER }),
      td('제품 체험 후기 콘텐츠 12건 작성, 우수 활동자 선정', XW[3])]),
  ], XW);

  const CQ = [1300, 3400, 1900, 3306];
  const cert = table([
    row([th('구분', CQ[0]), th('명칭', CQ[1]), th('취득일', CQ[2]), th('발행처 · 점수', CQ[3])], { header: true }),
    row([td('자격', CQ[0], { align: A.CENTER }), td('컴퓨터활용능력 1급', CQ[1]), td('2023.11', CQ[2], { align: A.CENTER }), td('대한상공회의소', CQ[3])]),
    row([td('어학', CQ[0], { align: A.CENTER }), td('공인 영어 성적 (○○)', CQ[1]), td('2024.01', CQ[2], { align: A.CENTER }), td('○○○점', CQ[3])]),
    row([td('자격', CQ[0], { align: A.CENTER }), td('운전면허 2종 보통', CQ[1]), td('2019.05', CQ[2], { align: A.CENTER }), td('○○지방경찰청', CQ[3])]),
  ], CQ);

  const SW = [1500, 8406];
  const skills = table([
    row([tl('문서 · 협업', SW[0]), td('한글, 워드, 엑셀(함수·피벗), 파워포인트, 협업 도구(문서 공동편집·업무 메신저)', SW[1])]),
    row([tl('데이터', SW[0]), td('스프레드시트 집계표 작성, SQL 기초 조회, 설문 데이터 정리', SW[1])]),
    row([tl('콘텐츠', SW[0]), td('이미지 편집 도구 기초, 카드뉴스·상세페이지 문안 작성', SW[1])]),
  ], SW);

  const doc = makeDoc([
    docTitle('이 력 서'),
    sectionTitle('인적 사항', { before: 140 }),
    personal,
    sectionTitle('학력'),
    edu,
    sectionTitle('경험 · 활동'),
    exp,
    sectionTitle('자격 · 어학'),
    cert,
    sectionTitle('기술 스택'),
    skills,
    p([run('위에 기재한 사항은 사실과 다름이 없습니다.', { size: 18 })], { align: A.CENTER, before: 260, after: 60 }),
    p([run('2026년 ○○월 ○○일          지원자   홍 길 동   (서명)', { size: 18 })], { align: A.CENTER, after: 40 }),
    p('※ 예시로 채워 둔 내용입니다. 본인 정보로 바꾸고 이 안내 줄은 지워 주세요.', { align: A.CENTER, size: 15, color: GRAY_TEXT, after: 0 }),
  ], { title: '이력서 (신입형)' });

  return d.Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, '이력서_신입형.docx'), b));
}

// ─────────────────────────────────────────────────────────────
// 2. 이력서_경력형.docx  (1~2쪽)
// ─────────────────────────────────────────────────────────────
function buildCareer() {
  const HW = [5906, 4000];
  const header = table([
    row([
      cell([
        p([run('홍 길 동', { size: 32, bold: true, color: NAVY, spacing: 60 })], { after: 40 }),
        p('온라인 마케팅 · 콘텐츠 운영 5년', { size: 19, color: NAVY, after: 0 }),
      ], { width: HW[0], borders: NO_BORDERS, padY: 0, valign: d.VerticalAlign.BOTTOM }),
      cell([
        p('010-0000-0000', { align: A.RIGHT, size: 18, after: 20 }),
        p('hong@example.com', { align: A.RIGHT, size: 18, after: 20 }),
        p('서울특별시 ○○구', { align: A.RIGHT, size: 18, after: 0 }),
      ], { width: HW[1], borders: NO_BORDERS, padY: 0, valign: d.VerticalAlign.BOTTOM }),
    ]),
  ], HW, { borders: NO_BORDERS });

  const rule = new d.Paragraph({
    children: [],
    spacing: { before: 60, after: 140, line: 240, lineRule: 'auto' },
    border: { bottom: { style: d.BorderStyle.SINGLE, size: 12, color: NAVY, space: 2 } },
  });

  // 회사 머리줄
  const CH = [4400, 2900, 2606];
  const company = (name, role, period) => table([
    row([
      cell(p(name, { after: 0, size: 19, bold: true, color: NAVY }), { width: CH[0], fill: NAVY_LIGHT }),
      cell(p(role, { after: 0, size: 18 }), { width: CH[1], fill: NAVY_LIGHT }),
      cell(p(period, { align: A.RIGHT, after: 0, size: 18 }), { width: CH[2], fill: NAVY_LIGHT }),
    ], { height: 400, rule: d.HeightRule.ATLEAST }),
  ], CH, { borders: cellBorders() });

  const PW = [2100, 2400, 1300, 4106];
  const projects = table([
    row([th('기간', PW[0]), th('프로젝트', PW[1]), th('역할', PW[2]), th('한 일과 결과', PW[3])], { header: true }),
    row([td('2024.03 ~ 2024.08', PW[0], { align: A.CENTER }), td('자사몰 상세페이지 개편', PW[1]), td('기획 총괄', PW[2], { align: A.CENTER }),
      td('카테고리 12개 페이지 구조·문안 재작성, 개편 전후 지표를 주간 단위로 비교 관리', PW[3])]),
    row([td('2023.05 ~ 2023.09', PW[0], { align: A.CENTER }), td('신규 라인 런칭 캠페인', PW[1]), td('콘텐츠 기획', PW[2], { align: A.CENTER }),
      td('광고 소재 24종 제작 관리, 채널 3곳 동시 집행 일정 조율', PW[3])]),
    row([td('2022.06 ~ 2022.10', PW[0], { align: A.CENTER }), td('리뷰 데이터 정비', PW[1]), td('데이터 정리', PW[2], { align: A.CENTER }),
      td('리뷰 1,200건 분류·태깅, 자주 나온 문의 15개를 상세페이지 문구 개선안으로 정리', PW[3])]),
  ], PW);

  const EW = [1500, 8406];
  const edu = table([
    row([tl('학력', EW[0]), td('2015.03 ~ 2019.08   ○○대학교 신문방송학 전공 졸업', EW[1])]),
    row([tl('자격', EW[0]), td('컴퓨터활용능력 1급 (2018.11) · 웹 분석 도구 공인 자격 (2023.04)', EW[1])]),
    row([tl('어학', EW[0]), td('공인 영어 성적 (○○) ○○○점 (2023.02)', EW[1])]),
  ], EW);

  const doc = makeDoc([
    header,
    rule,
    sectionTitle('경력 요약', { before: 0 }),
    bullet('소비재 브랜드의 온라인 채널 운영을 5년간 담당하며 상세페이지 기획부터 성과 정리까지 맡았습니다.'),
    bullet('최근 2년은 자사몰 콘텐츠 개편을 주도해 카테고리 12개 페이지를 다시 구성했습니다.'),
    bullet('제작 프로세스를 문서화해 신규 콘텐츠 리드타임을 5일에서 3일로 줄인 경험이 있습니다.'),
    sectionTitle('경력 사항'),
    company('△△주식회사', '온라인마케팅팀 · 대리', '2022.03 ~ 재직 중'),
    spacer(40),
    bullet('자사몰 상세페이지 개편을 담당해 주요 카테고리 12개 페이지의 구성과 문안을 다시 썼습니다.'),
    bullet('광고 소재 A/B 테스트를 월 4회 운영하고 결과를 팀 주간 리포트로 정리했습니다.'),
    bullet('콘텐츠 제작 프로세스를 문서화해 기획–검수–발행 리드타임을 5일에서 3일로 줄였습니다.'),
    bullet('협력사 2곳의 제작 일정을 조율하며 분기 캠페인 6건을 기한 안에 진행했습니다.'),
    spacer(120),
    company('□□주식회사', '마케팅팀 · 사원', '2019.09 ~ 2022.02'),
    spacer(40),
    bullet('브랜드 SNS 채널 2개를 운영하며 주 3회 콘텐츠를 발행했습니다.'),
    bullet('월간 성과 데이터를 정리해 채널별 게시물 유형과 반응의 관계를 리포트로 제출했습니다.'),
    bullet('오프라인 행사 2회의 홍보물 제작과 현장 운영을 지원했습니다.'),
    sectionTitle('프로젝트'),
    projects,
    sectionTitle('학력 · 자격'),
    edu,
    p('※ 예시로 채워 둔 내용입니다. 본인 경력으로 바꾸고 이 안내 줄은 지워 주세요.', { align: A.CENTER, size: 15, color: GRAY_TEXT, before: 200, after: 0 }),
  ], { title: '이력서 (경력형)' });

  return d.Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, '이력서_경력형.docx'), b));
}

// ─────────────────────────────────────────────────────────────
// 3. 자기소개서_템플릿.docx
// ─────────────────────────────────────────────────────────────
function buildCoverLetter() {
  const IW = [1100, 2200, 1200, 2100, 1100, 2206]; // = 9906
  const info = table([
    row([
      tl('성 명', IW[0]), td('홍 길 동', IW[1], { align: A.CENTER }),
      tl('지원 직무', IW[2]), td('온라인 마케팅', IW[3], { align: A.CENTER }),
      tl('작성일', IW[4]), td('2026. ○○. ○○.', IW[5], { align: A.CENTER }),
    ], { height: 420, rule: d.HeightRule.ATLEAST }),
  ], IW);

  const qHeading = (no, title, pageBreak) => new d.Paragraph({
    children: [
      run(`${no}. `, { size: 21, bold: true, color: NAVY }),
      run(title, { size: 21, bold: true, color: NAVY, spacing: 10 }),
    ],
    spacing: { before: pageBreak ? 0 : 260, after: 70, line: 264, lineRule: 'auto' },
    border: { bottom: { style: d.BorderStyle.SINGLE, size: 6, color: NAVY, space: 3 } },
    pageBreakBefore: !!pageBreak,
    keepNext: true,
  });

  const answerBox = (height) => table([
    row([cell(
      p('이곳에 작성합니다. (작성 후 이 회색 안내 문구는 지워 주세요.)', { size: 18, color: GRAY_TEXT, italics: true, after: 0 }),
      { width: 9906, valign: d.VerticalAlign.TOP, padY: 120 },
    )], { height, rule: d.HeightRule.ATLEAST }),
  ], [9906]);

  const question = (no, title, tips, lengthGuide, boxHeight, pageBreak) => [
    qHeading(no, title, pageBreak),
    p([run('작성 팁', { size: 16, bold: true, color: GRAY_TEXT })], { after: 20 }),
    ...tips.map((t) => tip(t)),
    p([run(lengthGuide, { size: 16, color: GRAY_TEXT })], { align: A.RIGHT, before: 40, after: 60 }),
    answerBox(boxHeight),
  ];

  const doc = makeDoc([
    docTitle('자기소개서', { size: 32, after: 140 }),
    spacer(40),
    info,

    ...question(1, '지원 동기', [
      '회사 소개를 옮겨 적기보다, 지원 직무에서 어떤 일을 하고 싶은지 한 문장으로 먼저 적습니다.',
      '그렇게 생각하게 된 본인의 경험 한 가지를 근거로 붙입니다.',
      '마지막 두세 줄은 입사 후 처음 6개월 동안 하고 싶은 일로 마무리합니다.',
    ], '권장 분량: 공백 포함 600~800자 (약 12~16줄)', 4300),

    ...question(2, '직무 역량', [
      '공고의 요구 역량 중 본인과 가장 잘 맞는 항목 두 가지를 고릅니다.',
      '역량마다 상황 → 한 일 → 결과 순서로 적고, 결과에는 숫자나 기간을 넣습니다.',
      '자격증 나열보다, 그 역량을 실제로 쓴 장면 하나가 더 잘 읽힙니다.',
    ], '권장 분량: 공백 포함 700~900자 (약 14~18줄)', 4600),

    ...question(3, '협업 경험', [
      '팀에서 맡은 역할과 본인이 실제로 한 행동을 구분해서 적습니다.',
      '의견이 갈렸던 지점과 그것을 좁힌 방법을 한 문장씩 넣습니다.',
      '"열심히", "최선을 다해" 대신 무엇을 어떻게 했는지 동사로 적습니다.',
    ], '권장 분량: 공백 포함 600~800자 (약 12~16줄)', 4400, true),

    ...question(4, '입사 후 포부', [
      '먼 목표보다 1년 차에 익히고 싶은 업무를 구체적으로 적는 편이 읽기 좋습니다.',
      '지원 직무의 실제 업무 흐름과 이어지는 목표인지 확인합니다.',
      '마지막 문장은 각오 대신 하고 싶은 일로 끝맺습니다.',
    ], '권장 분량: 공백 포함 500~700자 (약 10~14줄)', 4300),

    sectionTitle('제출 전 점검'),
    bullet('문항마다 첫 문장이 결론인지 확인했습니다.', { reference: 'kit-checks' }),
    bullet('회색 안내 문구를 모두 지웠습니다.', { reference: 'kit-checks' }),
    bullet('회사명 · 직무명을 지원하는 곳에 맞게 바꿨습니다.', { reference: 'kit-checks' }),
    bullet('맞춤법 검사를 한 번 돌렸습니다.', { reference: 'kit-checks' }),
    bullet('제출 파일 형식과 파일명 규칙을 공고에서 다시 확인했습니다.', { reference: 'kit-checks' }),
  ], { title: '자기소개서 템플릿' });

  return d.Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, '자기소개서_템플릿.docx'), b));
}

// ─────────────────────────────────────────────────────────────
// 4. 사용가이드.docx  (1쪽)
// ─────────────────────────────────────────────────────────────
function buildGuide() {
  const FW = [3000, 6906];
  const files = table([
    row([th('파일', FW[0]), th('쓰임', FW[1])], { header: true }),
    row([td('이력서_신입형.docx', FW[0]), td('경력이 없거나 3년 미만일 때. 학력 · 경험 · 자격 · 기술을 1쪽에 담는 표 서식', FW[1])]),
    row([td('이력서_경력형.docx', FW[0]), td('경력 3년 이상일 때. 경력 요약 3줄 + 회사별 성과 + 프로젝트 표', FW[1])]),
    row([td('자기소개서_템플릿.docx', FW[0]), td('4문항(지원 동기 · 직무 역량 · 협업 경험 · 입사 후 포부) 서식', FW[1])]),
  ], FW);

  const step = (no, title) => new d.Paragraph({
    children: [run(`${no}. ${title}`, { size: 20, bold: true, color: NAVY })],
    spacing: { before: 200, after: 60, line: 264, lineRule: 'auto' },
    keepNext: true,
  });
  const line = (t) => p(t, { size: 18, after: 30, indent: { left: 240 } });

  const doc = makeDoc([
    docTitle('사용 가이드', { size: 30, after: 130 }),
    p('워드(또는 한글에서 docx 열기)로 열어 내용을 바꿔 쓰는 서식입니다. 아래 네 가지만 알면 충분합니다.',
      { size: 18, before: 120, after: 120 }),
    files,

    step(1, '글꼴 바꾸기'),
    line('기본 글꼴은 맑은 고딕입니다. 한국에서 쓰는 워드에 기본 설치된 글꼴이라 그대로 두면 상대방 화면에서도 같게 보입니다.'),
    line('바꾸려면 Ctrl+A로 전체 선택 후 [홈] 탭 글꼴 상자에 원하는 글꼴 이름을 넣습니다. 표 안 글자도 함께 바뀝니다.'),
    line('제목만 바꾸려면 그 줄만 드래그해서 선택한 뒤 같은 방법으로 바꿉니다. 본문 크기는 9.5~10pt를 권합니다.'),

    step(2, '회색 안내(작성 팁) 문구 지우기'),
    line('회색 기울임 글자는 모두 안내 문구입니다. 제출 전에 남김없이 지웁니다.'),
    line('문단 왼쪽 여백을 세 번 연속 클릭하면 그 문단 전체가 선택됩니다. Delete를 누르면 왼쪽 회색 세로선까지 함께 사라집니다.'),
    line('표 안의 회색 예시 글자는 칸을 클릭해 드래그 선택한 뒤 지우고 본인 내용을 적습니다.'),

    step(3, 'PDF로 저장하기'),
    line('[파일] > [다른 이름으로 저장]에서 파일 형식을 PDF로 고릅니다. ([파일] > [내보내기] > [PDF/XPS 만들기]도 같습니다.)'),
    line('파일 이름은 「이름_직무_이력서」처럼 적으면 담당자가 찾기 쉽습니다. 예: 홍길동_온라인마케팅_이력서'),
    line('저장한 PDF를 한 번 열어 표가 다음 쪽으로 잘려 넘어가지 않았는지 확인합니다.'),

    step(4, '사진 넣기 (신입형 이력서)'),
    line('오른쪽 위 「사진」 칸을 클릭하고 [삽입] > [그림] > [이 디바이스]에서 사진을 고릅니다.'),
    line('사진이 칸보다 크면 모서리 손잡이를 안쪽으로 끌어 3.5 × 4.5cm에 맞춥니다. 안내 글자(사진 / 3.5 × 4.5 cm)는 지웁니다.'),
    line('사진을 요구하지 않는 공고라면 그 칸을 지워도 됩니다. 칸 안에 커서를 두고 [레이아웃] > [삭제] > [열 삭제]를 고릅니다.'),

    sectionTitle('막히기 쉬운 곳'),
    bullet('워드가 없다면 한글에서 [파일] > [불러오기]로 docx를 열 수 있습니다. 표 서식이 조금 달라 보일 수 있으니 열고 나서 줄 간격만 확인하십시오.', { size: 17 }),
    bullet('보내는 쪽과 받는 쪽의 글꼴이 달라 줄이 밀릴 수 있습니다. PDF로 저장해 보내면 화면 그대로 전달됩니다.', { size: 17 }),
    bullet('표가 다음 쪽으로 넘어가면 비어 있는 줄을 지우거나 [레이아웃] > [여백]에서 위아래 여백을 조금 줄입니다.', { size: 17 }),
    bullet('표에 줄을 더 쓰려면 표 마지막 칸에서 Tab 키를 누릅니다. 줄이 하나 생깁니다.', { size: 17 }),

    sectionTitle('알아두면 좋은 것'),
    bullet('주민등록번호 · 가족사항 칸은 넣지 않았습니다. 최근 채용 서식에서 빠지는 항목이라 그렇습니다. 공고에서 요구하면 그때 줄을 추가해 적으십시오.', { size: 17 }),
    bullet('이 파일은 구매자 본인 사용을 위한 서식입니다. 재배포 · 재판매는 하실 수 없습니다.', { size: 17 }),
  ], { title: '사용 가이드' });

  return d.Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, '사용가이드.docx'), b));
}

Promise.all([buildFresh(), buildCareer(), buildCoverLetter(), buildGuide()])
  .then(() => console.log('빌드 완료: 4종'))
  .catch((e) => { console.error(e); process.exit(1); });
