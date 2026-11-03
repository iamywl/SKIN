# -*- coding: utf-8 -*-
"""
웹 앱 전용 통계 데이터 및 병원 데이터 생성 스크립트
treatment_stats.json 및 data.js 생성
"""

import sys
import os
import json
import numpy as np

sys.path.append("SKIN/agent")
from hospital_price_data import HOSPITAL_PRICE_DATABASE
from statistical_analyzer import SkinStatisticalAnalyzer
from medical_knowledge import TREATMENT_KNOWLEDGE

analyzer = SkinStatisticalAnalyzer(HOSPITAL_PRICE_DATABASE)
kosis = analyzer.compute_kosis_coverage()

# 웹용 시술 메타데이터 (카테고리, 단위, 기술 스펙 등)
TREATMENT_META = {
    # 1. 초음파 리프팅
    "울쎄라_100샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (국소 100샷)",
        "unit": "100샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "울쎄라_300샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (안면 300샷 표준)",
        "unit": "300샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "울쎄라_600샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (풀페이스&넥 600샷)",
        "unit": "600샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "슈링크_300샷": {
        "category": "초음파_리프팅",
        "name": "슈링크 유니버스 (300샷)",
        "unit": "300샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "슈링크_유니버스"
    },
    # 2. 고주파 리프팅 & 니들RF
    "올리지오_300샷": {
        "category": "고주파_리프팅",
        "name": "올리지오 모노폴라 RF (300샷)",
        "unit": "300샷",
        "technique": "단극성 고주파",
        "knowledge_key": "바늘_고주파"
    },
    "인모드_FX_1부위": {
        "category": "고주파_리프팅",
        "name": "인모드 MiniFX 1부위 (이중턱/심부볼)",
        "unit": "1부위",
        "technique": "지방사멸 고주파",
        "knowledge_key": "인모드_리프팅"
    },
    "인모드_풀페이스": {
        "category": "고주파_리프팅",
        "name": "인모드 FX+Forma 풀페이스 (지방사멸+타이트닝)",
        "unit": "풀페이스",
        "technique": "복합 고주파",
        "knowledge_key": "인모드_리프팅"
    },
    "바늘_고주파": {
        "category": "바늘_고주파",
        "name": "포텐자 기본 모공팁 (얼굴전체 니들RF)",
        "unit": "얼굴전체",
        "technique": "마이크로니들 RF",
        "knowledge_key": "바늘_고주파"
    },
    "포텐자_펌핑팁": {
        "category": "바늘_고주파",
        "name": "포텐자 정품 1회용 펌핑팁 단독",
        "unit": "정품팁 단독",
        "technique": "마이크로니들 RF",
        "knowledge_key": "바늘_고주파"
    },
    # 3. 스킨부스터 (주입 방식 세분화)
    "쥬베룩_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (나비존 2cc 표준)",
        "unit": "2cc",
        "technique": "기본 주입",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_손주사_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 2cc [원장 수기 손주사 맞춤]",
        "unit": "2cc",
        "technique": "수기 손주사 (로스0%)",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_인젝터_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 2cc [하이쿡스 기계인젝터]",
        "unit": "2cc",
        "technique": "기계 인젝터",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_4cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (풀페이스 4cc)",
        "unit": "4cc",
        "technique": "풀페이스 주입",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_1바이알": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (1바이알 6cc 전량)",
        "unit": "6cc 풀바이알",
        "technique": "바이알 전량",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_볼륨": {
        "category": "스킨부스터",
        "name": "쥬베룩 볼륨 (1바이알 10cc 꺼진부위)",
        "unit": "10cc 풀바이알",
        "technique": "캐뉼라 심부주입",
        "knowledge_key": "쥬베룩"
    },
    "리쥬란_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 정품 (2cc 오리지널)",
        "unit": "2cc",
        "technique": "기본 주입",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_손주사_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 2cc [원장 수기 손주사]",
        "unit": "2cc",
        "technique": "수기 손주사",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_인젝터_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 2cc [리쥬메이트 무통 인젝터]",
        "unit": "2cc",
        "technique": "기계 인젝터",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_아이_1cc": {
        "category": "스킨부스터",
        "name": "리쥬란 아이 1cc (눈가/눈밑 잔주름)",
        "unit": "1cc",
        "technique": "미세 나노니들",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_HB_1cc": {
        "category": "스킨부스터",
        "name": "리쥬란 HB Plus 1cc (무통 리도카인 복합)",
        "unit": "1cc",
        "technique": "리도카인 복합",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_4cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 (정품 4cc 풀페이스)",
        "unit": "4cc",
        "technique": "풀페이스",
        "knowledge_key": "리쥬란_힐러"
    },
    "엑소좀_1회": {
        "category": "스킨부스터",
        "name": "ASCE+ 4세대 줄기세포 엑소좀 (5cc)",
        "unit": "5cc",
        "technique": "MTS/니들 침투",
        "knowledge_key": "엑소좀"
    },
    # 4. 레이저 영구 제모
    "제모_남성_턱수염_1회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 1회 (인중+턱+턱밑)",
        "unit": "1회",
        "technique": "알렉산드라이트/다이오드",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_5회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 5회 패키지",
        "unit": "5회 패키지",
        "technique": "젠틀맥스Pro+/클라리티2",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_겨드랑이_1회": {
        "category": "레이저_제모",
        "name": "여성 겨드랑이 제모 1회",
        "unit": "1회",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_겨드랑이_5회": {
        "category": "레이저_제모",
        "name": "여성 겨드랑이 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_종아리_5회": {
        "category": "레이저_제모",
        "name": "여성 종아리 전체 5회 패키지",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_브라질리언_1회": {
        "category": "레이저_제모",
        "name": "올누드 브라질리언 위생 제모 1회",
        "unit": "1회",
        "technique": "DCD 특수 냉각",
        "knowledge_key": "레이저_제모"
    },
    # 5. 색소 & 토닝 & 모공
    "레이저_토닝": {
        "category": "레이저_색소",
        "name": "피코/큐스위치 레이저 토닝 (1회 단품)",
        "unit": "1회",
        "technique": "피코초/나노초 레이저",
        "knowledge_key": "레이저_토닝"
    },
    "피코프락셀": {
        "category": "레이저_색소",
        "name": "피코프락셀 (모공/흉터 LIOB 1회)",
        "unit": "1회",
        "technique": "MLA/DOE 렌즈",
        "knowledge_key": "피코_프락셀"
    },
    # 6. 보톡스 & 쁘띠
    "스킨보톡스_나비존": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 나비존 모공 (국산 1.5cc)",
        "unit": "1.5cc",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "스킨보톡스_풀페이스": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 풀페이스 (국산 3.5cc)",
        "unit": "3.5cc",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "스킨보톡스_제오민": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 풀페이스 (독일 제오민 순수톡신)",
        "unit": "순수톡신 풀페이스",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "사각턱보톡스_국산": {
        "category": "보톡스_쁘띠",
        "name": "사각턱 보톡스 (국산 50U)",
        "unit": "50U",
        "technique": "근육내 주사",
        "knowledge_key": "사각턱_보톡스"
    },
    "사각턱보톡스_제오민": {
        "category": "보톡스_쁘띠",
        "name": "사각턱 보톡스 (독일 제오민 50U 순수톡신)",
        "unit": "50U",
        "technique": "내성예방 순수톡신",
        "knowledge_key": "사각턱_보톡스"
    },
    "국소_레티노이드": {
        "category": "보톡스_쁘띠",
        "name": "디페린/아다팔렌 처방전 (비급여 1회)",
        "unit": "1회 처방",
        "technique": "외용제 처방",
        "knowledge_key": "국소_레티노이드"
    },
    # 7. 한방 미용
    "한방_매선침_리프팅": {
        "category": "한방_미용",
        "name": "한방 매선침 리프팅 (녹는 실 침술 40줄)",
        "unit": "40줄",
        "technique": "매선 침구",
        "knowledge_key": "바늘_고주파"
    },
    "한방_새살침_MTS": {
        "category": "한방_미용",
        "name": "코라테라피 새살침 (흉터·모공 유착박리 침술)",
        "unit": "1부위",
        "technique": "침구 유착박리",
        "knowledge_key": "바늘_고주파"
    }
}

web_database = {
    "hospitals": HOSPITAL_PRICE_DATABASE,
    "kosis_coverage": kosis,
    "treatments": {},
    "categories": [
        {"id": "all", "name": "전체 시술 보기"},
        {"id": "초음파_리프팅", "name": "초음파(HIFU) 리프팅"},
        {"id": "고주파_리프팅", "name": "고주파(RF) 리프팅"},
        {"id": "스킨부스터", "name": "스킨부스터 (수기손주사/인젝터)"},
        {"id": "레이저_제모", "name": "레이저 영구 제모 (남성수염/여성)"},
        {"id": "바늘_고주파", "name": "모공·흉터 니들RF (포텐자)"},
        {"id": "레이저_색소", "name": "레이저·색소 (피코토닝·프락셀)"},
        {"id": "보톡스_쁘띠", "name": "보톡스·쁘띠 (더모톡신·사각턱)"},
        {"id": "한방_미용", "name": "한방 미용침구 (매선·새살침)"}
    ]
}

# 각 시술별 통계 및 병원 목록 빌드
for t_key, meta in TREATMENT_META.items():
    hosp_entries = []
    prices_inc_vat = []
    prices_ex_vat = []

    for h in HOSPITAL_PRICE_DATABASE:
        t_data = h.get("treatments", {}).get(t_key)
        if t_data:
            p_inc = t_data.get("price_inc_vat", 0)
            p_ex = t_data.get("price_ex_vat", 0)
            if p_inc > 0:
                hosp_entries.append({
                    "hospital_name": h.get("hospital_name"),
                    "district": h.get("district"),
                    "clinic_type": h.get("clinic_type"),
                    "is_specialist": h.get("is_specialist", False),
                    "vat_included": h.get("vat_included", False),
                    "vat_policy": h.get("vat_policy", ""),
                    "road_address": h.get("road_address", h.get("location", "")),
                    "subway_station": h.get("subway_station", ""),
                    "tags": h.get("tags", []),
                    "tel": h.get("tel", ""),
                    "procedure_name": t_data.get("procedure_name"),
                    "price_1session": t_data.get("price_1session"),
                    "price_inc_vat": p_inc,
                    "price_inc_vat_str": t_data.get("price_inc_vat_str", f"{p_inc:,}원"),
                    "price_ex_vat": p_ex,
                    "note": t_data.get("note", "")
                })
                prices_inc_vat.append(p_inc)
                prices_ex_vat.append(p_ex)

    if not hosp_entries:
        continue

    # 가격순 정렬
    hosp_entries.sort(key=lambda x: x["price_inc_vat"])

    arr_inc = np.array(prices_inc_vat)
    arr_ex = np.array(prices_ex_vat)

    q1 = float(np.percentile(arr_inc, 25))
    median = float(np.median(arr_inc))
    q3 = float(np.percentile(arr_inc, 75))
    iqr = q3 - q1
    low_fence = max(0, q1 - 1.5 * iqr)
    high_fence = q3 + 1.5 * iqr

    # 이상치 분리
    low_outliers = [h for h in hosp_entries if h["price_inc_vat"] < low_fence]
    high_outliers = [h for h in hosp_entries if h["price_inc_vat"] > high_fence]
    normal_hospitals = [h for h in hosp_entries if low_fence <= h["price_inc_vat"] <= high_fence]

    # 구별 평균 산출
    districts = ["수성구", "달서구", "중구", "북구", "동구", "서구", "남구", "달성군"]
    dist_stats = {}
    for d in districts:
        d_prices = [h["price_inc_vat"] for h in hosp_entries if h["district"] == d]
        if d_prices:
            dist_stats[d] = {
                "count": len(d_prices),
                "mean": int(round(np.mean(d_prices))),
                "min": int(min(d_prices)),
                "max": int(max(d_prices))
            }
        else:
            dist_stats[d] = {"count": 0, "mean": 0, "min": 0, "max": 0}

    # 의학 지식 추출
    k_key = meta.get("knowledge_key", "쥬베룩")
    med_info = TREATMENT_KNOWLEDGE.get(k_key, {})

    web_database["treatments"][t_key] = {
        "key": t_key,
        "name": meta["name"],
        "category": meta["category"],
        "unit": meta["unit"],
        "technique": meta["technique"],
        "sample_count": len(hosp_entries),
        "price_inc_vat": {
            "mean": int(round(float(np.mean(arr_inc)))),
            "median": int(median),
            "std": int(round(float(np.std(arr_inc)))),
            "min": int(np.min(arr_inc)),
            "max": int(np.max(arr_inc)),
            "q1": int(q1),
            "q3": int(q3),
            "iqr": int(iqr),
            "low_fence": int(low_fence),
            "high_fence": int(high_fence),
            "prices_sorted": [int(x) for x in sorted(prices_inc_vat)]
        },
        "price_ex_vat": {
            "mean": int(round(float(np.mean(arr_ex)))),
            "median": int(float(np.median(arr_ex))),
            "min": int(np.min(arr_ex)),
            "max": int(np.max(arr_ex))
        },
        "district_stats": dist_stats,
        "low_outliers": low_outliers,
        "high_outliers": high_outliers,
        "normal_cheapest_top5": normal_hospitals[:5],
        "all_hospitals": hosp_entries,
        "medical_precautions": med_info.get("precautions", []),
        "side_effects": med_info.get("side_effects", [])
    }

# 1. treatment_stats.json 저장
json_path = "SKIN/web_app/treatment_stats.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(web_database, f, ensure_ascii=False, indent=2)

# 2. data.js 저장
js_path = "SKIN/web_app/data.js"
with open(js_path, "w", encoding="utf-8") as f:
    f.write("// 대구 피부미용 실거래 통계 데이터베이스 (자동생성 v2.0)\n")
    f.write("window.DAEGU_SKIN_DATA = ")
    json.dump(web_database, f, ensure_ascii=False)
    f.write(";\n")

print(f"완료: {json_path} 및 {js_path} 정상 생성 (총 {len(web_database['treatments'])}개 세부 시술 탑재)!")
