# October 2025 Crypto Crash - 커뮤니티 데이터 시각화

## 📊 데이터셋 개요
- **총 레코드**: 145개 실제 커뮤니티 포스트/트윗
- **플랫폼**: X (Twitter) 83개, Reddit 62개
- **데이터 소스**: 100% 실제 URL (합성 0%)
- **수집 기간**: 2025년 9월 ~ 11월
- **주제**: October 2025 $19B 청산 이벤트

## 📁 파일 구조
```
outputs/
├── FINAL_COMMUNITY_DATASET_145.csv         # 메인 데이터셋
├── FINAL_COMMUNITY_DATASET_145.json        # JSON 형식
├── dataset_statistics.json                 # 통계 요약
├── comprehensive_visualization.py          # 시각화 스크립트
└── README_VISUALIZATION.md                 # 이 문서
```

## 🚀 VSCode에서 실행하기

### 1. 환경 준비
프로젝트 루트에서:
```bash
# UV 환경 활성화 (이미 설치된 경우)
uv sync

# 또는 필요한 패키지가 없다면
uv pip install pandas numpy matplotlib seaborn wordcloud networkx scikit-learn textblob vadersentiment koreanize-matplotlib
```

### 2. 데이터 파일 위치 확인
시각화 스크립트는 다음 파일이 **같은 디렉토리**에 있어야 합니다:
- `FINAL_COMMUNITY_DATASET_145.csv`
- `comprehensive_visualization.py`

**방법 1: 파일 이동**
```bash
# outputs 폴더로 이동
cd path/to/outputs

# 스크립트 실행
python comprehensive_visualization.py
```

**방법 2: 경로 수정**
스크립트 내 15번 줄을 수정:
```python
# 변경 전
df = pd.read_csv('FINAL_COMMUNITY_DATASET_145.csv')

# 변경 후 (절대 경로 또는 상대 경로)
df = pd.read_csv('outputs/FINAL_COMMUNITY_DATASET_145.csv')
```

### 3. 실행
```bash
# Python으로 직접 실행
python comprehensive_visualization.py

# 또는 UV로 실행
uv run python comprehensive_visualization.py
```

### 4. 결과 확인
같은 디렉토리에 10개의 PNG 파일이 생성됩니다:
1. `01_platform_distribution.png` - 플랫폼 분포
2. `02_category_distribution.png` - 카테고리 분포
3. `03_sentiment_analysis.png` - 감정 분석
4. `04_time_period_distribution.png` - 시간대 분포
5. `05_influence_score_analysis.png` - 영향력 분석
6. `06_wordclouds.png` - 워드클라우드
7. `07_keyword_heatmap.png` - 키워드 히트맵
8. `08_keyword_cooccurrence.png` - 키워드 공동 출현
9. `09_network_graph.png` - 네트워크 그래프
10. `10_comprehensive_dashboard.png` - 종합 대시보드

## 📈 생성되는 시각화

### 1. **플랫폼 분포** (파이 차트 + 바 차트)
- X vs Reddit 비율
- 각 플랫폼별 포스트 수

### 2. **카테고리 분포** (수평 바 차트)
- 10개 카테고리별 포스트 수
- 백분율 표시

### 3. **감정 분석** (도넛 차트 + 스택 바)
- 5가지 감정 (Very_Negative, Negative, Neutral, Mixed, Positive)
- 플랫폼별 감정 비교

### 4. **시간대 분석** (수평 바 차트)
- October 10, October 11, October 2025 등
- 크래시 전후 분포

### 5. **영향력 점수 분석** (4개 서브플롯)
- 전체 분포 히스토그램
- 플랫폼별 박스플롯
- 카테고리별 평균 영향력
- 감정별 평균 영향력

### 6. **워드클라우드** (4개)
- 전체 포스트
- X (Twitter) 전용
- Reddit 전용
- 부정 감정 포스트

### 7. **키워드 히트맵** (2개)
- 플랫폼별 키워드 빈도
- 카테고리별 키워드 빈도 (상위 8개)

### 8. **키워드 공동 출현 히트맵**
- 15개 키워드 간 동시 출현 매트릭스
- 어떤 키워드가 함께 나타나는지 분석

### 9. **네트워크 그래프**
- 상위 15명 작성자와 카테고리 관계
- 파란색 노드: 작성자
- 주황색 노드: 카테고리
- 엣지 두께: 포스트 수

### 10. **종합 대시보드**
- 7개 서브플롯에 모든 핵심 정보
- 한 눈에 보는 데이터 요약
- 통계 정보 박스

## 🎨 커스터마이징

### 색상 변경
```python
# 플랫폼 색상 (45-46번 줄)
colors = ['#1DA1F2', '#FF4500']  # Twitter blue, Reddit orange

# 감정 색상 (84-86번 줄)
colors_sent = {'Very_Negative': '#d62728', 'Negative': '#ff7f0e', 
               'Neutral': '#7f7f7f', 'Mixed': '#bcbd22', 'Positive': '#2ca02c'}
```

### 해상도 변경
```python
# 각 plt.savefig() 호출에서 dpi 조정
plt.savefig('filename.png', dpi=300, bbox_inches='tight')  # 현재: 300 DPI

# 더 높은 해상도: dpi=600
# 빠른 미리보기: dpi=150
```

### 워드클라우드 단어 수 조정
```python
# 175번 줄 근처
wc_all = WordCloud(width=800, height=400, background_color='white', 
                   stopwords=stopwords, colormap='viridis', 
                   max_words=100,  # 여기를 변경 (현재 100개)
                   relative_scaling=0.5).generate(all_text)
```

### 불용어 추가
```python
# 168-173번 줄
stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'can', 'this', 'that', 'these', 'those', 'it', 'its', 'as'])

# 여기에 추가:
stopwords.add('your_word')
```

## 🔧 문제 해결

### 한글 폰트 오류
```bash
# koreanize-matplotlib 설치
uv pip install koreanize-matplotlib

# 또는 수동으로 폰트 지정
plt.rcParams['font.family'] = 'NanumGothic'  # 또는 다른 한글 폰트
```

### 메모리 부족
큰 데이터셋에서 메모리 문제가 발생하면:
```python
# 각 시각화 후 메모리 해제
plt.close('all')
import gc
gc.collect()
```

### 파일 경로 오류
Windows에서:
```python
df = pd.read_csv(r'C:\path\to\FINAL_COMMUNITY_DATASET_145.csv')
```

Mac/Linux에서:
```python
df = pd.read_csv('/path/to/FINAL_COMMUNITY_DATASET_145.csv')
```

## 📊 데이터 컬럼 설명

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `platform` | str | 플랫폼 (X 또는 Reddit) |
| `url` | str | 원본 URL |
| `author` | str | 작성자 (@username 또는 r/subreddit) |
| `title` | str | 포스트/트윗 제목 |
| `category` | str | 카테고리 (10개) |
| `sentiment` | str | 감정 (5개) |
| `influence_score` | float | 영향력 점수 (0-60) |
| `time_period` | str | 시간대 분류 |
| `kw_*` | bool | 키워드 플래그 (15개) |
| `source_detail` | str | 상세 소스 정보 |

## 💡 추가 분석 아이디어

### Jupyter Notebook에서 인터랙티브 분석
```python
import pandas as pd
import plotly.express as px

df = pd.read_csv('FINAL_COMMUNITY_DATASET_145.csv')

# 인터랙티브 산점도
fig = px.scatter(df, x='influence_score', y='category', 
                color='sentiment', hover_data=['title', 'author'],
                title='Influence Score by Category')
fig.show()
```

### 시계열 분석 (날짜 추가 시)
```python
# 만약 날짜 컬럼이 있다면
df['date'] = pd.to_datetime(df['date'])
daily_counts = df.groupby('date').size()
daily_counts.plot(kind='line', figsize=(12, 6))
```

### Topic Modeling (LDA)
```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(max_features=100, stop_words='english')
X = vectorizer.fit_transform(df['title'])

lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(X)

# 토픽별 주요 단어
for idx, topic in enumerate(lda.components_):
    print(f"Topic {idx}:", [vectorizer.get_feature_names_out()[i] 
                           for i in topic.argsort()[-10:]])
```

## 📝 참고사항
- 모든 시각화는 300 DPI 고해상도로 저장
- 색상은 colorblind-friendly 팔레트 사용
- 그리드와 레이블로 가독성 최적화
- 각 차트에 명확한 제목과 범례 포함

## 🤝 기여
개선 사항이나 버그 리포트는 이슈로 제출해주세요!

## 📄 라이선스
이 프로젝트의 데이터는 공개 소스(X, Reddit)에서 수집되었으며, 교육 및 연구 목적으로만 사용됩니다.
