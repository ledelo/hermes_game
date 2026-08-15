# PLAYBOOK — 자율 수익 루프 운영 규칙

> 매 웨이크 시작: `git pull origin claude/autonomous-revenue-agent-bxoqos` → `ops/state.json` 읽기 → 아래 상태머신 1회 실행 → 변경사항 커밋+푸시.
> 도구 로딩: leviosa 도구가 안 보이면 ToolSearch 키워드 검색(예: `+list_listings`, `+create_listing_from_supplier`)으로 로드한다. MCP 재연결 시 도구 이름의 접두사(UUID)가 바뀔 수 있으므로 항상 베이스 이름으로 검색할 것. 컨테이너가 재생성됐다면 저장소를 다시 clone/checkout 후 진행.

## 목표
- 기한: 2026-08-26 (KST) / 목표: 추정 순수익 ₩1,000,000
- 순수익 정의: 네이버 정산예정액(수수료 차감 후) − 도매원가 − 공급사 배송비. `estimate_payouts(detailed=true)` + LAUNCH_QUEUE 원가로 계산.
- 정직 원칙: 목표는 목표일 뿐, 실적은 ledger.csv에 있는 그대로 보고한다. 과장 금지.

## 절대 가드레일 (위반 금지)
1. **마진 하한**: 옵션 포함 실효 순마진 10% 미만 상품은 등록/유지 금지. 할인도 하한 안에서만.
2. **재고 안전**: 공급사 재고 50 미만 상품 신규 등록 금지. 주문 수락 전 반드시 `inspect_supplier_product`로 재고 재확인. 재고 없으면 수락 대신 취소 처리.
3. **정직한 상품정보**: 공급사 정보에 없는 성능/효과 주장 금지. 가짜 리뷰·조작·허위 긴급성 금지. 원산지는 공급사 정보 기반으로 정확 기재.
3b. **상표/지재권**: 타사 상표명(맥세이프, 캐릭터명 등)을 상품명에 쓰지 않는다(리브랜딩 시 제거). 캐릭터/브랜드 도안 상품은 정품 라이선스 확인 전 등록 금지.
3c. **개인정보**: 등록 시 consent='disclosure'(제3자 제공 고지)를 기본 적용. 발주 시 구매자 정보는 배송에 필요한 최소한만 사용.
4. **카테고리 제외**: 식품/화장품/사료/생리대(단위가격 대상 — API 거부됨), 의류·신발(사이즈 반품 리스크), 어린이 전용 제품·전기용품 중 KC 인증 확인 불가 상품(LED/충전식 포함 — 상세페이지에 인증번호 확인된 경우만 허용).
5. **지출 권한 없음 + 무지출 모드 (2026-08-12 사용자 지시)**: 광고비 집행, 유료 구독, AI 커버 등 건당 과금 기능, 사용자 지갑에서 나가는 모든 결제는 하지 않는다. 도매 발주(결제)는 사용자에게 알림으로 위임하되 지시서에 해당 주문의 **정산예정액(이미 고객이 결제한 금액)을 병기**해 선지출이 회수 확정 자금임을 보여준다.
   - **플로트 캡**: 리스팅 등록 시 노출 재고를 3~5개로 설정해 동시 미정산 발주액이 ₩200,000을 넘지 않게 한다. 정산 입금이 확인되면 회수액만큼 재고 증량(자가증식 구조: 판매대금이 다음 원가를 낸다).
   - 품절 표시로 기회손실이 나더라도 캡을 깨지 않는다. 캡 상향은 사용자만 지시 가능.
6. **고객 응대**: 존댓말, 사실만, 약속은 스토어 정책 범위 내에서만. 배송 예상은 "영업일 2~4일"로 안내.
7. 밤(KST 22시~08시)에는 PushNotification 보내지 않는다 (주문 발주 알림은 예외).

## 상태머신

### 대기 중 사전검증 루틴 (2026-08-13 신설 — "대기 틱은 놀지 않는다")
- 연동 대기 틱마다 LAUNCH 후보를 앞에서부터 `inspect_supplier_product`(배치 모드)로 사전 실사: 옵션별 추가금·조합 재고·실배송비 확인 → 최악 조합 마진 ≥10% 검증 → 통과 시 `LAUNCH_READY`, 가격 조정 필요 시 인상가 기록, 시장성 상실 시 DROP.
- **도구 버그 주의**: `min/max_supply_price` 필드는 수량 티어 문자열("1+2140|50+2130")을 숫자로 잘못 이어붙임 — 신뢰 금지, `supply_price` 티어 문자열을 직접 파싱(1~3개 구간 단가 사용). 배송비는 `delivery.defaultFee` → `fee` → `tbl` 첫 구간 순으로 파싱.
- 리서치 단계의 배송비는 실사와 다를 수 있음(48557930 사례: 1,000→3,000원으로 원가 역전) — LAUNCH_READY 없이 등록 금지.
- **가격 교정은 반드시 큐 테이블 본문 셀을 직접 수정한다 (배치 요약 각주에만 적지 말 것)**. 2026-08-15 저녁 재검증에서 40209730·65225745가 교정 각주는 있으나 테이블 셀이 옛 가격으로 남아 있어 재등록 시 마진 8.2%/8.5%로 가드레일 위반이 날 뻔한 사례 발견. LAUNCH는 테이블 셀을 읽으므로 각주만으로는 보호되지 않는다.
- **저재고(<1000) 항목은 3일 이상 경과 시 재실사**한다 — 공급 재고·옵션 추가금은 며칠 새 바뀔 수 있음(19-22시 저녁 루프에서 수행).

### PHASE = AWAITING_CONNECTION (현재)
1. `list_listings(count_only=true)` 호출 → `NAVER_NOT_CONNECTED`면 아직 미연동.
2. 미연동 시:
   - `state.last_research_at`이 4시간 이상 전이면 **리서치 v2 (수요 우선)**: ① 트렌드 스캔 선행 — WebSearch로 최근 한국 커머스 트렌드 기사·급증 품목 확인(주 1회 이상 갱신, 출처를 큐에 기록). ② 스캔에서 도출된 키워드 + 시즌 캘린더 키워드로 `find_supplier_opportunities` 실행. ③ S/A등급 + 가드레일 통과분만 큐에 추가하되, 수요 근거(트렌드 출처/시즌 확정) 있는 품목에 ★태그 — LAUNCH와 확장 시 ★ 우선. ④ 구글 트렌드 일간(연예 위주)은 쇼핑 신호로 쓰지 않는다(2026-08-13 검증). `last_research_at` 갱신.
   - `state.last_reminder_at`이 24시간 이상 전이고 KST 09~21시면: PushNotification 1회 "네이버 연동 대기 중" 리마인드, `last_reminder_at` 갱신.
   - 그 외에는 아무것도 하지 않고 조용히 종료 (토큰 절약).
3. 연동 감지되면 → PHASE = LAUNCH 로 전환하고 즉시 LAUNCH 실행.

### PHASE = LAUNCH (연동 감지 직후 1회)
0. **트리거 빈도 복원**: list_triggers에서 'Hermes 자율 수익 루프' 찾아 update_trigger로 cron '0 * * * *'(매시간) 복원 — 운영 단계 주문 SLA 대응. (대기 중엔 2시간 간격으로 감축돼 있음)
1. `list_store_addresses` → 주소 ID 확보. `save_store_setup`에 shipping/return address id, 주소록의 전화번호(있으면), store_name 기반 brand_prefix 저장.
2. `get_store_setup`으로 최종 확인. phone이 없으면 톡톡 안내로 대체하고 진행.
3. LAUNCH_QUEUE 상위(Tier1 → Tier2)부터 최대 15개 등록. 상품별:
   a. `inspect_supplier_product` — 재고≥50, 옵션별 마진 재검증 (`sale_price >= total_cost / (1-0.066-0.10)` 최소식).
   b. `find_listing_categories`로 리프 카테고리 확보 (스로틀 시 유사 상품 카테고리 재사용).
   c. `create_listing_from_supplier` (target_margin_pct=18, use_discount=true, 상품명은 검색 키워드 조합으로 리브랜딩, features/highlights 사실 기반 작성).
   d. 성공 시 state.listings_created에 {item_no, product_id, origin_product_no, cost, price, margin} 기록.
4. PushNotification: "스토어 오픈: N개 상품 등록 완료".
5. PHASE = OPERATE.

### PHASE = OPERATE (매시간)
**매 웨이크 (경량)**:
1. `get_order_backlog(days=3)` — 신규 결제 주문 있으면:
   a. `inspect_supplier_product`로 재고 확인 → 있으면 `accept_order` (발주확인).
   b. **도매꾹 발주 지시서** 생성: 상품/옵션/수량/공급사 링크 정리 → PushNotification "주문 N건 발주 필요" (이건 결제라 사용자만 가능). journal에도 기록.
   c. 재고 없으면 수락하지 않고 품절 취소 처리 + 해당 리스팅 OUTOFSTOCK 전환.
2. 발송 대기 주문 중 운송장 확인되는 건 `mark_order_shipped`.
3. `review_claims` — 발송 전 취소는 승인(고객 친화), 반품/교환은 정책 기반 처리(첫 라이브 실행은 단건 테스트 후 확대). 애매하면 dry_run 미리보기 + 사용자 알림.
4. `draft_customer_replies` — 미답변 문의 있으면 사실 기반 존댓말 답변 작성 후 dry_run=false로 발송.

**일 1회 (state 타임스탬프 기준)**:
- `audit_supplier_stock` — margin_critical → 가격 인상 or OUTOFSTOCK; 품절 → OUTOFSTOCK.
- `estimate_payouts(어제~오늘, detailed=true)` → ledger.csv에 일자별 행 추가 (주문수/매출/추정순익/누적).
- journal/YYYY-MM-DD.md 작성.

**저녁 웨이크 1회 (KST 19~22시): 개선 루프 — 성과는 계속 나아져야 한다**
1. ledger 분석: 판매 발생 카테고리 → 유사 상품 리서치해 다음날 등록 후보 보강 (승자 2배수).
2. 등록 3일 경과 & 판매 0 리스팅: 가격 5% 인하(마진 하한 내) 또는 `update_listing`으로 태그/상품명 개선. 7일 경과 & 판매 0 → SUSPENSION 하고 큐의 새 상품으로 교체.
3. 신규 등록: 하루 최대 10개 (품질 우선, 가드레일 통과분만). 총 리스팅 100개 한도.
4. 실험 기록: journal에 "가설 → 변경 → 결과(다음날 확인)" 형식으로 남겨 다음 루프가 이어받게 한다.
5. **무자본 실험 트랙**: 저녁 루프마다 무지출 성장 아이디어 1개를 평가해 journal에 기록한다(예: 상품명/태그 SEO 리팩터링, 시즌 키워드 선점, 저가 볼륨 상품 비중 조정, 묶음 옵션 구성). 계정 개설·결제·인증이 필요한 아이디어는 사용자 승인 대기 목록에만 적는다. 검증 안 된 '무자본 부업' 류(리워드앱, 설문 등)는 시급 대비 가치가 없으므로 제안하지 않는다.

### PHASE = FINAL (2026-08-26 KST 이후 첫 웨이크)
1. ledger 합산 → 최종 결산 보고서 `ops/FINAL_REPORT.md` 작성 (목표 대비 실적, 잘된 것/안된 것, 인수인계).
2. 커밋+푸시, PushNotification으로 결과 통지.
3. `list_triggers`에서 이 루프 트리거 찾아 `update_trigger(enabled=false)`. 미발송 주문 등 미결 사항 있으면 비활성화 대신 사용자에게 알리고 유지.

## 실패 처리
- 도구 오류/스로틀: 해당 작업 스킵하고 다음 웨이크에 재시도. 같은 작업 3회 연속 실패 시 journal에 기록하고 사용자 알림.
- 네이버 API 한도(429): 15~20분 유휴가 필요하므로 그 웨이크는 종료.
- 절대 하지 말 것: 실패를 성공으로 기록, 추정치를 실측처럼 보고.
