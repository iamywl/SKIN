# -*- coding: utf-8 -*-
"""
웹 앱 전용 통계 데이터 및 병원 데이터 생성 스크립트
treatment_stats.json 및 data.js 생성
"""

import sys
import os
import json
import numpy as np

sys.path.append("SKIN/agent")
from hospital_price_data import HOSPITAL_PRICE_DATABASE
from statistical_analyzer import SkinStatisticalAnalyzer
from medical_knowledge import TREATMENT_KNOWLEDGE

from legal_compliance_agent import MedicalLegalComplianceAgent
legal_agent = MedicalLegalComplianceAgent()
# 의료법 제27조 및 정보통신망법 제70조 준수를 위한 전 표본 비식별 익명화
ANONYMIZED_DATABASE = legal_agent.anonymize_hospital_records(HOSPITAL_PRICE_DATABASE)
analyzer = SkinStatisticalAnalyzer(ANONYMIZED_DATABASE)
kosis = analyzer.compute_kosis_coverage()

# 웹용 시술 메타데이터 (카테고리, 단위, 기술 스펙 등)
TREATMENT_META = {
    # 1. 초음파 리프팅
    "울쎄라_100샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (국소 100샷)",
        "unit": "100샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "울쎄라_300샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (안면 300샷 표준)",
        "unit": "300샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "울쎄라_600샷": {
        "category": "초음파_리프팅",
        "name": "울쎄라 정품 (풀페이스&넥 600샷)",
        "unit": "600샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "울쎄라"
    },
    "슈링크_300샷": {
        "category": "초음파_리프팅",
        "name": "슈링크 유니버스 (300샷)",
        "unit": "300샷",
        "technique": "HIFU 초음파",
        "knowledge_key": "슈링크_유니버스"
    },
    # 2. 고주파 리프팅 & 니들RF
    "올리지오_300샷": {
        "category": "고주파_리프팅",
        "name": "올리지오 모노폴라 RF (300샷)",
        "unit": "300샷",
        "technique": "단극성 고주파",
        "knowledge_key": "바늘_고주파"
    },
    "인모드_FX_1부위": {
        "category": "고주파_리프팅",
        "name": "인모드 MiniFX 1부위 (이중턱/심부볼)",
        "unit": "1부위",
        "technique": "지방사멸 고주파",
        "knowledge_key": "인모드_리프팅"
    },
    "인모드_풀페이스": {
        "category": "고주파_리프팅",
        "name": "인모드 FX+Forma 풀페이스 (지방사멸+타이트닝)",
        "unit": "풀페이스",
        "technique": "복합 고주파",
        "knowledge_key": "인모드_리프팅"
    },
    "바늘_고주파": {
        "category": "바늘_고주파",
        "name": "포텐자 기본 모공팁 (얼굴전체 니들RF)",
        "unit": "얼굴전체",
        "technique": "마이크로니들 RF",
        "knowledge_key": "바늘_고주파"
    },
    "포텐자_펌핑팁": {
        "category": "바늘_고주파",
        "name": "포텐자 정품 1회용 펌핑팁 단독",
        "unit": "정품팁 단독",
        "technique": "마이크로니들 RF",
        "knowledge_key": "바늘_고주파"
    },
    # 3. 스킨부스터 (주입 방식 세분화)
    "쥬베룩_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (나비존 2cc 표준)",
        "unit": "2cc",
        "technique": "기본 주입",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_손주사_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 2cc [원장 수기 손주사 맞춤]",
        "unit": "2cc",
        "technique": "수기 손주사 (로스0%)",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_인젝터_2cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 2cc [하이쿡스 기계인젝터]",
        "unit": "2cc",
        "technique": "기계 인젝터",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_4cc": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (풀페이스 4cc)",
        "unit": "4cc",
        "technique": "풀페이스 주입",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_1바이알": {
        "category": "스킨부스터",
        "name": "쥬베룩 스킨 (1바이알 6cc 전량)",
        "unit": "6cc 풀바이알",
        "technique": "바이알 전량",
        "knowledge_key": "쥬베룩"
    },
    "쥬베룩_볼륨": {
        "category": "스킨부스터",
        "name": "쥬베룩 볼륨 (1바이알 10cc 꺼진부위)",
        "unit": "10cc 풀바이알",
        "technique": "캐뉼라 심부주입",
        "knowledge_key": "쥬베룩"
    },
    "리쥬란_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 정품 (2cc 오리지널)",
        "unit": "2cc",
        "technique": "기본 주입",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_손주사_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 2cc [원장 수기 손주사]",
        "unit": "2cc",
        "technique": "수기 손주사",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_인젝터_2cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 2cc [리쥬메이트 무통 인젝터]",
        "unit": "2cc",
        "technique": "기계 인젝터",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_아이_1cc": {
        "category": "스킨부스터",
        "name": "리쥬란 아이 1cc (눈가/눈밑 잔주름)",
        "unit": "1cc",
        "technique": "미세 나노니들",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_HB_1cc": {
        "category": "스킨부스터",
        "name": "리쥬란 HB Plus 1cc (무통 리도카인 복합)",
        "unit": "1cc",
        "technique": "리도카인 복합",
        "knowledge_key": "리쥬란_힐러"
    },
    "리쥬란_4cc": {
        "category": "스킨부스터",
        "name": "리쥬란 힐러 (정품 4cc 풀페이스)",
        "unit": "4cc",
        "technique": "풀페이스",
        "knowledge_key": "리쥬란_힐러"
    },
    "엑소좀_1회": {
        "category": "스킨부스터",
        "name": "ASCE+ 4세대 줄기세포 엑소좀 (5cc)",
        "unit": "5cc",
        "technique": "MTS/니들 침투",
        "knowledge_key": "엑소좀"
    },
    # 4. 레이저 영구 제모 (부위별/성별/패키지 세분화)
    # 4-1. 남성 제모 부위 (인중+앞턱 콤보 / 장비별 / 1년 무제한권)
    "제모_남성_인중_1회": {
        "category": "레이저_제모",
        "name": "남성 인중 제모 (단독 1회)",
        "unit": "1회",
        "technique": "알렉산드라이트/다이오드",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_인중_5회": {
        "category": "레이저_제모",
        "name": "남성 인중 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "알렉산드라이트/엔디야그",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_인중_앞턱_1회": {
        "category": "레이저_제모",
        "name": "남성 인중+앞턱(턱끝) 제모 1회",
        "unit": "1회",
        "technique": "인중+앞턱 집중 시술",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_인중_앞턱_5회": {
        "category": "레이저_제모",
        "name": "남성 인중+앞턱(턱끝) 제모 5회 [국민세트]",
        "unit": "5회 패키지",
        "technique": "인중+앞턱 5회 국민세트 (볼 제외)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_인중_앞턱_1년무제한": {
        "category": "레이저_제모",
        "name": "남성 인중+앞턱 1년 무제한권 (연 8~10회 유효)",
        "unit": "1년 무제한",
        "technique": "모주기 4~6주 주기 1년 프리패스",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱_턱밑_5회": {
        "category": "레이저_제모",
        "name": "남성 턱+턱밑 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "알렉산드라이트/엔디야그",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_볼_구레나룻_5회": {
        "category": "레이저_제모",
        "name": "남성 볼+구레나룻 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "알렉산드라이트/엔디야그",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_1회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 1회 (인중+턱+턱밑+볼)",
        "unit": "1회",
        "technique": "알렉산드라이트/다이오드",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_5회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 5회 [표준 종합]",
        "unit": "5회 패키지",
        "technique": "젠틀맥스Pro+/클라리티2",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_젠틀맥스_5회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 5회 [캔델라 젠틀맥스Pro+]",
        "unit": "5회 패키지",
        "technique": "캔델라 젠틀맥스Pro+ (26mm, DCD 순간가스냉각)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_클라리티_5회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 5회 [루트로닉 클라리티2]",
        "unit": "5회 패키지",
        "technique": "루트로닉 클라리티2 (755/1064nm, 지능형 ICD 쿨링)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_아포지_5회": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 5회 [사이노슈어 아포지+/다이오드]",
        "unit": "5회 패키지",
        "technique": "사이노슈어 아포지플러스 (짐머 에어쿨링 가성비)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_1년무제한": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 1년 무제한권 (표준/클라리티2)",
        "unit": "1년 무제한",
        "technique": "4~6주 주기 1년 프리패스 (연간 최대 8~10회)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_턱수염_젠틀맥스_1년무제한": {
        "category": "레이저_제모",
        "name": "남성 턱수염 전체 1년 무제한 [캔델라 젠틀맥스Pro+]",
        "unit": "1년 무제한",
        "technique": "캔델라 젠틀맥스Pro+ 끝판왕 1년 프리패스",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_브라질리언_5회": {
        "category": "레이저_제모",
        "name": "남성 브라질리언 위생 제모 5회",
        "unit": "5회 패키지",
        "technique": "DCD 특수 냉각 (남의사 전담)",
        "knowledge_key": "레이저_제모"
    },
    "제모_남성_다리전체_5회": {
        "category": "레이저_제모",
        "name": "남성 다리 전체 5회 (종아리+허벅지)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    # 4-2. 여성 제모 부위 (부위별 & 1년 무제한권)
    "제모_여성_겨드랑이_1회": {
        "category": "레이저_제모",
        "name": "여성 겨드랑이 제모 1회",
        "unit": "1회",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_겨드랑이_5회": {
        "category": "레이저_제모",
        "name": "여성 겨드랑이 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_겨드랑이_1년무제한": {
        "category": "레이저_제모",
        "name": "여성 겨드랑이 제모 1년 무제한권",
        "unit": "1년 무제한",
        "technique": "4~6주 주기 1년 프리패스 (연 8~10회)",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_인중_1회": {
        "category": "레이저_제모",
        "name": "여성 인중 잔털 제모 1회",
        "unit": "1회",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_인중_5회": {
        "category": "레이저_제모",
        "name": "여성 인중 잔털 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_인중_1년무제한": {
        "category": "레이저_제모",
        "name": "여성 인중 잔털 제모 1년 무제한권",
        "unit": "1년 무제한",
        "technique": "4~6주 주기 1년 프리패스",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_팔하완_5회": {
        "category": "레이저_제모",
        "name": "여성 팔 하완 5회 (손목~팔꿈치)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_팔전체_5회": {
        "category": "레이저_제모",
        "name": "여성 팔 전체 5회 (상완+하완)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_종아리_5회": {
        "category": "레이저_제모",
        "name": "여성 종아리 전체 5회 패키지",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_종아리_1년무제한": {
        "category": "레이저_제모",
        "name": "여성 종아리 전체 1년 무제한권",
        "unit": "1년 무제한",
        "technique": "6주 주기 1년 프리패스 (연 8회)",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_인중_1회": {
        "category": "레이저_제모",
        "name": "여성 인중 잔털 제모 1회",
        "unit": "1회",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_인중_5회": {
        "category": "레이저_제모",
        "name": "여성 인중 잔털 제모 5회 패키지",
        "unit": "5회 패키지",
        "technique": "비접촉 에어쿨링",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_팔하완_5회": {
        "category": "레이저_제모",
        "name": "여성 팔 하완 5회 (손목~팔꿈치)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_팔전체_5회": {
        "category": "레이저_제모",
        "name": "여성 팔 전체 5회 (상완+하완)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_종아리_5회": {
        "category": "레이저_제모",
        "name": "여성 종아리 전체 5회 패키지",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_다리전체_5회": {
        "category": "레이저_제모",
        "name": "여성 다리 전체 5회 (종아리+허벅지)",
        "unit": "5회 패키지",
        "technique": "넓은 스팟 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_비키니_5회": {
        "category": "레이저_제모",
        "name": "여성 비키니라인 5회 패키지",
        "unit": "5회 패키지",
        "technique": "DCD 비접촉 냉각 (여의사 전담)",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_브라질리언_5회": {
        "category": "레이저_제모",
        "name": "여성 브라질리언 올누드 5회",
        "unit": "5회 패키지",
        "technique": "DCD 특수 냉각 (여의사 1:1)",
        "knowledge_key": "레이저_제모"
    },
    "제모_여성_헤어라인_5회": {
        "category": "레이저_제모",
        "name": "여성 헤어라인/이마 5회 패키지",
        "unit": "5회 패키지",
        "technique": "정밀 디자인 레이저",
        "knowledge_key": "레이저_제모"
    },
    "제모_브라질리언_1회": {
        "category": "레이저_제모",
        "name": "올누드 브라질리언 위생 제모 1회 (남/녀)",
        "unit": "1회",
        "technique": "DCD 특수 냉각",
    # 5. 색소 & 토닝 & 모공 (장비별 / 1회 단품 vs 10회 패키지 희석방지 독립 규격)
    # 5-1. 일반 큐스위치 엔디야그 토닝
    "토닝_큐스위치_1회": {
        "category": "레이저_색소",
        "name": "일반 큐스위치 레이저 토닝 (1회 단품)",
        "unit": "1회 단품",
        "technique": "1064nm 큐스위치 엔디야그 (VRM/헬리오스)",
        "knowledge_key": "레이저_토닝"
    },
    "토닝_큐스위치_10회": {
        "category": "레이저_색소",
        "name": "일반 큐스위치 레이저 토닝 (10회 패키지)",
        "unit": "10회 패키지",
        "technique": "1064nm 큐스위치 10회 벌크 패키지",
        "knowledge_key": "레이저_토닝"
    },
    # 5-2. 국산 듀얼 피코토닝 (피코플러스/피코하이)
    "토닝_피코플러스_1회": {
        "category": "레이저_색소",
        "name": "피코 토닝 1회 단품 [피코플러스/피코하이]",
        "unit": "1회 단품",
        "technique": "피코초 450ps 듀얼 피코 레이저",
        "knowledge_key": "레이저_토닝"
    },
    "토닝_피코플러스_10회": {
        "category": "레이저_색소",
        "name": "피코 토닝 10회 패키지 [피코플러스/피코하이]",
        "unit": "10회 패키지",
        "technique": "피코초 듀얼토닝 10회 정규 패키지",
        "knowledge_key": "레이저_토닝"
    },
    # 5-3. 미국 사이노슈어 오리지널 피코슈어 (755nm 알렉스 끝판왕)
    "토닝_피코슈어_1회": {
        "category": "레이저_색소",
        "name": "피코슈어 755nm 1회 단품 [사이노슈어 정품]",
        "unit": "1회 단품",
        "technique": "미국 사이노슈어 755nm 알렉산드라이트 오리지널",
        "knowledge_key": "레이저_토닝"
    },
    "토닝_피코슈어_10회": {
        "category": "레이저_색소",
        "name": "피코슈어 755nm 10회 패키지 [사이노슈어 정품]",
        "unit": "10회 패키지",
        "technique": "피코슈어 755nm 10회 프리미엄 패키지",
        "knowledge_key": "레이저_토닝"
    },
    # 5-4. 피코프락셀 & 복합 듀얼
    "피코프락셀": {
        "category": "레이저_색소",
        "name": "피코프락셀 (모공/흉터 LIOB 1회 단품)",
        "unit": "1회 단품",
        "technique": "MLA/DOE 렌즈",
        "knowledge_key": "피코_프락셀"
    },
    "피코프락셀_3회": {
        "category": "레이저_색소",
        "name": "피코프락셀 (모공/흉터 LIOB 3회 패키지)",
        "unit": "3회 패키지",
        "technique": "MLA/DOE 렌즈 3회 코스",
        "knowledge_key": "피코_프락셀"
    },
    "듀얼토닝_복합_10회": {
        "category": "레이저_색소",
        "name": "듀얼 피코토닝+제네시스 홍조 10회 복합패키지",
        "unit": "10회 패키지",
        "technique": "피코토닝 + 롱펄스 제네시스 듀얼 복합",
        "knowledge_key": "레이저_토닝"
    },
        "knowledge_key": "피코_프락셀"
    },
    # 6. 보톡스 & 쁘띠
    "스킨보톡스_나비존": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 나비존 모공 (국산 1.5cc)",
        "unit": "1.5cc",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "스킨보톡스_풀페이스": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 풀페이스 (국산 3.5cc)",
        "unit": "3.5cc",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "스킨보톡스_제오민": {
        "category": "보톡스_쁘띠",
        "name": "스킨보톡스 풀페이스 (독일 제오민 순수톡신)",
        "unit": "순수톡신 풀페이스",
        "technique": "진피내 더모톡신",
        "knowledge_key": "스킨보톡스"
    },
    "사각턱보톡스_국산": {
        "category": "보톡스_쁘띠",
        "name": "사각턱 보톡스 (국산 50U)",
        "unit": "50U",
        "technique": "근육내 주사",
        "knowledge_key": "사각턱_보톡스"
    },
    "사각턱보톡스_제오민": {
        "category": "보톡스_쁘띠",
        "name": "사각턱 보톡스 (독일 제오민 50U 순수톡신)",
        "unit": "50U",
        "technique": "내성예방 순수톡신",
        "knowledge_key": "사각턱_보톡스"
    },
    "국소_레티노이드": {
        "category": "보톡스_쁘띠",
        "name": "디페린/아다팔렌 처방전 (비급여 1회)",
        "unit": "1회 처방",
        "technique": "외용제 처방",
        "knowledge_key": "국소_레티노이드"
    },
    # 7. 한방 미용
    "한방_매선침_리프팅": {
        "category": "한방_미용",
        "name": "한방 매선침 리프팅 (녹는 실 침술 40줄)",
        "unit": "40줄",
        "technique": "매선 침구",
        "knowledge_key": "바늘_고주파"
    },
    "한방_새살침_MTS": {
        "category": "한방_미용",
        "name": "코라테라피 새살침 (흉터·모공 유착박리 침술)",
        "unit": "1부위",
        "technique": "침구 유착박리",
        "knowledge_key": "바늘_고주파"
    }
}

web_database = {
    "hospitals": ANONYMIZED_DATABASE,
    "kosis_coverage": kosis,
    "treatments": {},
    "categories": [
        {"id": "all", "name": "전체 시술 보기"},
        {"id": "초음파_리프팅", "name": "초음파(HIFU) 리프팅"},
        {"id": "고주파_리프팅", "name": "고주파(RF) 리프팅"},
        {"id": "스킨부스터", "name": "스킨부스터 (수기손주사/인젝터)"},
        {"id": "레이저_제모", "name": "레이저 영구 제모 (남성수염/여성)"},
        {"id": "바늘_고주파", "name": "모공·흉터 니들RF (포텐자)"},
        {"id": "레이저_색소", "name": "레이저·색소 (피코토닝·프락셀)"},
        {"id": "보톡스_쁘띠", "name": "보톡스·쁘띠 (더모톡신·사각턱)"},
        {"id": "한방_미용", "name": "한방 미용침구 (매선·새살침)"}
    ]
}

# 각 시술별 통계 및 병원 목록 빌드
for t_key, meta in TREATMENT_META.items():
    hosp_entries = []
    prices_inc_vat = []
    prices_ex_vat = []

    for h in HOSPITAL_PRICE_DATABASE:
        t_data = h.get("treatments", {}).get(t_key)
        if t_data:
            p_inc = t_data.get("price_inc_vat", 0)
            p_ex = t_data.get("price_ex_vat", 0)
            if p_inc > 0:
                hosp_entries.append({
                    "hospital_name": h.get("hospital_name"),
                    "district": h.get("district"),
                    "clinic_type": h.get("clinic_type"),
                    "is_specialist": h.get("is_specialist", False),
                    "vat_included": h.get("vat_included", False),
                    "vat_policy": h.get("vat_policy", ""),
                    "road_address": h.get("road_address", h.get("location", "")),
                    "subway_station": h.get("subway_station", ""),
                    "tags": h.get("tags", []),
                    "tel": h.get("tel", ""),
                    "procedure_name": t_data.get("procedure_name"),
                    "price_1session": t_data.get("price_1session"),
                    "price_inc_vat": p_inc,
                    "price_inc_vat_str": t_data.get("price_inc_vat_str", f"{p_inc:,}원"),
                    "price_ex_vat": p_ex,
                    "note": t_data.get("note", "")
                })
                prices_inc_vat.append(p_inc)
                prices_ex_vat.append(p_ex)

    if not hosp_entries:
        continue

    # 가격순 정렬
    hosp_entries.sort(key=lambda x: x["price_inc_vat"])

    arr_inc = np.array(prices_inc_vat)
    arr_ex = np.array(prices_ex_vat)

    q1 = float(np.percentile(arr_inc, 25))
    median = float(np.median(arr_inc))
    q3 = float(np.percentile(arr_inc, 75))
    iqr = q3 - q1
    low_fence = max(0, q1 - 1.5 * iqr)
    high_fence = q3 + 1.5 * iqr

    # 이상치 분리
    low_outliers = [h for h in hosp_entries if h["price_inc_vat"] < low_fence]
    high_outliers = [h for h in hosp_entries if h["price_inc_vat"] > high_fence]
    normal_hospitals = [h for h in hosp_entries if low_fence <= h["price_inc_vat"] <= high_fence]

    # 구별 평균 산출
    districts = ["수성구", "달서구", "중구", "북구", "동구", "서구", "남구", "달성군"]
    dist_stats = {}
    for d in districts:
        d_prices = [h["price_inc_vat"] for h in hosp_entries if h["district"] == d]
        if d_prices:
            dist_stats[d] = {
                "count": len(d_prices),
                "mean": int(round(np.mean(d_prices))),
                "min": int(min(d_prices)),
                "max": int(max(d_prices))
            }
        else:
            dist_stats[d] = {"count": 0, "mean": 0, "min": 0, "max": 0}

    # 의학 지식 추출
    k_key = meta.get("knowledge_key", "쥬베룩")
    med_info = TREATMENT_KNOWLEDGE.get(k_key, {})

    web_database["treatments"][t_key] = {
        "key": t_key,
        "name": meta["name"],
        "category": meta["category"],
        "unit": meta["unit"],
        "technique": meta["technique"],
        "sample_count": len(hosp_entries),
        "price_inc_vat": {
            "mean": int(round(float(np.mean(arr_inc)))),
            "median": int(median),
            "std": int(round(float(np.std(arr_inc)))),
            "min": int(np.min(arr_inc)),
            "max": int(np.max(arr_inc)),
            "q1": int(q1),
            "q3": int(q3),
            "iqr": int(iqr),
            "low_fence": int(low_fence),
            "high_fence": int(high_fence),
            "prices_sorted": [int(x) for x in sorted(prices_inc_vat)]
        },
        "price_ex_vat": {
            "mean": int(round(float(np.mean(arr_ex)))),
            "median": int(float(np.median(arr_ex))),
            "min": int(np.min(arr_ex)),
            "max": int(np.max(arr_ex))
        },
        "district_stats": dist_stats,
        "low_outliers": low_outliers,
        "high_outliers": high_outliers,
        "normal_cheapest_top5": normal_hospitals[:5],
        "all_hospitals": hosp_entries,
        "medical_precautions": med_info.get("precautions", []),
        "side_effects": med_info.get("side_effects", [])
    }

# 1. treatment_stats.json 및 data.js 저장
for target_dir in ["SKIN/web_app", "deploy_skin", "deploy_skin/docs"]:
    os.makedirs(target_dir, exist_ok=True)
    j_p = os.path.join(target_dir, "treatment_stats.json")
    with open(j_p, "w", encoding="utf-8") as f:
        json.dump(web_database, f, ensure_ascii=False, indent=2)
    
    js_p = os.path.join(target_dir, "data.js")
    with open(js_p, "w", encoding="utf-8") as f:
        f.write("window.DAEGU_SKIN_DATA = ")
        json.dump(web_database, f, ensure_ascii=False)
        f.write(";\n")

print(f"완료: 전체 디렉토리에 동기화 저장 완료 (총 {len(web_database['treatments'])}개 세부 시술 탑재)!")
