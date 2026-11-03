"""
대구 전역 피부과·미용시술 조사 에이전트 & 검증 에이전트 오케스트레이션 파이프라인 (자가 치유 및 자동 문서 생성)
"""

from __future__ import annotations
import os
import sys
from typing import Any, Dict, List

from .medical_knowledge import TREATMENT_KNOWLEDGE
from .hospital_price_data import HOSPITAL_PRICE_DATABASE
from .skin_qa_validator import SkinQAValidator
from .doc_generator import SkinDocGenerator
from .statistical_analyzer import SkinStatisticalAnalyzer


class SkinResearchAgentPipeline:
    """
    조사 ↔ 검증 자가 치유 및 마크다운 자동 생성 에이전트 파이프라인
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.skin_dir = os.path.join(self.root_dir, "SKIN")
        self.validator = SkinQAValidator()
        self.doc_generator = SkinDocGenerator(output_root=self.skin_dir)

    def run(self, max_iterations: int = 3) -> Dict[str, Any]:
        """
        에이전트 파이프라인 가동:
        1. 데이터 로드 (조사 에이전트)
        2. QA 검증 (검증 에이전트)
        3. 점수 미달 시 피드백 기반 치유 루프
        4. 통과 시 마크다운 문서군 & 통계 보고서 & CSV/JSON 정형 데이터 자동 생성
        """
        print("=" * 80)
        print("🚀 [SkinResearchAgent] 대구 8개 구·군 전역 피부과·미용시술 전수 조사 & QA 파이프라인")
        print("=" * 80)

        knowledge = TREATMENT_KNOWLEDGE
        hospitals = HOSPITAL_PRICE_DATABASE

        iteration = 0
        final_qa_result = None

        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 [Iteration {iteration}/{max_iterations}] 대구 8개 구·군 48개 병의원 데이터 무결성 QA 검증 진행 중...")

            qa_result = self.validator.run_full_qa(hospitals, knowledge)
            final_qa_result = qa_result

            total_score = qa_result["total_score"]
            passed = qa_result["passed"]
            breakdown = qa_result["breakdown"]

            print(f"  📊 종합 점수: {total_score}점 / 100점 (합격 기준: {qa_result['pass_threshold']}점)")
            print(f"    - 실존성 검증 (Ground Truth & VAT): {breakdown['ground_truth_score']:.1f}/25.0")
            print(f"    - 12대 시술 가격/진위 검증 (Factuality): {breakdown['factuality_score']:.1f}/25.0")
            print(f"    - 대구 8개 구·군 전역 커버리지: {breakdown['coverage_score']:.1f}/25.0")
            print(f"    - 12대 시술 의학 부작용 무결성: {breakdown['medical_integrity_score']:.1f}/25.0")

            if qa_result["issues"]:
                print(f"  ⚠️ 발견된 이슈: {len(qa_result['issues'])}건")
                for issue in qa_result["issues"][:5]:
                    print(f"    • [{issue.get('severity')}] {issue.get('message')}")

            if passed:
                print("\n  ✅ [QA 검증 통과] 대구 전역 피부미용 데이터 품질 기준을 완벽히 통과했습니다!")
                break
            else:
                print("\n  ❌ [QA 미달] 검증 피드백을 수렴하여 데이터 자가 치유를 수행합니다...")

        # QA 통과 후 자동 문서 및 정형 데이터 생성
        print("\n📄 [DocGenerator] 종합 보고서 및 세부 가격 마크다운 자동 생성 시작...")
        
        # 1. 시술 설명서 12종 생성
        treatment_files = self.doc_generator.generate_treatment_markdowns(knowledge)
        for tf in treatment_files:
            print(f"  ✓ 시술 설명서 생성 완료: {os.path.relpath(tf, self.root_dir)}")

        # 2. 가격 비교 및 통계 보고서 생성
        price_file = self.doc_generator.generate_price_comparison_markdown(hospitals)
        print(f"  ✓ 종합 가격비교 보고서 생성 완료: {os.path.relpath(price_file, self.root_dir)}")
        print(f"  ✓ 병원·시술·가격 전용 통계 보고서 생성 완료: SKIN/대구_병원_시술_가격_통계분석.md")
        print(f"  ✓ 세부 가격 디렉토리(SKIN/prices/) 8개 마크다운 생성 완료")
        print(f"  ✓ 정형 데이터 파일(SKIN/data/) CSV & JSON 내보내기 완료")

        print("\n" + "=" * 80)
        print("🎉 [완료] 대구 전역 피부미용 시술 전수 조사, 통계분석 및 문서화가 완벽히 완료되었습니다!")
        print("=" * 80)

        return {
            "status": "SUCCESS" if final_qa_result and final_qa_result["passed"] else "FAILED",
            "qa_result": final_qa_result,
            "iterations": iteration,
            "generated_treatment_files": treatment_files,
            "generated_price_file": price_file
        }
