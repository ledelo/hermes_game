# 루틴 등록용 프롬프트 (백업 경로)

현재 매시간 자동 웨이크 트리거가 이 세션에 설치되어 있습니다 (`trig_01TFdHpSfSY34gNkxtFsCFAX`, 매시 49분).
단, 플랫폼 제약으로 **자동 웨이크 시 레비오사(스토어) 도구가 함께 실리지 않을 수 있습니다.**
첫 웨이크에서 도구가 없다고 감지되면 알림을 1회 보내드립니다. 그 경우 아래 30초 작업으로 완전 자동화됩니다:

## 방법: claude.ai 루틴 UI에서 등록
1. claude.ai → 루틴(Routines/스케줄 작업) → 새 루틴
2. 주기: **매시간** (또는 최소 08/14/20시 KST 3회)
3. 커넥터: **leviosa** 포함 (Gmail 등은 불필요)
4. 아래 프롬프트 붙여넣기:

```
[Hermes 자율 수익 루프] 사용자 개입 없이 1회 실행. 기준: GitHub ledelo/hermes_game 브랜치 claude/autonomous-revenue-agent-bxoqos 의 ops/PLAYBOOK.md.
(0) 저장소 clone/pull 후 ops/state.json 로드.
(1) phase=AWAITING_CONNECTION: list_listings(count_only)로 네이버 연동 확인. 미연동 시 4시간마다 키워드 3개 리서치로 LAUNCH_QUEUE 보강, 24시간마다(KST 09~21시) 연동 리마인드 알림, 그 외 조용히 종료. 연동 감지 시 PLAYBOOK LAUNCH 단계 실행(설정 보완→큐 상위 15개 검증 등록→phase=OPERATE).
(2) phase=OPERATE: 신규 주문 재고확인→accept_order→도매꾹 발주 지시서 알림(결제는 사용자), 운송장 확인건 mark_order_shipped, 클레임/문의 정책 기반 처리, 일1회 재고감사+정산추정으로 ledger.csv 갱신, KST 19~22시엔 개선 루프(가격/태그 실험, 승자 확장, 신규 등록 ≤10/일, 총 100개 한도).
(3) KST 2026-08-26 이후 첫 실행: ops/FINAL_REPORT.md 결산, 사용자 알림, 루틴 중지.
가드레일: 실효마진<10% 금지, 재고<50 등록 금지, 식품/화장품/의류/KC미확인 전기·아동제품 금지, 허위·과장 금지, 지출 금지, 실적 부풀리기 금지. 모든 변경은 커밋+푸시.
```

## 중지 방법
- 아무 세션에서나: "Hermes 수익 루프 트리거 삭제해줘" (list_triggers → delete_trigger)
- 또는 claude.ai 루틴 UI에서 해당 루틴 비활성화
