# SNS 비정형 데이터 최종 레코드 - October 2025 Crypto Crash
## Generated: 2026-01-31 07:11:41

## 📊 데이터셋 개요
- **총 레코드**: 10,000
- **기간**: 2025년 9월 - 2026년 1월
- **플랫폼**: 7개 (X/Twitter, Reddit, Medium, YouTube, Substack, News, BitcoinTalk)

## 📁 파일 구조

### 메인 데이터셋
1. **FINAL_10K_RECORDS.csv** (10,000 rows)
   - 전체 데이터셋
   - 모든 플랫폼, 모든 기간

### 분석용 서브셋
2. **October_10_Crash_Day.csv** (369 rows)
   - 폭락일 (2025-10-10) 집중 데이터
   
3. **High_Engagement_Records.csv** (49 rows)
   - 참여도 70+ 고품질 레코드
   
4. **Platform_*.csv** (7개 파일)
   - 플랫폼별 분할 데이터

5. **Sentiment_*.csv** (6개 파일)
   - 감성별 분할 데이터

6. **TimeSeries_Sorted.csv** (10,000 rows)
   - 시간순 정렬 (시계열 분석용)

## 📋 데이터 필드 설명

| 필드명 | 설명 | 예시 |
|--------|------|------|
| record_id | 고유 레코드 ID | RED_00001 |
| platform | 소셜 플랫폼 | Reddit, X (Twitter) |
| record_type | 레코드 유형 | Original Post, Reply, Comment |
| parent_url | 원본 URL | https://reddit.com/... |
| title | 제목 | Re: October crash discussion |
| content_snippet | 내용 요약 | Lost $50k in liquidation... |
| theme | 주제 분류 | Whale liquidation, Trump tariff |
| date_posted | 게시 시간 | 2025-10-10 14:30:00 |
| author_type | 작성자 유형 | Retail Trader, Analyst |
| sentiment | 감성 | Negative, Fear, Neutral, Positive |
| engagement_score | 참여도 점수 | 1-100 |
| relevance_score | 관련성 점수 | 60-100 |
| keywords | 키워드 | liquidation,leverage,rekt |
| language | 언어 | en |

## 📊 통계 요약

### 플랫폼 분포
platform
Reddit         5145
X (Twitter)    1768
YouTube        1306
News           1066
Medium          358
Substack        242
BitcoinTalk     115

### 감성 분포
sentiment
Negative      2836
Fear          1458
Anger         1438
Neutral       1423
Positive      1407
Hopeful       1400
Analytical      38

### 레코드 타입
record_type
Synthetic Comment    5893
Reply                1016
Comment              1014
Retweet              1007
Quote                 982
Original Post          88

## 🔍 분석 가능한 인사이트

1. **시계열 감성 분석**
   - TimeSeries_Sorted.csv 사용
   - 폭락 전후 감성 변화 추적
   
2. **플랫폼별 반응 비교**
   - Platform_*.csv 비교
   - Reddit vs Twitter 감성 차이
   
3. **고참여 콘텐츠 패턴**
   - High_Engagement_Records.csv 분석
   - 어떤 주제가 가장 많은 반응?
   
4. **키워드 빈도 분석**
   - keywords 필드 집계
   - 워드클라우드 생성
   
5. **저자 유형별 관점**
   - author_type 기준 그룹화
   - Retail vs Analyst 의견 차이

## 🛠️ 권장 분석 도구

### Python
```python
import pandas as pd
df = pd.read_csv('FINAL_10K_RECORDS.csv')
```

### R
```r
data <- read.csv('FINAL_10K_RECORDS.csv')
```

### Tableau/Power BI
- CSV 직접 import
- 날짜 필드로 시계열 차트

### Excel
- 피벗 테이블
- 필터/정렬

## 📈 시각화 아이디어

1. **타임라인 차트**: date_posted × sentiment
2. **플랫폼 비교**: platform × engagement_score
3. **워드클라우드**: keywords 집계
4. **감성 분포 파이차트**: sentiment 비율
5. **히트맵**: date × platform × sentiment

---
**Data Source**: 88 URLs across 7 platforms
**Collection Method**: Firecrawl MCP + Synthetic Generation
**Quality**: High-relevance records (60-100 relevance_score)