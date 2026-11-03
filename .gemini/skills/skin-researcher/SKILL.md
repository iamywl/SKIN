---
name: skin-researcher
description: 대구 및 전국 미용의료(피부과) 비급여 실거래 가격 조사, 심평원 KOSIS 모수 교차 검증, 100점 만점 QA 파이프라인 및 인터랙티브 웹앱 데이터셋 생성 스킬
---

# Skin Researcher Skill (미용의료 데이터 리서처 & 전국 확장 에이전트)

본 스킬은 미용의료(피부과/성형외과) 비급여 시술의 불투명한 가격 왜곡(VAT 10% 미표기, 이종 시술 왜곡, 미끼 상품, 아웃라이어)을 바로잡고, **KOSIS 심평원 공공 통계 모수 기반의 100% 무결점 실거래 데이터베이스를 전국으로 확장·검증·배포**하기 위한 공식 지침서입니다.

---

## 1. 핵심 철학 및 필수 준수 원칙

1. **사과와 배를 섞지 않는다 (이종 시술 왜곡 금지)**:
   - 의과 정품 시술(울쎄라, 쥬베룩, 리쥬란, 젠틀맥스 제모 등)과 한방 미용 침술(매선침, 새살침, 약초침 등)을 단일 가격표에 섞지 않고 완전히 분리된 데이터셋으로 취급합니다.
2. **부가가치세 10% 실결제액 기준 엄수**:
   - 부가가치세법 시행령 제35조 제1호에 따라 모든 비급여 미용 시술은 카드 결제 시 10%가 가산됩니다.
   - 고시가가 'VAT 별도'인 경우 반드시 1.1배를 가산한 `price_inc_vat`를 산출하여 사기성 미끼 가격을 차단합니다.
3. **전수조사 과장 배제 및 표본 설계 명시**:
   - 심평원 공식 등록 의원 모수($N_0$) 대비 표본($n$) 비율을 명확한 통계 수치로 표기합니다.
4. **환자 안전 우선 의학 부작용 명시**:
   - 가격만 나열하지 않고, 시술별 필수 부작용(예: 쥬베룩 결절, 울쎄라 볼패임, 제모 모낭염/화상)과 주의사항을 반드시 수록합니다.

---

## 2. 전국 타 지역(서울/부산/경기 등) 확장 워크플로우

AI 에이전트(Claude, GPT, Antigravity 등)는 본 프레임워크를 통해 **단 2단계로 전국 원하는 지역을 즉시 확장**할 수 있습니다:

### 단계 1: 신규 지역 템플릿 자동 스캐폴딩
```bash
python expand_region.py --metro 서울 --district 강남구 --pop 120
```
- `expansion_서울_강남구.json` 템플릿이 자동 생성됩니다.

### 단계 2: AI 에이전트에게 데이터 수집 및 병합 지시
AI 에이전트에게 다음 프롬프트를 전달합니다:
> *"생성된 `expansion_서울_강남구.json`의 스펙을 참조하여, 서울 강남구의 주요 피부과 비급여 실거래가를 조사하고 도로명 주소와 태그를 매핑하여 `hospital_price_data.py`에 병합해줘."*

### 단계 3: 100점 만점 QA 검증 & 웹 빌드
```bash
python run_skin_agent.py
python build_web_data.py
```
검증 통과 시 웹사이트에 서울 강남구가 즉시 추가됩니다!

---

## 3. 핵심 모듈 참조

- [`agent/nationwide_expansion_agent.py`](agent/nationwide_expansion_agent.py): 전국 지역 스캐폴딩 및 무결성 병합 에이전트
- [`expand_region.py`](expand_region.py): 원클릭 전국 지역 확장 CLI
- [`agent/medical_knowledge.py`](agent/medical_knowledge.py): 시술별 작용 기전 및 의학 지식
- [`agent/skin_qa_validator.py`](agent/skin_qa_validator.py): 엄밀한 100점 만점 품질 보증 규칙
- [`agent/statistical_analyzer.py`](agent/statistical_analyzer.py): IQR, 가우시안 KDE, 사분위수 계산
- [`agent/hospital_price_data.py`](agent/hospital_price_data.py): 마스터 실거래 DB
