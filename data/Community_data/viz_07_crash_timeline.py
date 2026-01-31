"""
시각화 7: 폭락 전후 시계열 비교 (Before-During-After)
Visualization 7: Crash Timeline Comparison
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\SNS_FINAL_RECORDS_20260131_071140\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 날짜 변환
df['date'] = pd.to_datetime(df['date_posted'])

# 폭락 전후 기간 정의
crash_date = pd.to_datetime('2025-10-10')
before_start = crash_date - pd.Timedelta(days=7)
after_end = crash_date + pd.Timedelta(days=7)

# 기간별 필터링
df_before = df[(df['date'] >= before_start) & (df['date'] < crash_date)]
df_during = df[df['date'].dt.date == crash_date.date()]
df_after = df[(df['date'] > crash_date) & (df['date'] <= after_end)]

# 시각화
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('폭락 전후 비교 분석 (Before-During-After Crash Analysis)\n2025-10-03 ~ 2025-10-17', 
             fontsize=20, fontweight='bold')

periods = [
    (df_before, 'Before Crash\n(7일 전)', '#4CAF50'),
    (df_during, 'Crash Day\n(10월 10일)', '#F44336'),
    (df_after, 'After Crash\n(7일 후)', '#FF9800')
]

# 1행: 감성 분포
for idx, (data, label, color) in enumerate(periods):
    if len(data) > 0:
        sentiment_dist = data['sentiment'].value_counts()
        axes[0, idx].pie(sentiment_dist, labels=sentiment_dist.index, autopct='%1.1f%%',
                        startangle=90, colors=['#FF4444', '#FF8800', '#CC0000', '#888888', '#44AA44', '#4444FF'])
        axes[0, idx].set_title(f'{label}\n감성 분포 ({len(data):,}개)', fontsize=14, fontweight='bold')
    else:
        axes[0, idx].text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)

# 2행: 플랫폼별 활동
for idx, (data, label, color) in enumerate(periods):
    if len(data) > 0:
        platform_dist = data['platform'].value_counts()
        axes[1, idx].barh(platform_dist.index, platform_dist.values, color=color, alpha=0.7)
        axes[1, idx].set_title(f'{label}\n플랫폼별 활동', fontsize=14, fontweight='bold')
        axes[1, idx].set_xlabel('레코드 수 (Records)', fontsize=11)
        axes[1, idx].grid(True, alpha=0.3, axis='x')
        
        # 값 표시
        for i, v in enumerate(platform_dist.values):
            axes[1, idx].text(v + 10, i, str(v), va='center', fontsize=10, fontweight='bold')
    else:
        axes[1, idx].text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_07_crash_timeline.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 비교
print("\n📊 기간별 통계 비교:")
print(f"\n폭락 전 (7일): {len(df_before):,}개 레코드")
print(f"폭락 당일: {len(df_during):,}개 레코드")
print(f"폭락 후 (7일): {len(df_after):,}개 레코드")

print("\n부정 감성 비율:")
for data, label in [(df_before, 'Before'), (df_during, 'During'), (df_after, 'After')]:
    if len(data) > 0:
        negative = len(data[data['sentiment'].isin(['Negative', 'Fear', 'Anger'])])
        pct = (negative / len(data)) * 100
        print(f"{label}: {pct:.1f}% ({negative:,}/{len(data):,})")

plt.show()
