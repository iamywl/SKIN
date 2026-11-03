"""
피부과 데이터 및 시술 정보 품질 보증 검증 에이전트 (Skin QA Validator Agent)
KOSIS 심평원 모수 대비 대구 8개 구·군 전수 조사율, 12대 시술 가격 이상치,
VAT 포함 여부 메타데이터, 의학 부작용 및 환자 안전 경고 무결성을 엄밀히 검증합니다.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple


class SkinQAValidator:
    """
    대구 전역 피부과 시술 조사 데이터 품질 검증 및 비평 에이전트
    """

    PASS_THRESHOLD = 85.0

    # 대구광역시 8개 구·군 전역 전수 검증
    REQUIRED_DISTRICTS = ["수성구", "달서구", "중구", "북구", "동구", "서구", "남구", "달성군"]

    # 12대 핵심 시술 대표 키
    CORE_TREATMENTS = [
        "바늘_고주파", "쥬베룩", "울쎄라", "레이저_토닝", "스킨보톡스", "국소_레티노이드",
        "리쥬란_2cc", "슈링크_300샷", "인모드_풀페이스", "올리지오_300샷", "사각턱보톡스_국산", "엑소좀_1회",
        "제모_남성_턱수염_5회", "제모_여성_겨드랑이_5회"
    ]

    PRICE_RANGES = {
        "바늘_고주파": (80_000, 600_000),
        "포텐자_펌핑팁": (150_000, 700_000),
        "쥬베룩": (100_000, 800_000),
        "쥬베룩_2cc": (100_000, 500_000),
        "쥬베룩_4cc": (200_000, 800_000),
        "쥬베룩_볼륨": (250_000, 1_200_000),
        "쥬베룩_손주사_2cc": (100_000, 550_000),
        "쥬베룩_인젝터_2cc": (100_000, 500_000),
        "리쥬란_2cc": (100_000, 450_000),
        "리쥬란_4cc": (200_000, 850_000),
        "리쥬란_아이_1cc": (70_000, 250_000),
        "리쥬란_HB_1cc": (80_000, 300_000),
        "울쎄라": (200_000, 3_000_000),
        "울쎄라_100샷": (80_000, 600_000),
        "울쎄라_300샷": (200_000, 2_000_000),
        "울쎄라_600샷": (400_000, 3_000_000),
        "슈링크_300샷": (50_000, 300_000),
        "슈링크_600샷": (100_000, 550_000),
        "인모드_FX_1부위": (9_000, 150_000),
        "인모드_풀페이스": (80_000, 400_000),
        "올리지오_300샷": (200_000, 900_000),
        "레이저_토닝": (20_000, 300_000),
        "피코프락셀": (40_000, 400_000),
        "스킨보톡스": (30_000, 450_000),
        "스킨보톡스_나비존": (30_000, 200_000),
        "스킨보톡스_풀페이스": (40_000, 450_000),
        "사각턱보톡스_국산": (15_000, 100_000),
        "사각턱보톡스_제오민": (50_000, 250_000),
        "엑소좀_1회": (80_000, 500_000),
        "국소_레티노이드": (5_000, 50_000),
        "제모_남성_턱수염_1회": (15_000, 300_000),
        "제모_남성_턱수염_5회": (80_000, 1_000_000),
        "제모_여성_겨드랑이_1회": (2_000, 80_000),
        "제모_여성_겨드랑이_5회": (10_000, 200_000),
        "제모_여성_종아리_5회": (80_000, 600_000),
        "제모_브라질리언_1회": (30_000, 350_000)
    }

    # TREATMENT_KNOWLEDGE의 12대 키와 일치
    MANDATORY_SIDE_EFFECTS = {
        "바늘_고주파": ["색소침착", "모낭염", "격자 자국", "화상"],
        "쥬베룩": ["결절", "육아종", "엠보싱"],
        "울쎄라": ["볼패임", "신경 손상", "화상"],
        "레이저_토닝": ["저색소", "과색소", "멜라닌"],
        "스킨보톡스": ["표정", "비대칭", "내성"],
        "국소_레티노이드": ["레티노이드 피부염", "초기 악화", "광과민성"],
        "리쥬란_힐러": ["엠보싱", "멍", "통증"],
        "슈링크_유니버스": ["화상", "볼패임", "신경"],
        "인모드_리프팅": ["멍", "화상", "볼살"],
        "피코_프락셀": ["출혈", "색소침착", "모낭염"],
        "사각턱_보톡스": ["내성", "저작력", "볼패임"],
        "엑소좀": ["알레르기", "모낭염"],
        "레이저_제모": ["모낭염", "화상", "색소침착", "다모증"]
    }

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []

    def _extract_number(self, price_str: str) -> int:
        nums = re.findall(r"\d+", price_str.replace(",", ""))
        return int(nums[0]) if nums else 0

    def validate_ground_truth(self, hospitals: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        score = 25.0
        issues = []

        if not hospitals:
            issues.append({"severity": "CRITICAL", "message": "병원 데이터가 비어 있습니다."})
            return 0.0, issues

        known_invalid_patterns = ["가상", "테스트", "임시", "가짜"]
        for hosp in hospitals:
            name = hosp.get("hospital_name", "")
            location = hosp.get("location", "")

            if any(p in name for p in known_invalid_patterns) or len(name) < 2:
                score -= 5.0
                issues.append({
                    "severity": "HIGH",
                    "target": name,
                    "message": f"의심스러운 상호명 감지: '{name}'"
                })

            if "대구" not in location:
                score -= 1.0
                issues.append({
                    "severity": "MEDIUM",
                    "target": name,
                    "message": f"소재지 대구 표기 누락 의심: {location}"
                })

            # VAT 정책 필드 검증
            if "vat_included" not in hosp:
                score -= 0.5
                issues.append({
                    "severity": "LOW",
                    "target": name,
                    "message": f"VAT 포함 여부(vat_included) 메타데이터 누락: {name}"
                })

        return max(0.0, score), issues

    def validate_factuality_and_outliers(self, hospitals: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        score = 25.0
        issues = []

        for hosp in hospitals:
            name = hosp.get("hospital_name", "")
            treatments = hosp.get("treatments", {})

            for t_key, t_data in treatments.items():
                if t_key not in self.PRICE_RANGES:
                    continue

                min_p, max_p = self.PRICE_RANGES[t_key]
                p1_str = t_data.get("price_1session", "")
                p1_val = self._extract_number(p1_str)

                if p1_val > 0 and (p1_val < min_p or p1_val > max_p):
                    score -= 1.0
                    issues.append({
                        "severity": "HIGH",
                        "target": f"{name} - {t_key}",
                        "message": f"시세 이상치 감지: {p1_str} (정상 범위: {min_p:,}원 ~ {max_p:,}원)"
                    })

        return max(0.0, score), issues

    def validate_coverage(self, hospitals: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        score = 25.0
        issues = []

        # 8개 구·군 전수 커버리지 확인
        for req_dist in self.REQUIRED_DISTRICTS:
            count = sum(1 for h in hospitals if h.get("district") == req_dist)
            if count == 0:
                score -= 8.0
                issues.append({
                    "severity": "CRITICAL",
                    "target": req_dist,
                    "message": f"대구 필수 권역 누락: '{req_dist}'"
                })
            elif count < 2:
                score -= 1.0
                issues.append({
                    "severity": "LOW",
                    "target": req_dist,
                    "message": f"권역 표본 부족: {req_dist} ({count}곳)"
                })

        # 시술 종목 커버리지 확인
        for req_t in self.CORE_TREATMENTS:
            matched = [h for h in hospitals if req_t in h.get("treatments", {})]
            if len(matched) < 5:
                score -= 1.0
                issues.append({
                    "severity": "MEDIUM",
                    "target": req_t,
                    "message": f"핵심 시술 표본수 부족: {req_t} ({len(matched)}곳)"
                })

        return max(0.0, score), issues

    def validate_medical_integrity(self, knowledge: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        score = 25.0
        issues = []

        for req_t, mandatory_keywords in self.MANDATORY_SIDE_EFFECTS.items():
            if req_t not in knowledge:
                score -= 4.0
                issues.append({
                    "severity": "CRITICAL",
                    "target": req_t,
                    "message": f"필수 시술 의학 지식 누락: {req_t}"
                })
                continue

            t_info = knowledge[req_t]
            side_effects_text = " ".join([
                f"{se.get('name', '')} {se.get('description', '')}"
                for se in t_info.get("side_effects", [])
            ])

            for kw in mandatory_keywords:
                if kw not in side_effects_text:
                    score -= 1.0
                    issues.append({
                        "severity": "HIGH",
                        "target": f"{req_t} 부작용",
                        "message": f"환자 안전 경고 필수 키워드 누락: '{kw}'"
                    })

        return max(0.0, score), issues

    def run_full_qa(self, hospitals: List[Dict[str, Any]], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        s1, i1 = self.validate_ground_truth(hospitals)
        s2, i2 = self.validate_factuality_and_outliers(hospitals)
        s3, i3 = self.validate_coverage(hospitals)
        s4, i4 = self.validate_medical_integrity(knowledge)

        total_score = round(s1 + s2 + s3 + s4, 1)
        all_issues = i1 + i2 + i3 + i4

        passed = total_score >= self.PASS_THRESHOLD and not any(i.get("severity") == "CRITICAL" for i in all_issues)

        return {
            "total_score": total_score,
            "passed": passed,
            "pass_threshold": self.PASS_THRESHOLD,
            "breakdown": {
                "ground_truth_score": s1,
                "factuality_score": s2,
                "coverage_score": s3,
                "medical_integrity_score": s4
            },
            "issue_count": len(all_issues),
            "issues": all_issues
        }
