#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crypto Fear & Greed Index + Bitcoin(BTC) 일봉 가격 수집 및 병합 스크립트

실행 방법:
  python fetch_btc_fng_20250901_20251031.py
  python fetch_btc_fng_20250901_20251031.py --start 2025-09-01 --end 2025-10-31
  python fetch_btc_fng_20250901_20251031.py --start 2025-09-01 --end 2025-10-31 --out ./output/my_data.csv
"""

import argparse
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_fear_greed_index(limit=0, timeout=30):
    """
    Crypto Fear & Greed Index 데이터를 Alternative.me API로부터 수집.
    
    Args:
        limit: 0이면 전체 데이터, 양수면 최근 N개
        timeout: 요청 타임아웃(초)
    
    Returns:
        pd.DataFrame: 수집된 Fear & Greed Index 데이터
    """
    url = "https://api.alternative.me/fng/"
    params = {
        "limit": limit,
        "format": "json"
    }
    
    logger.info(f"Fetching Fear & Greed Index from {url}")
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data:
            logger.error("API response missing 'data' field")
            return pd.DataFrame()
        
        df = pd.DataFrame(data["data"])
        logger.info(f"Fetched {len(df)} Fear & Greed records")
        
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Fear & Greed Index: {e}")
        return pd.DataFrame()


def process_fear_greed_data(df, start_date, end_date):
    """
    Fear & Greed Index 데이터를 처리.
    
    Args:
        df: 원본 DataFrame
        start_date: 시작 날짜 (YYYYMMDD 문자열)
        end_date: 종료 날짜 (YYYYMMDD 문자열)
    
    Returns:
        pd.DataFrame: 처리된 데이터
    """
    if df.empty:
        logger.warning("Empty Fear & Greed DataFrame")
        return pd.DataFrame()
    
    # 필드명 매핑
    df = df.rename(columns={
        'value': 'fear_greed',
        'value_classification': 'classification'
    })
    
    # timestamp(유닉스 초)를 UTC datetime으로 변환
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    
    # date 컬럼 생성 (YYYYMMDD)
    df['date'] = df['timestamp_utc'].dt.strftime('%Y%m%d')
    
    # fear_greed를 int로 변환
    df['fear_greed'] = pd.to_numeric(df['fear_greed'], errors='coerce').astype('Int64')
    
    # 기간 필터링
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    logger.info(f"Filtered Fear & Greed to {len(df)} records (date: {start_date} ~ {end_date})")
    
    if df.empty:
        logger.warning("No Fear & Greed data after filtering")
        return pd.DataFrame()
    
    # 같은 date에 여러 레코드가 있으면 timestamp_utc가 가장 이른 것만 유지
    df = df.sort_values('timestamp_utc')
    df = df.drop_duplicates(subset=['date'], keep='first')
    
    # date 오름차순 정렬
    df = df.sort_values('date').reset_index(drop=True)
    
    # 필요한 컬럼만 선택
    df = df[['date', 'fear_greed', 'classification', 'timestamp_utc']]
    
    logger.info(f"Processed Fear & Greed data: {len(df)} unique dates")
    
    return df


def fetch_btc_price(start_date_str, end_date_str, timeout=30):
    """
    Bitcoin(BTC) 가격 데이터를 Binance API로부터 수집.
    
    Args:
        start_date_str: 시작 날짜 (YYYYMMDD)
        end_date_str: 종료 날짜 (YYYYMMDD)
        timeout: 요청 타임아웃(초)
    
    Returns:
        pd.DataFrame: 수집된 BTC 가격 데이터
    """
    url = "https://api.binance.com/api/v3/klines"
    
    # YYYYMMDD를 datetime으로 변환 후 밀리초 타임스탬프로
    start_dt = datetime.strptime(start_date_str, '%Y%m%d').replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end_date_str, '%Y%m%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
    
    start_time_ms = int(start_dt.timestamp() * 1000)
    end_time_ms = int(end_dt.timestamp() * 1000)
    
    params = {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "startTime": start_time_ms,
        "endTime": end_time_ms,
        "limit": 1000
    }
    
    logger.info(f"Fetching BTC price from Binance API: {url}")
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            logger.error("API response is empty")
            return pd.DataFrame()
        
        # Binance klines 데이터: [open_time, open, high, low, close, volume, ...]
        # Close 가격(index 4)을 사용
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp_ms'] = pd.to_numeric(df['open_time'])
        df['price'] = pd.to_numeric(df['close'])
        
        logger.info(f"Fetched {len(df)} BTC daily price records from Binance")
        
        return df[['timestamp_ms', 'price']]
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch BTC price from Binance: {e}")
        return pd.DataFrame()


def process_btc_price_data(df, start_date, end_date):
    """
    BTC 가격 데이터를 일봉으로 처리.
    
    Args:
        df: 원본 DataFrame (이미 일봉)
        start_date: 시작 날짜 (YYYYMMDD 문자열)
        end_date: 종료 날짜 (YYYYMMDD 문자열)
    
    Returns:
        pd.DataFrame: 일봉 데이터
    """
    if df.empty:
        logger.warning("Empty BTC price DataFrame")
        return pd.DataFrame()
    
    # timestamp_ms를 UTC datetime으로 변환
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
    
    # date 컬럼 생성 (YYYYMMDD)
    df['date'] = df['timestamp_utc'].dt.strftime('%Y%m%d')
    
    # btc_price_usd 컬럼명 변경
    df['btc_price_usd'] = df['price']
    
    # 기간 필터링 (이미 API에서 필터링되었지만 재확인)
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    logger.info(f"Filtered BTC price to {len(df)} records (date: {start_date} ~ {end_date})")
    
    if df.empty:
        logger.warning("No BTC price data after filtering")
        return pd.DataFrame()
    
    # date 오름차순 정렬
    df = df.sort_values('date').reset_index(drop=True)
    
    # 필요한 컬럼만 선택
    df = df[['date', 'btc_price_usd']]
    
    logger.info(f"Processed BTC price data: {len(df)} daily records")
    
    return df


def merge_data(fng_df, btc_df):
    """
    Fear & Greed Index와 BTC 가격 데이터를 병합.
    
    Args:
        fng_df: Fear & Greed DataFrame
        btc_df: BTC 가격 DataFrame
    
    Returns:
        pd.DataFrame: 병합된 데이터
    """
    if fng_df.empty or btc_df.empty:
        logger.error("Cannot merge: one or both DataFrames are empty")
        return pd.DataFrame()
    
    # date 기준 inner join
    merged = pd.merge(fng_df, btc_df, on='date', how='inner')
    
    logger.info(f"Merged data: {len(merged)} records")
    
    # 날짜 누락 체크
    fng_dates = set(fng_df['date'])
    btc_dates = set(btc_df['date'])
    merged_dates = set(merged['date'])
    
    missing_from_btc = fng_dates - btc_dates
    missing_from_fng = btc_dates - fng_dates
    
    if missing_from_btc:
        logger.warning(f"Fear & Greed dates not in BTC data ({len(missing_from_btc)}): {sorted(missing_from_btc)[:10]}...")
    
    if missing_from_fng:
        logger.warning(f"BTC dates not in Fear & Greed data ({len(missing_from_fng)}): {sorted(missing_from_fng)[:10]}...")
    
    # 컬럼 순서 고정
    merged = merged[['date', 'btc_price_usd', 'fear_greed', 'classification', 'timestamp_utc']]
    
    # timestamp_utc를 ISO8601 문자열로 변환
    merged['timestamp_utc'] = merged['timestamp_utc'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return merged


def save_to_csv(df, output_path):
    """
    DataFrame을 CSV 파일로 저장.
    
    Args:
        df: 저장할 DataFrame
        output_path: 출력 파일 경로
    """
    if df.empty:
        logger.error("Cannot save empty DataFrame")
        return
    
    # 디렉토리 생성
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV 저장
    df.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(df)} records to {output_path}")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='Fetch and merge Crypto Fear & Greed Index and Bitcoin price data'
    )
    parser.add_argument(
        '--start',
        type=str,
        default='2025-09-01',
        help='Start date (YYYY-MM-DD format, default: 2025-09-01)'
    )
    parser.add_argument(
        '--end',
        type=str,
        default='2025-10-31',
        help='End date (YYYY-MM-DD format, default: 2025-10-31)'
    )
    parser.add_argument(
        '--out',
        type=str,
        default='./data/btc_fear_greed_20250901_20251031.csv',
        help='Output CSV file path (default: ./data/btc_fear_greed_20250901_20251031.csv)'
    )
    
    args = parser.parse_args()
    
    # 날짜 형식 변환 (YYYY-MM-DD → YYYYMMDD)
    try:
        start_date = datetime.strptime(args.start, '%Y-%m-%d').strftime('%Y%m%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d').strftime('%Y%m%d')
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return
    
    logger.info(f"Date range: {start_date} ~ {end_date}")
    logger.info(f"Output path: {args.out}")
    
    # Fear & Greed Index 수집 및 처리
    fng_raw = fetch_fear_greed_index(limit=0)
    fng_processed = process_fear_greed_data(fng_raw, start_date, end_date)
    
    if fng_processed.empty:
        logger.error("Failed to process Fear & Greed Index data")
        return
    
    # BTC 가격 수집 및 처리
    btc_raw = fetch_btc_price(start_date, end_date)
    btc_processed = process_btc_price_data(btc_raw, start_date, end_date)
    
    if btc_processed.empty:
        logger.error("Failed to process BTC price data")
        return
    
    # 데이터 병합
    merged = merge_data(fng_processed, btc_processed)
    
    if merged.empty:
        logger.error("Failed to merge data")
        return
    
    # CSV 저장
    save_to_csv(merged, args.out)
    
    logger.info("Process completed successfully")


if __name__ == "__main__":
    main()
