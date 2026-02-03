"""
Task 10: Open Interest 및 고래 행동 분석
미결제약정(Open Interest) 급증 시점과 가격 변동성 관계 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_and_analyze_oi_data(df):
    """Open Interest 데이터 로드 및 기초 분석"""
    
    print("\n" + "=" * 80)
    print("📊 Open Interest 데이터 분석")
    print("=" * 80)
    
    # Open_Interest 컬럼 확인
    if 'Open_Interest' not in df.columns:
        print("\n⚠️  Open_Interest 컬럼이 없습니다.")
        return None
    
    print(f"\n📈 Open Interest 통계:")
    print(f"   평균: {df['Open_Interest'].mean():,.2f}")
    print(f"   중앙값: {df['Open_Interest'].median():,.2f}")
    print(f"   표준편차: {df['Open_Interest'].std():,.2f}")
    print(f"   최소: {df['Open_Interest'].min():,.2f}")
    print(f"   최대: {df['Open_Interest'].max():,.2f}")
    print(f"   범위: {df['Open_Interest'].max() - df['Open_Interest'].min():,.2f}")
    
    # OI 변화율 계산
    df['OI_change_pct'] = df['Open_Interest'].pct_change() * 100
    df['OI_change_abs'] = df['Open_Interest'].diff()
    
    # 가격 변화율 계산
    df['price_change_pct'] = df['BTC_Price'].pct_change() * 100
    df['price_volatility'] = df['price_change_pct'].abs()
    
    print(f"\n📊 OI 변화율 통계:")
    print(f"   평균: {df['OI_change_pct'].mean():+.2f}%")
    print(f"   표준편차: {df['OI_change_pct'].std():.2f}%")
    print(f"   최소: {df['OI_change_pct'].min():+.2f}%")
    print(f"   최대: {df['OI_change_pct'].max():+.2f}%")
    
    return df

def detect_oi_spikes(df):
    """OI 급증/급감 시점 탐지"""
    
    print("\n" + "=" * 80)
    print("🔍 Open Interest 급증/급감 탐지")
    print("=" * 80)
    
    # Z-score 기반 이상치 탐지
    oi_change = df['OI_change_pct'].dropna()
    mean = oi_change.mean()
    std = oi_change.std()
    
    # 임계값: 평균 ± 2 표준편차
    upper_threshold = mean + 2 * std
    lower_threshold = mean - 2 * std
    
    print(f"\n📊 이상치 임계값:")
    print(f"   평균: {mean:+.2f}%")
    print(f"   표준편차: {std:.2f}%")
    print(f"   상한 (급증): {upper_threshold:+.2f}%")
    print(f"   하한 (급감): {lower_threshold:+.2f}%")
    
    # 급증/급감 시점
    df['OI_spike_up'] = df['OI_change_pct'] > upper_threshold
    df['OI_spike_down'] = df['OI_change_pct'] < lower_threshold
    df['OI_anomaly'] = df['OI_spike_up'] | df['OI_spike_down']
    
    spikes_up = df[df['OI_spike_up']]
    spikes_down = df[df['OI_spike_down']]
    
    print(f"\n🔥 OI 급증 발생: {len(spikes_up)}회")
    if len(spikes_up) > 0:
        print("   날짜 | OI 변화 | 가격 변화 | BTC 가격")
        print("-" * 80)
        for idx, row in spikes_up.iterrows():
            date = row['date'].date()
            oi_change = row['OI_change_pct']
            price_change = row.get('price_change_pct', np.nan)
            btc_price = row['BTC_Price']
            print(f"   {date} | OI: {oi_change:+6.2f}% | 가격: {price_change:+6.2f}% | ${btc_price:,.0f}")
    
    print(f"\n📉 OI 급감 발생: {len(spikes_down)}회")
    if len(spikes_down) > 0:
        print("   날짜 | OI 변화 | 가격 변화 | BTC 가격")
        print("-" * 80)
        for idx, row in spikes_down.iterrows():
            date = row['date'].date()
            oi_change = row['OI_change_pct']
            price_change = row.get('price_change_pct', np.nan)
            btc_price = row['BTC_Price']
            print(f"   {date} | OI: {oi_change:+6.2f}% | 가격: {price_change:+6.2f}% | ${btc_price:,.0f}")
    
    return df

def analyze_oi_price_correlation(df):
    """OI와 가격 변동의 상관관계 분석"""
    
    print("\n" + "=" * 80)
    print("📊 OI-가격 상관관계 분석")
    print("=" * 80)
    
    # 결측치 제거
    analysis_df = df[['Open_Interest', 'BTC_Price', 'OI_change_pct', 
                      'price_change_pct', 'price_volatility']].dropna()
    
    if len(analysis_df) < 3:
        print("\n⚠️  분석할 데이터가 부족합니다.")
        return
    
    # 상관계수 계산
    correlations = []
    
    # 1. OI vs 가격
    corr1, p1 = stats.pearsonr(analysis_df['Open_Interest'], analysis_df['BTC_Price'])
    correlations.append(('Open_Interest vs BTC_Price', corr1, p1))
    
    # 2. OI 변화율 vs 가격 변화율
    corr2, p2 = stats.pearsonr(analysis_df['OI_change_pct'], analysis_df['price_change_pct'])
    correlations.append(('OI_change vs Price_change', corr2, p2))
    
    # 3. OI vs 가격 변동성
    corr3, p3 = stats.pearsonr(analysis_df['Open_Interest'], analysis_df['price_volatility'])
    correlations.append(('Open_Interest vs Price_Volatility', corr3, p3))
    
    # 4. OI 변화율 vs 가격 변동성
    corr4, p4 = stats.pearsonr(analysis_df['OI_change_pct'].abs(), analysis_df['price_volatility'])
    correlations.append(('OI_change (abs) vs Price_Volatility', corr4, p4))
    
    print("\n📈 상관관계 분석 결과:")
    print("-" * 80)
    for name, corr, pval in correlations:
        sig = "✅ 유의함" if pval < 0.05 else "⚠️  유의하지 않음"
        print(f"   {name:40s} | r={corr:+.4f} | p={pval:.4f} {sig}")

def analyze_crash_period_oi(df):
    """급락 시점 전후 OI 분석"""
    
    print("\n" + "=" * 80)
    print("📉 급락 시점(10/10) 전후 OI 분석")
    print("=" * 80)
    
    crash_date = pd.to_datetime('2025-10-10')
    
    # 급락 전후 7일
    window = 7
    pre_crash = df[(df['date'] >= crash_date - pd.Timedelta(days=window)) & 
                   (df['date'] < crash_date)]
    post_crash = df[(df['date'] >= crash_date) & 
                    (df['date'] <= crash_date + pd.Timedelta(days=window))]
    
    if len(pre_crash) > 0:
        print(f"\n🔹 급락 전 {window}일:")
        print(f"   평균 OI: {pre_crash['Open_Interest'].mean():,.2f}")
        print(f"   평균 OI 변화율: {pre_crash['OI_change_pct'].mean():+.2f}%")
        print(f"   평균 가격 변화율: {pre_crash['price_change_pct'].mean():+.2f}%")
    
    if len(post_crash) > 0:
        print(f"\n🔹 급락 후 {window}일:")
        print(f"   평균 OI: {post_crash['Open_Interest'].mean():,.2f}")
        print(f"   평균 OI 변화율: {post_crash['OI_change_pct'].mean():+.2f}%")
        print(f"   평균 가격 변화율: {post_crash['price_change_pct'].mean():+.2f}%")
    
    # 급락 당일
    crash_day = df[df['date'] == crash_date]
    if len(crash_day) > 0:
        row = crash_day.iloc[0]
        print(f"\n🔴 급락 당일 (2025-10-10):")
        print(f"   OI: {row['Open_Interest']:,.2f}")
        print(f"   OI 변화율: {row['OI_change_pct']:+.2f}%")
        print(f"   가격 변화율: {row['price_change_pct']:+.2f}%")
        print(f"   BTC 가격: ${row['BTC_Price']:,.2f}")

def plot_oi_analysis(df):
    """OI 분석 시각화"""
    
    print("\n" + "=" * 80)
    print("📈 Open Interest 시각화")
    print("=" * 80)
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle('Open Interest 및 고래 행동 패턴 분석', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    crash_date = pd.to_datetime('2025-10-10')
    
    # ===== 그래프 1: OI와 BTC 가격 시계열 =====
    ax1 = axes[0, 0]
    
    # OI (왼쪽 축)
    color1 = '#FF6B6B'
    ax1.set_xlabel('날짜', fontsize=11)
    ax1.set_ylabel('Open Interest', color=color1, fontsize=11, fontweight='bold')
    ax1.plot(df['date'], df['Open_Interest'], color=color1, linewidth=2.5, 
            marker='o', markersize=4, label='Open Interest')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # 가격 (오른쪽 축)
    ax2 = ax1.twinx()
    color2 = '#4ECDC4'
    ax2.set_ylabel('BTC 가격 (USD)', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(df['date'], df['BTC_Price'], color=color2, linewidth=2, 
            alpha=0.7, label='BTC Price')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 급락일 마킹
    ax1.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    ax1.set_title('Open Interest vs BTC 가격', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    
    # ===== 그래프 2: OI 변화율 =====
    ax3 = axes[0, 1]
    
    colors_oi = ['red' if x < 0 else 'green' for x in df['OI_change_pct'].fillna(0)]
    ax3.bar(df['date'], df['OI_change_pct'], color=colors_oi, alpha=0.7, 
           edgecolor='black', linewidth=0.5, width=0.8)
    ax3.axhline(0, color='black', linewidth=1)
    ax3.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    # 임계값 선
    if 'OI_change_pct' in df.columns:
        mean = df['OI_change_pct'].mean()
        std = df['OI_change_pct'].std()
        ax3.axhline(mean + 2*std, color='red', linestyle='--', linewidth=1.5, 
                   alpha=0.7, label='급증 임계값')
        ax3.axhline(mean - 2*std, color='blue', linestyle='--', linewidth=1.5, 
                   alpha=0.7, label='급감 임계값')
    
    ax3.set_xlabel('날짜', fontsize=11)
    ax3.set_ylabel('OI 변화율 (%)', fontsize=11, fontweight='bold')
    ax3.set_title('Open Interest 변화율', fontsize=13, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # ===== 그래프 3: OI vs 가격 산점도 =====
    ax4 = axes[1, 0]
    
    scatter = ax4.scatter(df['Open_Interest'], df['BTC_Price'], 
                         c=df['date'].astype('int64'), cmap='viridis',
                         alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
    
    # 회귀선
    mask = ~(df['Open_Interest'].isna() | df['BTC_Price'].isna())
    if mask.sum() > 1:
        X = df.loc[mask, 'Open_Interest'].values
        y = df.loc[mask, 'BTC_Price'].values
        z = np.polyfit(X, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(X.min(), X.max(), 100)
        ax4.plot(x_line, p(x_line), 'r--', linewidth=2, 
                label=f'회귀선 (기울기: {z[0]:.2f})')
        
        corr, pval = stats.pearsonr(X, y)
        ax4.text(0.05, 0.95, f'r = {corr:.4f}\np = {pval:.4f}', 
                transform=ax4.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    ax4.set_xlabel('Open Interest', fontsize=11, fontweight='bold')
    ax4.set_ylabel('BTC 가격 (USD)', fontsize=11, fontweight='bold')
    ax4.set_title('OI vs BTC 가격 (산점도)', fontsize=13, fontweight='bold', pad=10)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--')
    
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('날짜', fontsize=9)
    
    # ===== 그래프 4: OI 변화율 vs 가격 변화율 =====
    ax5 = axes[1, 1]
    
    mask = ~(df['OI_change_pct'].isna() | df['price_change_pct'].isna())
    plot_df = df[mask]
    
    if len(plot_df) > 0:
        # 이상치 표시
        normal = plot_df[~plot_df['OI_anomaly']]
        anomaly = plot_df[plot_df['OI_anomaly']]
        
        ax5.scatter(normal['OI_change_pct'], normal['price_change_pct'], 
                   alpha=0.6, s=80, c='steelblue', edgecolors='black', linewidth=0.5,
                   label='정상')
        
        if len(anomaly) > 0:
            ax5.scatter(anomaly['OI_change_pct'], anomaly['price_change_pct'], 
                       alpha=0.8, s=150, c='red', marker='*', edgecolors='darkred', 
                       linewidth=1, label='OI 이상치')
        
        # 회귀선
        if len(plot_df) > 1:
            X = plot_df['OI_change_pct'].values
            y = plot_df['price_change_pct'].values
            z = np.polyfit(X, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(X.min(), X.max(), 100)
            ax5.plot(x_line, p(x_line), 'g--', linewidth=2, alpha=0.7,
                    label=f'회귀선')
    
    ax5.axhline(0, color='black', linewidth=1, alpha=0.5)
    ax5.axvline(0, color='black', linewidth=1, alpha=0.5)
    ax5.set_xlabel('OI 변화율 (%)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('가격 변화율 (%)', fontsize=11, fontweight='bold')
    ax5.set_title('OI 변화 vs 가격 변화', fontsize=13, fontweight='bold', pad=10)
    ax5.legend(loc='best', fontsize=9)
    ax5.grid(True, alpha=0.3, linestyle='--')
    
    # ===== 그래프 5: OI vs 가격 변동성 =====
    ax6 = axes[2, 0]
    
    mask = ~(df['Open_Interest'].isna() | df['price_volatility'].isna())
    plot_df = df[mask]
    
    if len(plot_df) > 0:
        scatter = ax6.scatter(plot_df['Open_Interest'], plot_df['price_volatility'], 
                            c=plot_df['date'].astype('int64'), cmap='plasma',
                            alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
        
        # 회귀선
        if len(plot_df) > 1:
            X = plot_df['Open_Interest'].values
            y = plot_df['price_volatility'].values
            z = np.polyfit(X, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(X.min(), X.max(), 100)
            ax6.plot(x_line, p(x_line), 'r--', linewidth=2)
            
            corr, pval = stats.pearsonr(X, y)
            ax6.text(0.05, 0.95, f'r = {corr:.4f}\np = {pval:.4f}', 
                    transform=ax6.transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    ax6.set_xlabel('Open Interest', fontsize=11, fontweight='bold')
    ax6.set_ylabel('가격 변동성 (절대값 %)', fontsize=11, fontweight='bold')
    ax6.set_title('OI vs 가격 변동성', fontsize=13, fontweight='bold', pad=10)
    ax6.grid(True, alpha=0.3, linestyle='--')
    
    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('날짜', fontsize=9)
    
    # ===== 그래프 6: 급락 전후 OI 비교 =====
    ax7 = axes[2, 1]
    
    window = 7
    pre_crash = df[(df['date'] >= crash_date - pd.Timedelta(days=window)) & 
                   (df['date'] < crash_date)]
    post_crash = df[(df['date'] >= crash_date) & 
                    (df['date'] <= crash_date + pd.Timedelta(days=window))]
    
    periods = []
    oi_means = []
    oi_change_means = []
    
    if len(pre_crash) > 0:
        periods.append(f'급락 전\n{window}일')
        oi_means.append(pre_crash['Open_Interest'].mean())
        oi_change_means.append(pre_crash['OI_change_pct'].mean())
    
    if len(post_crash) > 0:
        periods.append(f'급락 후\n{window}일')
        oi_means.append(post_crash['Open_Interest'].mean())
        oi_change_means.append(post_crash['OI_change_pct'].mean())
    
    x = np.arange(len(periods))
    width = 0.35
    
    bars1 = ax7.bar(x - width/2, oi_means, width, label='평균 OI', 
                    color='steelblue', alpha=0.7, edgecolor='black')
    
    # 오른쪽 축
    ax8 = ax7.twinx()
    bars2 = ax8.bar(x + width/2, oi_change_means, width, label='평균 OI 변화율 (%)', 
                    color='coral', alpha=0.7, edgecolor='black')
    
    ax7.set_xlabel('기간', fontsize=11, fontweight='bold')
    ax7.set_ylabel('평균 Open Interest', fontsize=11, fontweight='bold', color='steelblue')
    ax8.set_ylabel('평균 OI 변화율 (%)', fontsize=11, fontweight='bold', color='coral')
    ax7.set_title('급락 전후 OI 비교', fontsize=13, fontweight='bold', pad=10)
    ax7.set_xticks(x)
    ax7.set_xticklabels(periods)
    ax7.tick_params(axis='y', labelcolor='steelblue')
    ax8.tick_params(axis='y', labelcolor='coral')
    ax7.legend(loc='upper left', fontsize=9)
    ax8.legend(loc='upper right', fontsize=9)
    ax7.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # 값 표시
    for bar in bars1:
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:+.2f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "14_open_interest_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()

def main():
    print("=" * 80)
    print("Task 10: Open Interest 및 고래 행동 분석")
    print("=" * 80)
    
    # 1. 데이터 로드
    print("\n📂 데이터 로드 중...")
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    print(f"✅ 데이터 로드 완료: {df.shape}")
    
    # 2. OI 데이터 분석
    df = load_and_analyze_oi_data(df)
    
    if df is None:
        print("\n⚠️  Open Interest 데이터가 없어 분석을 종료합니다.")
        return
    
    # 3. OI 급증/급감 탐지
    df = detect_oi_spikes(df)
    
    # 4. 상관관계 분석
    analyze_oi_price_correlation(df)
    
    # 5. 급락 시점 분석
    analyze_crash_period_oi(df)
    
    # 6. 시각화
    plot_oi_analysis(df)
    
    # 7. 결과 저장
    oi_analysis = df[['date', 'Open_Interest', 'OI_change_pct', 'OI_change_abs',
                      'BTC_Price', 'price_change_pct', 'price_volatility',
                      'OI_spike_up', 'OI_spike_down', 'OI_anomaly']].copy()
    oi_analysis.to_csv(OUTPUT_DIR / "open_interest_analysis.csv", 
                      index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 10 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '14_open_interest_analysis.png'}")
    print(f"   2. {OUTPUT_DIR / 'open_interest_analysis.csv'}")

if __name__ == "__main__":
    main()
