"""
시각화 1: 타임라인 차트 - 날짜별 감성 변화
Visualization 1: Timeline Chart - Sentiment Over Time
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 날짜 변환
df['date'] = pd.to_datetime(df['date_posted']).dt.date

# 일별 감성 집계
sentiment_timeline = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)

# 시각화
plt.figure(figsize=(16, 10))

# 색상 매핑 (감성별)
colors = {
    'Negative': '#FF4444',
    'Fear': '#FF8800',
    'Anger': '#CC0000',
    'Neutral': '#888888',
    'Positive': '#44AA44',
    'Hopeful': '#4444FF',
    'Analytical': '#8844FF'
}

# 라인 플롯
for sentiment in sentiment_timeline.columns:
    if sentiment in colors:
        plt.plot(sentiment_timeline.index, sentiment_timeline[sentiment], 
                label=sentiment, linewidth=2.5, marker='o', markersize=4,
                color=colors.get(sentiment, '#000000'), alpha=0.8)

# 폭락일 표시
crash_date = pd.to_datetime('2025-10-10').date()
plt.axvline(crash_date, color='red', linestyle='--', linewidth=3, 
            label='폭락일 (Crash Day)', alpha=0.7)

# 9월/10월 구분선
sep_oct = pd.to_datetime('2025-10-01').date()
plt.axvline(sep_oct, color='blue', linestyle=':', linewidth=2, 
            label='10월 시작', alpha=0.5)

plt.title('October 2025 암호화폐 폭락 - 일별 감성 변화 추이\nDaily Sentiment Timeline During Crypto Crash', 
          fontsize=18, fontweight='bold', pad=20)
plt.xlabel('날짜 (Date)', fontsize=14, fontweight='bold')
plt.ylabel('레코드 수 (Number of Records)', fontsize=14, fontweight='bold')
plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_01_timeline_sentiment.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

plt.show()