# -*- coding: utf-8 -*-
"""
따꼼 빠꼼 전국 지역 확장 실행기 (CLI & AI 에이전트 인터페이스)
사용법: python expand_region.py --metro 서울 --district 강남구 --pop 120
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent.nationwide_expansion_agent import NationwideExpansionAgent

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="따꼼 빠꼼 전국 미용의료 데이터 확장 실행기")
    parser.add_argument("--metro", type=str, default="서울", help="광역시/도 (예: 서울, 부산, 대전 등)")
    parser.add_argument("--district", type=str, default="강남구", help="시/군/구 (예: 강남구, 해운대구 등)")
    parser.add_argument("--pop", type=int, default=120, help="심평원 등록 피부과 의원 모수")

    args = parser.parse_args()
    agent = NationwideExpansionAgent()
    template = agent.scaffold_new_region(args.metro, args.district, args.pop)
    
    out_file = f"expansion_{args.metro}_{args.district}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        import json
        json.dump(template, f, ensure_ascii=False, indent=2)

    print(f"\n[완료] {args.metro} {args.district} 템플릿 생성 완료: {out_file}")
    print("AI 에이전트에게 '이 JSON 템플릿에 실거래 데이터를 채워줘'라고 지시하시면 전국 확장이 즉시 완료됩니다!")
