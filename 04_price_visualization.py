"""
Task 4: 기본 시각화 - 가격 시계열 그래프
비트코인 가격의 시계열 변화를 시각화하고 10월 10일 급락 시점 마킹
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_btc_price_timeseries(df):
    """비트코인 가격 시계열 그래프"""
    
    print("\n" + "=" * 80)
    print("📈 비트코인 가격 시계열 그래프 생성")
    print("=" * 80)
    
    # 10월 10일 찾기
    crash_date = pd.to_datetime('2025-10-10')
    crash_data = df[df['date'] == crash_date]
    
    if len(crash_data) > 0:
        crash_price = crash_data['BTC_Price'].values[0]
        print(f"\n⚠️  급락 시점 감지:")
        print(f"   날짜: {crash_date.date()}")
        print(f"   가격: ${crash_price:,.2f}")
    
    # 가격 변화율 계산
    df['price_change_pct'] = df['BTC_Price'].pct_change() * 100
    
    # 최고가, 최저가 찾기
    max_price = df['BTC_Price'].max()
    min_price = df['BTC_Price'].min()
    max_date = df[df['BTC_Price'] == max_price]['date'].values[0]
    min_date = df[df['BTC_Price'] == min_price]['date'].values[0]
    
    print(f"\n📊 가격 통계:")
    print(f"   최고가: ${max_price:,.2f} ({pd.to_datetime(max_date).date()})")
    print(f"   최저가: ${min_price:,.2f} ({pd.to_datetime(min_date).date()})")
    print(f"   변동폭: ${max_price - min_price:,.2f} ({(max_price - min_price) / min_price * 100:.2f}%)")
    
    # Figure 생성
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    fig.suptitle('비트코인 가격 시계열 분석 (2025.09.01 ~ 2025.10.31)', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    # ===== 그래프 1: 가격 추세 =====
    ax1 = axes[0]
    
    # 가격 선 그래프
    ax1.plot(df['date'], df['BTC_Price'], linewidth=2.5, color='#2E86AB', 
             label='BTC Price', marker='o', markersize=4, alpha=0.8)
    
    # 이동평균선 추가
    df['MA7'] = df['BTC_Price'].rolling(window=7).mean()
    ax1.plot(df['date'], df['MA7'], linewidth=2, color='#F77F00', 
             linestyle='--', label='7일 이동평균', alpha=0.7)
    
    # 최고가/최저가 마킹
    ax1.scatter([max_date], [max_price], s=200, c='green', marker='^', 
                zorder=5, label=f'최고가 (${max_price:,.0f})', edgecolors='darkgreen', linewidths=2)
    ax1.scatter([min_date], [min_price], s=200, c='red', marker='v', 
                zorder=5, label=f'최저가 (${min_price:,.0f})', edgecolors='darkred', linewidths=2)
    
    # 10월 10일 급락 마킹
    if len(crash_data) > 0:
        ax1.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, 
                    label='10월 10일 급락', alpha=0.8)
        ax1.scatter([crash_date], [crash_price], s=300, c='red', marker='X', 
                    zorder=6, edgecolors='darkred', linewidths=2)
        
        # 급락 구간 강조
        crash_window = df[(df['date'] >= crash_date - pd.Timedelta(days=3)) & 
                          (df['date'] <= crash_date + pd.Timedelta(days=3))]
        ax1.fill_between(crash_window['date'], 
                         crash_window['BTC_Price'].min() * 0.99,
                         crash_window['BTC_Price'].max() * 1.01,
                         color='red', alpha=0.1)
    
    ax1.set_xlabel('날짜', fontsize=12, fontweight='bold')
    ax1.set_ylabel('가격 (USD)', fontsize=12, fontweight='bold')
    ax1.set_title('비트코인 가격 추세 및 주요 이벤트', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # ===== 그래프 2: 일일 변화율 =====
    ax2 = axes[1]
    
    # 변화율 바 차트
    colors = ['red' if x < 0 else 'green' for x in df['price_change_pct']]
    ax2.bar(df['date'], df['price_change_pct'], color=colors, alpha=0.6, width=0.8)
    
    # 0 기준선
    ax2.axhline(0, color='black', linewidth=1, linestyle='-', alpha=0.5)
    
    # 10월 10일 마킹
    if len(crash_data) > 0:
        ax2.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
        crash_idx = df[df['date'] == crash_date].index[0]
        if crash_idx > 0:
            crash_change = df.loc[crash_idx, 'price_change_pct']
            if not pd.isna(crash_change):
                ax2.text(crash_date, crash_change, f'{crash_change:.2f}%', 
                        ha='center', va='bottom' if crash_change > 0 else 'top',
                        fontsize=10, fontweight='bold', color='red')
    
    ax2.set_xlabel('날짜', fontsize=12, fontweight='bold')
    ax2.set_ylabel('일일 변화율 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('비트코인 일일 가격 변화율', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
    
    plt.tight_layout()
    
    # 저장
    output_file = OUTPUT_DIR / "01_btc_price_timeseries.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()
    
    return fig

def plot_price_with_volume(df):
    """가격과 SNS 활동량 함께 표시"""
    
    print("\n" + "=" * 80)
    print("📊 가격 vs SNS 활동량 그래프 생성")
    print("=" * 80)
    
    fig, ax1 = plt.subplots(figsize=(16, 8))
    
    # 가격 (왼쪽 축)
    color1 = '#2E86AB'
    ax1.set_xlabel('날짜', fontsize=12, fontweight='bold')
    ax1.set_ylabel('BTC 가격 (USD)', color=color1, fontsize=12, fontweight='bold')
    ax1.plot(df['date'], df['BTC_Price'], color=color1, linewidth=2.5, 
             label='BTC Price', marker='o', markersize=4)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # SNS 활동량 (오른쪽 축)
    ax2 = ax1.twinx()
    color2 = '#F77F00'
    ax2.set_ylabel('SNS 게시물 수', color=color2, fontsize=12, fontweight='bold')
    ax2.fill_between(df['date'], 0, df['sns_post_count'], 
                     color=color2, alpha=0.3, label='SNS Posts')
    ax2.plot(df['date'], df['sns_post_count'], color=color2, linewidth=2, 
             marker='s', markersize=3)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # 10월 10일 마킹
    crash_date = pd.to_datetime('2025-10-10')
    if crash_date in df['date'].values:
        ax1.axvline(crash_date, color='red', linestyle=':', linewidth=2.5, alpha=0.8)
    
    plt.title('비트코인 가격 vs SNS 활동량', fontsize=16, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 범례 통합
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "02_btc_price_vs_sns.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 그래프 저장: {output_file}")
    
    plt.show()
    
    return fig

def main():
    print("=" * 80)
    print("Task 4: 기본 시각화 - 가격 시계열 그래프")
    print("=" * 80)
    
    # 데이터 로드
    print("\n📂 데이터 로드 중...")
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    print(f"✅ 데이터 로드 완료: {df.shape}")
    
    # 그래프 1: 가격 시계열
    fig1 = plot_btc_price_timeseries(df)
    
    # 그래프 2: 가격 vs SNS
    fig2 = plot_price_with_volume(df)
    
    print("\n" + "=" * 80)
    print("Task 4 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 그래프:")
    print(f"   1. {OUTPUT_DIR / '01_btc_price_timeseries.png'}")
    print(f"   2. {OUTPUT_DIR / '02_btc_price_vs_sns.png'}")

if __name__ == "__main__":
    main()
