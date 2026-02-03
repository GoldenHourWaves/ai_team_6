"""
시각화 6: 저자 유형별 감성 분석
Visualization 6: Author Type Sentiment Analysis
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

# 저자 유형별 감성 교차 분석
author_sentiment = pd.crosstab(df['author_type'], df['sentiment'], normalize='index') * 100

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('저자 유형별 감성 및 참여도 분석\nAuthor Type Sentiment & Engagement Analysis', 
             fontsize=20, fontweight='bold')

# 1. 저자 유형별 감성 비율 (Stacked Bar)
author_sentiment.plot(kind='bar', stacked=True, ax=axes[0, 0], 
                      color=['#FF4444', '#FF8800', '#CC0000', '#888888', '#44AA44', '#4444FF', '#8844FF'])
axes[0, 0].set_title('저자 유형별 감성 비율 (Sentiment by Author Type)', 
                     fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('저자 유형 (Author Type)', fontsize=12)
axes[0, 0].set_ylabel('비율 (Percentage %)', fontsize=12)
axes[0, 0].legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 2. 저자 유형별 평균 참여도
author_engagement = df.groupby('author_type')['engagement_score'].mean().sort_values(ascending=False)
colors_eng = plt.cm.viridis(range(len(author_engagement)))

axes[0, 1].barh(author_engagement.index, author_engagement.values, color=colors_eng)
axes[0, 1].set_title('저자 유형별 평균 참여도 (Average Engagement)', 
                     fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('평균 참여도 점수 (Avg Score)', fontsize=12)
axes[0, 1].set_ylabel('저자 유형 (Author Type)', fontsize=12)
axes[0, 1].grid(True, alpha=0.3, axis='x')

# 값 표시
for i, v in enumerate(author_engagement.values):
    axes[0, 1].text(v + 0.5, i, f'{v:.1f}', va='center', fontsize=11, fontweight='bold')

# 3. 저자 유형별 레코드 수
author_counts = df['author_type'].value_counts()
axes[1, 0].pie(author_counts, labels=author_counts.index, autopct='%1.1f%%',
              startangle=90, colors=plt.cm.Set3(range(len(author_counts))))
axes[1, 0].set_title('저자 유형 분포 (Author Type Distribution)', 
                     fontsize=14, fontweight='bold')

# 4. 히트맵 - 저자 유형 x 감성 (실제 개수)
author_sent_count = pd.crosstab(df['author_type'], df['sentiment'])
sns.heatmap(author_sent_count, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1, 1])
axes[1, 1].set_title('저자 유형 x 감성 분포 (Author x Sentiment Matrix)', 
                     fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('감성 (Sentiment)', fontsize=12)
axes[1, 1].set_ylabel('저자 유형 (Author Type)', fontsize=12)

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_06_author_type_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 저자 유형별 감성 비율 (%):")
print(author_sentiment.round(1))

print("\n📊 저자 유형별 평균 참여도:")
print(author_engagement.round(2))

plt.show()
