# 📉 Bitcoin Market Crash Analysis

**2025년 10월 비트코인 급락 종합 분석 프로젝트**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [분석 결과](#-분석-결과)
- [설치 방법](#-설치-방법)
- [사용 방법](#-사용-방법)
- [프로젝트 구조](#-프로젝트-구조)
- [기술 스택](#-기술-스택)
- [팀 정보](#-팀-정보)

## 🎯 프로젝트 개요

2025년 10월 10일 발생한 비트코인 급락(-7.22%)의 원인을 다각도로 분석한 데이터 사이언스 프로젝트입니다.
거시경제 지표, 뉴스 감성, 소셜 미디어 활동, 파생상품 데이터 등을 통합하여 시장 급락의 트리거와 패턴을 파악했습니다.

### 분석 기간

- **데이터 기간**: 2025년 9월 1일 ~ 10월 31일 (61일)
- **급락 발생일**: 2025년 10월 10일
- **데이터 소스**: 6개 CSV 파일, 총 28,340 레코드

### 핵심 연구 질문

1. 시장 급락의 트리거와 정치적 요인의 상관관계
2. 투자자 심리 분석 (공포와 탐욕의 교차)
3. 거시경제 지표와 가상자산의 관계
4. 감성-가격 회귀 분석
5. Open Interest(미결제약정) 패턴 분석
6. 네트워크 관계도를 통한 변수 간 연결성 파악

## ✨ 주요 기능

### 1. 📊 데이터 파이프라인

- **자동화된 데이터 검증**: 6개 소스 파일의 무결성 검증
- **시계열 통합**: 날짜 기준 데이터 병합 (61×53 마스터 데이터프레임)
- **결측치 처리**: 전방향 보간법(forward fill) 적용

### 2. 📈 15가지 시각화 분석

- 가격 추이 및 변화 속도 분석
- 상관관계 히트맵 (전체 & 고상관)
- 정치 테마 시계열 및 시차 상관관계
- 감성-가격 회귀 분석 (산점도 & 잔차)
- 거시경제 모델링 (R² = 0.4448)
- Open Interest vs 가격 분석
- 감성별 워드클라우드 (전체/긍정/부정/중립)
- 네트워크 그래프 (전체 & 단순화)

### 3. 🌐 인터랙티브 대시보드

- **Streamlit 웹 애플리케이션**
- 날짜 범위 필터링 슬라이더
- 거시경제 변수 선택 드롭다운
- 5개 탭: 가격/감성/거시경제/상관관계/종합
- 실시간 차트 업데이트
- CSV 데이터 다운로드 기능

### 4. 📄 자동 리포트 생성

- **PDF 형식 종합 분석 리포트** (5+ MB)
- 표지, 요약, 8개 섹션, 결론 페이지
- 18+ 고품질 차트 이미지 포함
- 한글 폰트 지원 (맑은 고딕)

## 🔬 분석 결과

### 주요 발견사항

#### 1. 거시경제 변수의 높은 설명력 ⭐

- **R² = 0.4448**: M2 통화량, 10년물 금리, 달러 인덱스가 가격 변동의 44.5%를 설명
- M2 통화량: +4,241 표준화 계수 (강한 양의 영향)
- 달러 인덱스: -3,740 표준화 계수 (강한 음의 영향)
- 10년물 금리: +2,223 표준화 계수 (양의 영향)
- **감성 변수(R² = 0.1974)보다 2배 이상 높은 설명력**

#### 2. Open Interest의 선행 지표 가능성 📊

- OI와 가격의 강한 양의 상관관계: **r = +0.684**
- 급락 전 평균 OI: 103.95 (최고치)
- 급락 후 평균 OI: 71.74 (**-31% 감소**)
- 10월 11일 OI 급감 **-32%** → 대규모 청산 발생 신호

#### 3. 정치 테마의 시차 효과 📰

- 정치 관련 뉴스가 가격에 **1일 선행** (lag correlation)
- 급락 전 3일간 정치 테마 **+17.4% 급증**
- 7개 주요 스파이크 날짜 식별

#### 4. SNS 활동의 중심 역할 💬

- `sns_post_count`가 최고 연결 중심성: **0.667**
- 커뮤니티 활동이 시장 전반의 허브 역할
- 네트워크에서 16개 노드, 48개 엣지 분석

#### 5. 부정 감성의 유의한 영향 😟

- `tone_neg_share`가 가격과 유의한 관계: **p = 0.040**
- 네트워크에서 허브 역할: **betweenness = 0.229**
- 전체 감성 평균: -0.190 (부정 우세)

## 🚀 설치 방법

### 필수 요구사항

- Python 3.11 이상
- pip 또는 uv (패키지 관리자)
- Git

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/ai_team_6.git
cd ai_team_6
```

### 2. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
# uv 사용 (권장)
uv pip install -r requirements.txt

# pip 사용
pip install -r requirements.txt
```

### 주요 라이브러리

- `pandas==2.3.3` - 데이터 처리
- `numpy==2.4.2` - 수치 연산
- `matplotlib==3.10.8` - 시각화
- `seaborn==0.13.2` - 통계 시각화
- `scipy==1.17.0` - 과학 계산
- `scikit-learn==1.8.0` - 머신러닝
- `streamlit==1.53.1` - 대시보드
- `plotly==6.5.2` - 인터랙티브 차트
- `reportlab==4.4.9` - PDF 생성
- `wordcloud==1.9.6` - 워드클라우드
- `networkx==3.6.1` - 네트워크 분석

## 💻 사용 방법

### 1. 데이터 분석 파이프라인 실행

전체 분석을 순차적으로 실행:

```bash
# Task 1-3: 데이터 로딩, 정제, 통합
python 01_data_loading_validation.py
python 02_data_cleaning_standardization.py
python 03_data_integration.py

# Task 4-6: 가격 및 정치 분석
python 04_price_visualization.py
python 05_correlation_heatmap.py
python 06_political_themes_analysis.py

# Task 7-9: 감성 및 거시경제 분석
python 07_sentiment_analysis.py
python 08_sentiment_price_regression.py
python 09_macroeconomic_regression.py

# Task 10-12: 파생상품, 워드클라우드, 네트워크
python 10_open_interest_analysis.py
python 11_wordcloud_generation.py
python 12_network_analysis.py
```

### 2. Streamlit 대시보드 실행

```bash
streamlit run dashboard_app.py
```

브라우저에서 자동으로 열립니다: `http://localhost:8501`

#### 대시보드 사용법

1. **사이드바**: 날짜 범위 선택, 주요 지표 확인
2. **가격 분석 탭**: 가격 추이, Open Interest 비교
3. **감성 분석 탭**: 뉴스 및 커뮤니티 감성 추이
4. **거시경제 탭**: M2, 금리, 달러 인덱스 선택 및 비교
5. **상관관계 탭**: 인터랙티브 히트맵, Top 10 상관관계
6. **종합 분석 탭**: 주요 발견사항, 데이터 테이블, CSV 다운로드

### 3. PDF 리포트 생성

```bash
python 14_generate_report.py
```

생성된 리포트 위치: `output/reports/Bitcoin_Crash_Analysis_Report_YYYYMMDD_HHMMSS.pdf`

## 📁 프로젝트 구조

```
ai_team_6/
├── data/                           # 데이터 디렉토리
│   ├── processed/                  # 가공된 데이터
│   │   └── integrated/             # 통합 마스터 데이터
│   │       └── master_data_integrated.csv
│   ├── Community_data/             # 커뮤니티 데이터
│   ├── files/                      # 원본 파일
│   └── news/                       # 뉴스 데이터 (일별 CSV)
│
├── output/                         # 출력 디렉토리
│   ├── visualizations/             # 생성된 차트 (18+ PNG)
│   └── reports/                    # PDF 리포트
│
├── 01_data_loading_validation.py  # Task 1: 데이터 검증
├── 02_data_cleaning_standardization.py  # Task 2: 데이터 정제
├── 03_data_integration.py         # Task 3: 데이터 통합
├── 04_price_visualization.py      # Task 4: 가격 시각화
├── 05_correlation_heatmap.py      # Task 5: 상관관계 분석
├── 06_political_themes_analysis.py # Task 6: 정치 테마 분석
├── 07_sentiment_analysis.py       # Task 7: 감성 분석
├── 08_sentiment_price_regression.py # Task 8: 감성-가격 회귀
├── 09_macroeconomic_regression.py # Task 9: 거시경제 모델
├── 10_open_interest_analysis.py   # Task 10: Open Interest
├── 11_wordcloud_generation.py     # Task 11: 워드클라우드
├── 12_network_analysis.py         # Task 12: 네트워크 분석
├── 14_generate_report.py          # Task 14: PDF 리포트
├── dashboard_app.py                # Task 13: Streamlit 대시보드
│
├── .taskmaster/                    # Task Master 프로젝트 관리
│   └── tasks/
│       └── tasks.json              # 15개 태스크 정의
│
├── README.md                       # 본 문서
├── USER_GUIDE.md                   # 사용자 가이드
├── requirements.txt                # Python 의존성
└── pyproject.toml                  # 프로젝트 설정
```

## 🛠️ 기술 스택

### 데이터 분석

- **Pandas**: 데이터프레임 조작, 시계열 처리
- **NumPy**: 배열 연산, 수학 함수
- **SciPy**: 통계 검정, 상관관계 분석

### 머신러닝

- **Scikit-learn**: 선형 회귀, StandardScaler
- **NetworkX**: 그래프 분석, 중심성 계산

### 시각화

- **Matplotlib**: 정적 차트 생성
- **Seaborn**: 통계 시각화, 히트맵
- **Plotly**: 인터랙티브 차트
- **WordCloud**: 텍스트 시각화

### 웹 애플리케이션

- **Streamlit**: 인터랙티브 대시보드
- **ReportLab**: PDF 리포트 생성

### 개발 도구

- **UV**: 빠른 Python 패키지 관리
- **Task Master AI**: 프로젝트 작업 관리
- **Git**: 버전 관리

## 📊 데이터 소스

### 1. 가격 데이터

- BTC_Price: 비트코인 USD 가격
- BTC_Price_Speed: 1차 미분 (변화율)
- BTC_Price_Accel: 2차 미분 (가속도)

### 2. 거시경제 지표

- M2SL: M2 통화량
- Yield_10Y: 미국 10년물 국채 수익률
- USD_Index: 달러 인덱스
- CPI: 소비자물가지수

### 3. 뉴스 감성

- tone_mean: 평균 감성 점수
- tone_pos_share: 긍정 뉴스 비율
- tone_neg_share: 부정 뉴스 비율
- 정치 테마 카운트 (7개 카테고리)

### 4. 커뮤니티 데이터

- sns_post_count: SNS 게시물 수
- sentiment_mean: 커뮤니티 감성 평균

### 5. 파생상품

- Open_Interest: 선물 미결제약정

## 👥 팀 정보

**Team Doge** - AI Team 6

이 프로젝트는 데이터 사이언스 팀 프로젝트로 개발되었습니다.

## 📝 라이선스

This project is licensed under the MIT License.

## 🙏 감사의 말

- GDELT Project: 뉴스 데이터 제공
- Reddit/YouTube API: 커뮤니티 데이터
- 거시경제 데이터 제공 기관

## 📞 문의

프로젝트 관련 문의사항은 GitHub Issues를 통해 남겨주세요.

---

**Last Updated**: 2026-02-03  
**Version**: 1.0.0

```

```
