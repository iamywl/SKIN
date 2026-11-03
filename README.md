# 💉 따꼼 빠꼼 (DDAKKOM PPAKKOM)

> **"피부는 따꼼! 시세는 빠꼼!"**  
> 대구 104개 병의원 비급여 피부과 실결제액(VAT 10% 포함) 통계 위치 & 이상치(Outlier) 팩트체크 플랫폼

[![Live Web](https://img.shields.io/badge/Live%20Web-따꼼%20빠꼼%20접속하기-2563EB?style=for-the-badge&logo=googlechrome&logoColor=white)](https://iamywl.github.io/SKIN/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-iamywl%2FSKIN-181717?style=for-the-badge&logo=github)](https://github.com/iamywl/SKIN)
[![License: MIT](https://img.shields.io/badge/License-MIT-059669.svg?style=for-the-badge)](LICENSE)
[![Design: Anti--AI](https://img.shields.io/badge/Design-Monochrome%20%2B%201%20Accent-slate?style=for-the-badge)](DESIGN.md)
[![Nationwide](https://img.shields.io/badge/Expansion-AI%20Agent%20Ready-purple?style=for-the-badge)](expand_region.py)

---

## 🌐 라이브 웹사이트 (Live Demo)
👉 **[https://iamywl.github.io/SKIN/](https://iamywl.github.io/SKIN/)**  
*(별도 설치나 회원가입 없이 브라우저에서 0.5초 만에 열리는 100% 무료 공익 정적 웹 애플리케이션)*

---

## 💡 기획 의도: 왜 '따꼼 빠꼼'인가요?

피부과 시술은 받을 때 살짝 **'따꼼'**하지만, 내 지갑에서 나가는 시세 정보만큼은 **'빠꼼'**하게 꿰뚫어 봐야 합니다!

국내 비급여 피부의료 시장은 극심한 가격 왜곡이 존재합니다:
1. **VAT 10% 미표기 착시**: 인터넷에는 10만원이라 해놓고 결제할 때 "부가세 10% 별도예요"라며 11만원을 긁는 꼼수.
2. **이종 시술 왜곡 (사과와 배 혼입)**: 정통 의과 정품(울쎄라, 쥬베룩 등) 표에 한방 침구 시술(매선침, 약침)을 마구잡이로 섞어 왜곡하는 문제.
3. **미끼 상품과 희석 용량**: 첫 방문 이벤트 초저가와 정상 용량 시세의 미분리.
4. **허위 전수조사 사칭**: 표본 몇 개만 조사하고 '전수조사'라고 과장 광고하는 행태.

**'따꼼 빠꼼'은 건강보험심사평가원(HIRA) 국가통계포털 KOSIS 공식 모수($N_0=78$)와 대구 8개 구·군 104개 병원 표본을 바탕으로, 카드 실결제액(VAT 10% 포함) 기준의 100% 무결점 가격 통계를 제공합니다.**

---

## 🎨 인간 디자이너 표준 디자인 시스템 ([DESIGN.md](DESIGN.md))

AI 특유의 촌스러운 보라/네온 그라데이션을 완전히 버리고 프로덕션 헬스케어 표준을 확립했습니다:

* **컬러 팔레트 제한 (Monochrome + 1 Accent)**:
  - 그라데이션(`linear-gradient`) 원천 금지.
  - Slate/Zinc 계열 9단계 무채색 베이스에 **단 하나의 단단한 블루 악센트(Solid Blue)**만 적용.
* **타이포그래피 스케일 (엄격한 수치 지정)**:
  - `Pretendard Variable` 최적화.
  - 제목: 음수 자간 `-0.025em`, 단단한 행간 `1.25`.
  - 본문: 자간 `-0.01em`, 가독성 행간 `1.6`.
  - 숫자/금액: `tabular-nums`로 자릿수 정렬 일치.
* **그리드와 정렬의 밀도**:
  - 붕 뜬 중앙 정렬을 배제하고 **왼쪽 정렬 중심**의 정보 구조.
  - **8px 배수(p-2, p-4, p-6, gap-4) 기반의 단단한 간격 체계**.
* **시각 장식 절제**:
  - 과도한 블러(`blur-3xl`), 3D 아이콘, 네온 아우라 완전 제거.
  - **1px 플랫 보더(`border-slate-200`)**와 **절제된 얕은 그림자**만 사용.

---

## ✨ 핵심 기능

1. **시술 기법 초정밀 세분화 (총 37개 규격)**:
   * **쥬베룩**: 수기 손주사(로스 0% 맞춤) vs 하이쿡스 기계 인젝터 vs 2cc / 4cc / 6cc 풀바이알 vs 볼륨(10cc).
   * **리쥬란**: 원장 수기 손주사 2cc vs 리쥬메이트 인젝터 vs 리쥬란 아이(1cc) vs 리쥬란 HB Plus(무통).
   * **레이저 제모**: 캔델라 젠틀맥스 프로 플러스(알렉산드라이트 755nm DCD 가스 냉각) vs 클라리티2 vs 다이오드. 남성 턱수염 1회/5회, 여성 겨드랑이, 종아리 등 전 부위 실거래가 비교.
2. **가우시안 정규분포(KDE) & 사분위수(IQR) 가격 위치 진단**:
   * 제안받은 견적을 입력하면 대구 실거래가 곡선 위에 **내 가격 핀**을 매핑하여 대구 상위 몇 %인지 즉시 분석.
3. **아웃라이어(이상치) 경고**:
   * 하위 이상치(미끼 의심, 용량 희석 주의) 및 상위 초고가 병원 자동 필터링.
4. **104개 병원 도로명 주소 & 지하철역 도보 정보**:
   * 실제 도로명 주소와 `[피부과전문의]`, `[대형네트워크]`, `[젠틀맥스Pro+]`, `[울쎄라정품]`, `[정찰제]` 태그 필터 탑재.

---

## 🌍 전국 타 지역(서울/부산/경기 등) 확장 에이전트 탑재!

대구를 넘어 **서울 강남/홍대, 부산 서면/해운대, 인천 송도** 등 전국의 데이터를 **AI 에이전트를 이용해 10분 만에 손쉽게 확장**할 수 있는 에이전트 프레임워크를 기본 탑재하고 있습니다.

### 1. 신규 지역 템플릿 원클릭 생성
```bash
python expand_region.py --metro 서울 --district 강남구 --pop 120
```
- `expansion_서울_강남구.json` 스캐폴딩 템플릿이 자동 생성됩니다.

### 2. AI 에이전트(Claude, GPT, Antigravity)에게 지시
> *"생성된 `expansion_서울_강남구.json` 규격에 맞춰 강남구 피부과 비급여 실거래가를 채우고 `hospital_price_data.py`에 병합해줘."*

### 3. 100점 만점 QA 검증 & 웹 빌드
```bash
python run_skin_agent.py
python build_web_data.py
```
- 무결성 검증을 통과하면 웹사이트에 신규 지역이 즉시 반영됩니다!

---

## 🚀 로컬 실행 방법

```bash
# 저장소 복제
git clone https://github.com/iamywl/SKIN.git
cd SKIN

# 로컬 웹 서버 실행 (포트 8080)
python -m http.server 8080
```
브라우저에서 `http://localhost:8080` 접속.

---

## 🤝 기여하기 (Contributing)

* 누구나 본인의 지역 병원 데이터나 신규 시술을 추가할 수 있습니다. 자세한 내용은 **[`CONTRIBUTING.md`](CONTRIBUTING.md)**를 참조해 주세요.
* AI 에이전트 활용 지침은 **[`SKILL.md`](SKILL.md)**에 명시되어 있습니다.

---

## 📜 라이선스 (License)

본 프로젝트의 모든 코드와 데이터는 [MIT License](LICENSE)에 따라 자유롭게 사용, 수정, 배포할 수 있습니다.
