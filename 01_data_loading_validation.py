"""
Task 1: 데이터 로딩 및 초기 검증
모든 CSV 파일을 읽고 데이터 구조 확인
"""

import pandas as pd
import os
from pathlib import Path

# 데이터 경로 설정
DATA_DIR = Path("data/processed")

# 로드할 CSV 파일 목록
csv_files = {
    "bitcoin_news": DATA_DIR / "bitcoin_news_merged_0.csv",
    "features_daily": DATA_DIR / "features_daily.csv",
    "gdelt_articles": DATA_DIR / "gdelt_articles_modified_0.csv",
    "daily_data": DATA_DIR / "merged_정형데이터" / "daily_data_merged.csv",
    "m2_inflation": DATA_DIR / "merged_정형데이터" / "merged_m2_inflation.csv",
    "sns_youtube": DATA_DIR / "SNS_Youtube_data" / "FINAL_SNS_YOUTUBE.csv"
}

def load_and_inspect_data():
    """모든 CSV 파일을 로드하고 기본 정보 출력"""
    
    data_dict = {}
    
    print("=" * 80)
    print("데이터 로딩 및 초기 검증 시작")
    print("=" * 80)
    
    for name, filepath in csv_files.items():
        print(f"\n{'='*80}")
        print(f"📁 {name.upper()}")
        print(f"파일 경로: {filepath}")
        print(f"{'='*80}")
        
        if not filepath.exists():
            print(f"⚠️  파일이 존재하지 않습니다: {filepath}")
            continue
        
        try:
            # CSV 파일 로드
            df = pd.read_csv(filepath)
            data_dict[name] = df
            
            # 기본 정보 출력
            print(f"\n✅ 로드 성공!")
            print(f"📊 행 수: {len(df):,}")
            print(f"📊 열 수: {len(df.columns):,}")
            print(f"📊 파일 크기: {filepath.stat().st_size / 1024:.2f} KB")
            
            # 컬럼 정보
            print(f"\n📋 컬럼 목록 (총 {len(df.columns)}개):")
            for i, col in enumerate(df.columns, 1):
                dtype = df[col].dtype
                null_count = df[col].isnull().sum()
                null_pct = (null_count / len(df)) * 100
                print(f"  {i:2d}. {col:40s} | {str(dtype):10s} | 결측치: {null_count:5d} ({null_pct:5.2f}%)")
            
            # 날짜 컬럼 확인
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                print(f"\n📅 날짜 관련 컬럼: {date_cols}")
                for col in date_cols:
                    print(f"  - {col}: {df[col].dtype}")
                    print(f"    샘플: {df[col].head(3).tolist()}")
            
            # 데이터 샘플 (처음 3행)
            print(f"\n🔍 데이터 샘플 (처음 3행):")
            print(df.head(3).to_string())
            
            # 기본 통계
            if len(df.select_dtypes(include=['number']).columns) > 0:
                print(f"\n📈 수치형 컬럼 기본 통계:")
                print(df.describe().to_string())
            
        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")
            continue
    
    # 전체 요약
    print(f"\n\n{'='*80}")
    print("📊 전체 데이터 요약")
    print(f"{'='*80}")
    print(f"✅ 로드 성공한 파일 수: {len(data_dict)}/{len(csv_files)}")
    
    total_rows = sum(len(df) for df in data_dict.values())
    total_cols = sum(len(df.columns) for df in data_dict.values())
    print(f"📊 총 행 수: {total_rows:,}")
    print(f"📊 총 컬럼 수: {total_cols:,}")
    
    print(f"\n{'='*80}")
    print("데이터 로딩 검증 완료 ✅")
    print(f"{'='*80}\n")
    
    return data_dict

if __name__ == "__main__":
    loaded_data = load_and_inspect_data()
    
    # 데이터를 반환하여 다음 작업에서 사용 가능
    print(f"\n✅ {len(loaded_data)}개의 데이터셋이 메모리에 로드되었습니다.")
    print(f"   사용 가능한 데이터셋: {list(loaded_data.keys())}")
