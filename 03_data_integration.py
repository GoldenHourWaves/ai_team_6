"""
Task 3: 전체 데이터 통합 (Master DataFrame 생성)
날짜를 기준으로 모든 정제된 데이터를 하나의 DataFrame으로 병합
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 정제된 데이터 경로
CLEANED_DIR = Path("data/processed/cleaned")
OUTPUT_DIR = Path("data/processed/integrated")
OUTPUT_DIR.mkdir(exist_ok=True)

def aggregate_sns_daily(df_sns):
    """SNS/YouTube 데이터를 일별로 집계"""
    print("  📊 SNS/YouTube 데이터 일별 집계 중...")
    
    # 일별 집계
    daily_agg = df_sns.groupby('date').agg({
        'engagement': ['sum', 'mean', 'max'],
        'content': 'count',
        'platform': lambda x: (x == 'YouTube').sum(),  # YouTube 게시물 수
        'type': lambda x: (x == 'video').sum()  # 비디오 수
    }).reset_index()
    
    # 컬럼명 평탄화
    daily_agg.columns = [
        'date',
        'sns_engagement_total',
        'sns_engagement_mean',
        'sns_engagement_max',
        'sns_post_count',
        'sns_youtube_count',
        'sns_video_count'
    ]
    
    print(f"  ✅ SNS 데이터 집계 완료: {len(daily_agg)}일")
    return daily_agg

def integrate_all_data():
    """모든 정제된 데이터를 하나의 Master DataFrame으로 통합"""
    
    print("=" * 80)
    print("Task 3: 전체 데이터 통합 시작")
    print("=" * 80)
    
    # ===== 1. Features Daily 로드 (뉴스 테마 데이터) =====
    print("\n[1/4] Features Daily 데이터 로드 중...")
    df_features = pd.read_csv(CLEANED_DIR / "features_daily_cleaned.csv")
    df_features['date'] = pd.to_datetime(df_features['date'])
    print(f"  Shape: {df_features.shape}")
    print(f"  날짜 범위: {df_features['date'].min()} ~ {df_features['date'].max()}")
    
    # ===== 2. Daily Data 로드 (가격 + 거시경제 지표) =====
    print("\n[2/4] Daily Data 로드 중...")
    df_daily = pd.read_csv(CLEANED_DIR / "daily_data_cleaned.csv")
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    print(f"  Shape: {df_daily.shape}")
    print(f"  날짜 범위: {df_daily['date'].min()} ~ {df_daily['date'].max()}")
    
    # ===== 3. M2 & Inflation 로드 =====
    print("\n[3/4] M2 & Inflation 데이터 로드 중...")
    df_m2 = pd.read_csv(CLEANED_DIR / "m2_inflation_daily_expanded.csv")
    df_m2['date'] = pd.to_datetime(df_m2['date'])
    print(f"  Shape: {df_m2.shape}")
    print(f"  날짜 범위: {df_m2['date'].min()} ~ {df_m2['date'].max()}")
    
    # ===== 4. SNS/YouTube 로드 및 집계 =====
    print("\n[4/4] SNS/YouTube 데이터 로드 및 집계 중...")
    df_sns = pd.read_csv(CLEANED_DIR / "sns_youtube_cleaned.csv")
    df_sns['date'] = pd.to_datetime(df_sns['date'])
    print(f"  원본 Shape: {df_sns.shape}")
    print(f"  날짜 범위: {df_sns['date'].min()} ~ {df_sns['date'].max()}")
    
    df_sns_daily = aggregate_sns_daily(df_sns)
    
    # ===== 데이터 병합 =====
    print("\n" + "=" * 80)
    print("📦 데이터 병합 시작")
    print("=" * 80)
    
    # Step 1: Features + Daily Data
    print("\n[Step 1] Features + Daily Data 병합...")
    df_master = df_features.merge(df_daily, on='date', how='outer')
    print(f"  병합 후 Shape: {df_master.shape}")
    print(f"  결측치: {df_master.isna().sum().sum()}개")
    
    # Step 2: + M2 & Inflation
    print("\n[Step 2] + M2 & Inflation 병합...")
    df_master = df_master.merge(df_m2, on='date', how='left')
    print(f"  병합 후 Shape: {df_master.shape}")
    print(f"  결측치: {df_master.isna().sum().sum()}개")
    
    # Step 3: + SNS Daily
    print("\n[Step 3] + SNS Daily 병합...")
    df_master = df_master.merge(df_sns_daily, on='date', how='left')
    print(f"  병합 후 Shape: {df_master.shape}")
    print(f"  결측치: {df_master.isna().sum().sum()}개")
    
    # ===== 날짜 순 정렬 =====
    df_master = df_master.sort_values('date').reset_index(drop=True)
    
    # ===== SNS 결측치 처리 (데이터가 없는 날은 0으로) =====
    sns_cols = [col for col in df_master.columns if col.startswith('sns_')]
    for col in sns_cols:
        df_master[col] = df_master[col].fillna(0)
    
    print("\n" + "=" * 80)
    print("📊 통합 데이터 정보")
    print("=" * 80)
    
    print(f"\n✅ Master DataFrame 생성 완료!")
    print(f"   Shape: {df_master.shape}")
    print(f"   날짜 범위: {df_master['date'].min()} ~ {df_master['date'].max()}")
    print(f"   총 결측치: {df_master.isna().sum().sum()}개")
    
    # 컬럼 그룹별 정보
    print(f"\n📋 컬럼 그룹:")
    print(f"   - 날짜: 1개")
    print(f"   - 뉴스 메타: {len([c for c in df_master.columns if c.startswith('n_') or c.startswith('tone_')])}개")
    print(f"   - 뉴스 테마: {len([c for c in df_master.columns if c.startswith('theme_cnt_')])}개")
    print(f"   - 가격 데이터: {len([c for c in df_master.columns if 'Price' in c or 'Open_Interest' in c])}개")
    print(f"   - 거시경제: {len([c for c in df_master.columns if any(x in c for x in ['Yield', 'USD', 'M2', 'CPI'])])}개")
    print(f"   - SNS: {len(sns_cols)}개")
    
    # 결측치가 있는 컬럼 확인
    missing_cols = df_master.columns[df_master.isna().any()].tolist()
    if missing_cols:
        print(f"\n⚠️  결측치가 있는 컬럼 ({len(missing_cols)}개):")
        for col in missing_cols[:10]:  # 상위 10개만 표시
            missing_count = df_master[col].isna().sum()
            missing_pct = (missing_count / len(df_master)) * 100
            print(f"   - {col}: {missing_count}개 ({missing_pct:.2f}%)")
        if len(missing_cols) > 10:
            print(f"   ... 외 {len(missing_cols) - 10}개")
    
    # ===== 데이터 저장 =====
    print("\n" + "=" * 80)
    print("💾 데이터 저장 중...")
    print("=" * 80)
    
    # CSV 저장
    output_csv = OUTPUT_DIR / "master_data_integrated.csv"
    df_master.to_csv(output_csv, index=False)
    print(f"  ✅ {output_csv}")
    
    # 요약 통계 저장
    summary_file = OUTPUT_DIR / "master_data_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Master DataFrame 요약 통계\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Shape: {df_master.shape}\n")
        f.write(f"날짜 범위: {df_master['date'].min()} ~ {df_master['date'].max()}\n")
        f.write(f"총 결측치: {df_master.isna().sum().sum()}개\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("컬럼 목록\n")
        f.write("=" * 80 + "\n\n")
        for i, col in enumerate(df_master.columns, 1):
            dtype = df_master[col].dtype
            null_count = df_master[col].isna().sum()
            null_pct = (null_count / len(df_master)) * 100
            f.write(f"{i:3d}. {col:50s} | {str(dtype):20s} | 결측: {null_count:3d} ({null_pct:5.2f}%)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("수치형 컬럼 기본 통계\n")
        f.write("=" * 80 + "\n\n")
        f.write(df_master.describe().to_string())
    
    print(f"  ✅ {summary_file}")
    
    # 샘플 데이터 확인
    print("\n" + "=" * 80)
    print("🔍 데이터 샘플 (처음 5행)")
    print("=" * 80)
    
    # 주요 컬럼만 선택해서 출력
    key_cols = ['date', 'BTC_Price', 'tone_mean', 'Open_Interest', 
                'M2SL', 'CPI_YoY_Inflation_Rate', 'sns_post_count']
    available_cols = [col for col in key_cols if col in df_master.columns]
    print(df_master[available_cols].head().to_string(index=False))
    
    print("\n" + "=" * 80)
    print("Task 3 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 통합 데이터가 {output_csv}에 저장되었습니다.")
    
    return df_master

if __name__ == "__main__":
    master_df = integrate_all_data()
    
    print(f"\n✅ Master DataFrame이 메모리에 로드되었습니다.")
    print(f"   변수명: master_df")
    print(f"   Shape: {master_df.shape}")
