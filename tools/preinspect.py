#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LAUNCH 후보 사전실사 판정기.
사용: python3 preinspect.py <inspect결과파일> '<plan_json:{"item_no":계획가,...}>'
- supply_price 티어 문자열("1+2140|50+2130")을 직접 파싱 (min/max_supply_price 필드는 버그로 신뢰 금지)
- 옵션 최악 조합(가용 재고>0) 추가금 반영, 실배송비는 defaultFee→fee→tbl 순
- 판정: 최악마진>=10% & 재고>=50 → PASS / 재고미달 STOCK_FAIL / 마진미달 PRICE_UP(권장가 병기, 최악마진 12% 기준)
"""
import json, sys, math
FEE=0.066
def tier1(s):
    try: return min(int(seg.split("+")[1]) for seg in str(s).split("|") if int(seg.split("+")[0])<=3)
    except Exception:
        try: return int(s)
        except Exception: return None
def fee_of(d):
    for k in ("defaultFee","fee"):
        v=d.get(k)
        if v:
            try: return int(v)
            except Exception: pass
    tbl=d.get("tbl") or ""
    try: return int(tbl.split("|")[0].split("+")[1])
    except Exception: return 3000
def main():
    by=json.loads(json.load(open(sys.argv[1]))["result"])["items_by_no"]
    plan=json.loads(sys.argv[2])
    res={"PASS":[], "PRICE_UP":[], "STOCK_FAIL":[], "ERROR":[]}
    for no,p in plan.items():
        it=by.get(no)
        if not it or not isinstance(it,dict) or not it.get("supply_price"):
            res["ERROR"].append(no); print(f"{no}: 데이터 없음/오류"); continue
        base=tier1(it["supply_price"]); ship=fee_of(it.get("delivery") or {}); inv=it.get("inventory",0)
        if base is None: res["ERROR"].append(no); print(f"{no}: 단가 파싱 실패 {it['supply_price']}"); continue
        opts=(it.get("options") or {}).get("combinations") or []
        live=[o for o in opts if o.get("available") and o.get("stock",0)>0]
        smax=max((o.get("surcharge",0) for o in live), default=0)
        wc=base+smax+ship
        wm=(p-p*FEE-wc)/p*100
        if inv<50: v="STOCK_FAIL"
        elif wm>=10: v="PASS"
        else: v="PRICE_UP"
        rec=math.ceil(wc/(1-FEE-0.12)/100)*100 if v=="PRICE_UP" else ""
        res[v].append(no)
        print(f"{no}: 재고{inv} 단가{base} 추가금{smax} 배송{ship} 계획{p} 최악마진{wm:.1f}% → {v}{' 권장가 '+str(rec) if rec else ''}")
    print("\n요약:", {k:len(v) for k,v in res.items()})
if __name__=="__main__": main()
