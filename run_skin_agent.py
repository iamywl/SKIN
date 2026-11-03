"""
대구 피부과 모공 치료 조사 ↔ QA 검증 자동화 실행기
"""

import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from SKIN.agent.skin_agent_pipeline import SkinResearchAgentPipeline


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline = SkinResearchAgentPipeline(root_dir=root_dir)
    result = pipeline.run(max_iterations=3)

    qa = result.get("qa_result", {})
    print("\n[📊 최종 실행 요약]")
    print(f"- 완료 상태: {result['status']}")
    print(f"- QA 종합 점수: {qa.get('total_score', 0)}점 (합격 기준: {qa.get('pass_threshold', 85)}점)")
    print(f"- 반복 순환 횟수: {result['iterations']}회")
    print(f"- 생성된 시술 설명서: {len(result['generated_treatment_files'])}개")
    print(f"- 가격 비교 보고서: {os.path.basename(result['generated_price_file'])}")


if __name__ == "__main__":
    main()
