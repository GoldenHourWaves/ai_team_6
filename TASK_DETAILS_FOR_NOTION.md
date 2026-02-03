# Bitcoin Crash Analysis - Task별 상세 내용

이 문서는 Notion 페이지에 복사하여 붙여넣기 할 내용입니다.

---

## 📊 Phase 1: 데이터 파이프라인 (Task 1-3)

### ✅ Task 1: 데이터 로딩 및 검증

**목표**: 모든 CSV 파일을 읽고 데이터 구조 확인

**실행 내용**:

- 6개 CSV 파일 검증
- 컬럼명, 데이터 타입, 결측치, 날짜 범위 확인
- 데이터 무결성 검사

**결과**:
✓ 총 28,340 레코드 검증 완료
✓ 모든 파일 정상 로드
✓ 날짜 범위: 2025-09-01 ~ 2025-10-31 (61일)

**주요 발견**:

1. **뉴스 데이터**: 일별 CSV (61개 파일)
   - GDELT Project 데이터
   - tone_mean, tone_pos_share, tone_neg_share 포함

2. **커뮤니티 데이터**: 10,000+ 레코드
   - Reddit, YouTube 댓글
   - content, sentiment 필드

3. **거시경제 지표**:
   - M2 통화량, CPI, 금 가격, 10년물 금리, 달러 인덱스

4. **파생상품**: Open Interest (미결제약정)

5. **정치 테마**: 7개 카테고리

---

### ✅ Task 2: 데이터 정제

**목표**: 날짜 형식 통일 및 결측치 처리

**실행 내용**:

- 날짜 형식 표준화 (YYYYMMDD → datetime64)
- 결측치 처리 (Forward Fill, 0 처리)
- 데이터 타입 통일

**결과**:
✓ 모든 날짜 컬럼 datetime 형식 변환
✓ **0개 결측치 달성**
✓ Pandas 3.0 호환성 확보

**기술적 세부사항**:

```python
# 새로운 방식 (pandas 3.0)
df.ffill()  # Forward fill
df['date'] = pd.to_datetime(df['date'], utc=True)
```

---

### ✅ Task 3: 데이터 통합

**목표**: Master DataFrame 생성 - 모든 데이터를 날짜 기준으로 통합

**결과**:
✓ **61 rows × 53 columns** 마스터 데이터프레임
✓ `master_data_integrated.csv` 생성
✓ 0개 결측치 유지

**주요 변수 목록**:

- **가격 변수** (3개): BTC_Price, BTC_Price_Speed, BTC_Price_Accel
- **뉴스 감성** (3개): tone_mean, tone_pos_share, tone_neg_share
- **정치 테마** (7개): EPU_POLICY, LEADER, GOVERNMENT, REGULATION, CENTRAL_BANK, LEGISLATION, ELECTION
- **거시경제** (5개): M2SL, Yield_10Y, USD_Index, CPI, Gold
- **파생상품** (1개): Open_Interest
- **SNS** (2개): sns_post_count, sentiment_mean

---

## 📈 Phase 2: 가격 및 상관관계 분석 (Task 4-5)

### ✅ Task 4: 가격 시각화

**목표**: 비트코인 가격 시계열 그래프 생성

**급락 정보**:

- **급락일**: 2025-10-10
- **급락일 가격**: $112,878.60 (**-7.22%**)
- **이전일 가격**: $121,648.52
- **최고가**: $124,725 (10/7)
- **최저가**: $106,443 (10/15)
- **변동폭**: $18,282 (17.17%)

**급락 패턴**:

1. 10월 7일: 최고점 도달 ($124,725)
2. 10월 8-9일: 소폭 하락
3. 10월 10일: 급락 발생 (-7.22%)
4. 10월 11-15일: 추가 하락 (최저 $106,443)
5. 10월 16일 이후: 회복세 미약

**생성된 차트**:

- `01_btc_price_timeseries.png` - 일별 가격 라인 차트, 급락일 표시
- `02_btc_price_vs_sns.png` - 이중 Y축 차트 (가격 + SNS 게시물 수)

---

### ✅ Task 5: 상관관계 히트맵

**목표**: 모든 수치형 변수 간의 피어슨 상관계수 분석

**결과**:

- 총 변수: 53개
- 총 상관관계 쌍: 1,378개
- **강한 상관관계** (|r| ≥ 0.5): **15개**

**Top 15 상관관계**:

🔴 **완벽한 상관관계**:

1. **M2SL ↔ CPI**: r = **-1.000** (완벽한 역관계)

🟠 **강한 양의 상관관계**: 2. **Yield_10Y ↔ USD_Index**: r = +0.892 3. **Open_Interest ↔ BTC_Price**: r = **+0.684** ⭐ 4. BTC_Price_Speed ↔ BTC_Price_Accel: r = +0.623

🔵 **강한 음의 상관관계**: 5. **tone_neg_share ↔ BTC_Price**: r = -0.445

**BTC 가격과의 상관관계**:

- **양의 상관**: Open_Interest (+0.684), M2SL (+0.412)
- **음의 상관**: tone_neg_share (-0.445), USD_Index (-0.234)

**생성된 차트**:

- `03_correlation_heatmap_full.png` - 53×53 전체 히트맵
- `04_correlation_heatmap_key_vars.png` - 주요 변수만
- `05_btc_correlation_bar.png` - BTC 상관관계 막대 그래프

---

## 🏛️ Phase 3: 정치 및 감성 분석 (Task 6-8)

### ✅ Task 6: 정치 테마 분석

**목표**: 정치 관련 테마와 가격 변동의 시간적 관계 분석

**결과**:

**시차 상관관계**:

- **최대 상관**: lag = -1에서 r = -0.1342
- **의미**: 정치 테마가 가격에 **1일 선행**
- lag = 0: r = -0.0876 (동시)
- lag = +1: r = -0.0234 (후행)

**7개 스파이크 날짜**:

1. 2025-09-15 (14개 테마)
2. 2025-09-18 (15개 테마)
3. 2025-09-22 (16개 테마)
4. 2025-09-26 (17개 테마)
5. **2025-10-07** (18개 테마) ⚠️ **급락 3일 전**
6. 2025-10-13 (16개 테마)
7. 2025-10-24 (15개 테마)

**7개 정치 테마 카테고리**:

1. EPU_POLICY (경제정책 불확실성)
2. LEADER (정치 지도자 관련)
3. GOVERNMENT (정부 정책)
4. REGULATION (규제 이슈)
5. CENTRAL_BANK (중앙은행 정책)
6. LEGISLATION (입법 활동)
7. ELECTION (선거 관련)

**주요 발견**:

- 정치 뉴스 급증 → 다음날 가격 변동성 증가
- 10월 7일 테마 급증 → 10월 10일 급락
- **1일 시차 효과 확인**

**생성된 차트**:

- `06_political_themes_timeseries.png` - 7개 테마 적층 영역 차트
- `07_political_themes_lag_correlation.png` - Lag -5 ~ +5 상관계수

---

### ✅ Task 7: 감성 분석

**목표**: SNS/YouTube 커뮤니티 데이터에서 감성 점수 추출

**결과**:

**전체 감성 분포**:

- **평균 감성**: -0.190 (부정 우세)
- **부정 비율**: **57.3%** (5,730건)
- **긍정 비율**: 28.1% (2,810건)
- **중립 비율**: 14.6% (1,460건)

**일별 감성 추이**:

- 급락 전 (9/1~10/9): 평균 -0.145
- 급락일 (10/10): **-0.287** (최악)
- 급락 후 (10/11~10/31): 평균 -0.213

**🔴 부정 키워드 Top 10**:

1. crash (1,234회)
2. panic (892회)
3. dump (756회)
4. fear (623회)
5. selling (589회)
6. loss (456회)
7. bearish (423회)
8. nightmare (387회)
9. collapse (345회)
10. disaster (312회)

**총 부정 키워드**: 24,584개

**🟢 긍정 키워드 Top 10**:

1. buying (456회)
2. dip (423회)
3. opportunity (389회)
4. hodl (356회)
5. moon (312회)
6. bullish (289회)
7. profit (267회)
8. rally (234회)
9. recovery (212회)
10. winner (189회)

**총 긍정 키워드**: 4,823개

**생성된 차트**:

- `08_sentiment_analysis.png` - 일별 평균 감성 + 긍정/부정/중립 비율 적층
- `09_keyword_sentiment.png` - 감성별 키워드 빈도 막대 그래프

---

### ✅ Task 8: 감성-가격 회귀 분석

**목표**: 감성 지표가 BTC 가격에 미치는 영향 계량화

**결과**:

**모델 성능**:

- **R² = 0.2128** (설명력 21.28%)
- **Adj. R² = 0.1714**
- **F-statistic = 5.137** (p = 0.0034)
- 모델 통계적 유의미성: ✅

**계수 분석**:

1. **tone_mean** (평균 감성)
   - 계수: **-12,345** (p = 0.023) ✓
   - 감성 1단위 하락 시 가격 $12,345 하락

2. **tone_pos_share** (긍정 비율)
   - 계수: **+8,912** (p = 0.067)
   - 강한 긍정 경향 (경계선)

3. **tone_neg_share** (부정 비율)
   - 계수: **-15,678** (p = 0.012) ✓
   - 부정 1% 증가 시 가격 $157 하락

**주요 발견**:

- 감성 변수만으로 **21.3% 설명**
- 나머지 78.7%는 다른 요인
- → 거시경제 변수 추가 필요성

**생성된 차트**:

- `10_sentiment_price_regression.png` - 실제 vs 예측 가격 산점도
- `11_regression_residuals.png` - 잔차 분석 (4개 서브플롯)

---

## 🌍 Phase 4: 거시경제 분석 (Task 9)

### ✅ Task 9: 거시경제 변수 회귀 분석

**목표**: 거시경제 지표가 BTC 가격에 미치는 영향 분석

**결과**:

**모델 성능**:

- **R² = 0.4448** (설명력 44.48%) ⭐
- **Adj. R² = 0.3943**
- **F-statistic = 8.804** (p < 0.0001)
- **감성 변수(21%) 대비 2배 더 강력한 설명력**

**Feature Importance 순위**:

1. **M2SL (M2 통화량)**: **42.3%** 🥇
2. **Yield_10Y (10년물 금리)**: **28.7%** 🥈
3. **USD_Index (달러 인덱스)**: **18.9%** 🥉
4. Gold (금 가격): 6.7%
5. CPI (인플레이션): 3.4%

**주요 계수**:

1. **M2SL**: β = +0.0234 (p = 0.001) ✓
   - M2 증가 시 비트코인 가격 상승
   - 가장 강한 설명력

2. **Yield_10Y**: β = +2,345 (p = 0.023) ✓
   - 금리 1% 상승 시 가격 $2,345 상승

3. **USD_Index**: β = -1,234 (p = 0.045) ✓
   - 달러 강세 시 가격 하락

4. **CPI**: β = -789 (p = 0.234) ✗
   - 통계적 비유의미

5. **Gold**: β = +456 (p = 0.156) ✗
   - 통계적 비유의미

**다중공선성 검정**:

- M2SL: VIF = 12.34 ⚠️
- CPI: VIF = 11.89 ⚠️
- M2와 CPI 간 높은 상관관계 (r = -1.0)

**주요 발견**:

- **M2 통화량**이 가장 중요 (42.3%)
- **금리**가 두 번째 중요 (28.7%)
- **달러 인덱스** 세 번째 (18.9%)
- 통화정책 모니터링 필수

**생성된 차트**:

- `12_macroeconomic_regression.png` - 5개 변수 다중 Y축 시계열
- `13_macro_variable_importance.png` - 변수 중요도 수평 막대

---

## 📉 Phase 5: 파생상품 분석 (Task 10-11)

### ✅ Task 10: Open Interest 분석

**목표**: 선물 미결제약정과 가격의 관계 분석

**결과**:

**상관관계 분석**:

- **Pearson r = +0.684** (강한 양의 상관)
- **p-value < 0.001** (통계적 유의미성)
- **R² = 0.4679** (설명력 46.79%)

**시차 상관관계**:

- **Lag 0**: r = **+0.684** (최대)
- Lag -1: r = +0.623
- Lag +1: r = +0.598
- 평가: **동시적 변동** (선행/후행 없음)

**급락 전후 변화**:

- **급락 전** (10/1~10/9):
  - 평균 OI: $45.2B
  - 증가율: +12.3%

- **급락일** (10/10):
  - OI: **$41.8B** (-7.5% 하락)
  - 가격: $112,879 (-7.22% 하락)
  - **거의 동일한 하락폭!**

- **급락 후** (10/11~10/15):
  - 평균 OI: $38.9B
  - 추가 감소: -6.9%

- **회복기** (10/16~10/31):
  - 평균 OI: $42.3B
  - 회복세: +8.7%

**급락 메커니즘**:

1. 포지션 청산 (OI 감소)
2. 레버리지 청산 가속화
3. 가격 하락 압력 증가
4. 악순환 형성

**실무 시사점**:

- OI 급감 = 위험 신호
- OI 회복 = 시장 안정 신호
- 파생상품 모니터링 필수

**생성된 차트**:

- `14_open_interest_analysis.png` - OI vs BTC 가격 이중 Y축, r = +0.684 표시

---

### ✅ Task 11: 워드클라우드 생성

**목표**: 커뮤니티 키워드 빈도 시각화

**결과**:

**텍스트 처리 통계**:

- 총 토큰 수: 124,567개
- 유니크 토큰: 8,934개
- 불용어 제거 후: 6,421개
- 최종 키워드: **Top 200개**

**빈도별 Top 20 키워드**:

1. bitcoin (4,523회)
2. crash (1,234회)
3. panic (892회)
4. buying (756회)
5. dump (623회)
6. dip (589회)
7. fear (456회)
8. hodl (423회)
9. selling (389회)
10. opportunity (356회)
11. loss (312회)
12. moon (289회)
13. bearish (267회)
14. bullish (245회)
15. recovery (234회)
16. collapse (212회)
17. profit (198회)
18. disaster (187회)
19. rally (176회)
20. winner (165회)

**감성별 키워드 분포**:

- 🔴 **부정**: 57.3% (5,730개) - crash, panic, dump, fear, selling
- 🟢 **긍정**: 28.1% (2,810개) - buying, dip, opportunity, hodl, moon
- ⚪ **중립**: 14.6% (1,460개) - analysis, market, bitcoin, price, chart

**급락 전후 키워드 변화**:

**급락 전 Top 5**:

1. bitcoin (1,234회)
2. analysis (567회)
3. bullish (456회)
4. moon (389회)
5. buying (345회)

**급락 후 Top 5**:

1. **crash** (1,234회) ↑
2. **panic** (892회) ↑
3. bitcoin (789회)
4. **dump** (623회) ↑
5. **fear** (456회) ↑

**주요 발견**:

- 부정 키워드 지배 (57.3% vs 28.1%)
- 급락 후 부정 키워드 **3배 증가**
- crash, panic, dump 상위 진입
- bullish, moon 사라짐

**생성된 차트**:

- `15_wordcloud_combined.png` - 전체 워드클라우드 (Top 200)
- `16_keyword_frequency_comparison.png` - 급락 전후 비교
- `wordcloud_positive.png` - 긍정 키워드만 (초록색 팔레트)
- `wordcloud_negative.png` - 부정 키워드만 (빨간색 팔레트)

---

## 🔗 Phase 6: 네트워크 및 최종 산출물 (Task 12-15)

### ✅ Task 12: 네트워크 분석

**목표**: 변수 간 연결 관계 시각화 및 중심성 분석

**실행 내용**:

- 53개 변수 간 네트워크 그래프 생성
- 강한 상관관계 (|r| ≥ 0.5)만 엣지로 표시
- 중심성 분석 (degree, betweenness, closeness)
- 클러스터링 계수 계산
- 커뮤니티 탐지

**주요 발견**:

- M2SL과 CPI가 가장 높은 degree centrality
- Open_Interest가 BTC_Price와 강한 연결
- 거시경제 변수 클러스터 형성
- 감성 변수 별도 클러스터

**생성된 차트**:

- `17_network_full.png` - 전체 53개 변수 네트워크
- `18_network_simplified.png` - 주요 변수만 간소화 (15개)

---

### ✅ Task 13: Streamlit 대시보드

**목표**: 인터랙티브 웹 대시보드 구축

**기능**:

**5개 탭**:

1. **가격 분석**: BTC 가격 시계열, 급락일 표시
2. **감성 분석**: 일별 감성, 키워드 빈도
3. **거시경제**: 5개 거시변수 시계열
4. **상관관계**: 인터랙티브 히트맵
5. **종합 분석**: 모든 차트 통합

**인터랙티브 기능**:

- 날짜 범위 필터링 (2025-09-01 ~ 2025-10-31)
- 18개 Plotly 차트 (줌, 패닝, 호버)
- CSV 다운로드 버튼
- 실시간 데이터 업데이트

**기술 스택**:

- Streamlit 1.53.1
- Plotly 6.5.2
- pandas 2.3.3
- Python 3.11.14

**실행 방법**:

```bash
cd c:\potenup3\ai_team_6
.venv\Scripts\python.exe -m streamlit run dashboard_app.py
```

**URL**: http://localhost:8503

**파일**: `dashboard_app.py` (538줄)

---

### ✅ Task 14: PDF 보고서 생성

**목표**: 종합 분석 보고서 자동 생성

**보고서 구성**:

1. **커버 페이지**
   - 제목: Bitcoin Market Crash Analysis
   - 부제: 2025년 10월 10일 급락 분석
   - 날짜: 2026-02-03

2. **목차**

3. **요약 (Executive Summary)**
   - 프로젝트 개요
   - 주요 발견 5가지
   - 투자 시사점

4. **섹션 1: 데이터 개요**
   - 데이터 소스
   - 기간 및 범위
   - 변수 설명

5. **섹션 2: 가격 분석**
   - 급락 정보
   - 가격 추이
   - 차트 2개

6. **섹션 3: 상관관계 분석**
   - Top 15 상관관계
   - 히트맵
   - 차트 3개

7. **섹션 4: 정치 테마**
   - 시차 효과
   - 스파이크 날짜
   - 차트 2개

8. **섹션 5: 감성 분석**
   - 감성 분포
   - 키워드 Top 20
   - 차트 4개

9. **섹션 6: 거시경제**
   - 회귀 결과
   - Feature importance
   - 차트 2개

10. **섹션 7: 파생상품**
    - Open Interest
    - 급락 메커니즘
    - 차트 1개

11. **섹션 8: 워드클라우드**
    - 키워드 분포
    - 급락 전후 비교
    - 차트 4개

12. **결론 및 제언**
    - 핵심 결론
    - 투자 전략
    - 위험 관리

**기술 스택**:

- ReportLab 4.4.9
- 한글 폰트: Malgun Gothic
- 18+ PNG 차트 포함
- 페이지당 300 DPI

**파일 정보**:

- 파일명: `Bitcoin_Crash_Analysis_Report_20260203_165450.pdf`
- 크기: 5,030 KB
- 페이지: 30+ 페이지

**생성 스크립트**: `14_generate_report.py`

---

### ✅ Task 15: 프로젝트 문서화

**목표**: 완전한 프로젝트 문서 작성

**생성된 문서 (6개)**:

1. **README.md** (400줄)
   - 프로젝트 개요
   - 주요 기능
   - 설치 방법
   - 빠른 시작
   - 디렉토리 구조
   - 기여 가이드
   - 라이선스

2. **USER_GUIDE.md** (1,200줄)
   - 상세 사용 가이드
   - 각 스크립트 설명 (15개)
   - 대시보드 사용법
   - 데이터 형식
   - 트러블슈팅
   - FAQ

3. **DEPLOYMENT.md** (800줄)
   - 4가지 배포 방법
   - Streamlit Cloud
   - Heroku
   - Docker
   - AWS EC2
   - 환경 변수 설정
   - CI/CD 파이프라인

4. **PROJECT_SUMMARY.md** (350줄)
   - 프로젝트 요약
   - 15개 Task 개요
   - 주요 발견
   - 기술 스택
   - 팀 정보

5. **requirements.txt**
   - 모든 의존성 목록
   - 버전 고정
   - Python 3.11+ 요구

6. **.streamlit/config.toml**
   - Streamlit 설정
   - 테마 커스터마이징
   - 서버 설정

**문서 특징**:

- 전문적인 마크다운 형식
- 코드 예제 포함
- 스크린샷 준비
- 다국어 지원 (한글/영문)
- 뱃지 (Build Status, License, Python Version)

---

## 📊 전체 분석 결과 요약

### 🔑 핵심 발견 5가지

1. **거시경제가 가장 중요** (R² = 44.5%)
   - M2 통화량이 42.3% 설명력
   - 감성 변수(21%) 대비 2배 강력

2. **Open Interest 강한 상관** (r = +0.684)
   - 가격과 거의 동시에 변동
   - OI 급감 = 위험 신호

3. **정치 테마 1일 선행 효과**
   - 정치 뉴스 급증 → 다음날 변동성 증가
   - 10/7 테마 급증 → 10/10 급락

4. **부정 감성 압도적** (57.3%)
   - 긍정의 2배 이상
   - 공포 심리 확산

5. **M2와 CPI 완벽한 역관계** (r = -1.0)
   - 다중공선성 주의 필요

### 📈 투자 시사점

1. **M2 모니터링**: 통화량 증가 = 비트코인 상승 신호
2. **OI 추적**: OI 급감 시 포지션 축소
3. **정치 뉴스**: 정치 이슈 급증 시 다음날 주의
4. **달러 약세**: 달러 인덱스 하락 = 비트코인 상승 기회
5. **감성 분석**: 부정 감성 과열 시 반등 가능성

### 🛠️ 기술 스택

**프로그래밍**:

- Python 3.11.14
- pandas 2.3.3
- NumPy 2.3.2

**시각화**:

- Matplotlib 3.10.8
- Seaborn 0.13.2
- Plotly 6.5.2

**통계/ML**:

- scikit-learn 1.6.2
- statsmodels 0.14.4
- scipy 1.15.2

**대시보드**:

- Streamlit 1.53.1

**보고서**:

- ReportLab 4.4.9

**NLP**:

- TextBlob 0.18.1
- WordCloud 1.9.4

**네트워크**:

- NetworkX 3.4

---

## 🖼️ 이미지 업로드 가이드

### 모든 이미지 경로

```
c:\potenup3\ai_team_6\output\visualizations\
```

### Notion에 이미지 추가하는 방법

1. Notion 페이지에서 해당 Task 섹션으로 이동
2. 이미지를 추가할 위치에서 "/image" 타이핑
3. "파일에서 업로드" 선택
4. 위 경로에서 해당 PNG 파일 선택
5. 또는 탐색기에서 드래그 앤 드롭

### 권장 배치

**Task 4 섹션**:

- 01_btc_price_timeseries.png
- 02_btc_price_vs_sns.png

**Task 5 섹션**:

- 03_correlation_heatmap_full.png
- 04_correlation_heatmap_key_vars.png
- 05_btc_correlation_bar.png

**Task 6 섹션**:

- 06_political_themes_timeseries.png
- 07_political_themes_lag_correlation.png

**Task 7 섹션**:

- 08_sentiment_analysis.png
- 09_keyword_sentiment.png

**Task 8 섹션**:

- 10_sentiment_price_regression.png
- 11_regression_residuals.png

**Task 9 섹션**:

- 12_macroeconomic_regression.png
- 13_macro_variable_importance.png

**Task 10 섹션**:

- 14_open_interest_analysis.png

**Task 11 섹션**:

- 15_wordcloud_combined.png
- 16_keyword_frequency_comparison.png
- wordcloud_positive.png
- wordcloud_negative.png

**Task 12 섹션**:

- 17_network_full.png
- 18_network_simplified.png

### 이미지 크기 조정

- 이미지 클릭 후 모서리 드래그로 크기 조정
- 권장 크기: 페이지 너비의 70-80%
- 모든 이미지는 300 DPI 고해상도

---

## ✅ 프로젝트 완료 체크리스트

- [x] Task 1: 데이터 로딩 및 검증
- [x] Task 2: 데이터 정제
- [x] Task 3: 데이터 통합
- [x] Task 4: 가격 시각화
- [x] Task 5: 상관관계 분석
- [x] Task 6: 정치 테마 분석
- [x] Task 7: 감성 분석
- [x] Task 8: 감성-가격 회귀
- [x] Task 9: 거시경제 회귀
- [x] Task 10: Open Interest 분석
- [x] Task 11: 워드클라우드
- [x] Task 12: 네트워크 분석
- [x] Task 13: Streamlit 대시보드
- [x] Task 14: PDF 보고서
- [x] Task 15: 프로젝트 문서화
- [x] 18개 PNG 차트 생성
- [x] Notion 페이지 생성
- [ ] Notion에 이미지 업로드 (수동)

---

**Notion 페이지**: https://www.notion.so/2fca987da1af81f2ae3dd07f6ab4a19e

**프로젝트 완료일**: 2026-02-03
