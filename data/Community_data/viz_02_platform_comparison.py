"""
시각화 2: 플랫폼별 참여도 비교
Visualization 2: Platform Engagement Comparison
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

# 플랫폼별 통계
platform_stats = df.groupby('platform').agg({
    'engagement_score': ['mean', 'median', 'max'],
    'record_id': 'count'
}).round(2)

platform_stats.columns = ['평균_참여도', '중간값_참여도', '최대_참여도', '레코드_수']
platform_stats = platform_stats.sort_values('평균_참여도', ascending=False)

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('플랫폼별 참여도 및 활동 분석\nPlatform Engagement & Activity Analysis', 
             fontsize=20, fontweight='bold')

# 1. 박스플롯 - 플랫폼별 참여도 분포
sns.boxplot(data=df, y='platform', x='engagement_score', 
            palette='Set2', ax=axes[0, 0], orient='h')
axes[0, 0].set_title('플랫폼별 참여도 분포 (Engagement Distribution)', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('참여도 점수 (Engagement Score)', fontsize=12)
axes[0, 0].set_ylabel('플랫폼 (Platform)', fontsize=12)
axes[0, 0].grid(True, alpha=0.3, axis='x')

# 2. 막대 그래프 - 플랫폼별 평균 참여도
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
axes[0, 1].barh(platform_stats.index, platform_stats['평균_참여도'], color=colors)
axes[0, 1].set_title('플랫폼별 평균 참여도 (Average Engagement)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('평균 참여도 (Average Score)', fontsize=12)
axes[0, 1].set_ylabel('플랫폼 (Platform)', fontsize=12)
axes[0, 1].grid(True, alpha=0.3, axis='x')

# 값 표시
for i, v in enumerate(platform_stats['평균_참여도']):
    axes[0, 1].text(v + 1, i, f'{v:.1f}', va='center', fontsize=11, fontweight='bold')

# 3. 파이 차트 - 플랫폼별 레코드 비율
axes[1, 0].pie(platform_stats['레코드_수'], labels=platform_stats.index, 
               autopct='%1.1f%%', colors=colors, startangle=90)
axes[1, 0].set_title('플랫폼별 레코드 비율 (Record Distribution)', fontsize=14, fontweight='bold')

# 4. 산점도 - 레코드 수 vs 평균 참여도
axes[1, 1].scatter(platform_stats['레코드_수'], platform_stats['평균_참여도'], 
                   s=platform_stats['레코드_수']/10, c=colors, alpha=0.6, edgecolors='black', linewidth=2)
axes[1, 1].set_title('레코드 수 vs 평균 참여도 (Volume vs Engagement)', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('레코드 수 (Number of Records)', fontsize=12)
axes[1, 1].set_ylabel('평균 참여도 (Average Engagement)', fontsize=12)
axes[1, 1].grid(True, alpha=0.3)

# 플랫폼명 표시
for idx, (name, row) in enumerate(platform_stats.iterrows()):
    axes[1, 1].annotate(name, (row['레코드_수'], row['평균_참여도']), 
                       fontsize=10, ha='center', fontweight='bold')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_02_platform_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 플랫폼별 통계:")
print(platform_stats)

plt.show()
