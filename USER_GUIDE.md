# 📖 사용자 가이드 (User Guide)

**Bitcoin Market Crash Analysis - 완벽 가이드**

## 목차

1. [시작하기](#1-시작하기)
2. [데이터 분석 실행](#2-데이터-분석-실행)
3. [대시보드 사용법](#3-대시보드-사용법)
4. [PDF 리포트 생성](#4-pdf-리포트-생성)
5. [문제 해결](#5-문제-해결)
6. [고급 사용법](#6-고급-사용법)

---

## 1. 시작하기

### 1.1 환경 설정 체크리스트

시작하기 전에 다음 항목을 확인하세요:

- [ ] Python 3.11 이상 설치
- [ ] Git 설치
- [ ] 최소 10GB 여유 디스크 공간
- [ ] 안정적인 인터넷 연결 (대시보드 실행 시)

### 1.2 설치 과정

#### Step 1: 저장소 클론

```bash
git clone https://github.com/your-username/ai_team_6.git
cd ai_team_6
```

#### Step 2: 가상환경 생성

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate

# Windows CMD
python -m venv .venv
.venv\Scripts\activate.bat

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

가상환경 활성화 확인:

- 터미널 프롬프트 앞에 `(.venv)` 표시가 나타나야 합니다

#### Step 3: 의존성 설치

```bash
# UV 사용 (빠름, 권장)
pip install uv
uv pip install pandas numpy matplotlib seaborn scipy scikit-learn streamlit plotly reportlab wordcloud networkx

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

설치 확인:

```bash
python -c "import pandas, streamlit, reportlab; print('설치 성공!')"
```

### 1.3 데이터 준비

프로젝트에 필요한 데이터는 이미 `data/` 디렉토리에 포함되어 있습니다:

- `data/news/`: 일별 뉴스 데이터 (bitcoin_news_YYYYMMDD.csv)
- `data/Community_data/`: 커뮤니티 데이터
- `data/files/`: 기타 원본 파일

데이터 검증:

```bash
python 01_data_loading_validation.py
```

---

## 2. 데이터 분석 실행

### 2.1 전체 파이프라인 실행

분석은 15개의 태스크로 구성되어 있으며, 순차적으로 실행해야 합니다.

#### 🔹 Phase 1: 데이터 준비 (Tasks 1-3)

**Task 1: 데이터 로딩 및 검증**

```bash
python 01_data_loading_validation.py
```

- 6개 CSV 파일 검증
- 총 28,340 레코드 확인
- 결측치 보고서 생성

**Task 2: 데이터 정제**

```bash
python 02_data_cleaning_standardization.py
```

- 날짜 형식 표준화 (datetime64)
- 결측치 전방향 보간
- 0개 결측치 달성

**Task 3: 데이터 통합**

```bash
python 03_data_integration.py
```

- 날짜 기준 병합
- 61×53 마스터 데이터프레임 생성
- `data/processed/integrated/master_data_integrated.csv` 저장

#### 🔹 Phase 2: 가격 및 상관관계 (Tasks 4-5)

**Task 4: 가격 시각화**

```bash
python 04_price_visualization.py
```

출력:

- `01_price_trend.png`: 가격 추이 + 급락일 표시
- `02_price_trend_with_speed.png`: 가격 변화 속도

**Task 5: 상관관계 히트맵**

```bash
python 05_correlation_heatmap.py
```

출력:

- `03_correlation_heatmap_full.png`: 전체 변수
- `04_correlation_heatmap_high.png`: |r| ≥ 0.5
- `05_correlation_heatmap_macro.png`: 거시경제 변수
- `high_correlations.csv`: 상위 15개 상관관계

#### 🔹 Phase 3: 테마 및 감성 분석 (Tasks 6-8)

**Task 6: 정치 테마 분석**

```bash
python 06_political_themes_analysis.py
```

- 7개 정치 테마 시계열
- 시차 상관관계 분석 (lag -5 to +5)
- 스파이크 날짜 식별

**Task 7: 감성 분석**

```bash
python 07_sentiment_analysis.py
```

- 10,000 레코드 감성 추출
- 긍정/부정/중립 분류
- `sentiment_daily_analysis.csv` 생성

**Task 8: 감성-가격 회귀**

```bash
python 08_sentiment_price_regression.py
```

- 다중 선형 회귀 (R² = 0.1974)
- tone_neg_share 유의성 확인 (p = 0.040)

#### 🔹 Phase 4: 거시경제 및 파생상품 (Tasks 9-10)

**Task 9: 거시경제 회귀**

```bash
python 09_macroeconomic_regression.py
```

- M2SL, Yield_10Y, USD_Index 모델
- R² = 0.4448 (44.5% 설명력)
- F-test p < 0.000001

**Task 10: Open Interest 분석**

```bash
python 10_open_interest_analysis.py
```

- OI vs 가격 상관관계 (r = +0.684)
- 급락 전후 OI 변화 (-31%)

#### 🔹 Phase 5: 고급 시각화 (Tasks 11-12)

**Task 11: 워드클라우드**

```bash
python 11_wordcloud_generation.py
```

- 전체/긍정/부정/중립 4개 워드클라우드
- 24,584 부정 키워드 식별

**Task 12: 네트워크 분석**

```bash
python 12_network_analysis.py
```

- 16개 노드, 48개 엣지 네트워크
- 중심성 분석 (degree, betweenness, closeness)

### 2.2 출력 파일 확인

모든 분석이 완료되면 다음 파일들이 생성됩니다:

```
output/visualizations/
├── 01_price_trend.png
├── 02_price_trend_with_speed.png
├── 03_correlation_heatmap_full.png
├── 04_correlation_heatmap_high.png
├── 05_correlation_heatmap_macro.png
├── 06_political_themes_timeseries.png
├── 07_political_price_correlation.png
├── 08_sentiment_regression_scatter.png
├── 09_sentiment_regression_residuals.png
├── 10_macro_regression_scatter.png
├── 11_macro_regression_residuals.png
├── 12_open_interest_price.png
├── 13_open_interest_crash_analysis.png
├── 14_wordcloud_overall.png
├── 15_wordcloud_positive.png
├── 16_wordcloud_negative.png
├── 17_network_full.png
└── 18_network_simplified.png
```

---

## 3. 대시보드 사용법

### 3.1 대시보드 실행

```bash
streamlit run dashboard_app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에 접속됩니다.

### 3.2 대시보드 구성

#### 🎛️ 사이드바 (왼쪽)

**날짜 범위 선택**

- 시작일/종료일 선택
- 기본값: 전체 기간 (2025-09-01 ~ 2025-10-31)
- 변경 시 모든 차트 자동 업데이트

**주요 지표 카드**

- 평균 가격
- 최고가/최저가
- 변동폭

#### 📊 메인 영역

**탭 1: 📈 가격 분석**

1. **가격 추이 차트**
   - 인터랙티브 라인 차트
   - 급락일 (10/10) 빨간 선 표시
   - 마우스 오버로 정확한 값 확인

2. **가격 통계 카드**
   - 평균 가격
   - 표준편차
   - 변동계수
   - 최대 상승/하락률

3. **Open Interest vs 가격**
   - 이중 Y축 차트
   - OI (왼쪽 축), 가격 (오른쪽 축)
   - 상관관계 시각화

**탭 2: 💬 감성 분석**

1. **뉴스 감성 추이**
   - tone_mean 시계열
   - 0선 기준 (양수 = 긍정, 음수 = 부정)

2. **커뮤니티 감성 추이**
   - Reddit/YouTube 감성 평균

3. **감성 지표 비교**
   - 평균 뉴스 감성
   - 긍정/부정 비율

**탭 3: 🌍 거시경제**

1. **지표 선택 드롭다운**
   - M2SL (M2 통화량)
   - Yield_10Y (10년물 금리)
   - USD_Index (달러 인덱스)

2. **선택 지표 vs 가격**
   - 이중 Y축 비교 차트
   - 상관계수 표시

3. **통계 정보**
   - 평균, 표준편차, 최소/최대
   - BTC 가격과 상관계수

4. **전체 지표 정규화 차트**
   - 모든 지표를 0-1 범위로 정규화
   - 추세 비교 용이

**탭 4: 📊 상관관계**

1. **인터랙티브 히트맵**
   - Plotly 기반
   - 마우스 오버로 정확한 값
   - 색상: 파랑(음의 상관) ~ 빨강(양의 상관)

2. **강한 상관관계 Top 10**
   - 테이블 형식
   - 변수 쌍 및 상관계수
   - 절대값 기준 정렬

**탭 5: 🔍 종합 분석**

1. **주요 발견사항**
   - 5개 섹션 요약
   - 투자 시사점

2. **필터링된 데이터 테이블**
   - 선택한 날짜 범위의 데이터
   - 스크롤 가능
   - 컬럼: 날짜, 가격, 감성, 거시경제 등

3. **CSV 다운로드 버튼**
   - 현재 필터링된 데이터 내보내기
   - 파일명: `bitcoin_analysis_STARTDATE_ENDDATE.csv`

### 3.3 대시보드 인터랙션 팁

- **줌**: 차트를 드래그하여 특정 영역 확대
- **리셋**: 차트 위 홈 아이콘 클릭
- **팬**: 확대 후 이동 아이콘으로 차트 이동
- **범례**: 클릭하여 특정 데이터 시리즈 숨기기/표시
- **다운로드**: 카메라 아이콘으로 차트 PNG 저장

---

## 4. PDF 리포트 생성

### 4.1 리포트 생성

```bash
python 14_generate_report.py
```

### 4.2 실행 과정

```
============================================================
PDF 분석 리포트 생성 시작
============================================================

[1/4] 데이터 로딩...
  ✓ 데이터 로드 완료: 61 rows

[2/4] PDF 문서 생성...

[3/4] 리포트 컨텐츠 생성...
  • 표지 페이지
  • 요약 페이지
  • 분석 섹션들
  • 결론 페이지

[4/4] PDF 파일 생성 중...

============================================================
✓ PDF 리포트 생성 완료!
  파일 위치: output/reports/Bitcoin_Crash_Analysis_Report_20260203_165450.pdf
  파일 크기: 5030.21 KB
============================================================
```

### 4.3 리포트 구성

**표지 (Cover Page)**

- 프로젝트 제목
- 분석 기간
- 급락 발생일
- 생성 날짜

**요약 (Executive Summary)**

- 5가지 핵심 발견사항
- 수치 기반 요약

**8개 분석 섹션**

1. 가격 추이 분석
2. 상관관계 분석
3. 정치 테마 영향 분석
4. 감성-가격 회귀 분석
5. 거시경제 지표 분석
6. Open Interest 분석
7. 감성 워드클라우드
8. 네트워크 관계 분석

**결론 (Conclusion)**

- 주요 발견사항 정리
- 투자 시사점

### 4.4 리포트 활용

**인쇄 설정**

- 용지: A4
- 방향: 세로
- 컬러: 권장

**공유 방법**

- 이메일 첨부 (5+ MB)
- 클라우드 스토리지 링크
- PDF 뷰어에서 주석 추가 가능

---

## 5. 문제 해결

### 5.1 일반적인 오류

#### 오류: `ModuleNotFoundError: No module named 'pandas'`

**해결책**:

```bash
pip install pandas
# 또는 전체 재설치
pip install -r requirements.txt
```

#### 오류: `FileNotFoundError: data/processed/integrated/master_data_integrated.csv`

**해결책**:

```bash
# Task 1-3을 순서대로 실행
python 01_data_loading_validation.py
python 02_data_cleaning_standardization.py
python 03_data_integration.py
```

#### 오류: `TypeError: unsupported operand type(s) for +: 'int' and 'Timestamp'`

**원인**: pandas 버전 충돌
**해결책**:

```bash
pip install pandas==2.3.3
```

#### 대시보드가 열리지 않음

**해결책**:

```bash
# 포트 확인
netstat -ano | findstr :8501

# 다른 포트 사용
streamlit run dashboard_app.py --server.port 8502
```

### 5.2 한글 폰트 문제

#### PDF에서 한글이 깨짐

**Windows**:

- `malgun.ttf` 파일이 `C:/Windows/Fonts/`에 있는지 확인
- 없으면 영문 폰트로 자동 대체됨

**macOS**:

```python
# 14_generate_report.py 수정
font_path = "/System/Library/Fonts/AppleGothic.ttf"
```

**Linux**:

```bash
sudo apt-get install fonts-nanum
```

### 5.3 성능 최적화

#### 대시보드가 느림

**해결책**:

- 날짜 범위를 좁게 설정
- 브라우저 캐시 삭제
- Streamlit 캐싱 활용 (자동)

#### 메모리 부족

**해결책**:

```python
# 스크립트에서 청크 처리
df = pd.read_csv(file, chunksize=10000)
```

---

## 6. 고급 사용법

### 6.1 커스텀 날짜 범위 분석

특정 기간만 분석하려면:

```python
# 03_data_integration.py 수정
start_date = '2025-10-05'
end_date = '2025-10-15'
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
```

### 6.2 새로운 변수 추가

1. **데이터 추가**:
   - `data/news/` 또는 `data/files/`에 CSV 배치

2. **스크립트 수정**:

```python
# 01_data_loading_validation.py
new_file = "data/files/new_variable.csv"
new_df = pd.read_csv(new_file)
```

3. **통합**:

```python
# 03_data_integration.py
master_df = master_df.merge(new_df, on='date', how='left')
```

### 6.3 배포 옵션

#### Streamlit Cloud (무료)

1. GitHub에 프로젝트 푸시
2. [streamlit.io/cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭
4. 저장소 선택: `your-username/ai_team_6`
5. Main file: `dashboard_app.py`
6. Deploy 클릭

#### Heroku

```bash
# Procfile 생성
echo "web: streamlit run dashboard_app.py --server.port $PORT" > Procfile

# runtime.txt
echo "python-3.11.14" > runtime.txt

# 배포
heroku create bitcoin-crash-analysis
git push heroku main
```

#### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard_app.py"]
```

```bash
# 빌드 및 실행
docker build -t bitcoin-analysis .
docker run -p 8501:8501 bitcoin-analysis
```

### 6.4 자동화 스크립트

모든 분석을 한 번에 실행:

```bash
# run_all.sh (macOS/Linux)
#!/bin/bash
for i in {1..12}; do
    python $(printf "%02d" $i)_*.py
done
python 14_generate_report.py
```

```powershell
# run_all.ps1 (Windows)
1..12 | ForEach-Object {
    $file = Get-ChildItem -Filter "$("{0:D2}" -f $_)_*.py"
    python $file.Name
}
python 14_generate_report.py
```

### 6.5 Task Master 사용

프로젝트는 Task Master AI로 관리됩니다:

```bash
# 태스크 상태 확인
cat .taskmaster/tasks/tasks.json

# 특정 태스크 정보
# Task 1-15의 상세 정보 확인
```

---

## 📞 추가 지원

### 문서

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Pandas 공식 문서](https://pandas.pydata.org/docs/)
- [Matplotlib 가이드](https://matplotlib.org/stable/tutorials/index.html)

### 문의

- GitHub Issues: 버그 리포트 및 기능 요청
- Email: 프로젝트 관련 문의

---

**마지막 업데이트**: 2026-02-03  
**문서 버전**: 1.0.0
