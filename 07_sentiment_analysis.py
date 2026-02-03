"""
Task 7: SNS/YouTube 감성 분석
커뮤니티 데이터에서 감성 점수 추출 및 BTC 가격과의 관계 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
COMMUNITY_DIR = Path("data/Community_data")
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 감성 매핑 (sentiment 컬럼의 텍스트를 점수로 변환)
SENTIMENT_MAP = {
    'Positive': 1.0,
    'Hopeful': 0.7,
    'Optimistic': 0.8,
    'Neutral': 0.0,
    'Skeptical': -0.3,
    'Skeptic': -0.3,
    'Fear': -0.8,
    'Panic': -0.9,
    'Negative': -1.0,
    'Bearish': -0.6,
    'Bullish': 0.6,
    'Worried': -0.5,
    'Anxious': -0.7,
    'Excited': 0.8,
    'FOMO': 0.5,
    'FUD': -0.7
}

def load_community_data():
    """커뮤니티 데이터 로드"""
    
    print("\n" + "=" * 80)
    print("📂 커뮤니티 데이터 로드")
    print("=" * 80)
    
    # FINAL_10K_RECORDS.csv 로드
    file_path = COMMUNITY_DIR / "FINAL_10K_RECORDS.csv"
    df = pd.read_csv(file_path)
    
    print(f"\n✅ 데이터 로드 완료: {df.shape}")
    print(f"   기간: {df['date_posted'].min()} ~ {df['date_posted'].max()}")
    print(f"\n📊 컬럼: {list(df.columns)}")
    
    # 날짜 변환
    df['date_posted'] = pd.to_datetime(df['date_posted'], utc=True, errors='coerce')
    df['date'] = df['date_posted'].dt.date
    
    # Sentiment 분포
    print(f"\n💬 Sentiment 분포:")
    sentiment_counts = df['sentiment'].value_counts()
    for sent, count in sentiment_counts.head(10).items():
        print(f"   {sent}: {count} ({count/len(df)*100:.1f}%)")
    
    return df

def analyze_sentiment_scores(df):
    """감성 점수 계산 및 분석"""
    
    print("\n" + "=" * 80)
    print("📊 감성 점수 분석")
    print("=" * 80)
    
    # Sentiment를 점수로 변환
    df['sentiment_score'] = df['sentiment'].map(SENTIMENT_MAP)
    
    # 매핑되지 않은 sentiment 처리
    unmapped = df[df['sentiment_score'].isna()]['sentiment'].unique()
    if len(unmapped) > 0:
        print(f"\n⚠️  매핑되지 않은 sentiment: {unmapped}")
        # 기본값 0으로 처리
        df['sentiment_score'].fillna(0, inplace=True)
    
    print(f"\n📈 감성 점수 통계:")
    print(f"   평균: {df['sentiment_score'].mean():.3f}")
    print(f"   중앙값: {df['sentiment_score'].median():.3f}")
    print(f"   표준편차: {df['sentiment_score'].std():.3f}")
    print(f"   최소: {df['sentiment_score'].min():.3f}")
    print(f"   최대: {df['sentiment_score'].max():.3f}")
    
    # 일별 집계
    daily_sentiment = df.groupby('date').agg({
        'sentiment_score': ['mean', 'median', 'std', 'count'],
        'engagement_score': 'mean',
        'relevance_score': 'mean'
    }).reset_index()
    
    daily_sentiment.columns = ['date', 'sentiment_mean', 'sentiment_median', 
                               'sentiment_std', 'post_count', 
                               'engagement_mean', 'relevance_mean']
    
    print(f"\n📅 일별 데이터: {len(daily_sentiment)}일")
    
    return df, daily_sentiment

def classify_sentiment_periods(daily_sentiment, price_df):
    """감성 구간 분류 (panic selling vs buying the dip)"""
    
    print("\n" + "=" * 80)
    print("🔍 감성 구간 분류")
    print("=" * 80)
    
    # 가격 데이터와 병합
    daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
    price_df['date'] = pd.to_datetime(price_df['date'])
    
    merged = pd.merge(daily_sentiment, price_df[['date', 'BTC_Price']], 
                     on='date', how='left')
    
    # 가격 변화율 계산
    merged['price_change_pct'] = merged['BTC_Price'].pct_change() * 100
    
    # 감성 구간 분류
    # Panic Selling: 매우 부정적 감성 (sentiment < -0.3)
    # Fear: 부정적 감성 (-0.3 <= sentiment < 0)
    # Neutral: 중립 (0 <= sentiment < 0.3)
    # Buying the Dip: 긍정적 감성 (sentiment >= 0.3)
    
    def classify_period(row):
        sent = row['sentiment_mean']
        if sent < -0.3:
            return 'Panic Selling'
        elif sent < 0:
            return 'Fear'
        elif sent < 0.3:
            return 'Neutral'
        else:
            return 'Buying the Dip'
    
    merged['period_type'] = merged.apply(classify_period, axis=1)
    
    print(f"\n📊 구간 분포:")
    period_counts = merged['period_type'].value_counts()
    for period, count in period_counts.items():
        avg_price_change = merged[merged['period_type'] == period]['price_change_pct'].mean()
        print(f"   {period}: {count}일 (평균 가격 변화: {avg_price_change:+.2f}%)")
    
    return merged

def plot_sentiment_timeseries(merged_df):
    """감성 시계열 시각화"""
    
    print("\n" + "=" * 80)
    print("📈 감성 시계열 시각화")
    print("=" * 80)
    
    fig, axes = plt.subplots(4, 1, figsize=(16, 16))
    fig.suptitle('SNS/YouTube 커뮤니티 감성 분석', fontsize=18, fontweight='bold', y=0.995)
    
    crash_date = pd.to_datetime('2025-10-10')
    
    # ===== 그래프 1: 감성 점수 + BTC 가격 =====
    ax1 = axes[0]
    
    # 감성 점수 (왼쪽 축)
    color1 = '#FF6B6B'
    ax1.set_xlabel('날짜', fontsize=11)
    ax1.set_ylabel('평균 감성 점수', color=color1, fontsize=11, fontweight='bold')
    ax1.plot(merged_df['date'], merged_df['sentiment_mean'], 
            color=color1, linewidth=2.5, marker='o', markersize=4, label='평균 감성')
    ax1.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.fill_between(merged_df['date'], 0, merged_df['sentiment_mean'], 
                     where=(merged_df['sentiment_mean'] >= 0), alpha=0.3, 
                     color='green', label='긍정 구간')
    ax1.fill_between(merged_df['date'], 0, merged_df['sentiment_mean'], 
                     where=(merged_df['sentiment_mean'] < 0), alpha=0.3, 
                     color='red', label='부정 구간')
    
    # BTC 가격 (오른쪽 축)
    ax2 = ax1.twinx()
    color2 = '#4ECDC4'
    ax2.set_ylabel('BTC 가격 (USD)', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(merged_df['date'], merged_df['BTC_Price'], 
            color=color2, linewidth=2, alpha=0.7, label='BTC Price')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 10월 10일 마킹
    ax1.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    ax1.set_title('커뮤니티 감성 vs 비트코인 가격', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    
    # ===== 그래프 2: 감성 구간 색상 코딩 =====
    ax3 = axes[1]
    
    period_colors = {
        'Panic Selling': '#8B0000',
        'Fear': '#FF6347',
        'Neutral': '#FFD700',
        'Buying the Dip': '#32CD32'
    }
    
    for period, color in period_colors.items():
        period_data = merged_df[merged_df['period_type'] == period]
        if len(period_data) > 0:
            ax3.scatter(period_data['date'], period_data['sentiment_mean'], 
                       c=color, label=period, s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    ax3.plot(merged_df['date'], merged_df['sentiment_mean'], 
            color='gray', linewidth=1.5, alpha=0.5, zorder=0)
    ax3.axhline(0, color='black', linestyle='-', linewidth=1)
    ax3.axhline(0.3, color='green', linestyle='--', linewidth=1, alpha=0.5, label='긍정 임계값')
    ax3.axhline(-0.3, color='red', linestyle='--', linewidth=1, alpha=0.5, label='공포 임계값')
    ax3.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    ax3.set_xlabel('날짜', fontsize=11)
    ax3.set_ylabel('평균 감성 점수', fontsize=11, fontweight='bold')
    ax3.set_title('감성 구간 분류 (Panic Selling vs Buying the Dip)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=9, ncol=2)
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # ===== 그래프 3: 포스트 수와 감성의 관계 =====
    ax4 = axes[2]
    
    # 포스트 수 (왼쪽 축)
    color1 = '#9B59B6'
    ax4.set_xlabel('날짜', fontsize=11)
    ax4.set_ylabel('일별 포스트 수', color=color1, fontsize=11, fontweight='bold')
    ax4.bar(merged_df['date'], merged_df['post_count'], 
           color=color1, alpha=0.6, label='포스트 수', width=0.8)
    ax4.tick_params(axis='y', labelcolor=color1)
    
    # 감성 점수 (오른쪽 축)
    ax5 = ax4.twinx()
    color2 = '#E74C3C'
    ax5.set_ylabel('평균 감성 점수', color=color2, fontsize=11, fontweight='bold')
    ax5.plot(merged_df['date'], merged_df['sentiment_mean'], 
            color=color2, linewidth=2.5, marker='o', markersize=4, label='평균 감성')
    ax5.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax5.tick_params(axis='y', labelcolor=color2)
    
    ax4.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    ax4.set_title('포스트 활동량 vs 감성 점수', fontsize=13, fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax4.legend(loc='upper left', fontsize=9)
    ax5.legend(loc='upper right', fontsize=9)
    
    # ===== 그래프 4: 가격 변화율 vs 감성 점수 산점도 =====
    ax6 = axes[3]
    
    scatter = ax6.scatter(merged_df['sentiment_mean'], merged_df['price_change_pct'], 
                         c=merged_df['post_count'], cmap='plasma', 
                         s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # 회귀선
    mask = ~(merged_df['sentiment_mean'].isna() | merged_df['price_change_pct'].isna())
    if mask.sum() > 1:
        x = merged_df.loc[mask, 'sentiment_mean']
        y = merged_df.loc[mask, 'price_change_pct']
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line_x = np.array([x.min(), x.max()])
        line_y = slope * line_x + intercept
        ax6.plot(line_x, line_y, 'r--', linewidth=2, 
                label=f'회귀선 (r={r_value:.3f}, p={p_value:.3f})')
        
        print(f"\n📈 감성-가격 변화 상관관계:")
        print(f"   상관계수: {r_value:.4f}")
        print(f"   p-value: {p_value:.4f} {'(유의함)' if p_value < 0.05 else '(유의하지 않음)'}")
        print(f"   기울기: {slope:.4f}")
    
    ax6.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax6.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax6.set_xlabel('평균 감성 점수', fontsize=11, fontweight='bold')
    ax6.set_ylabel('가격 변화율 (%)', fontsize=11, fontweight='bold')
    ax6.set_title('감성 점수 vs 가격 변화율 (산점도)', fontsize=13, fontweight='bold', pad=10)
    ax6.legend(loc='best', fontsize=9)
    ax6.grid(True, alpha=0.3, linestyle='--')
    
    # 컬러바
    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('포스트 수', fontsize=10)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "08_sentiment_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()

def analyze_keyword_sentiment(df):
    """키워드별 감성 분석"""
    
    print("\n" + "=" * 80)
    print("🔑 키워드별 감성 분석")
    print("=" * 80)
    
    # 키워드 추출 및 감성 집계
    keyword_sentiment = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['keywords']):
            keywords = [k.strip() for k in str(row['keywords']).split(',')]
            for keyword in keywords:
                keyword_sentiment.append({
                    'keyword': keyword,
                    'sentiment_score': row['sentiment_score'],
                    'engagement': row['engagement_score']
                })
    
    keyword_df = pd.DataFrame(keyword_sentiment)
    
    # 키워드별 평균 감성 계산
    keyword_summary = keyword_df.groupby('keyword').agg({
        'sentiment_score': ['mean', 'count'],
        'engagement': 'mean'
    }).reset_index()
    
    keyword_summary.columns = ['keyword', 'avg_sentiment', 'count', 'avg_engagement']
    keyword_summary = keyword_summary[keyword_summary['count'] >= 10]  # 최소 10회 이상 등장
    keyword_summary = keyword_summary.sort_values('count', ascending=False)
    
    print(f"\n📊 Top 20 키워드 (최소 10회 이상):")
    print("-" * 80)
    
    top_keywords = keyword_summary.head(20)
    for idx, row in top_keywords.iterrows():
        sentiment_label = "😊" if row['avg_sentiment'] > 0.2 else "😟" if row['avg_sentiment'] < -0.2 else "😐"
        print(f"  {sentiment_label} {row['keyword']:25s} | 감성: {row['avg_sentiment']:+.3f} | 언급: {row['count']:4.0f}회")
    
    # 가장 긍정적/부정적 키워드
    print(f"\n🟢 가장 긍정적 키워드 (Top 5):")
    most_positive = keyword_summary.nlargest(5, 'avg_sentiment')
    for idx, row in most_positive.iterrows():
        print(f"   {row['keyword']:25s} | 감성: {row['avg_sentiment']:+.3f} | 언급: {row['count']:4.0f}회")
    
    print(f"\n🔴 가장 부정적 키워드 (Top 5):")
    most_negative = keyword_summary.nsmallest(5, 'avg_sentiment')
    for idx, row in most_negative.iterrows():
        print(f"   {row['keyword']:25s} | 감성: {row['avg_sentiment']:+.3f} | 언급: {row['count']:4.0f}회")
    
    # 키워드 감성 막대 그래프
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_20 = keyword_summary.head(20).sort_values('avg_sentiment')
    colors = ['red' if s < 0 else 'green' for s in top_20['avg_sentiment']]
    
    ax.barh(range(len(top_20)), top_20['avg_sentiment'], color=colors, alpha=0.7, edgecolor='black')
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels(top_20['keyword'], fontsize=10)
    ax.set_xlabel('평균 감성 점수', fontsize=12, fontweight='bold')
    ax.set_title('Top 20 키워드별 평균 감성 점수', fontsize=14, fontweight='bold', pad=15)
    ax.axvline(0, color='black', linewidth=2)
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "09_keyword_sentiment.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 키워드 감성 그래프 저장: {output_file}")
    
    plt.show()
    
    return keyword_summary

def main():
    print("=" * 80)
    print("Task 7: SNS/YouTube 감성 분석")
    print("=" * 80)
    
    # 1. 커뮤니티 데이터 로드
    community_df = load_community_data()
    
    # 2. 감성 점수 계산
    community_df, daily_sentiment = analyze_sentiment_scores(community_df)
    
    # 3. 가격 데이터 로드
    print("\n📂 가격 데이터 로드 중...")
    price_df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    price_df['date'] = pd.to_datetime(price_df['date'])
    print(f"✅ 가격 데이터 로드 완료: {price_df.shape}")
    
    # 4. 감성 구간 분류
    merged_df = classify_sentiment_periods(daily_sentiment, price_df)
    
    # 5. 감성 시계열 시각화
    plot_sentiment_timeseries(merged_df)
    
    # 6. 키워드별 감성 분석
    keyword_summary = analyze_keyword_sentiment(community_df)
    
    # 7. 결과 저장
    merged_df.to_csv(OUTPUT_DIR / "sentiment_daily_analysis.csv", index=False, encoding='utf-8-sig')
    keyword_summary.to_csv(OUTPUT_DIR / "keyword_sentiment_summary.csv", index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 7 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '08_sentiment_analysis.png'}")
    print(f"   2. {OUTPUT_DIR / '09_keyword_sentiment.png'}")
    print(f"   3. {OUTPUT_DIR / 'sentiment_daily_analysis.csv'}")
    print(f"   4. {OUTPUT_DIR / 'keyword_sentiment_summary.csv'}")

if __name__ == "__main__":
    main()
