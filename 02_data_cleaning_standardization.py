"""
Task 2: 날짜 형식 통일 및 데이터 정제
모든 데이터의 날짜 형식을 datetime으로 변환하고 결측치 처리
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 데이터 경로 설정
DATA_DIR = Path("data/processed")

def convert_date_to_datetime(date_value):
    """
    다양한 날짜 형식을 datetime으로 변환
    YYYYMMDD (int/str) -> datetime
    YYYY-MM-DD (str) -> datetime
    """
    if pd.isna(date_value):
        return pd.NaT
    
    # int64 또는 숫자 형태의 YYYYMMDD
    if isinstance(date_value, (int, np.integer)):
        return pd.to_datetime(str(date_value), format='%Y%m%d')
    
    # 문자열 형태
    date_str = str(date_value)
    
    # YYYYMMDD 형식 (8자리)
    if len(date_str) == 8 and date_str.isdigit():
        return pd.to_datetime(date_str, format='%Y%m%d')
    
    # 기타 형식은 pandas가 자동 파싱
    try:
        return pd.to_datetime(date_str)
    except:
        return pd.NaT

def clean_and_standardize_data():
    """모든 CSV 파일을 로드하고 날짜 형식 통일 및 결측치 처리"""
    
    print("=" * 80)
    print("Task 2: 날짜 형식 통일 및 데이터 정제 시작")
    print("=" * 80)
    
    # ===== 1. Bitcoin News Data =====
    print("\n[1/6] Bitcoin News 데이터 처리 중...")
    df_news = pd.read_csv(DATA_DIR / "bitcoin_news_merged_0.csv")
    print(f"  원본 shape: {df_news.shape}")
    
    # 날짜 변환
    df_news['date'] = df_news['date'].apply(convert_date_to_datetime)
    print(f"  ✅ date 컬럼 datetime 변환 완료")
    print(f"  결측치: date={df_news['date'].isna().sum()}, v2_themes={df_news['v2_themes'].isna().sum()}")
    
    # ===== 2. Features Daily Data =====
    print("\n[2/6] Features Daily 데이터 처리 중...")
    df_features = pd.read_csv(DATA_DIR / "features_daily.csv")
    print(f"  원본 shape: {df_features.shape}")
    
    df_features['date'] = df_features['date'].apply(convert_date_to_datetime)
    print(f"  ✅ date 컬럼 datetime 변환 완료")
    print(f"  결측치: {df_features.isna().sum().sum()}개 (모든 컬럼)")
    
    # ===== 3. GDELT Articles Data =====
    print("\n[3/6] GDELT Articles 데이터 처리 중...")
    df_gdelt = pd.read_csv(DATA_DIR / "gdelt_articles_modified_0.csv")
    print(f"  원본 shape: {df_gdelt.shape}")
    
    df_gdelt['date'] = df_gdelt['date'].apply(convert_date_to_datetime)
    df_gdelt['published_at_utc_dt'] = pd.to_datetime(df_gdelt['published_at_utc_dt'])
    print(f"  ✅ 날짜 컬럼 datetime 변환 완료")
    print(f"  결측치: date={df_gdelt['date'].isna().sum()}, title={df_gdelt['title'].isna().sum()}")
    
    # ===== 4. Daily Data (거시경제 + 가격 데이터) =====
    print("\n[4/6] Daily Data 처리 중...")
    df_daily = pd.read_csv(DATA_DIR / "merged_정형데이터" / "daily_data_merged.csv")
    print(f"  원본 shape: {df_daily.shape}")
    
    # 날짜 변환
    df_daily['Date'] = df_daily['Date'].apply(convert_date_to_datetime)
    df_daily = df_daily.rename(columns={'Date': 'date'})  # 컬럼명 통일
    
    print(f"\n  [결측치 처리 전]")
    for col in df_daily.columns:
        if df_daily[col].isna().sum() > 0:
            print(f"    {col}: {df_daily[col].isna().sum()} ({df_daily[col].isna().sum()/len(df_daily)*100:.2f}%)")
    
    # 날짜 순 정렬
    df_daily = df_daily.sort_values('date').reset_index(drop=True)
    
    # 결측치 처리 전략
    # 1. 선형 보간 (연속적인 수치 데이터)
    numeric_cols = ['Yield_10Y', 'Gold_Price_YF', 'Gold_Price_Investing', 'USD_Index']
    for col in numeric_cols:
        if col in df_daily.columns:
            df_daily[col] = df_daily[col].interpolate(method='linear', limit_direction='both')
    
    # 2. Forward fill (속도 관련 데이터 - 이전 값 유지)
    speed_cols = ['BTC_Price_Speed', 'M2_Expansion_Speed']
    for col in speed_cols:
        if col in df_daily.columns:
            df_daily[col] = df_daily[col].fillna(0)  # 속도는 0으로 초기화
    
    print(f"\n  [결측치 처리 후]")
    for col in df_daily.columns:
        if df_daily[col].isna().sum() > 0:
            print(f"    {col}: {df_daily[col].isna().sum()} ({df_daily[col].isna().sum()/len(df_daily)*100:.2f}%)")
    
    if df_daily.isna().sum().sum() == 0:
        print(f"  ✅ 모든 결측치 처리 완료!")
    
    # ===== 5. M2 & Inflation Data =====
    print("\n[5/6] M2 & Inflation 데이터 처리 중...")
    df_m2 = pd.read_csv(DATA_DIR / "merged_정형데이터" / "merged_m2_inflation.csv")
    print(f"  원본 shape: {df_m2.shape}")
    
    df_m2['Date'] = df_m2['Date'].apply(convert_date_to_datetime)
    df_m2 = df_m2.rename(columns={'Date': 'date'})
    
    print(f"  결측치 처리 전: M2SL={df_m2['M2SL'].isna().sum()}")
    
    # M2는 월별 데이터이므로 일별로 확장 (Forward Fill)
    # 날짜 범위 생성 (9월 1일 ~ 11월 1일)
    date_range = pd.date_range(start='2025-09-01', end='2025-11-01', freq='D')
    df_m2_expanded = pd.DataFrame({'date': date_range})
    
    # 기존 M2 데이터와 병합 (월 첫날 데이터만 있음)
    df_m2_expanded = df_m2_expanded.merge(df_m2, on='date', how='left')
    
    # Forward fill로 일별 확장
    df_m2_expanded['M2SL'] = df_m2_expanded['M2SL'].ffill()
    df_m2_expanded['CPI_YoY_Inflation_Rate'] = df_m2_expanded['CPI_YoY_Inflation_Rate'].ffill()
    
    print(f"  ✅ M2 데이터를 일별로 확장 (Forward Fill)")
    print(f"  확장 후 shape: {df_m2_expanded.shape}")
    print(f"  결측치 처리 후: M2SL={df_m2_expanded['M2SL'].isna().sum()}, CPI={df_m2_expanded['CPI_YoY_Inflation_Rate'].isna().sum()}")
    
    df_m2 = df_m2_expanded
    
    # ===== 6. SNS/YouTube Data =====
    print("\n[6/6] SNS/YouTube 데이터 처리 중...")
    df_sns = pd.read_csv(DATA_DIR / "SNS_Youtube_data" / "FINAL_SNS_YOUTUBE.csv")
    print(f"  원본 shape: {df_sns.shape}")
    
    df_sns['STD_DATE'] = df_sns['STD_DATE'].apply(convert_date_to_datetime)
    df_sns = df_sns.rename(columns={'STD_DATE': 'date'})
    df_sns['original_date'] = pd.to_datetime(df_sns['original_date'], utc=True, errors='coerce')
    
    print(f"  ✅ 날짜 컬럼 datetime 변환 완료")
    print(f"  결측치: url={df_sns['url'].isna().sum()}")
    
    # ===== 정제된 데이터 저장 =====
    print("\n" + "=" * 80)
    print("정제된 데이터 저장 중...")
    print("=" * 80)
    
    output_dir = Path("data/processed/cleaned")
    output_dir.mkdir(exist_ok=True)
    
    df_news.to_csv(output_dir / "bitcoin_news_cleaned.csv", index=False)
    print(f"  ✅ bitcoin_news_cleaned.csv 저장")
    
    df_features.to_csv(output_dir / "features_daily_cleaned.csv", index=False)
    print(f"  ✅ features_daily_cleaned.csv 저장")
    
    df_gdelt.to_csv(output_dir / "gdelt_articles_cleaned.csv", index=False)
    print(f"  ✅ gdelt_articles_cleaned.csv 저장")
    
    df_daily.to_csv(output_dir / "daily_data_cleaned.csv", index=False)
    print(f"  ✅ daily_data_cleaned.csv 저장")
    
    df_m2.to_csv(output_dir / "m2_inflation_daily_expanded.csv", index=False)
    print(f"  ✅ m2_inflation_daily_expanded.csv 저장")
    
    df_sns.to_csv(output_dir / "sns_youtube_cleaned.csv", index=False)
    print(f"  ✅ sns_youtube_cleaned.csv 저장")
    
    # ===== 최종 검증 =====
    print("\n" + "=" * 80)
    print("📊 최종 검증 결과")
    print("=" * 80)
    
    datasets = {
        'bitcoin_news': df_news,
        'features_daily': df_features,
        'gdelt_articles': df_gdelt,
        'daily_data': df_daily,
        'm2_inflation': df_m2,
        'sns_youtube': df_sns
    }
    
    for name, df in datasets.items():
        date_col = 'date'
        if date_col in df.columns:
            print(f"\n✅ {name}")
            print(f"   날짜 타입: {df[date_col].dtype}")
            print(f"   날짜 범위: {df[date_col].min()} ~ {df[date_col].max()}")
            print(f"   총 결측치: {df.isna().sum().sum()}개")
            print(f"   Shape: {df.shape}")
    
    print("\n" + "=" * 80)
    print("Task 2 완료! ✅")
    print("=" * 80)
    
    return datasets

if __name__ == "__main__":
    cleaned_data = clean_and_standardize_data()
    print(f"\n✅ 정제된 데이터셋이 data/processed/cleaned/ 디렉토리에 저장되었습니다.")
