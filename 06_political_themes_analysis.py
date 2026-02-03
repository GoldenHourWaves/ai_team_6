"""
Task 6: 정치 테마 시계열 분석
EPU_POLICY, LEADER, GOVERNMENT 테마와 비트코인 가격 변동의 시간적 관계 탐색
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_political_themes_timeseries(df):
    """정치 관련 테마의 시계열 분석"""
    
    print("\n" + "=" * 80)
    print("🏛️  정치 테마 시계열 분석")
    print("=" * 80)
    
    # 정치 관련 테마 컬럼
    political_themes = [
        'theme_cnt__EPU_POLICY',
        'theme_cnt__LEADER', 
        'theme_cnt__GENERAL_GOVERNMENT',
        'theme_cnt__EPU_POLICY_GOVERNMENT'
    ]
    
    # 존재하는 컬럼만 선택
    available_themes = [t for t in political_themes if t in df.columns]
    print(f"\n📊 분석할 정치 테마: {len(available_themes)}개")
    for theme in available_themes:
        print(f"   - {theme}")
    
    # 10월 10일 찾기
    crash_date = pd.to_datetime('2025-10-10')
    
    # Figure 생성
    fig, axes = plt.subplots(3, 1, figsize=(16, 14))
    fig.suptitle('정치 테마와 비트코인 가격의 시간적 관계', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    # ===== 그래프 1: 가격과 정치 테마 중첩 =====
    ax1 = axes[0]
    
    # 가격 (왼쪽 축)
    color1 = '#2E86AB'
    ax1.set_xlabel('날짜', fontsize=11)
    ax1.set_ylabel('BTC 가격 (USD)', color=color1, fontsize=11, fontweight='bold')
    ax1.plot(df['date'], df['BTC_Price'], color=color1, linewidth=2.5, 
             label='BTC Price', marker='o', markersize=3)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 정치 테마 합계 (오른쪽 축)
    df['political_themes_total'] = df[available_themes].sum(axis=1)
    
    ax2 = ax1.twinx()
    color2 = '#DC143C'
    ax2.set_ylabel('정치 테마 언급 수 (합계)', color=color2, fontsize=11, fontweight='bold')
    ax2.fill_between(df['date'], 0, df['political_themes_total'], 
                     color=color2, alpha=0.3, label='Political Themes')
    ax2.plot(df['date'], df['political_themes_total'], color=color2, 
             linewidth=2, marker='s', markersize=3)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # 10월 10일 마킹
    ax1.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    ax1.set_title('비트코인 가격 vs 정치 테마 언급량', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 범례 통합
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    
    # ===== 그래프 2: 개별 정치 테마 추세 =====
    ax3 = axes[1]
    
    colors = ['#DC143C', '#FF6347', '#FF8C00', '#FFD700']
    for i, theme in enumerate(available_themes):
        theme_name = theme.replace('theme_cnt__', '').replace('_', ' ')
        ax3.plot(df['date'], df[theme], label=theme_name, 
                linewidth=2, marker='o', markersize=3, color=colors[i % len(colors)])
    
    # 10월 10일 마킹
    ax3.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8, 
                label='10/10 Crash')
    
    ax3.set_xlabel('날짜', fontsize=11)
    ax3.set_ylabel('테마 언급 횟수', fontsize=11, fontweight='bold')
    ax3.set_title('개별 정치 테마 시계열 추이', fontsize=13, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=9, ncol=2)
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # ===== 그래프 3: 가격 변화율과 정치 테마의 관계 =====
    ax4 = axes[2]
    
    # 가격 변화율 계산
    df['price_change_pct'] = df['BTC_Price'].pct_change() * 100
    
    # Scatter plot
    scatter = ax4.scatter(df['political_themes_total'], df['price_change_pct'], 
                         c=df['date'].astype('int64'), cmap='viridis',
                         alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
    
    # 회귀선 추가
    mask = ~(df['political_themes_total'].isna() | df['price_change_pct'].isna())
    if mask.sum() > 0:
        x = df.loc[mask, 'political_themes_total']
        y = df.loc[mask, 'price_change_pct']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax4.plot(x, p(x), "r--", linewidth=2, label=f'회귀선 (기울기: {z[0]:.4f})')
        
        # 상관계수 계산
        corr, pval = stats.pearsonr(x, y)
        print(f"\n📈 정치 테마 총량 vs 가격 변화율:")
        print(f"   상관계수: {corr:.4f}")
        print(f"   p-value: {pval:.4f} {'(유의함)' if pval < 0.05 else '(유의하지 않음)'}")
    
    ax4.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax4.set_xlabel('정치 테마 총 언급 수', fontsize=11, fontweight='bold')
    ax4.set_ylabel('가격 변화율 (%)', fontsize=11, fontweight='bold')
    ax4.set_title('정치 테마 언급량 vs 가격 변화율 (산점도)', fontsize=13, fontweight='bold', pad=10)
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--')
    
    # 컬러바 추가
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('날짜', fontsize=10)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "06_political_themes_timeseries.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()
    
    return fig

def analyze_theme_peaks(df):
    """정치 테마 급증 시점 분석"""
    
    print("\n" + "=" * 80)
    print("🔍 정치 테마 급증 시점 분석")
    print("=" * 80)
    
    # 정치 테마 합계
    political_themes = [
        'theme_cnt__EPU_POLICY',
        'theme_cnt__LEADER', 
        'theme_cnt__GENERAL_GOVERNMENT',
        'theme_cnt__EPU_POLICY_GOVERNMENT'
    ]
    available_themes = [t for t in political_themes if t in df.columns]
    df['political_themes_total'] = df[available_themes].sum(axis=1)
    
    # 상위 10% 임계값
    threshold = df['political_themes_total'].quantile(0.9)
    peak_days = df[df['political_themes_total'] >= threshold].copy()
    
    print(f"\n📊 정치 테마 급증 기준: {threshold:.0f} (상위 10%)")
    print(f"🔥 급증 발생 일수: {len(peak_days)}일\n")
    
    if len(peak_days) > 0:
        print("급증 시점 목록:")
        print("-" * 80)
        for idx, row in peak_days.iterrows():
            date = row['date'].date()
            theme_count = row['political_themes_total']
            price = row['BTC_Price']
            price_change = row.get('price_change_pct', np.nan)
            
            print(f"  {date} | 테마: {theme_count:3.0f}개 | 가격: ${price:,.0f} | 변화: {price_change:+.2f}%")
        
        # 10월 10일 전후 분석
        crash_date = pd.to_datetime('2025-10-10')
        pre_crash = peak_days[peak_days['date'] < crash_date]
        post_crash = peak_days[peak_days['date'] >= crash_date]
        
        print(f"\n🕐 급락 이전 급증: {len(pre_crash)}일")
        print(f"🕑 급락 이후 급증: {len(post_crash)}일")
        
        # 급락 직전 3일 평균
        crash_window = df[(df['date'] >= crash_date - pd.Timedelta(days=3)) & 
                         (df['date'] < crash_date)]
        if len(crash_window) > 0:
            avg_before = crash_window['political_themes_total'].mean()
            print(f"\n📉 급락 직전 3일 평균 정치 테마: {avg_before:.1f}")
            print(f"   전체 평균 대비: {(avg_before / df['political_themes_total'].mean() - 1) * 100:+.1f}%")

def create_lag_correlation_analysis(df):
    """시차 상관관계 분석 (정치 테마가 가격에 선행/후행하는지)"""
    
    print("\n" + "=" * 80)
    print("⏱️  시차 상관관계 분석")
    print("=" * 80)
    
    # 정치 테마 합계
    political_themes = [
        'theme_cnt__EPU_POLICY',
        'theme_cnt__LEADER', 
        'theme_cnt__GENERAL_GOVERNMENT',
        'theme_cnt__EPU_POLICY_GOVERNMENT'
    ]
    available_themes = [t for t in political_themes if t in df.columns]
    df['political_themes_total'] = df[available_themes].sum(axis=1)
    
    # 시차별 상관계수 계산 (-5일 ~ +5일)
    lags = range(-5, 6)
    correlations = []
    
    for lag in lags:
        if lag < 0:
            # 정치 테마가 선행 (테마 → 가격)
            shifted_theme = df['political_themes_total'].shift(-lag)
            corr = df['BTC_Price'].corr(shifted_theme)
        elif lag > 0:
            # 가격이 선행 (가격 → 테마)
            shifted_price = df['BTC_Price'].shift(-lag)
            corr = shifted_price.corr(df['political_themes_total'])
        else:
            # 동시
            corr = df['BTC_Price'].corr(df['political_themes_total'])
        
        correlations.append(corr)
    
    # 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['red' if c < 0 else 'green' for c in correlations]
    ax.bar(lags, correlations, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    
    # 0 기준선
    ax.axhline(0, color='black', linewidth=1, linestyle='-')
    ax.axvline(0, color='blue', linewidth=2, linestyle='--', alpha=0.5, label='동시점')
    
    # 최대 상관계수 표시
    max_corr_idx = np.argmax(np.abs(correlations))
    max_lag = lags[max_corr_idx]
    max_corr = correlations[max_corr_idx]
    
    ax.scatter([max_lag], [max_corr], s=200, c='blue', marker='*', 
              zorder=5, edgecolors='darkblue', linewidths=2)
    ax.text(max_lag, max_corr, f'  최대: {max_corr:.3f}\n  ({max_lag}일)', 
           fontsize=10, fontweight='bold', va='bottom' if max_corr > 0 else 'top')
    
    ax.set_xlabel('시차 (일)', fontsize=12, fontweight='bold')
    ax.set_ylabel('상관계수', fontsize=12, fontweight='bold')
    ax.set_title('정치 테마와 비트코인 가격의 시차 상관관계\n(음수: 테마가 선행, 양수: 가격이 선행)', 
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(lags)
    ax.set_xticklabels([f'{l:+d}' for l in lags])
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "07_political_themes_lag_correlation.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 시차 상관관계 그래프 저장: {output_file}")
    
    plt.show()
    
    print(f"\n📊 시차 상관관계 분석 결과:")
    print(f"   최대 상관계수: {max_corr:.4f} (시차: {max_lag}일)")
    
    if max_lag < 0:
        print(f"   ➡️  정치 테마가 가격보다 {abs(max_lag)}일 선행하는 경향")
    elif max_lag > 0:
        print(f"   ⬅️  가격이 정치 테마보다 {max_lag}일 선행하는 경향")
    else:
        print(f"   🔄 정치 테마와 가격이 동시에 움직이는 경향")

def main():
    print("=" * 80)
    print("Task 6: 정치 테마 시계열 분석")
    print("=" * 80)
    
    # 데이터 로드
    print("\n📂 데이터 로드 중...")
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    print(f"✅ 데이터 로드 완료: {df.shape}")
    
    # 1. 정치 테마 시계열 시각화
    plot_political_themes_timeseries(df)
    
    # 2. 테마 급증 시점 분석
    analyze_theme_peaks(df)
    
    # 3. 시차 상관관계 분석
    create_lag_correlation_analysis(df)
    
    print("\n" + "=" * 80)
    print("Task 6 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 시각화:")
    print(f"   1. {OUTPUT_DIR / '06_political_themes_timeseries.png'}")
    print(f"   2. {OUTPUT_DIR / '07_political_themes_lag_correlation.png'}")

if __name__ == "__main__":
    main()
