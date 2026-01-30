# SNS/커뮤니티 비정형 데이터 수집 전략
## October 2025 Crypto Crash - Social Media Analysis

---

## 🎯 수집 목표
- **기간**: 2025년 9월 1일 ~ 10월 31일 (2개월)
- **플랫폼**: X(Twitter), Reddit
- **목적**: "검은 10월" 폭락 사태 전후 소셜 감성/반응 분석

---

## 📱 데이터 소스 전략

### 1. X (Twitter) 
**수집 방법:**
- ✅ Firecrawl Search (가능한 범위)
- ✅ X RSS 피드 (nitter.net 대안 활용)
- ✅ 주요 인플루언서 타임라인 스크래핑

**타겟 계정 (Crypto Twitter Influencers):**
- @APompliano (Anthony Pompliano)
- @CryptoKaleo
- @intocryptoverse
- @RookieXBT
- @lookonchain (Whale tracking)
- @coinglass_com (Data analytics)
- @Crypto_Bitlord
- @AltcoinGordon
- @TheCryptoLark
- @IvanOnTech

**키워드:**
- "crypto crash"
- "bitcoin liquidation"
- "October crash"
- "$BTC liquidation"
- "crypto bloodbath"
- "black October crypto"
- "Trump tariff crypto"
- "Hyperliquid liquidation"
- "Binance crash"
- "whale manipulation"

### 2. Reddit
**수집 방법:**
- ✅ Reddit RSS 피드
- ✅ Firecrawl 스크래핑
- ✅ Subreddit 아카이브

**타겟 Subreddits:**
- r/CryptoCurrency (5M+ members)
- r/Bitcoin (6M+ members)
- r/ethereum (2M+ members)
- r/CryptoMarkets (1M+ members)
- r/BitcoinMarkets
- r/solana
- r/altcoin
- r/binance
- r/wallstreetbets (crypto discussion)
- r/defi

**검색 쿼리:**
- "October crash"
- "liquidation"
- "lost everything"
- "Trump tariff"
- "market manipulation"
- "whale activity"
- "exchange issues"

---

## 🔧 수집 도구

### 도구 1: Firecrawl
- X 검색 결과 스크래핑
- Reddit 스레드 스크래핑

### 도구 2: RSS 피드
- Reddit RSS: `https://www.reddit.com/r/[SUBREDDIT]/search.rss?q=[QUERY]&restrict_sr=on&sort=relevance&t=all`
- X 대안 RSS (가능한 경우)

### 도구 3: 직접 HTML 파싱
- 필요시 Beautiful Soup / Selenium

---

## 📊 데이터 구조

**수집할 필드:**
- `post_id` - 고유 ID
- `platform` - Twitter / Reddit
- `author` - 작성자
- `timestamp` - 게시 시간
- `content` - 본문
- `engagement` - likes/retweets/comments
- `sentiment` - (추후 분석용)
- `keywords` - 매칭된 키워드
- `url` - 원본 링크

---

## ⏱️ 타임라인

**Phase 1: Reddit 수집 (우선순위 높음)**
- Reddit RSS 피드가 가장 안정적
- 시간대별 크롤링 가능

**Phase 2: X(Twitter) 수집**
- Firecrawl Search 활용
- 주요 인플루언서 포스트 수집

**Phase 3: 데이터 정제 & 구조화**
- CSV/JSON 변환
- 중복 제거
- 감성 분석 준비

---

## 🎯 목표 데이터량
- Reddit: 500+ posts
- X(Twitter): 300+ tweets
- **Total: 800+ SNS records**

