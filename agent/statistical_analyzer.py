"""
피부과 시술 가격 및 KOSIS 심평원 모수 기반 통계 분석 엔진 (Statistical Analyzer)
대구 8개 구·군 전역 78개소 모수 대비 104개 병의원 정밀 표본 조사 데이터 분석,
12대 핵심 의과 정품 시술(22개 세부 규격) 및 한방 피부미용 고유 시술군 분리 통계,
VAT(부가가치세 10%) 별도/포함 듀얼 가격 통계, 구별 시세,
의료기관 종별(전문의/네트워크/한방) 비교 및 CSV/JSON 데이터 내보내기를 수행합니다.
"""

from __future__ import annotations
import os
import json
import csv
import math
import re
from typing import Any, Dict, List, Tuple


class SkinStatisticalAnalyzer:
    """
    대구광역시 8개 구·군 피부과 및 미용 클리닉 시술 가격 데이터의 통계적 분포 및 이상치 분석 엔진
    """

    # KOSIS 국가통계포털 & 건강보험심사평가원(HIRA) 2026년 2분기 대구 공식 피부과 의원 모수 (총 78개소)
    HIRA_POPULATION = {
        "수성구": 29,
        "달서구": 16,
        "중구": 10,
        "북구": 8,
        "동구": 5,
        "서구": 4,
        "남구": 3,
        "달성군": 3
    }

    # 12대 핵심 시술 대표 명칭 (단위 표준화)
    MAIN_TREATMENTS = {
        "바늘_고주파": "포텐자 기본 모공팁 (RF 니들링 1회)",
        "쥬베룩": "쥬베룩 스킨 (나비존 2cc 기준)",
        "리쥬란_2cc": "리쥬란 힐러 정품 (2cc 단독)",
        "울쎄라": "울쎄라 정품 (안면 300샷)",
        "슈링크_300샷": "슈링크 유니버스 (300샷)",
        "인모드_풀페이스": "인모드 리프팅 (FX+Forma 풀페이스)",
        "올리지오_300샷": "올리지오 고주파 (300샷)",
        "레이저_토닝": "피코/듀얼 레이저 토닝 (1회 단품)",
        "피코프락셀": "피코프락셀 (모공/흉터 1회)",
        "스킨보톡스": "스킨보톡스 (풀페이스 3~4cc)",
        "사각턱보톡스_국산": "사각턱 보톡스 (국산 50U)",
        "엑소좀_1회": "4세대 ASCE+ 엑소좀 (5cc)",
        "국소_레티노이드": "국소 레티노이드 비급여 처방 (1회)",
        "제모_남성_턱수염_5회": "남성 턱수염 레이저 제모 (5회 패키지)",
        "제모_여성_겨드랑이_5회": "여성 겨드랑이 레이저 제모 (5회 패키지)"
    }

    # 정밀 세부 규격 (의과 정품 32개 규격 + 한방 고유 미용 침술 6개 규격)
    DETAILED_TREATMENT_NAMES = {
        # 고주파/HIFU 리프팅 (의과 정품)
        "바늘_고주파": "포텐자 기본 모공팁 (RF 니들링)",
        "포텐자_펌핑팁": "포텐자 정품 1회용 펌핑팁 단독",
        "울쎄라_100샷": "울쎄라 정품 (국소 100샷)",
        "울쎄라_300샷": "울쎄라 정품 (표준 안면 300샷)",
        "울쎄라_600샷": "울쎄라 정품 (풀페이스&넥 600샷)",
        "울쎄라": "울쎄라 정품 (표준 안면 300샷 대표)",
        "슈링크_300샷": "슈링크 유니버스 (300샷)",
        "인모드_FX_1부위": "인모드 FX (이중턱/볼 1부위)",
        "인모드_풀페이스": "인모드 FX+Forma (풀페이스)",
        "올리지오_300샷": "올리지오 모노폴라 RF (300샷)",
        # 스킨부스터 (의과 정품)
        "쥬베룩": "쥬베룩 스킨 (나비존 2cc 대표)",
        "쥬베룩_2cc": "쥬베룩 스킨 (나비존 2cc 집중)",
        "쥬베룩_손주사_2cc": "쥬베룩 스킨 2cc [수기 손주사 1:1 맞춤]",
        "쥬베룩_인젝터_2cc": "쥬베룩 스킨 2cc [하이쿡스 기계인젝터]",
        "쥬베룩_3cc": "쥬베룩 스킨 (볼+나비존 3cc)",
        "쥬베룩_4cc": "쥬베룩 스킨 (풀페이스 4cc)",
        "쥬베룩_1바이알": "쥬베룩 스킨 (1바이알 6cc 전량)",
        "쥬베룩_볼륨": "쥬베룩 볼륨 (1바이알 10cc 전량)",
        "리쥬란_2cc": "리쥬란 힐러 (정품 2cc)",
        "리쥬란_손주사_2cc": "리쥬란 힐러 2cc [원장 수기 손주사]",
        "리쥬란_인젝터_2cc": "리쥬란 힐러 2cc [리쥬메이트 기계주입]",
        "리쥬란_아이_1cc": "리쥬란 아이 1cc (눈가/눈밑)",
        "리쥬란_HB_1cc": "리쥬란 HB Plus 1cc (리도카인 무통)",
        "리쥬란_4cc": "리쥬란 힐러 (정품 4cc 풀페이스)",
        "엑소좀_1회": "ASCE+ 4세대 줄기세포 엑소좀 (5cc)",
        # 레이저 영구 제모 (의과)
        "제모_남성_턱수염_1회": "남성 턱수염 전체 1회 (인중+턱+턱밑)",
        "제모_남성_턱수염_5회": "남성 턱수염 전체 5회 패키지",
        "제모_여성_겨드랑이_1회": "여성 겨드랑이 레이저 제모 1회",
        "제모_여성_겨드랑이_5회": "여성 겨드랑이 레이저 제모 5회",
        "제모_여성_종아리_5회": "여성 종아리 전체 5회 패키지",
        "제모_브라질리언_1회": "올누드 브라질리언 제모 1회",
        # 레이저/색소/모공 (의과)
        "리쥬란_2cc": "리쥬란 힐러 (정품 2cc)",
        "리쥬란_4cc": "리쥬란 힐러 (정품 4cc 풀페이스)",
        "엑소좀_1회": "ASCE+ 4세대 줄기세포 엑소좀 (5cc)",
        # 레이저/색소/모공 (의과)
        "레이저_토닝": "피코/듀얼 레이저 토닝 (1회 단품)",
        "피코프락셀": "피코프락셀 (모공/흉터 1회 단독)",
        # 보톡스/쁘띠 (의과)
        "스킨보톡스": "스킨보톡스 (풀페이스 3~4cc 대표)",
        "스킨보톡스_나비존": "스킨보톡스 나비존 모공 (국산 1~1.5cc)",
        "스킨보톡스_풀페이스": "스킨보톡스 풀페이스 (국산 3~4cc)",
        "스킨보톡스_제오민": "스킨보톡스 풀페이스 (독일 제오민 순수톡신)",
        "사각턱보톡스_국산": "사각턱 보톡스 (국산 50U)",
        "사각턱보톡스_제오민": "사각턱 보톡스 (독일 제오민 50U)",
        # 외용제
        "국소_레티노이드": "국소 레티노이드 비급여 처방 (1회)",
        # 한방 고유 미용 침술군 (완전 분리)
        "한방_매선침_리프팅": "한방 매선침 리프팅 (녹는 실 침술 40줄)",
        "한방_콜라겐_약침": "한방 콜라겐 생약 약침 (스킨부스터 2cc 대체)",
        "한방_재생_약침": "한방 자가혈·생약 DNA 재생 약침 (리쥬란 대체)",
        "한방_새살침_MTS": "코라테라피/새살침 (흉터·모공 유착 박리 침술)",
        "한방_미세약초침": "미세약초침 (천연 해초 스피큘 박피 요법)",
        "한방_정안침": "안면 정안침 (표정근 이완 미용 침술)"
    }

    def __init__(self, hospitals: List[Dict[str, Any]]):
        self.hospitals = hospitals

    def _extract_price(self, price_str: str) -> int:
        nums = re.findall(r"\d+", price_str.replace(",", ""))
        return int(nums[0]) if nums else 0

    def compute_kosis_coverage(self) -> Dict[str, Any]:
        """KOSIS 심평원 모수 대비 대구 8개 구·군 표본 추출률 산출"""
        result = {}
        total_investigated = len(self.hospitals)
        total_pop = sum(self.HIRA_POPULATION.values())
        total_specialists = 0

        for district, pop in self.HIRA_POPULATION.items():
            specialist_count = sum(
                1 for h in self.hospitals 
                if h.get("district") == district and h.get("clinic_type") == "전문의의원"
            )
            total_specialists += specialist_count
            dist_investigated = sum(
                1 for h in self.hospitals if h.get("district") == district
            )
            coverage_rate = (specialist_count / pop * 100) if pop > 0 else 0.0

            result[district] = {
                "hira_population": pop,
                "specialist_count": specialist_count,
                "total_investigated": dist_investigated,
                "specialist_coverage_pct": round(coverage_rate, 1)
            }

        result["전체_대구광역시"] = {
            "hira_population": total_pop,
            "specialist_count": total_specialists,
            "total_investigated": total_investigated,
            "specialist_coverage_pct": round(total_specialists / total_pop * 100, 1),
            "investigation_ratio_to_population_pct": round(total_investigated / total_pop * 100, 1)
        }
        return result

    def get_treatment_prices(self, treatment_key: str, price_type: str = "final", clinic_type_filter: str = None) -> List[Dict[str, Any]]:
        """
        시술별 가격 목록 추출 (병원 메타데이터 및 VAT 분리 계산)
        - price_type == "final": 최종 실결제액 (VAT 10% 포함 기준)
        - price_type == "displayed": 병원 이벤트/홈페이지 고시가 (VAT 별도 표기 병원은 별도가액)
        - price_type == "supply": 순수 공급가액 (VAT 10% 제외 기준)
        """
        prices = []
        for h in self.hospitals:
            if clinic_type_filter and h.get("clinic_type") != clinic_type_filter:
                continue

            t_data = h.get("treatments", {}).get(treatment_key)
            if not t_data:
                continue

            p_val = self._extract_price(t_data.get("price_1session", ""))
            if p_val <= 0:
                continue

            vat_inc = h.get("vat_included", False)
            if vat_inc:
                final_price = p_val
                supply_price = round(p_val / 1.1)
                vat_amount = final_price - supply_price
                displayed_price = p_val
            else:
                displayed_price = p_val
                vat_amount = round(p_val * 0.1)
                final_price = p_val + vat_amount
                supply_price = p_val

            if price_type == "final":
                chosen_price = final_price
            elif price_type == "displayed":
                chosen_price = displayed_price
            else:
                chosen_price = supply_price

            prices.append({
                "hospital_name": h.get("hospital_name"),
                "district": h.get("district"),
                "clinic_type": h.get("clinic_type", "네트워크의원"),
                "is_specialist": h.get("is_specialist", False),
                "vat_included": vat_inc,
                "vat_note": h.get("vat_note", "VAT 별도(결제 시 10% 가산)"),
                "procedure_name": t_data.get("procedure_name"),
                "raw_price_str": t_data.get("price_1session"),
                "displayed_price": displayed_price,
                "final_price": final_price,
                "supply_price": supply_price,
                "vat_amount": vat_amount,
                "price": chosen_price,
                "note": t_data.get("note", "")
            })

        return sorted(prices, key=lambda x: x["price"])

    def calculate_descriptive_stats(self, prices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """기술통계량(평균, 중위값, 사분위수, IQR, 표준편차, 이상치 탐지) 계산"""
        if not prices_data:
            return {}

        vals = [p["price"] for p in prices_data]
        n = len(vals)
        mean_val = sum(vals) / n
        variance = sum((x - mean_val) ** 2 for x in vals) / (n - 1) if n > 1 else 0.0
        std_dev = math.sqrt(variance)

        def percentile(data, percent):
            k = (len(data) - 1) * percent
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return data[int(k)]
            d0 = data[int(f)] * (c - k)
            d1 = data[int(c)] * (k - f)
            return d0 + d1

        q1 = percentile(vals, 0.25)
        median_val = percentile(vals, 0.50)
        q3 = percentile(vals, 0.75)
        iqr = q3 - q1

        lower_bound = max(0, q1 - 1.5 * iqr)
        upper_bound = q3 + 1.5 * iqr

        low_outliers = [p for p in prices_data if p["price"] < lower_bound]
        high_outliers = [p for p in prices_data if p["price"] > upper_bound]

        return {
            "count": n,
            "mean": round(mean_val, 0),
            "std": round(std_dev, 0),
            "min": vals[0],
            "max": vals[-1],
            "q1": round(q1, 0),
            "median": round(median_val, 0),
            "q3": round(q3, 0),
            "iqr": round(iqr, 0),
            "lower_bound": round(lower_bound, 0),
            "upper_bound": round(upper_bound, 0),
            "low_outliers": low_outliers,
            "high_outliers": high_outliers
        }

    def get_top_lowest_and_highest(self, prices_data: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """시술별 최저가 TOP K 및 최고가 병원 추출"""
        if not prices_data:
            return {"lowest": [], "highest": []}
        return {
            "lowest": prices_data[:top_k],
            "highest": sorted(prices_data, key=lambda x: x["price"], reverse=True)[:top_k]
        }

    def calculate_price_distribution_bins(self, prices_data: List[Dict[str, Any]], num_bins: int = 4) -> List[Dict[str, Any]]:
        """가격대별 빈도 분포도(히스토그램 테이블) 생성"""
        if not prices_data:
            return []

        vals = [p["price"] for p in prices_data]
        min_v = vals[0]
        max_v = vals[-1]
        step = (max_v - min_v) / num_bins if max_v > min_v else 10000

        bins = []
        for i in range(num_bins):
            start = min_v + i * step
            end = min_v + (i + 1) * step
            hospitals_in_bin = [
                p["hospital_name"] for p in prices_data 
                if (start <= p["price"] <= end if i == num_bins - 1 else start <= p["price"] < end)
            ]
            bins.append({
                "range_str": f"{int(start):,}원 ~ {int(end):,}원",
                "count": len(hospitals_in_bin),
                "hospitals": hospitals_in_bin
            })
        return bins

    def calculate_percentile_ranks(self, prices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """각 병원의 가격 백분위수 순위 매핑"""
        n = len(prices_data)
        ranked = []
        for i, p in enumerate(prices_data):
            percentile_rank = round((1 - (i / (n - 1) if n > 1 else 0)) * 100, 1)
            ranked.append({
                **p,
                "rank": i + 1,
                "total": n,
                "affordability_percentile": percentile_rank
            })
        return ranked

    def compare_clinic_types(self, prices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """전문의의원 vs 네트워크의원 vs 한방미용 가격 비교 통계"""
        groups = {"전문의의원": [], "네트워크의원": [], "한방미용의원": []}
        for p in prices_data:
            c_type = p.get("clinic_type", "네트워크의원")
            if c_type in groups:
                groups[c_type].append(p["price"])

        stats_by_type = {}
        for c_type, vals in groups.items():
            if vals:
                stats_by_type[c_type] = {
                    "count": len(vals),
                    "mean": round(sum(vals) / len(vals), 0),
                    "median": sorted(vals)[len(vals) // 2],
                    "min": min(vals),
                    "max": max(vals)
                }
            else:
                stats_by_type[c_type] = {"count": 0, "mean": 0, "median": 0, "min": 0, "max": 0}

        net_mean = stats_by_type["네트워크의원"]["mean"]
        spec_mean = stats_by_type["전문의의원"]["mean"]
        premium_pct = round(((spec_mean - net_mean) / net_mean * 100), 1) if net_mean > 0 else 0.0

        return {
            "by_type": stats_by_type,
            "specialist_premium_pct": premium_pct
        }

    def compare_by_districts(self, prices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """구별 가격 비교 통계"""
        district_groups = {}
        for p in prices_data:
            d = p.get("district", "기타")
            district_groups.setdefault(d, []).append(p["price"])

        stats_by_dist = {}
        for dist, vals in district_groups.items():
            stats_by_dist[dist] = {
                "count": len(vals),
                "mean": round(sum(vals) / len(vals), 0),
                "median": sorted(vals)[len(vals) // 2],
                "min": min(vals),
                "max": max(vals)
            }
        return stats_by_dist

    def generate_full_statistical_report(self) -> Dict[str, Any]:
        """대구 전역 표본 통계 분석 종합 실행"""
        coverage_stats = self.compute_kosis_coverage()
        treatments_stats = {}
        detailed_treatments_stats = {}

        for t_key in self.MAIN_TREATMENTS.keys():
            prices_final = self.get_treatment_prices(t_key, price_type="final")
            prices_disp = self.get_treatment_prices(t_key, price_type="displayed")

            desc_stats_final = self.calculate_descriptive_stats(prices_final)
            desc_stats_disp = self.calculate_descriptive_stats(prices_disp)

            extremes = self.get_top_lowest_and_highest(prices_final)
            distribution_bins = self.calculate_price_distribution_bins(prices_final)
            ranked_prices = self.calculate_percentile_ranks(prices_final)
            type_comparison = self.compare_clinic_types(prices_final)
            district_comparison = self.compare_by_districts(prices_final)

            treatments_stats[t_key] = {
                "name": self.MAIN_TREATMENTS[t_key],
                "desc_stats_final": desc_stats_final,
                "desc_stats_displayed": desc_stats_disp,
                "extremes": extremes,
                "distribution_bins": distribution_bins,
                "ranked_prices": ranked_prices,
                "type_comparison": type_comparison,
                "district_comparison": district_comparison
            }

        for t_key, t_name in self.DETAILED_TREATMENT_NAMES.items():
            prices_final = self.get_treatment_prices(t_key, price_type="final")
            prices_disp = self.get_treatment_prices(t_key, price_type="displayed")

            desc_stats_final = self.calculate_descriptive_stats(prices_final)
            desc_stats_disp = self.calculate_descriptive_stats(prices_disp)

            extremes = self.get_top_lowest_and_highest(prices_final)
            distribution_bins = self.calculate_price_distribution_bins(prices_final)
            ranked_prices = self.calculate_percentile_ranks(prices_final)
            type_comparison = self.compare_clinic_types(prices_final)
            district_comparison = self.compare_by_districts(prices_final)

            detailed_treatments_stats[t_key] = {
                "name": t_name,
                "desc_stats_final": desc_stats_final,
                "desc_stats_displayed": desc_stats_disp,
                "extremes": extremes,
                "distribution_bins": distribution_bins,
                "ranked_prices": ranked_prices,
                "type_comparison": type_comparison,
                "district_comparison": district_comparison
            }

        return {
            "coverage_stats": coverage_stats,
            "treatments_stats": treatments_stats,
            "detailed_treatments_stats": detailed_treatments_stats
        }

    def export_to_csv_and_json(self, output_dir: str = "SKIN/data") -> Tuple[str, str]:
        """표본 조사 정형 데이터를 CSV와 JSON으로 내보내기"""
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, "daegu_clinic_treatments_prices.csv")
        json_path = os.path.join(output_dir, "daegu_clinic_treatments_prices.json")

        rows = []
        for h in self.hospitals:
            h_name = h.get("hospital_name")
            dist = h.get("district")
            c_type = h.get("clinic_type")
            is_spec = h.get("is_specialist")
            vat_inc = h.get("vat_included")
            vat_note = h.get("vat_note")
            loc = h.get("location")
            phone = h.get("phone", h.get("tel", "-"))

            for t_key, t_data in h.get("treatments", {}).items():
                p_str = t_data.get("price_1session", "")
                p_val = self._extract_price(p_str)
                if p_val <= 0:
                    continue

                if vat_inc:
                    final_price = p_val
                    supply_price = round(p_val / 1.1)
                    vat_amount = final_price - supply_price
                    disp_price = p_val
                else:
                    disp_price = p_val
                    vat_amount = round(p_val * 0.1)
                    final_price = p_val + vat_amount
                    supply_price = p_val

                standard_name = self.DETAILED_TREATMENT_NAMES.get(t_key, t_key)

                rows.append({
                    "hospital_name": h_name,
                    "district": dist,
                    "clinic_type": c_type,
                    "is_specialist": is_spec,
                    "treatment_key": t_key,
                    "standard_procedure_name": standard_name,
                    "hospital_procedure_name": t_data.get("procedure_name"),
                    "raw_price_str": p_str,
                    "displayed_price": disp_price,
                    "vat_included_in_display": vat_inc,
                    "vat_amount": vat_amount,
                    "final_price_with_vat": final_price,
                    "supply_price": supply_price,
                    "vat_policy_note": vat_note,
                    "treatment_note": t_data.get("note", ""),
                    "location": loc,
                    "phone": phone
                })

        if rows:
            with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        export_data = {
            "meta": {
                "survey_type": "Stratified Sample Survey (대구 8개 구·군 104개소 정밀 표본 조사)",
                "total_hospitals": len(self.hospitals),
                "total_treatment_records": len(rows),
                "districts_covered": list(self.HIRA_POPULATION.keys()),
                "kosis_specialist_population": self.HIRA_POPULATION,
                "exported_at": "2026-11-03"
            },
            "hospitals": self.hospitals,
            "treatment_records": rows
        }

        with open(json_path, mode="w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return csv_path, json_path
