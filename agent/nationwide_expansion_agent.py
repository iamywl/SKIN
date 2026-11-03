# -*- coding: utf-8 -*-
"""
전국 미용의료 데이터 자동 확장 에이전트 (Nationwide Expansion Agent)
대구를 넘어 서울(강남/홍대/잠실), 부산(서면/해운대), 인천(송도/부평) 등
전국 모든 시·군·구 데이터를 AI 에이전트가 10초 만에 무결점으로 자동 확장/병합할 수 있도록 지원하는 프레임워크입니다.
"""

from __future__ import annotations
import os
import sys
import json
import argparse
from typing import Dict, List, Any

# 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.medical_knowledge import TREATMENT_KNOWLEDGE
from agent.skin_qa_validator import SkinQAValidator
from agent.statistical_analyzer import SkinStatisticalAnalyzer


class NationwideExpansionAgent:
    """
    타 지역 비급여 피부과 데이터 자동 확장 및 통합 에이전트
    """

    SUPPORTED_REGIONS = {
        "서울": ["강남구", "서초구", "송파구", "마포구", "용산구", "영등포구"],
        "부산": ["부산진구", "해운대구", "수영구", "동래구", "남구"],
        "인천": ["연수구", "남동구", "부평구"],
        "대전": ["유성구", "서구"],
        "광주": ["서구", "광산구"],
        "경기": ["성남시_분당구", "수원시_팔달구", "고양시_일산동구"]
    }

    def __init__(self, master_db_path: str = "agent/hospital_price_data.py"):
        self.master_db_path = master_db_path

    def scaffold_new_region(self, metro: str, district: str, hira_population: int) -> Dict[str, Any]:
        """
        새로운 시·군·구의 데이터 템플릿과 HIRA 심평원 모수 기준을 자동 스캐폴딩합니다.
        """
        print(f"🚀 [NationwideExpansion] {metro} {district} (심평원 모수: {hira_population}개소) 신규 확장 스캐폴딩 시작...")

        template = {
            "region_meta": {
                "metro": metro,
                "district": district,
                "hira_population": hira_population,
                "standard_currency": "KRW",
                "vat_mandatory": True  # 부가가치세법 제35조 의무 적용
            },
            "sample_hospitals_template": [
                {
                    "metro": metro,
                    "district": district,
                    "hospital_name": f"{district} OO피부과의원",
                    "category": "피부과 전문의",
                    "clinic_type": "전문의의원",
                    "is_specialist": True,
                    "vat_included": False,
                    "vat_policy": "VAT 10% 별도",
                    "road_address": f"{metro} {district} 중심상업로 100",
                    "subway_station": f"{district}역 1번 출구 도보 1분",
                    "tags": ["피부과전문의", "울쎄라정품인증", "젠틀맥스Pro+보유", "VAT별도주의", "전용주차장"],
                    "treatments": {
                        "울쎄라_300샷": {
                            "procedure_name": "울쎄라 정품 안면 300샷",
                            "price_ex_vat": 800000,
                            "price_inc_vat": 880000,
                            "price_inc_vat_str": "880,000원",
                            "note": "DeepSEE 실시간 초음파 모니터링 (VAT 별도)"
                        },
                        "쥬베룩_2cc": {
                            "procedure_name": "쥬베룩 스킨 2cc [수기 손주사 1:1 맞춤]",
                            "price_ex_vat": 220000,
                            "price_inc_vat": 242000,
                            "price_inc_vat_str": "242,000원",
                            "note": "원장 직접 손주사 (로스 0%)"
                        },
                        "제모_남성_턱수염_5회": {
                            "procedure_name": "남성 턱수염 전체 5회 패키지",
                            "price_ex_vat": 500000,
                            "price_inc_vat": 550000,
                            "price_inc_vat_str": "550,000원",
                            "note": "캔델라 젠틀맥스 프로 플러스 DCD 냉각"
                        }
                    }
                }
            ]
        }
        return template

    def validate_and_merge(self, new_hospitals: List[Dict[str, Any]]) -> bool:
        """
        신규 지역 데이터를 병합하기 전 100점 만점 QA 무결성 검증을 수행합니다.
        """
        print(f"🔍 [NationwideExpansion] {len(new_hospitals)}개 병원 데이터 무결성 검증 중...")
        validator = SkinQAValidator()
        score, report = validator.evaluate_dataset(new_hospitals)

        print(f"📊 QA 검증 점수: {score}/100점")
        if score < 85.0:
            print("❌ [검증 탈락] 데이터 기준 미달로 병합이 중단되었습니다:")
            for issue in report:
                print(f"  • [{issue.get('severity')}] {issue.get('message')}")
            return False

        print("✅ [검증 통과] 신규 지역 데이터가 무결성 기준을 통과했습니다.")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="따꼼 빠꼼 전국 미용의료 데이터 자동 확장 에이전트")
    parser.add_argument("--metro", type=str, default="서울", help="광역시/도 (예: 서울, 부산, 인천 등)")
    parser.add_argument("--district", type=str, default="강남구", help="시/군/구 (예: 강남구, 해운대구 등)")
    parser.add_argument("--pop", type=int, default=120, help="KOSIS 심평원 등록 의원 모수")

    args = parser.parse_args()
    agent = NationwideExpansionAgent()
    result = agent.scaffold_new_region(args.metro, args.district, args.pop)
    
    out_file = f"expansion_{args.metro}_{args.district}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"🎉 성공적으로 신규 지역 스캐폴딩 파일이 생성되었습니다: {out_file}")
    print("👉 AI 에이전트(Claude, GPT, Antigravity)에게 이 파일을 전달하여 실거래가를 채운 뒤 병합하세요!")
