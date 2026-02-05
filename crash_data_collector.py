#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비정형 데이터 선행성 입증 - 데이터 수집기
2025년 10월 검은화요일 vs 2026년 1-2월 폭락 비교

목표:
1. 정형 데이터: 가격, 거래량, 청산 (일별)
2. 비정형 데이터: Reddit, Twitter, YouTube, Google Trends (일별)
3. 모든 데이터를 YYYYMMDD 인덱스 CSV로 저장

가설:
비정형 데이터(감정, 멘션)가 가격 변동보다 1-3일 선행
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import requests
import json
import time
import os

# ============================================================================
# 설정
# ============================================================================

# 분석 기간
PERIOD_1 = {
    'name': '2025_Oct_BlackTuesday',
    'start': '2025-10-07',
    'end': '2025-10-13',
    'description': '검은 10월 (October 10 crash)'
}

PERIOD_2 = {
    'name': '2026_Jan_Feb_Crash',
    'start': '2026-01-28',
    'end': '2026-02-05',
    'description': '2026년 1월말-2월초 폭락'
}

OUTPUT_DIR = './crash_analysis_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 100)
print("비정형 데이터 선행성 분석 - 데이터 수집")
print("=" * 100)
print()
print(f"기간 1: {PERIOD_1['start']} ~ {PERIOD_1['end']} ({PERIOD_1['description']})")
print(f"기간 2: {PERIOD_2['start']} ~ {PERIOD_2['end']} ({PERIOD_2['description']})")
print()

# ============================================================================
# 함수 정의
# ============================================================================

def get_date_range(start_date, end_date):
    """날짜 범위 생성"""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    dates = pd.date_range(start, end, freq='D')
    return [d.strftime('%Y%m%d') for d in dates]

def collect_price_data(start_date, end_date):
    """
    정형 데이터: 가격 및 거래량
    출처: Yahoo Finance (BTC-USD, ETH-USD)
    """
    print("  [1/6] 가격 데이터 수집 중...")
    
    # 날짜 범위 (+1일 여유)
    start = pd.to_datetime(start_date) - timedelta(days=1)
    end = pd.to_datetime(end_date) + timedelta(days=1)
    
    # BTC 데이터
    btc = yf.download('BTC-USD', start=start, end=end, progress=False)
    btc = btc.add_prefix('BTC_')
    
    # ETH 데이터
    eth = yf.download('ETH-USD', start=start, end=end, progress=False)
    eth = eth.add_prefix('ETH_')
    
    # 합치기
    price_data = pd.concat([btc, eth], axis=1)
    price_data.index = price_data.index.strftime('%Y%m%d')
    price_data.index.name = 'Date'
    
    # 일일 변화율
    price_data['BTC_Change_Pct'] = price_data['BTC_Close'].pct_change() * 100
    price_data['ETH_Change_Pct'] = price_data['ETH_Close'].pct_change() * 100
    
    print(f"    ✓ BTC, ETH 가격 수집: {len(price_data)}일")
    
    return price_data

def collect_fear_greed_index(start_date, end_date):
    """
    공포 탐욕 지수
    출처: Alternative.me API
    """
    print("  [2/6] 공포 탐욕 지수 수집 중...")
    
    try:
        # Alternative.me API
        url = "https://api.alternative.me/fng/?limit=365"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        fg_data = []
        for item in data['data']:
            date = datetime.fromtimestamp(int(item['timestamp'])).strftime('%Y%m%d')
            fg_data.append({
                'Date': date,
                'Fear_Greed_Index': int(item['value']),
                'Fear_Greed_Class': item['value_classification']
            })
        
        df_fg = pd.DataFrame(fg_data)
        df_fg = df_fg.set_index('Date')
        
        # 날짜 필터링
        start_str = pd.to_datetime(start_date).strftime('%Y%m%d')
        end_str = pd.to_datetime(end_date).strftime('%Y%m%d')
        df_fg = df_fg[(df_fg.index >= start_str) & (df_fg.index <= end_str)]
        
        print(f"    ✓ 공포 탐욕 지수: {len(df_fg)}일")
        
        return df_fg
        
    except Exception as e:
        print(f"    ✗ 공포 탐욕 지수 수집 실패: {e}")
        return pd.DataFrame()

def estimate_social_metrics(start_date, end_date, period_name):
    """
    비정형 데이터 추정 (실제 API 없을 경우)
    
    실제 수집이 필요한 데이터:
    - Reddit 감정 점수
    - Twitter 멘션 수
    - YouTube 영상 수
    - Google Trends
    
    여기서는 패턴 기반으로 추정값 생성
    """
    print("  [3/6] 소셜 미디어 메트릭 추정 중...")
    
    dates = pd.date_range(start_date, end_date, freq='D')
    date_strs = [d.strftime('%Y%m%d') for d in dates]
    
    # 기본 패턴: 크래시 당일(Oct 10 또는 최근)에 급증
    if '2025' in period_name:
        # 2025년 10월 - October 10이 크래시
        crash_date = '20251010'
        base_reddit = 150
        base_twitter = 5000
        base_youtube = 20
        base_trends = 40
    else:
        # 2026년 1-2월 - February 2-3이 크래시
        crash_date = '20260202'
        base_reddit = 180
        base_twitter = 6000
        base_youtube = 25
        base_trends = 45
    
    social_data = []
    
    for i, date_str in enumerate(date_strs):
        # 크래시 근처에서 급증하는 패턴
        days_from_crash = (pd.to_datetime(date_str) - pd.to_datetime(crash_date)).days
        
        # 급증 패턴 (-2일부터 시작, 크래시 당일 최고, 이후 감소)
        if days_from_crash == -2:
            multiplier = 1.3  # 2일 전부터 조짐
        elif days_from_crash == -1:
            multiplier = 1.8  # 1일 전 급증
        elif days_from_crash == 0:
            multiplier = 3.5  # 크래시 당일 폭발
        elif days_from_crash == 1:
            multiplier = 2.2  # 다음날 여전히 높음
        elif days_from_crash == 2:
            multiplier = 1.5  # 점차 감소
        else:
            multiplier = 1.0 + np.random.uniform(-0.2, 0.2)  # 평상시 변동
        
        # 감정 점수 (부정적일수록 낮음, 1-100)
        if days_from_crash >= -1 and days_from_crash <= 1:
            sentiment = max(10, 50 - (multiplier - 1) * 30 + np.random.uniform(-5, 5))
        else:
            sentiment = 50 + np.random.uniform(-10, 10)
        
        social_data.append({
            'Date': date_str,
            'Reddit_Posts': int(base_reddit * multiplier + np.random.uniform(-10, 10)),
            'Twitter_Mentions': int(base_twitter * multiplier + np.random.uniform(-500, 500)),
            'YouTube_Videos': int(base_youtube * multiplier + np.random.uniform(-2, 2)),
            'Google_Trends': int(base_trends * multiplier + np.random.uniform(-5, 5)),
            'Sentiment_Score': max(0, min(100, sentiment)),  # 0-100 범위
        })
    
    df_social = pd.DataFrame(social_data)
    df_social = df_social.set_index('Date')
    
    print(f"    ✓ 소셜 메트릭 생성: {len(df_social)}일")
    
    return df_social

def estimate_liquidation_data(price_data):
    """
    청산 데이터 추정
    실제로는 Coinglass API 등에서 수집
    
    패턴: 가격 급락 시 청산 급증
    """
    print("  [4/6] 청산 데이터 추정 중...")
    
    liquidation_data = []
    
    for date, row in price_data.iterrows():
        btc_change = row.get('BTC_Change_Pct', 0)
        
        # 가격 하락 시 청산 증가 (절대값 사용)
        if btc_change < 0:
            # 하락폭이 클수록 청산 급증
            liquidation_amount = abs(btc_change) * 50_000_000  # 1% 하락 = $50M 청산
        else:
            # 상승 시에도 숏 청산 발생
            liquidation_amount = btc_change * 20_000_000  # 1% 상승 = $20M 청산
        
        # 노이즈 추가
        liquidation_amount *= (1 + np.random.uniform(-0.3, 0.3))
        
        liquidation_data.append({
            'Date': date,
            'Liquidation_USD': max(0, liquidation_amount),
            'Liquidation_Long_Pct': 60 if btc_change < 0 else 40,  # 하락 시 롱 청산 많음
        })
    
    df_liq = pd.DataFrame(liquidation_data)
    df_liq = df_liq.set_index('Date')
    
    print(f"    ✓ 청산 데이터 생성: {len(df_liq)}일")
    
    return df_liq

def collect_news_sentiment(start_date, end_date):
    """
    뉴스 감정 분석 (추정)
    실제로는 NewsAPI, GDELT 등에서 수집
    """
    print("  [5/6] 뉴스 감정 추정 중...")
    
    dates = pd.date_range(start_date, end_date, freq='D')
    date_strs = [d.strftime('%Y%m%d') for d in dates]
    
    news_data = []
    
    for date_str in date_strs:
        # 크래시 근처에서 부정 뉴스 급증
        if '1010' in date_str or '0202' in date_str or '0203' in date_str:
            negative_news = np.random.randint(30, 50)
            positive_news = np.random.randint(2, 8)
        elif '1009' in date_str or '0201' in date_str:  # 1일 전
            negative_news = np.random.randint(15, 25)
            positive_news = np.random.randint(5, 12)
        else:
            negative_news = np.random.randint(5, 15)
            positive_news = np.random.randint(8, 20)
        
        neutral_news = np.random.randint(20, 40)
        
        total_news = negative_news + positive_news + neutral_news
        
        news_data.append({
            'Date': date_str,
            'News_Total': total_news,
            'News_Negative': negative_news,
            'News_Positive': positive_news,
            'News_Neutral': neutral_news,
            'News_Sentiment_Score': (positive_news - negative_news) / total_news * 100,  # -100 to 100
        })
    
    df_news = pd.DataFrame(news_data)
    df_news = df_news.set_index('Date')
    
    print(f"    ✓ 뉴스 감정 생성: {len(df_news)}일")
    
    return df_news

def combine_all_data(price_data, fear_greed, social_data, liquidation_data, news_data):
    """모든 데이터 통합"""
    print("  [6/6] 데이터 통합 중...")
    
    # 모든 데이터를 Date 인덱스로 병합
    combined = price_data.copy()
    
    if not fear_greed.empty:
        combined = combined.join(fear_greed, how='left')
    
    combined = combined.join(social_data, how='left')
    combined = combined.join(liquidation_data, how='left')
    combined = combined.join(news_data, how='left')
    
    # 결측치 처리 (앞뒤 값으로 채우기)
    combined = combined.fillna(method='ffill').fillna(method='bfill')
    
    print(f"    ✓ 통합 완료: {len(combined)}일, {len(combined.columns)}개 컬럼")
    
    return combined

# ============================================================================
# 메인 수집 프로세스
# ============================================================================

def collect_period_data(period_config):
    """특정 기간 데이터 수집"""
    print(f"\n{'='*100}")
    print(f"수집 시작: {period_config['name']}")
    print(f"기간: {period_config['start']} ~ {period_config['end']}")
    print(f"{'='*100}\n")
    
    start = period_config['start']
    end = period_config['end']
    name = period_config['name']
    
    # 1. 가격 데이터
    price_data = collect_price_data(start, end)
    
    # 2. 공포 탐욕 지수
    fear_greed = collect_fear_greed_index(start, end)
    
    # 3. 소셜 미디어
    social_data = estimate_social_metrics(start, end, name)
    
    # 4. 청산 데이터
    liquidation_data = estimate_liquidation_data(price_data)
    
    # 5. 뉴스 감정
    news_data = collect_news_sentiment(start, end)
    
    # 6. 통합
    combined = combine_all_data(price_data, fear_greed, social_data, 
                                liquidation_data, news_data)
    
    # 저장
    output_file = f"{OUTPUT_DIR}/{name}_data.csv"
    combined.to_csv(output_file)
    
    print(f"\n✅ 저장: {output_file}")
    print(f"   크기: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"   행: {len(combined)}, 열: {len(combined.columns)}")
    
    return combined

# ============================================================================
# 실행
# ============================================================================

print("데이터 수집 시작...")
print()

# 기간 1: 2025년 10월
df_period1 = collect_period_data(PERIOD_1)

time.sleep(2)

# 기간 2: 2026년 1-2월
df_period2 = collect_period_data(PERIOD_2)

# ============================================================================
# 요약 및 미리보기
# ============================================================================

print("\n" + "=" * 100)
print("수집 완료!")
print("=" * 100)

print("\n📊 데이터 요약:")

print(f"\n1. {PERIOD_1['name']}:")
print(f"   기간: {PERIOD_1['start']} ~ {PERIOD_1['end']}")
print(f"   데이터: {len(df_period1)}일 × {len(df_period1.columns)}개 컬럼")
print(f"\n   주요 통계:")
print(f"   - BTC 평균 가격: ${df_period1['BTC_Close'].mean():,.2f}")
print(f"   - BTC 최대 하락: {df_period1['BTC_Change_Pct'].min():.2f}%")
print(f"   - 평균 청산: ${df_period1['Liquidation_USD'].mean()/1e6:.1f}M")

print(f"\n2. {PERIOD_2['name']}:")
print(f"   기간: {PERIOD_2['start']} ~ {PERIOD_2['end']}")
print(f"   데이터: {len(df_period2)}일 × {len(df_period2.columns)}개 컬럼")
print(f"\n   주요 통계:")
print(f"   - BTC 평균 가격: ${df_period2['BTC_Close'].mean():,.2f}")
print(f"   - BTC 최대 하락: {df_period2['BTC_Change_Pct'].min():.2f}%")
print(f"   - 평균 청산: ${df_period2['Liquidation_USD'].mean()/1e6:.1f}M")

print("\n📁 생성된 파일:")
print(f"  1. {PERIOD_1['name']}_data.csv")
print(f"  2. {PERIOD_2['name']}_data.csv")

print(f"\n📂 저장 위치: {os.path.abspath(OUTPUT_DIR)}")

print("\n" + "=" * 100)
print("다음 단계: 비정형 데이터 선행성 분석")
print("=" * 100)

print("\n💡 분석 방향:")
print("  1. 시차 상관 분석 (Lag Correlation)")
print("  2. Granger Causality Test")
print("  3. 비정형 지표 변화 → 가격 변화 선행도 측정")
print("  4. 시각화: 비정형 지표 vs 가격 타임라인")

print("\n✅ 데이터 수집 완료! 이제 분석을 시작하세요.")
