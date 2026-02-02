"""
시각화 4: 감성 분포 파이차트
Visualization 4: Sentiment Distribution Pie Chart
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 감성 분포 계산
sentiment_counts = df['sentiment'].value_counts()

# 시각화 - 2개의 파이차트
fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle('October 2025 암호화폐 폭락 - 감성 분석\nSentiment Analysis of Crypto Crash', 
             fontsize=20, fontweight='bold')

# 색상 매핑
colors = {
    'Negative': '#FF4444',
    'Fear': '#FF8800',
    'Anger': '#CC0000',
    'Neutral': '#888888',
    'Positive': '#44AA44',
    'Hopeful': '#4444FF',
    'Analytical': '#8844FF'
}

sentiment_colors = [colors.get(sent, '#CCCCCC') for sent in sentiment_counts.index]

# 1. 전체 기간 감성 분포
explode = [0.05 if sent in ['Negative', 'Fear', 'Anger'] else 0 for sent in sentiment_counts.index]

axes[0].pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
           colors=sentiment_colors, startangle=90, explode=explode,
           shadow=True, textprops={'fontsize': 12, 'fontweight': 'bold'})
axes[0].set_title('전체 기간 감성 분포 (Overall Sentiment Distribution)\n(Sep-Oct 2025)', 
                  fontsize=16, fontweight='bold', pad=20)

# 2. 폭락일 (Oct 10) 감성 분포
df['date'] = pd.to_datetime(df['date_posted']).dt.date
crash_date = pd.to_datetime('2025-10-10').date()
crash_day_df = df[df['date'] == crash_date]

if len(crash_day_df) > 0:
    crash_sentiment = crash_day_df['sentiment'].value_counts()
    crash_colors = [colors.get(sent, '#CCCCCC') for sent in crash_sentiment.index]
    explode2 = [0.05 if sent in ['Negative', 'Fear', 'Anger'] else 0 for sent in crash_sentiment.index]
    
    axes[1].pie(crash_sentiment, labels=crash_sentiment.index, autopct='%1.1f%%',
               colors=crash_colors, startangle=90, explode=explode2,
               shadow=True, textprops={'fontsize': 12, 'fontweight': 'bold'})
    axes[1].set_title('폭락일 감성 분포 (Crash Day Sentiment)\n(2025-10-10)', 
                      fontsize=16, fontweight='bold', pad=20)
else:
    axes[1].text(0.5, 0.5, 'No data for crash day', ha='center', va='center')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_04_sentiment_pie.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 전체 감성 분포:")
print(sentiment_counts)
print(f"\n전체 레코드: {len(df):,}개")

if len(crash_day_df) > 0:
    print(f"\n폭락일 (2025-10-10) 감성 분포:")
    print(crash_sentiment)
    print(f"폭락일 레코드: {len(crash_day_df):,}개")

plt.show()
