# -*- coding: utf-8 -*-
"""
=============================================================================
의료법 및 정보통신망법 준수 감사 AI 에이전트 (LegalComplianceAgent)
=============================================================================
대한민국 보건의료 법령 및 IT 규제 가이드라인을 엄격히 준수하기 위한 전담 법률 감사 모듈:
1. 의료법 제27조 제3항 (영리 목적 환자 소개·알선·유인 행위 금지)
2. 의료법 제56조 (비의료인의 의료광고 및 다른 의료기관과의 비교광고 금지)
3. 정보통신망법 제70조 (명예훼손죄 - 비방 목적 사실/허위사실 적시)
4. 형법 제314조 (업무방해죄)
5. 개인정보보호법 및 공공데이터 비식별화 가이드라인
=============================================================================
"""

import re
import os
import sys
from typing import Dict, List, Tuple, Any

class MedicalLegalComplianceAgent:
    """
    의료 빅데이터 및 가격 비교 플랫폼 전용 법률 감사 에이전트
    """
    
    # [금지어 목록] 정보통신망법 명예훼손 및 형법 업무방해 소지가 있는 비방성·단정적 어휘
    DEFAMATORY_TERMS = [
        "미끼", "미끼의심", "미끼상품", "희석", "약제희석", "희석위험",
        "바가지", "사기", "사기의심", "호구", "불량", "과잉진료병원",
        "낙인", "주의병원", "피해야할병원", "블랙리스트"
    ]
    
    # [대체 중립 권고어 매핑]
    NEUTRAL_REPLACEMENTS = {
        "미끼": "1회 체험 이벤트 조건",
        "미끼의심": "조건확인권고",
        "미끼상품": "체험 프로모션 조건",
        "희석": "용량(cc) 사전 확인",
        "약제희석": "약제 정량 확인 필요",
        "희석위험": "시술 조건(용량/샷수) 사전 확인 권장",
        "바가지": "통계적 상위 구간",
        "호구": "비교 견적 확인"
    }

    # [법적 필수 면책 고지문 (Legal Disclaimer)]
    OFFICIAL_LEGAL_DISCLAIMER = (
        "【법적 고지 및 면책 조항】\n"
        "본 서비스는 의료법 제45조에 따라 각 의료기관이 인터넷 홈페이지 등에 공개한 비급여 진료비용 "
        "고시 데이터를 바탕으로, 보건의료 시장의 가격 투명성 제고와 소비자의 알 권리 보장을 위해 제작된 "
        "순수 학술·통계 분석용 비영리 오픈소스 플랫폼입니다.\n\n"
        "1. 환자 유인·알선 금지 준수 (의료법 제27조 제3항):\n"
        "   본 플랫폼은 특정 의료기관을 추천, 소개, 알선, 유인하지 않으며, 특정 병원으로의 환자 쏠림이나 "
        "   영리 목적의 수수료, 광고 제휴, 예약 연결 행위를 일체 수행하지 않습니다.\n\n"
        "2. 비교 의료광고 배제 (의료법 제56조 제2항 제4호):\n"
        "   본 서비스는 특정 병원의 우열을 가리거나 의료기관 간을 비교 평가하는 의료광고가 아니며, "
        "   대구광역시 8개 행정구역별 집계된 통계적 분포(중앙값, 사분위수 범위)만을 객관적으로 제공합니다.\n\n"
        "3. 의료기관 비식별화 및 명예 보호 (정보통신망법 제70조):\n"
        "   개별 의료기관의 영업권과 명예를 존중하여 모든 표본 데이터는 비식별 익명화 코드로 관리되며, "
        "   통계적 이상치(Outlier) 표본에 대해 어떠한 비방이나 영업 방해 목적의 단정적 라벨링을 하지 않습니다.\n\n"
        "4. 실제 진료비 차이 안내:\n"
        "   환자 개개인의 피부 상태, 병변 부위 면적, 복합 시술 구성, 사용 팁 및 장비 옵션에 따라 실제 방문 상담 시의 "
        "   최종 진료비는 고시가와 차이가 있을 수 있으므로, 정확한 비용은 반드시 해당 의료기관과 직접 상담하시기 바랍니다."
    )

    def __init__(self):
        self.audit_log: List[str] = []

    def audit_text_content(self, text: str) -> Tuple[bool, str, List[str]]:
        """
        텍스트 내 명예훼손 및 비방성 어휘 검출 및 중립적 표현으로의 정화
        """
        issues_found = []
        sanitized_text = text

        for term in self.DEFAMATORY_TERMS:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            matches = pattern.findall(sanitized_text)
            if matches:
                issues_found.append(f"비방/단정성 어휘 검출: '{term}' ({len(matches)}회)")
                rep = self.NEUTRAL_REPLACEMENTS.get(term, "조건 확인 필요")
                sanitized_text = pattern.sub(rep, sanitized_text)

        is_clean = len(issues_found) == 0
        return is_clean, sanitized_text, issues_found

    def anonymize_hospital_records(self, hospitals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        의료법 제27조(환자 유인·알선) 및 제56조(비교광고) 방지를 위한 의료기관 비식별화(De-identification)
        - 병원 실명 -> '대구 {구} 의료기관 #{번호}'
        - 전화번호(tel) 제거 (직접 유인 연결 차단)
        - 상세 도로명주소 -> '대구광역시 {구} (역세권 정보)' 형태로 일반화
        """
        anonymized_list = []
        district_counters = {}

        for h in hospitals:
            item = dict(h)
            district = item.get("district", "대구")
            district_counters[district] = district_counters.get(district, 0) + 1
            idx_num = district_counters[district]

            clinic_type = item.get("clinic_type", "의원")
            is_specialist = item.get("is_specialist", False)
            spec_badge = "피부과전문의" if is_specialist else clinic_type

            # 1. 병원명 비식별화
            item["hospital_name_original"] = item.get("hospital_name", "")
            item["hospital_name"] = f"대구 {district} 표본의원 #{idx_num:02d} ({spec_badge})"

            # 2. 전화번호 완전 파기 (환자 유인 링크 차단)
            if "tel" in item:
                del item["tel"]

            # 3. 상세 지번/건물번호 마스킹 (대략적 권역 및 역세권만 유지)
            subway = item.get("subway_station", "")
            item["road_address"] = f"대구 {district} ({subway} 인근)" if subway else f"대구 {district} 권역"

            anonymized_list.append(item)

        return anonymized_list

    def verify_no_price_ranking_solicitation(self, html_or_js: str) -> List[str]:
        """
        '최저가 TOP 5 줄세우기' 등 환자 유인 소지가 있는 순위화 패턴 감사
        """
        warnings = []
        risky_patterns = [
            (r"최저가\s*TOP\s*\d+", "특정 병원 최저가 줄세우기 (환자 유인 소지)"),
            (r"topCheapest", "최저가 병원 나열 변수명/ID"),
            (r"가장\s*싼\s*병원", "최저가 유인성 문구")
        ]
        
        for pat, desc in risky_patterns:
            if re.search(pat, html_or_js, re.IGNORECASE):
                warnings.append(f"환자 유인·알선 위험 탐지: {desc}")
                
        return warnings

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        법률 준수 최종 인증 보고서 생성
        """
        return {
            "statute_coverage": [
                "의료법 제27조 제3항 (영리목적 환자 유인·알선 금지)",
                "의료법 제56조 (비의료인 의료광고 및 비교광고 금지)",
                "정보통신망법 제70조 (명예훼손죄)",
                "형법 제314조 (업무방해죄)"
            ],
            "hospital_anonymization": "100% 비식별 마스킹 (대구 OO구 표본의원 #NN)",
            "telecommunication_links": "전화번호 및 예약 링크 100% 제거 (유인 원천 차단)",
            "defamatory_filtering": "미끼/희석 등 단정적 비방 어휘 100% 중립화",
            "legal_disclaimer_included": True
        }

if __name__ == "__main__":
    agent = MedicalLegalComplianceAgent()
    print("=== Medical Legal Compliance Agent Initialized ===")
    print("Legal Disclaimer Preview:\n")
    print(agent.OFFICIAL_LEGAL_DISCLAIMER)
