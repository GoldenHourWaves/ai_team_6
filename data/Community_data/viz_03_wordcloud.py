"""
시각화 3: 워드클라우드 - 키워드 빈도
Visualization 3: Word Cloud - Keyword Frequency
"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\FINAL_10K_RECORDS.csv'
df = pd.read_csv(data_path)

# 키워드 추출 및 전처리
all_keywords = []
for keywords_str in df['keywords'].dropna():
    keywords = keywords_str.split(',')
    all_keywords.extend([k.strip() for k in keywords])

# 키워드 빈도 계산
keyword_counts = Counter(all_keywords)
top_keywords = dict(keyword_counts.most_common(50))

# 시각화 - 2개 워드클라우드
fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle('October 2025 암호화폐 폭락 - 키워드 분석\nKeyword Analysis of Crypto Crash', 
             fontsize=20, fontweight='bold')

# 1. 전체 키워드 워드클라우드
wordcloud1 = WordCloud(
    width=800, 
    height=600,
    background_color='white',
    colormap='Reds',
    relative_scaling=0.5,
    min_font_size=10
).generate_from_frequencies(top_keywords)

axes[0].imshow(wordcloud1, interpolation='bilinear')
axes[0].set_title('전체 키워드 빈도 (Overall Keywords)', fontsize=16, fontweight='bold', pad=20)
axes[0].axis('off')

# 2. 부정 감성 키워드만
negative_df = df[df['sentiment'].isin(['Negative', 'Fear', 'Anger'])]
negative_keywords = []
for keywords_str in negative_df['keywords'].dropna():
    keywords = keywords_str.split(',')
    negative_keywords.extend([k.strip() for k in keywords])

negative_counts = Counter(negative_keywords)
top_negative = dict(negative_counts.most_common(50))

wordcloud2 = WordCloud(
    width=800,
    height=600,
    background_color='white',
    colormap='YlOrRd',
    relative_scaling=0.5,
    min_font_size=10
).generate_from_frequencies(top_negative)

axes[1].imshow(wordcloud2, interpolation='bilinear')
axes[1].set_title('부정 감성 키워드 (Negative Sentiment Keywords)', 
                  fontsize=16, fontweight='bold', pad=20)
axes[1].axis('off')

plt.tight_layout()

# 저장
output_path = r'C:\junwoo\AI_Project_01_Team6\data\Community_data\viz_03_wordcloud.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 저장 완료: {output_path}")

# Top 20 키워드 출력
print("\n📊 상위 20개 키워드:")
for i, (keyword, count) in enumerate(keyword_counts.most_common(20), 1):
    print(f"{i:2d}. {keyword:20s}: {count:5d}회")

plt.show()
