# 🚀 배포 가이드 (Deployment Guide)

**Bitcoin Market Crash Analysis Dashboard 배포**

## 목차

1. [Streamlit Cloud 배포](#1-streamlit-cloud-배포-무료)
2. [Heroku 배포](#2-heroku-배포)
3. [Docker 배포](#3-docker-배포)
4. [AWS EC2 배포](#4-aws-ec2-배포)

---

## 1. Streamlit Cloud 배포 (무료)

### 1.1 사전 준비

- GitHub 계정
- Streamlit Cloud 계정 (무료)
- 프로젝트 GitHub 저장소

### 1.2 배포 단계

#### Step 1: GitHub에 푸시

```bash
# Git 초기화 (아직 안했다면)
git init
git add .
git commit -m "Initial commit: Bitcoin Crash Analysis"

# GitHub 저장소 생성 후
git remote add origin https://github.com/your-username/ai_team_6.git
git push -u origin main
```

#### Step 2: Streamlit Cloud 설정

1. [share.streamlit.io](https://share.streamlit.io/) 접속
2. "New app" 버튼 클릭
3. 다음 정보 입력:
   - **Repository**: `your-username/ai_team_6`
   - **Branch**: `main`
   - **Main file path**: `dashboard_app.py`
   - **App URL** (custom): `bitcoin-crash-analysis` (선택사항)

4. "Advanced settings" 클릭
   - **Python version**: `3.11`

5. "Deploy!" 클릭

#### Step 3: 배포 확인

- 배포 완료까지 약 5-10분 소요
- URL: `https://your-app-name.streamlit.app`
- 로그 확인 가능

### 1.3 문제 해결

**오류: "ModuleNotFoundError"**

```bash
# requirements.txt 확인
cat requirements.txt
```

**오류: "Out of memory"**

- Streamlit Cloud 무료 플랜은 1GB RAM 제한
- 데이터 크기 축소 또는 캐싱 최적화

**오류: "File not found"**

- 경로를 상대 경로로 변경

```python
# 절대 경로 (X)
df = pd.read_csv("C:/potenup3/ai_team_6/data/...")

# 상대 경로 (O)
df = pd.read_csv("data/processed/integrated/master_data_integrated.csv")
```

### 1.4 업데이트

```bash
# 코드 수정 후
git add .
git commit -m "Update dashboard"
git push

# Streamlit Cloud가 자동으로 재배포
```

---

## 2. Heroku 배포

### 2.1 사전 준비

```bash
# Heroku CLI 설치
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# macOS: brew tap heroku/brew && brew install heroku

# 로그인
heroku login
```

### 2.2 배포 파일 생성

#### Procfile

```bash
echo "web: streamlit run dashboard_app.py --server.port $PORT --server.address 0.0.0.0" > Procfile
```

#### setup.sh

```bash
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF
```

#### runtime.txt

```bash
echo "python-3.11.14" > runtime.txt
```

### 2.3 배포 실행

```bash
# Heroku 앱 생성
heroku create bitcoin-crash-analysis

# Git 푸시
git add .
git commit -m "Add Heroku config"
git push heroku main

# 앱 열기
heroku open
```

### 2.4 로그 확인

```bash
heroku logs --tail
```

---

## 3. Docker 배포

### 3.1 Dockerfile 생성

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 포트 노출
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 실행 명령
ENTRYPOINT ["streamlit", "run", "dashboard_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3.2 .dockerignore 생성

```bash
cat > .dockerignore << 'EOF'
.venv/
__pycache__/
*.pyc
.git/
.gitignore
.DS_Store
README.md
EOF
```

### 3.3 빌드 및 실행

```bash
# 이미지 빌드
docker build -t bitcoin-analysis:latest .

# 컨테이너 실행
docker run -p 8501:8501 bitcoin-analysis:latest

# 백그라운드 실행
docker run -d -p 8501:8501 --name bitcoin-app bitcoin-analysis:latest
```

### 3.4 Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
```

```bash
# 실행
docker-compose up -d

# 중지
docker-compose down
```

### 3.5 Docker Hub 배포

```bash
# 로그인
docker login

# 태그
docker tag bitcoin-analysis:latest your-username/bitcoin-analysis:latest

# 푸시
docker push your-username/bitcoin-analysis:latest
```

---

## 4. AWS EC2 배포

### 4.1 EC2 인스턴스 생성

1. AWS Console → EC2 → "Launch Instance"
2. **AMI**: Ubuntu Server 22.04 LTS
3. **Instance Type**: t2.medium (4GB RAM 권장)
4. **Security Group**:
   - SSH (22) - Your IP
   - Custom TCP (8501) - Anywhere
5. Key pair 다운로드

### 4.2 인스턴스 접속

```bash
# SSH 접속
ssh -i "your-key.pem" ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com
```

### 4.3 환경 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install python3.11 python3.11-venv python3-pip -y

# Git 설치
sudo apt install git -y

# 프로젝트 클론
git clone https://github.com/your-username/ai_team_6.git
cd ai_team_6

# 가상환경 생성
python3.11 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4.4 Streamlit 실행 (백그라운드)

#### 방법 1: nohup

```bash
nohup streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

#### 방법 2: systemd (권장)

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/bitcoin-dashboard.service
```

```ini
[Unit]
Description=Bitcoin Crash Analysis Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai_team_6
Environment="PATH=/home/ubuntu/ai_team_6/.venv/bin"
ExecStart=/home/ubuntu/ai_team_6/.venv/bin/streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable bitcoin-dashboard
sudo systemctl start bitcoin-dashboard

# 상태 확인
sudo systemctl status bitcoin-dashboard

# 로그 확인
sudo journalctl -u bitcoin-dashboard -f
```

### 4.5 Nginx 리버스 프록시 (선택사항)

```bash
# Nginx 설치
sudo apt install nginx -y

# 설정 파일
sudo nano /etc/nginx/sites-available/bitcoin-dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# 심볼릭 링크
sudo ln -s /etc/nginx/sites-available/bitcoin-dashboard /etc/nginx/sites-enabled/

# Nginx 재시작
sudo nginx -t
sudo systemctl restart nginx
```

### 4.6 HTTPS 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo certbot renew --dry-run
```

---

## 5. 성능 최적화

### 5.1 Streamlit 캐싱

```python
# dashboard_app.py
@st.cache_data(ttl=3600)  # 1시간 캐싱
def load_data():
    df = pd.read_csv("data/processed/integrated/master_data_integrated.csv")
    return df
```

### 5.2 데이터 압축

```bash
# CSV를 Parquet으로 변환 (더 작고 빠름)
pip install pyarrow

# Python 스크립트
import pandas as pd
df = pd.read_csv("master_data_integrated.csv")
df.to_parquet("master_data_integrated.parquet")
```

### 5.3 이미지 최적화

```bash
# PNG 압축
pip install pillow

# Python 스크립트
from PIL import Image
img = Image.open("chart.png")
img.save("chart_compressed.png", optimize=True, quality=85)
```

---

## 6. 모니터링

### 6.1 Uptime 체크

**UptimeRobot** (무료):

1. [uptimerobot.com](https://uptimerobot.com) 가입
2. "Add New Monitor" 클릭
3. URL: `https://your-app.streamlit.app`
4. 5분마다 체크

### 6.2 로그 분석

```bash
# Streamlit 로그
tail -f ~/.streamlit/logs/*.log

# 시스템 로그 (EC2)
sudo journalctl -u bitcoin-dashboard -f
```

### 6.3 메트릭 수집

```python
# dashboard_app.py에 추가
import time
from datetime import datetime

# 페이지 뷰 카운터
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1

st.sidebar.write(f"Total Views: {st.session_state.page_views}")
```

---

## 7. 보안

### 7.1 비밀 정보 관리

```bash
# .streamlit/secrets.toml (로컬)
# GitHub에 커밋하지 말 것!
[api]
key = "your-secret-key"
```

Streamlit Cloud에서:

1. App settings → Secrets
2. TOML 형식으로 입력

### 7.2 인증 추가

```python
# dashboard_app.py
import streamlit as st

def check_password():
    """Simple password check"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # 메인 앱 코드
    main()
```

---

## 📞 지원

배포 관련 문제:

- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io/)
- GitHub Issues: 프로젝트 저장소

---

**마지막 업데이트**: 2026-02-03  
**문서 버전**: 1.0.0
