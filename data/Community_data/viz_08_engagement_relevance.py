"""
시각화 8: 참여도 vs 관련성 산점도 분석
Visualization 8: Engagement vs Relevance Scatter Analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('참여도 vs 관련성 분석\nEngagement vs Relevance Analysis', 
             fontsize=20, fontweight='bold')

# 색상 매핑
sentiment_colors = {
    'Negative': '#FF4444',
    'Fear': '#FF8800',
    'Anger': '#CC0000',
    'Neutral': '#888888',
    'Positive': '#44AA44',
    'Hopeful': '#4444FF',
    'Analytical': '#8844FF'
}

# 1. 전체 산점도 (감성별 색상)
for sentiment in df['sentiment'].unique():
    subset = df[df['sentiment'] == sentiment]
    axes[0, 0].scatter(subset['relevance_score'], subset['engagement_score'],
                      alpha=0.5, s=30, c=sentiment_colors.get(sentiment, '#CCCCCC'),
                      label=sentiment)

axes[0, 0].set_title('참여도 vs 관련성 (전체)\nEngagement vs Relevance (All)', 
                     fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('관련성 점수 (Relevance Score)', fontsize=12)
axes[0, 0].set_ylabel('참여도 점수 (Engagement Score)', fontsize=12)
axes[0, 0].legend(loc='best', fontsize=9)
axes[0, 0].grid(True, alpha=0.3)

# 2. 플랫폼별 산점도
for platform in df['platform'].unique()[:7]:  # 상위 7개
    subset = df[df['platform'] == platform]
    axes[0, 1].scatter(subset['relevance_score'], subset['engagement_score'],
                      alpha=0.4, s=30, label=platform)

axes[0, 1].set_title('참여도 vs 관련성 (플랫폼별)\nEngagement vs Relevance (Platform)', 
                     fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('관련성 점수 (Relevance Score)', fontsize=12)
axes[0, 1].set_ylabel('참여도 점수 (Engagement Score)', fontsize=12)
axes[0, 1].legend(loc='best', fontsize=9)
axes[0, 1].grid(True, alpha=0.3)

# 3. 밀도 플롯 (Hexbin)
hexbin = axes[1, 0].hexbin(df['relevance_score'], df['engagement_score'],
                          gridsize=30, cmap='YlOrRd', mincnt=1)
axes[1, 0].set_title('참여도 vs 관련성 밀도\nDensity Plot', 
                     fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('관련성 점수 (Relevance Score)', fontsize=12)
axes[1, 0].set_ylabel('참여도 점수 (Engagement Score)', fontsize=12)
plt.colorbar(hexbin, ax=axes[1, 0], label='레코드 밀도 (Density)')
axes[1, 0].grid(True, alpha=0.3)

# 4. 4분면 분석
median_relevance = df['relevance_score'].median()
median_engagement = df['engagement_score'].median()

# 4분면 정의
df['quadrant'] = 'Low-Low'
df.loc[(df['relevance_score'] >= median_relevance) & (df['engagement_score'] >= median_engagement), 'quadrant'] = 'High-High'
df.loc[(df['relevance_score'] >= median_relevance) & (df['engagement_score'] < median_engagement), 'quadrant'] = 'High Rel-Low Eng'
df.loc[(df['relevance_score'] < median_relevance) & (df['engagement_score'] >= median_engagement), 'quadrant'] = 'Low Rel-High Eng'

quadrant_counts = df['quadrant'].value_counts()
colors_quad = ['#4CAF50', '#FFC107', '#FF5722', '#9E9E9E']

axes[1, 1].pie(quadrant_counts, labels=quadrant_counts.index, autopct='%1.1f%%',
              startangle=90, colors=colors_quad)
axes[1, 1].set_title('4분면 분석 (Quadrant Analysis)\nHigh/Low Engagement & Relevance', 
                     fontsize=14, fontweight='bold')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_08_engagement_relevance.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 4분면 분포:")
print(quadrant_counts)

print(f"\n중간값 (Median):")
print(f"  관련성: {median_relevance:.1f}")
print(f"  참여도: {median_engagement:.1f}")

# High-High 샘플
high_high = df[df['quadrant'] == 'High-High']
print(f"\nHigh-High 레코드: {len(high_high):,}개")
print(f"  평균 관련성: {high_high['relevance_score'].mean():.1f}")
print(f"  평균 참여도: {high_high['engagement_score'].mean():.1f}")

plt.show()
