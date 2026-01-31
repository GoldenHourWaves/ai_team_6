"""
시각화 9: 키워드 빈도 막대 그래프 (Top 30)
Visualization 9: Top Keywords Bar Chart
"""

import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 키워드 추출
all_keywords = []
for keywords_str in df['keywords'].dropna():
    keywords = keywords_str.split(',')
    all_keywords.extend([k.strip() for k in keywords])

keyword_counts = Counter(all_keywords)

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(20, 14))
fig.suptitle('키워드 빈도 분석\nKeyword Frequency Analysis', 
             fontsize=20, fontweight='bold')

# 1. Top 30 전체 키워드
top_30 = dict(keyword_counts.most_common(30))
colors = plt.cm.Reds([(i/30) for i in range(30)])

axes[0, 0].barh(list(top_30.keys())[::-1], list(top_30.values())[::-1], color=colors[::-1])
axes[0, 0].set_title('Top 30 키워드 (Overall)', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('빈도 (Frequency)', fontsize=12)
axes[0, 0].grid(True, alpha=0.3, axis='x')

# 값 표시
for i, (keyword, count) in enumerate(list(top_30.items())[::-1]):
    axes[0, 0].text(count + 50, i, f'{count:,}', va='center', fontsize=9)

# 2. 폭락 관련 키워드만
crash_keywords = ['liquidation', 'crash', 'dump', 'selloff', 'panic', 'bloodbath', 
                  'rekt', 'lost', 'manipulation', 'whale']
crash_counts = {k: keyword_counts[k] for k in crash_keywords if k in keyword_counts}

axes[0, 1].bar(crash_counts.keys(), crash_counts.values(), color='#FF4444', alpha=0.7)
axes[0, 1].set_title('폭락 관련 키워드 (Crash-related)', fontsize=14, fontweight='bold')
axes[0, 1].set_ylabel('빈도 (Frequency)', fontsize=12)
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 값 표시
for keyword, count in crash_counts.items():
    axes[0, 1].text(keyword, count + 20, f'{count:,}', ha='center', fontsize=10, fontweight='bold')

# 3. 시장 관련 키워드
market_keywords = ['bitcoin', 'BTC', 'crypto', 'market', 'ethereum', 'ETH', 
                   'leverage', 'margin call', 'futures', 'derivatives']
market_counts = {k: keyword_counts[k] for k in market_keywords if k in keyword_counts}

axes[1, 0].bar(market_counts.keys(), market_counts.values(), color='#4CAF50', alpha=0.7)
axes[1, 0].set_title('시장 관련 키워드 (Market-related)', fontsize=14, fontweight='bold')
axes[1, 0].set_ylabel('빈도 (Frequency)', fontsize=12)
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 값 표시
for keyword, count in market_counts.items():
    axes[1, 0].text(keyword, count + 20, f'{count:,}', ha='center', fontsize=10, fontweight='bold')

# 4. 키워드 카테고리별 합계
categories = {
    '폭락/청산\n(Crash)': ['liquidation', 'crash', 'dump', 'selloff', 'panic', 'bloodbath', 'rekt'],
    '암호화폐\n(Crypto)': ['bitcoin', 'BTC', 'crypto', 'ethereum', 'ETH', 'altcoin'],
    '거래/레버리지\n(Trading)': ['leverage', 'margin call', 'futures', 'derivatives', 'trading'],
    '조작의혹\n(Manipulation)': ['manipulation', 'whale', 'insider', 'coordinated'],
    '거래소\n(Exchange)': ['exchange', 'Binance', 'Hyperliquid', 'Bybit'],
    '정책/뉴스\n(Policy)': ['Trump', 'tariff', 'China', 'trade war', 'geopolitical']
}

category_totals = {}
for cat, keywords in categories.items():
    total = sum(keyword_counts.get(k, 0) for k in keywords)
    category_totals[cat] = total

colors_cat = ['#FF4444', '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#FFC107']
axes[1, 1].pie(category_totals.values(), labels=category_totals.keys(), 
              autopct='%1.1f%%', startangle=90, colors=colors_cat)
axes[1, 1].set_title('키워드 카테고리별 분포\n(Keyword Categories)', fontsize=14, fontweight='bold')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_09_keyword_frequency.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# 통계 출력
print("\n📊 Top 20 키워드:")
for i, (keyword, count) in enumerate(keyword_counts.most_common(20), 1):
    print(f"{i:2d}. {keyword:25s}: {count:6,}회")

print("\n📊 카테고리별 합계:")
for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
    print(f"{cat:30s}: {total:6,}회")

plt.show()
