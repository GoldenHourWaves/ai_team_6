"""
시각화 5: 히트맵 - 날짜 x 플랫폼 x 감성
Visualization 5: Heatmap - Date x Platform x Sentiment
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

# 날짜 변환
df['date'] = pd.to_datetime(df['date_posted']).dt.date

# 부정 감성만 필터링 (Negative, Fear, Anger)
negative_sentiments = ['Negative', 'Fear', 'Anger']
df_negative = df[df['sentiment'].isin(negative_sentiments)]

# 날짜 x 플랫폼 피벗 테이블
date_platform_pivot = df.groupby(['date', 'platform']).size().unstack(fill_value=0)

# 날짜 x 감성 피벗 테이블 (부정 감성)
date_sentiment_pivot = df_negative.groupby(['date', 'sentiment']).size().unstack(fill_value=0)

# 시각화
fig, axes = plt.subplots(2, 1, figsize=(18, 14))
fig.suptitle('October 2025 암호화폐 폭락 - 시공간 활동 히트맵\nSpatio-Temporal Activity Heatmap', 
             fontsize=20, fontweight='bold')

# 1. 날짜 x 플랫폼 히트맵
sns.heatmap(date_platform_pivot.T, cmap='YlOrRd', annot=False, 
            fmt='d', cbar_kws={'label': '레코드 수 (Records)'}, ax=axes[0])
axes[0].set_title('일별 플랫폼 활동 히트맵 (Daily Platform Activity)', 
                  fontsize=16, fontweight='bold', pad=15)
axes[0].set_xlabel('날짜 (Date)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('플랫폼 (Platform)', fontsize=12, fontweight='bold')

# 폭락일 표시
crash_date = pd.to_datetime('2025-10-10').date()
if crash_date in date_platform_pivot.index:
    crash_idx = list(date_platform_pivot.index).index(crash_date)
    axes[0].axvline(crash_idx + 0.5, color='red', linewidth=3, linestyle='--')

# x축 레이블 회전
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha='right')

# 2. 날짜 x 부정감성 히트맵
sns.heatmap(date_sentiment_pivot.T, cmap='Reds', annot=False,
            fmt='d', cbar_kws={'label': '부정 레코드 수 (Negative Records)'}, ax=axes[1])
axes[1].set_title('일별 부정 감성 히트맵 (Daily Negative Sentiment)', 
                  fontsize=16, fontweight='bold', pad=15)
axes[1].set_xlabel('날짜 (Date)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('감성 (Sentiment)', fontsize=12, fontweight='bold')

# 폭락일 표시
if crash_date in date_sentiment_pivot.index:
    crash_idx2 = list(date_sentiment_pivot.index).index(crash_date)
    axes[1].axvline(crash_idx2 + 0.5, color='darkred', linewidth=3, linestyle='--')

axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_05_heatmap.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 플랫폼별 총 활동:")
print(date_platform_pivot.sum().sort_values(ascending=False))

print("\n📊 부정 감성 총계:")
print(date_sentiment_pivot.sum().sort_values(ascending=False))

plt.show()
