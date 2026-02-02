# 🎥 YouTube API 설정 가이드

## 📋 목차
1. [API 키 발급 (5분)](#api-키-발급)
2. [스크립트 설정](#스크립트-설정)
3. [실행](#실행)
4. [예상 결과](#예상-결과)

---

## 🔑 API 키 발급

### Step 1: Google Cloud Console 접속
1. https://console.cloud.google.com/ 접속
2. Google 계정으로 로그인

### Step 2: 프로젝트 생성
1. 상단의 **"프로젝트 선택"** 클릭
2. **"새 프로젝트"** 클릭
3. 프로젝트 이름: `crypto-youtube-analyzer` 입력
4. **"만들기"** 클릭

### Step 3: YouTube Data API v3 활성화
1. 왼쪽 메뉴 **"API 및 서비스" > "라이브러리"** 클릭
2. 검색창에 `YouTube Data API v3` 입력
3. **"YouTube Data API v3"** 클릭
4. **"사용 설정"** 클릭

### Step 4: API 키 생성
1. 왼쪽 메뉴 **"사용자 인증 정보"** 클릭
2. 상단의 **"+ 사용자 인증 정보 만들기"** 클릭
3. **"API 키"** 선택
4. API 키가 생성됨 → **복사** 버튼 클릭

**예시:**
```
AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
```

### Step 5: API 키 제한 (선택, 보안 강화)
1. 생성된 API 키 옆 **"키 제한사항 설정"** 클릭
2. **"API 제한사항"** → **"키 제한"** 선택
3. **"YouTube Data API v3"** 선택
4. **"저장"** 클릭

---

## ⚙️ 스크립트 설정

### 1. API 키 입력
`youtube_mass_collector.py` 파일을 열고 **18번 줄**을 수정:

```python
# 수정 전
API_KEY = 'YOUR_YOUTUBE_API_KEY_HERE'

# 수정 후 (발급받은 키 붙여넣기)
API_KEY = 'AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567'
```

### 2. 수집 설정 확인 (선택)
**23-32번 줄**에서 원하는대로 조정:

```python
COLLECTION_CONFIG = {
    'date_range': {
        'start': '2025-09-01T00:00:00Z',  # 시작일
        'end': '2025-10-31T23:59:59Z'     # 종료일
    },
    'target_videos': 1000,          # 목표 영상 수
    'target_comments': 15000,       # 목표 댓글 수
    'max_comments_per_video': 100,  # 영상당 최대 댓글
    'target_captions': 10000,       # 목표 자막 문장 수
}
```

---

## 🚀 실행

### 방법 1: VSCode 터미널
```bash
# 패키지 설치
uv pip install google-api-python-client youtube-transcript-api pandas

# 실행
python youtube_mass_collector.py
```

### 방법 2: Jupyter Notebook
```python
# 패키지 설치
!pip install google-api-python-client youtube-transcript-api pandas

# 실행
%run youtube_mass_collector.py
```

### 방법 3: 명령 프롬프트 (Windows)
```cmd
cd C:\경로\to\your\folder
pip install google-api-python-client youtube-transcript-api pandas
python youtube_mass_collector.py
```

---

## 📊 예상 결과

### 수집 시간
- **영상 검색**: 5-10분 (1,000개)
- **댓글 수집**: 30-60분 (15,000개)
- **자막 수집**: 30-45분 (10,000개 문장)
- **총 소요 시간**: 1.5-2시간

### 수집 데이터
```
📁 youtube_data_collection/
├── youtube_videos_20260202_120000.csv      (1,000개)
├── youtube_comments_20260202_120000.csv    (15,000개)
├── youtube_captions_20260202_120000.csv    (10,000개)
└── youtube_collection_20260202_120000.json (전체 통합)

총: 26,000개 텍스트 데이터
```

### 파일 크기
- 영상 메타데이터: ~300 KB
- 댓글: ~3-5 MB
- 자막: ~2-3 MB
- JSON: ~8-10 MB
- **총**: ~15 MB

---

## 💡 할당량 관리

### YouTube API 할당량
- **무료 할당량**: 10,000 units/일
- **소비량**:
  - 검색: 100 units/요청
  - 영상 상세: 1 unit/영상
  - 댓글: 1 unit/영상
  - 자막: API 할당량 미사용 (별도 라이브러리)

### 예상 소비량
```
검색: 25 키워드 × 100 units = 2,500 units
영상 상세: 1,000 영상 × 1 unit = 1,000 units
댓글: 1,000 영상 × 1 unit = 1,000 units
─────────────────────────────────────────
총: 4,500 units (45% 사용)
```

✅ **하루에 충분히 완료 가능!**

### 할당량 초과 시
1. 다음날 다시 실행 (매일 자정 UTC 리셋)
2. 또는 Google Cloud 유료 플랜 ($0.002/unit)

---

## 🔧 문제 해결

### ❌ "quotaExceeded" 오류
**원인**: 일일 할당량 10,000 units 초과

**해결**:
1. 내일 다시 실행
2. 또는 `target_videos`, `target_comments` 줄이기
3. 또는 유료 플랜 사용

### ❌ "keyInvalid" 오류
**원인**: API 키가 잘못됨

**해결**:
1. API 키 다시 복사
2. YouTube Data API v3 활성화 확인
3. 키 제한사항 확인 (IP 제한 등)

### ❌ "commentsDisabled" 경고
**원인**: 일부 영상은 댓글 비활성화

**해결**: 정상 동작 (자동으로 건너뜀)

### ❌ "TranscriptsDisabled" 경고
**원인**: 일부 영상은 자막 없음

**해결**: 정상 동작 (자동으로 건너뜀)

### ⚠️ 수집이 너무 느림
**원인**: Rate limit

**해결**:
- 이미 최적화됨 (시간 지연 포함)
- 더 빠르게: 불가능 (YouTube 정책)

---

## 📈 수집 최적화 팁

### 1. 키워드 최적화
현재 25개 키워드 사용 중. 더 추가하려면:

```python
SEARCH_KEYWORDS = [
    # 기존 25개...
    
    # 추가 키워드
    'crypto crash analysis',
    'bitcoin technical analysis October',
    'altseason over 2025',
    # ...
]
```

### 2. 병렬 처리 (고급)
여러 API 키 사용 시 더 빠름 (별도 구현 필요)

### 3. 중간 저장 활용
스크립트 중단 시에도 데이터 보존:
- `videos_metadata.csv`
- `comments_temp.csv`

---

## 🎯 목표 달성 체크리스트

### 필수 조건
- [ ] Google 계정 있음
- [ ] YouTube API 키 발급 완료
- [ ] 패키지 설치 완료
- [ ] API 키 스크립트에 입력

### 실행 전
- [ ] 날짜 범위 확인 (2025-09-01 ~ 10-31)
- [ ] 저장 경로 확인 (`./youtube_data_collection`)
- [ ] 디스크 여유 공간 확인 (최소 100 MB)

### 실행 후
- [ ] 영상 1,000개 이상 수집
- [ ] 댓글 10,000개 이상 수집
- [ ] 자막 5,000개 이상 수집
- [ ] 총 텍스트 15,000-26,000개 달성

---

## 🚀 빠른 시작 (5분)

```bash
# 1. API 키 발급 (위 가이드 참고)

# 2. 패키지 설치
pip install google-api-python-client youtube-transcript-api pandas

# 3. API 키 입력 (스크립트 18번 줄)
# API_KEY = 'YOUR_API_KEY'

# 4. 실행!
python youtube_mass_collector.py

# 5. 완료! (1-2시간 후)
# 📂 youtube_data_collection/ 폴더 확인
```

---

## 📞 도움이 필요하신가요?

### 자주 하는 실수
1. API 키를 `'` 안에 넣지 않음 → `API_KEY = AIza...` (X)
2. YouTube Data API v3 활성화 안 함
3. 할당량 초과 (다음날 재시도)

### 확인 사항
- ✅ API 키가 따옴표 안에 있나요?
- ✅ YouTube Data API v3가 활성화되어 있나요?
- ✅ 인터넷 연결이 안정적인가요?

---

**준비되셨나요? 지금 바로 시작하세요!** 🚀
