"""
시각화 10: 종합 대시보드 - 핵심 인사이트
Visualization 10: Comprehensive Dashboard
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 날짜 변환
df['date'] = pd.to_datetime(df['date_posted']).dt.date

# Figure 생성
fig = plt.figure(figsize=(24, 14))
gs = GridSpec(3, 4, figure=fig, hspace=0.3, wspace=0.3)

fig.suptitle('October 2025 암호화폐 폭락 종합 대시보드\nComprehensive Dashboard - Black October Crypto Crash', 
             fontsize=24, fontweight='bold', y=0.98)

# 1. KPI 박스 (좌상단)
ax1 = fig.add_subplot(gs[0, :2])
ax1.axis('off')

total_records = len(df)
total_platforms = df['platform'].nunique()
date_range = f"{df['date'].min()} ~ {df['date'].max()}"
negative_pct = (len(df[df['sentiment'].isin(['Negative', 'Fear', 'Anger'])]) / total_records) * 100

kpi_text = f"""
【핵심 지표 (Key Metrics)】

총 레코드: {total_records:,}개
분석 기간: {date_range}
플랫폼 수: {total_platforms}개
부정 감성 비율: {negative_pct:.1f}%

가장 활발한 플랫폼: {df['platform'].value_counts().index[0]} ({df['platform'].value_counts().iloc[0]:,}개)
가장 많은 감성: {df['sentiment'].value_counts().index[0]} ({df['sentiment'].value_counts().iloc[0]:,}개)
평균 참여도: {df['engagement_score'].mean():.1f}점
평균 관련성: {df['relevance_score'].mean():.1f}점
"""

ax1.text(0.1, 0.5, kpi_text, fontsize=13, verticalalignment='center',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
        family='monospace', fontweight='bold')

# 2. 일별 트렌드 (우상단)
ax2 = fig.add_subplot(gs[0, 2:])
daily_counts = df.groupby('date').size()
ax2.plot(daily_counts.index, daily_counts.values, linewidth=3, color='#2196F3', marker='o')
ax2.fill_between(daily_counts.index, daily_counts.values, alpha=0.3, color='#2196F3')

crash_date = pd.to_datetime('2025-10-10').date()
ax2.axvline(crash_date, color='red', linestyle='--', linewidth=2, label='폭락일')

ax2.set_title('일별 레코드 수 트렌드 (Daily Activity Trend)', fontsize=14, fontweight='bold')
ax2.set_xlabel('날짜 (Date)', fontsize=11)
ax2.set_ylabel('레코드 수 (Records)', fontsize=11)
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

# 3. 플랫폼 분포 (중좌)
ax3 = fig.add_subplot(gs[1, :2])
platform_counts = df['platform'].value_counts()
colors_plat = plt.cm.Set3(range(len(platform_counts)))
ax3.barh(platform_counts.index, platform_counts.values, color=colors_plat)
ax3.set_title('플랫폼별 레코드 분포 (Platform Distribution)', fontsize=14, fontweight='bold')
ax3.set_xlabel('레코드 수 (Records)', fontsize=11)
ax3.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(platform_counts.values):
    ax3.text(v + 50, i, f'{v:,}', va='center', fontsize=10, fontweight='bold')

# 4. 감성 파이 (중우)
ax4 = fig.add_subplot(gs[1, 2:])
sentiment_counts = df['sentiment'].value_counts()
colors_sent = ['#FF4444', '#FF8800', '#CC0000', '#888888', '#44AA44', '#4444FF', '#8844FF']
explode = [0.05 if s in ['Negative', 'Fear', 'Anger'] else 0 for s in sentiment_counts.index]

ax4.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
       colors=colors_sent[:len(sentiment_counts)], explode=explode, startangle=90)
ax4.set_title('감성 분포 (Sentiment Distribution)', fontsize=14, fontweight='bold')

# 5. 히트맵 (하단 좌)
ax5 = fig.add_subplot(gs[2, :2])
date_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
sns.heatmap(date_sentiment.T, cmap='YlOrRd', ax=ax5, cbar_kws={'label': 'Records'})
ax5.set_title('일별 감성 히트맵 (Daily Sentiment Heatmap)', fontsize=14, fontweight='bold')
ax5.set_xlabel('날짜 (Date)', fontsize=11)
ax5.set_ylabel('감성 (Sentiment)', fontsize=11)
ax5.tick_params(axis='x', rotation=45)

# 6. 저자 유형 (하단 우)
ax6 = fig.add_subplot(gs[2, 2:])
author_counts = df['author_type'].value_counts()
ax6.bar(author_counts.index, author_counts.values, color=plt.cm.viridis(range(len(author_counts))))
ax6.set_title('저자 유형 분포 (Author Type Distribution)', fontsize=14, fontweight='bold')
ax6.set_ylabel('레코드 수 (Records)', fontsize=11)
ax6.tick_params(axis='x', rotation=45)
ax6.grid(True, alpha=0.3, axis='y')

for i, (idx, val) in enumerate(author_counts.items()):
    ax6.text(i, val + 30, f'{val:,}', ha='center', fontsize=9, fontweight='bold')

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_10_comprehensive_dashboard.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

print("\n" + "="*80)
print("📊 종합 대시보드 생성 완료!")
print("="*80)
print(f"\n총 레코드: {total_records:,}개")
print(f"분석 기간: {date_range}")
print(f"부정 감성: {negative_pct:.1f}%")
print(f"\n가장 활발한 날: {daily_counts.idxmax()} ({daily_counts.max():,}개 레코드)")
print(f"가장 활발한 플랫폼: {platform_counts.index[0]} ({platform_counts.iloc[0]:,}개)")

plt.show()
