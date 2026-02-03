"""
Task 5: 상관관계 히트맵 생성
모든 수치형 변수 간의 피어슨 상관계수를 계산하고 히트맵으로 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_correlation_heatmap_full(df):
    """전체 변수 상관관계 히트맵"""
    
    print("\n" + "=" * 80)
    print("🔥 전체 변수 상관관계 히트맵 생성")
    print("=" * 80)
    
    # 수치형 컬럼만 선택 (date 제외)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"\n📊 수치형 변수: {len(numeric_cols)}개")
    
    # 상관계수 계산
    corr_matrix = df[numeric_cols].corr()
    
    # 히트맵 생성
    fig, ax = plt.subplots(figsize=(20, 18))
    
    # 마스크 생성 (대각선 위쪽만 표시)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    # 히트맵 그리기
    sns.heatmap(corr_matrix, 
                mask=mask,
                annot=False,  # 숫자가 너무 많아서 생략
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                vmin=-1,
                vmax=1,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8, "label": "상관계수"},
                ax=ax)
    
    plt.title('전체 변수 간 상관관계 히트맵\n(피어슨 상관계수)', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "03_correlation_heatmap_full.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 전체 히트맵 저장: {output_file}")
    
    plt.show()
    
    return corr_matrix

def create_correlation_heatmap_key_vars(df):
    """주요 변수 상관관계 히트맵 (가독성 향상)"""
    
    print("\n" + "=" * 80)
    print("🎯 주요 변수 상관관계 히트맵 생성")
    print("=" * 80)
    
    # 주요 변수 선택
    key_vars = [
        'BTC_Price',
        'Open_Interest',
        'tone_mean',
        'tone_neg_share',
        'tone_pos_share',
        'n_articles',
        'Yield_10Y',
        'Gold_Price_YF',
        'USD_Index',
        'M2SL',
        'CPI_YoY_Inflation_Rate',
        'sns_post_count',
        'sns_engagement_total',
        'theme_cnt__EPU_POLICY',
        'theme_cnt__LEADER',
        'theme_cnt__GENERAL_GOVERNMENT',
        'theme_cnt__ECON_BITCOIN'
    ]
    
    # 데이터프레임에 존재하는 변수만 선택
    available_vars = [v for v in key_vars if v in df.columns]
    print(f"\n📌 선택된 변수: {len(available_vars)}개")
    for var in available_vars:
        print(f"   - {var}")
    
    # 상관계수 계산
    corr_matrix = df[available_vars].corr()
    
    # 히트맵 생성
    fig, ax = plt.subplots(figsize=(14, 12))
    
    sns.heatmap(corr_matrix,
                annot=True,  # 숫자 표시
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                vmin=-1,
                vmax=1,
                square=True,
                linewidths=1,
                cbar_kws={"shrink": 0.9, "label": "상관계수"},
                ax=ax,
                annot_kws={'size': 9})
    
    plt.title('주요 변수 간 상관관계 히트맵\n(비트코인 가격, 뉴스 톤, 거시경제 지표, SNS 활동)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "04_correlation_heatmap_key_vars.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 주요 변수 히트맵 저장: {output_file}")
    
    plt.show()
    
    return corr_matrix

def find_high_correlations(corr_matrix, threshold=0.7):
    """높은 상관관계를 가진 변수 쌍 찾기"""
    
    print("\n" + "=" * 80)
    print(f"🔍 높은 상관관계 변수 쌍 탐색 (|r| > {threshold})")
    print("=" * 80)
    
    # 상관관계 쌍 추출
    high_corr_pairs = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > threshold:
                high_corr_pairs.append({
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'correlation': corr_val
                })
    
    if high_corr_pairs:
        # 데이터프레임으로 변환 및 정렬
        df_high_corr = pd.DataFrame(high_corr_pairs)
        df_high_corr = df_high_corr.sort_values('correlation', key=abs, ascending=False)
        
        print(f"\n✅ 발견된 높은 상관관계: {len(df_high_corr)}쌍\n")
        print(df_high_corr.to_string(index=False))
        
        # CSV로 저장
        output_csv = OUTPUT_DIR / "high_correlations.csv"
        df_high_corr.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\n✅ 높은 상관관계 목록 저장: {output_csv}")
        
        return df_high_corr
    else:
        print(f"\n⚠️  임계값({threshold})을 넘는 상관관계가 발견되지 않았습니다.")
        return None

def create_btc_correlation_bar_chart(df):
    """비트코인 가격과 다른 변수들의 상관관계 막대 그래프"""
    
    print("\n" + "=" * 80)
    print("📊 BTC 가격 상관관계 막대 그래프 생성")
    print("=" * 80)
    
    # BTC_Price와 다른 변수들의 상관계수 계산
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col != 'BTC_Price']
    
    correlations = df[numeric_cols + ['BTC_Price']].corr()['BTC_Price'].drop('BTC_Price')
    correlations = correlations.sort_values(key=abs, ascending=True)
    
    # 상위 20개만 선택
    top_corr = correlations.tail(20)
    
    # 막대 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = ['red' if x < 0 else 'green' for x in top_corr.values]
    top_corr.plot(kind='barh', color=colors, alpha=0.7, ax=ax)
    
    ax.set_xlabel('상관계수', fontsize=12, fontweight='bold')
    ax.set_ylabel('변수', fontsize=12, fontweight='bold')
    ax.set_title('비트코인 가격과 다른 변수들의 상관관계\n(상위 20개)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.axvline(0, color='black', linewidth=1, linestyle='-')
    ax.grid(True, alpha=0.3, axis='x')
    
    # 값 레이블 추가
    for i, v in enumerate(top_corr.values):
        ax.text(v, i, f' {v:.3f}', va='center', fontsize=9)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "05_btc_correlation_bar.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 막대 그래프 저장: {output_file}")
    
    plt.show()
    
    print(f"\n🏆 BTC 가격과 가장 높은 상관관계를 보이는 변수:")
    print(f"   1. {correlations.abs().idxmax()}: {correlations.abs().max():.3f}")
    print(f"\n📉 BTC 가격과 가장 낮은 상관관계를 보이는 변수:")
    print(f"   1. {correlations.idxmin()}: {correlations.min():.3f}")

def main():
    print("=" * 80)
    print("Task 5: 상관관계 히트맵 생성")
    print("=" * 80)
    
    # 데이터 로드
    print("\n📂 데이터 로드 중...")
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    print(f"✅ 데이터 로드 완료: {df.shape}")
    
    # 1. 전체 변수 히트맵
    corr_full = create_correlation_heatmap_full(df)
    
    # 2. 주요 변수 히트맵
    corr_key = create_correlation_heatmap_key_vars(df)
    
    # 3. 높은 상관관계 쌍 찾기
    high_corr_df = find_high_correlations(corr_key, threshold=0.7)
    
    # 4. BTC 가격 상관관계 막대 그래프
    create_btc_correlation_bar_chart(df)
    
    print("\n" + "=" * 80)
    print("Task 5 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 시각화:")
    print(f"   1. {OUTPUT_DIR / '03_correlation_heatmap_full.png'}")
    print(f"   2. {OUTPUT_DIR / '04_correlation_heatmap_key_vars.png'}")
    print(f"   3. {OUTPUT_DIR / '05_btc_correlation_bar.png'}")
    if high_corr_df is not None:
        print(f"   4. {OUTPUT_DIR / 'high_correlations.csv'}")

if __name__ == "__main__":
    main()
