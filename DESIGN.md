# 📐 따꼼 빠꼼 (DDAKKOM PPAKKOM) 디자인 시스템 규격서 (DESIGN.md)

> **문서 버전**: v2.5.0 (Strict Human-Crafted Medical Standard)  
> **슬로건**: "피부는 따꼼! 시세는 빠꼼!"  
> **원칙**: AI 특유의 화려한 네온 그라데이션을 완전히 배제하고, **Monochrome + 1 Accent**, **엄격한 타이포그래피 수치**, **8px 기반 왼쪽 정렬 밀도**, **1px 플랫 보더**를 준수하는 정통 프로덕션 헬스케어 인터페이스입니다.

---

## 1. 4대 핵심 디자인 원칙 (Anti-AI Design Rules)

### 1.1 컬러 팔레트 제한 (Monochrome + 1 Accent, No Gradient)
* **그라데이션 원천 금지**: `linear-gradient`, `radial-gradient` 등 AI가 무분별하게 사용하는 보라-마젠타-인디고 그라데이션을 100% 금지합니다.
* **무채색 9단계 베이스**: Slate/Zinc 계열 9단계(`Slate 50 ~ Slate 950`)만을 배경과 서피스에 사용합니다.
* **단 하나의 단단한 브랜드 악센트 (Solid 1종)**:
  - 라이트 모드: `#1D4ED8` (Solid Blue 700)
  - 다크 모드: `#3B82F6` (Solid Blue 500)
* **상태 배지**: 화려한 형광색 대신, 저채도의 은은한 단색 틴트(1px 보더)만 허용합니다.

| 토큰명 | 라이트 모드 (Default) | 다크 모드 | 용도 |
| :--- | :--- | :--- | :--- |
| `--bg-canvas` | `#F8FAFC` (Slate 50) | `#090D14` (Slate 950) | 전체 캔버스 배경 |
| `--bg-card` | `#FFFFFF` (Pure White) | `#111827` (Gray 900) | 메인 카드 표면 |
| `--bg-card-sub` | `#F1F5F9` (Slate 100) | `#1F2937` (Gray 800) | 입력창, 테이블 헤더 |
| `--border-color` | `#E2E8F0` (Slate 200) | `#1F2937` (Gray 800) | 1px 플랫 외곽선 |
| `--text-primary` | `#0F172A` (Slate 900) | `#F9FAFB` (Gray 50) | 제목 및 핵심 수치 |
| `--text-secondary` | `#334155` (Slate 700) | `#D1D5DB` (Gray 300) | 본문 및 레이블 |
| `--text-muted` | `#64748B` (Slate 500) | `#9CA3AF` (Gray 400) | 캡션, 단위, 비고 |
| `--accent-primary` | `#1D4ED8` (Solid Blue 700) | `#3B82F6` (Solid Blue 500) | 단일 포인트 컬러 (버튼, 차트) |

---

### 1.2 타이포그래피 스케일 및 폰트 페어링 (구체적 수치 엄격 준수)
* **글꼴**: `Pretendard Variable`, system-ui (Inter/Roboto 단독 사용 지양).
* **숫자 및 금액**: `font-variant-numeric: tabular-nums;` (테이블/차트 내 금액 자릿수 일치).
* **수치 규격**:
  * **헤딩(Headings, h1~h4)**: 
    - `letter-spacing: -0.025em;` (단단하게 결속된 음수 자간)
    - `line-height: 1.25;` (늘어지지 않는 타이트한 행간)
    - `font-weight: 700;`
  * **본문(Body)**:
    - `letter-spacing: -0.01em;`
    - `line-height: 1.6;` (가독성을 위한 편안한 행간)
    - `font-weight: 400 / 500;`
  * **캡션 및 뱃지**:
    - `letter-spacing: -0.005em;`
    - `line-height: 1.3;`
    - `font-size: 11px ~ 12px; font-weight: 600;`

---

### 1.3 그리드와 정렬의 밀도 (Density & 8px Spacing)
* **중앙 정렬 남발 금지**: 모든 텍스트, 인풋, 메트릭 카드는 **왼쪽 정렬(Left-aligned)**을 원칙으로 하여 시선의 자연스러운 Z-패턴 흐름을 보장합니다.
* **8px 배수 간격 체계**:
  - `p-2 (8px)`, `p-4 (16px)`, `p-6 (24px)`
  - 컴포넌트 간 여백: `gap-2 (8px)`, `gap-4 (16px)`, `gap-6 (24px)`
* **컴팩트한 핀테크/대시보드 밀도**: 붕 뜬 여백을 없애고 한눈에 4대 핵심 지표(내 실결제액, 중앙값, 정상 시세 IQR, 차액)가 비교되도록 구조화합니다.

---

### 1.4 시각 요소(장식) 절제
* **네온 글로우 & 과도한 블러 완전 배제**: `blur-3xl`, 형광 아우라, 3D 입체 아이콘 금지.
* **1px 플랫 보더**: 카드와 구분선은 오직 `1px solid var(--border-color)`로만 경계를 짓습니다.
* **초절제 얕은 그림자(Subtle Shadow)**:
  `box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.05);`

---

## 2. 타 지역(서울/부산/경기 등) 확장 시 디자인 일관성 가이드

다른 지역(예: 서울 강남구, 부산 서면 등)을 확장할 때도 다음 가이드라인을 반드시 동일하게 유지해야 합니다:

1. **차트 색상 일관성**:
   - 일반 행정구 막대는 통일된 `--accent-primary` 단색 톤으로 렌더링.
   - 사용자가 드롭다운에서 선택한 구(Target District)만 하이라이트 레드(`#EF4444`)로 표시.
   - 상단에 `[● 일반 구 평균] [● 내가 선택한 구: OO구]` 범례 배지를 반드시 유지.
2. **단위 및 부가세 표기 규격**:
   - 모든 병원 고시가는 `150,000원`, 실결제액은 `165,000원 (VAT포함)` 형식 준수.
   - 샷수는 `300샷`, 용량은 `2cc / 4cc / 풀바이알`로 표준화.
3. **태그 시스템 표준화**:
   - `[피부과전문의]`: `var(--bg-card-sub)` 바탕 + 1px 보더.
   - `[대형네트워크]`, `[젠틀맥스Pro+보유]`, `[울쎄라정품인증]`, `[VAT포함정찰제]` 등 표준 태그 명명 규칙 준수.
