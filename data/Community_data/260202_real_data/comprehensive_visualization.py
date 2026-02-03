#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
October 2025 Crypto Crash - 커뮤니티 데이터 종합 시각화
145개 실제 URL 기반 비정형 데이터 분석

Required packages (from pyproject.toml):
- pandas, numpy, matplotlib, seaborn
- wordcloud, networkx
- scikit-learn, textblob, vadersentiment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from textblob import TextBlob
from vadersentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (koreanize-matplotlib 사용)
try:
    import koreanize_matplotlib
    koreanize_matplotlib.matplotlib_settings()
except:
    plt.rcParams['font.family'] = 'DejaVu Sans'

# 스타일 설정
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 100)
print("커뮤니티 데이터 종합 시각화 시작")
print("=" * 100)

# ============================================================================
# 1. 데이터 로드
# ============================================================================
print("\n[1/12] 데이터 로드 중...")

df = pd.read_csv('FINAL_COMMUNITY_DATASET_145.csv')
print(f"✅ {len(df)}개 레코드 로드 완료")
print(f"   컬럼: {len(df.columns)}개")
print(f"   플랫폼: X {len(df[df['platform']=='X'])}개, Reddit {len(df[df['platform']=='Reddit'])}개")

# ============================================================================
# 2. 기본 통계 확인
# ============================================================================
print("\n[2/12] 원본 데이터 확인...")

# 상위 10개 출력
print("\n📊 데이터 샘플 (상위 5개):")
print(df[['platform', 'author', 'title', 'category', 'sentiment', 'influence_score']].head())

print("\n📈 기본 통계:")
print(f"  카테고리 수: {df['category'].nunique()}개")
print(f"  고유 작성자: {df['author'].nunique()}명")
print(f"  평균 영향력 점수: {df['influence_score'].mean():.2f}")
print(f"  최대 영향력 점수: {df['influence_score'].max():.2f}")

# ============================================================================
# 3. 플랫폼별 분포 (파이 차트)
# ============================================================================
print("\n[3/12] 플랫폼별 분포 시각화...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 파이 차트
platform_counts = df['platform'].value_counts()
colors = ['#1DA1F2', '#FF4500']  # Twitter blue, Reddit orange
axes[0].pie(platform_counts, labels=platform_counts.index, autopct='%1.1f%%',
           colors=colors, startangle=90, textprops={'fontsize': 12})
axes[0].set_title('Platform Distribution', fontsize=14, fontweight='bold')

# 바 차트
axes[1].bar(platform_counts.index, platform_counts.values, color=colors, alpha=0.7, edgecolor='black')
axes[1].set_ylabel('Number of Posts', fontsize=12)
axes[1].set_title('Posts by Platform', fontsize=14, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(platform_counts.values):
    axes[1].text(i, v + 2, str(v), ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('01_platform_distribution.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 01_platform_distribution.png")
plt.close()

# ============================================================================
# 4. 카테고리별 분포 (수평 바 차트)
# ============================================================================
print("\n[4/12] 카테고리별 분포 시각화...")

fig, ax = plt.subplots(figsize=(12, 8))

category_counts = df['category'].value_counts().sort_values()
colors_cat = plt.cm.Spectral(np.linspace(0, 1, len(category_counts)))

category_counts.plot(kind='barh', ax=ax, color=colors_cat, edgecolor='black', linewidth=0.8)
ax.set_xlabel('Number of Posts', fontsize=12, fontweight='bold')
ax.set_ylabel('Category', fontsize=12, fontweight='bold')
ax.set_title('Post Distribution by Category', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# 값 표시
for i, v in enumerate(category_counts.values):
    ax.text(v + 0.5, i, f'{v} ({v/len(df)*100:.1f}%)', 
            va='center', fontsize=10)

plt.tight_layout()
plt.savefig('02_category_distribution.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 02_category_distribution.png")
plt.close()

# ============================================================================
# 5. 감정 분석 (스택 바 차트 + 도넛 차트)
# ============================================================================
print("\n[5/12] 감정 분석 시각화...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 도넛 차트
sentiment_counts = df['sentiment'].value_counts()
colors_sent = {'Very_Negative': '#d62728', 'Negative': '#ff7f0e', 
               'Neutral': '#7f7f7f', 'Mixed': '#bcbd22', 'Positive': '#2ca02c'}
colors_list = [colors_sent.get(s, '#333333') for s in sentiment_counts.index]

wedges, texts, autotexts = axes[0].pie(sentiment_counts, labels=sentiment_counts.index, 
                                        autopct='%1.1f%%', colors=colors_list,
                                        startangle=90, pctdistance=0.85,
                                        textprops={'fontsize': 10})
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
axes[0].add_artist(centre_circle)
axes[0].set_title('Sentiment Distribution', fontsize=14, fontweight='bold')

# 플랫폼별 감정 비교
sentiment_platform = pd.crosstab(df['platform'], df['sentiment'])
sentiment_platform_pct = sentiment_platform.div(sentiment_platform.sum(axis=1), axis=0) * 100

sentiment_platform_pct.plot(kind='bar', stacked=True, ax=axes[1], 
                            color=[colors_sent.get(s, '#333333') for s in sentiment_platform_pct.columns],
                            edgecolor='black', linewidth=0.8)
axes[1].set_ylabel('Percentage (%)', fontsize=12)
axes[1].set_xlabel('Platform', fontsize=12)
axes[1].set_title('Sentiment by Platform', fontsize=14, fontweight='bold')
axes[1].legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=0)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('03_sentiment_analysis.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 03_sentiment_analysis.png")
plt.close()

# ============================================================================
# 6. 시간대별 분석 (바 차트)
# ============================================================================
print("\n[6/12] 시간대별 분석 시각화...")

fig, ax = plt.subplots(figsize=(14, 6))

time_counts = df['time_period'].value_counts().sort_values()
colors_time = plt.cm.viridis(np.linspace(0, 1, len(time_counts)))

time_counts.plot(kind='barh', ax=ax, color=colors_time, edgecolor='black', linewidth=0.8)
ax.set_xlabel('Number of Posts', fontsize=12, fontweight='bold')
ax.set_ylabel('Time Period', fontsize=12, fontweight='bold')
ax.set_title('Post Distribution by Time Period', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(time_counts.values):
    ax.text(v + 0.5, i, str(v), va='center', fontsize=10)

plt.tight_layout()
plt.savefig('04_time_period_distribution.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 04_time_period_distribution.png")
plt.close()

# ============================================================================
# 7. 영향력 점수 분석 (히스토그램 + 박스플롯)
# ============================================================================
print("\n[7/12] 영향력 점수 분석...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 히스토그램
axes[0, 0].hist(df['influence_score'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
axes[0, 0].axvline(df['influence_score'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {df["influence_score"].mean():.2f}')
axes[0, 0].axvline(df['influence_score'].median(), color='green', linestyle='--', 
                   linewidth=2, label=f'Median: {df["influence_score"].median():.2f}')
axes[0, 0].set_xlabel('Influence Score', fontsize=12)
axes[0, 0].set_ylabel('Frequency', fontsize=12)
axes[0, 0].set_title('Influence Score Distribution', fontsize=14, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# 플랫폼별 박스플롯
df.boxplot(column='influence_score', by='platform', ax=axes[0, 1], 
           patch_artist=True, grid=True)
axes[0, 1].set_title('Influence Score by Platform', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Platform', fontsize=12)
axes[0, 1].set_ylabel('Influence Score', fontsize=12)
plt.sca(axes[0, 1])
plt.xticks(rotation=0)

# 카테고리별 평균 영향력 (상위 10개)
category_influence = df.groupby('category')['influence_score'].mean().sort_values(ascending=False).head(10)
axes[1, 0].barh(range(len(category_influence)), category_influence.values, 
                color=plt.cm.plasma(np.linspace(0, 1, len(category_influence))),
                edgecolor='black', linewidth=0.8)
axes[1, 0].set_yticks(range(len(category_influence)))
axes[1, 0].set_yticklabels(category_influence.index, fontsize=10)
axes[1, 0].set_xlabel('Average Influence Score', fontsize=12)
axes[1, 0].set_title('Top 10 Categories by Avg Influence', fontsize=14, fontweight='bold')
axes[1, 0].grid(axis='x', alpha=0.3)

# 감정별 영향력
sentiment_influence = df.groupby('sentiment')['influence_score'].mean().sort_values(ascending=False)
axes[1, 1].bar(range(len(sentiment_influence)), sentiment_influence.values,
               color=[colors_sent.get(s, '#333333') for s in sentiment_influence.index],
               edgecolor='black', linewidth=0.8, alpha=0.8)
axes[1, 1].set_xticks(range(len(sentiment_influence)))
axes[1, 1].set_xticklabels(sentiment_influence.index, rotation=45, ha='right')
axes[1, 1].set_ylabel('Average Influence Score', fontsize=12)
axes[1, 1].set_title('Average Influence by Sentiment', fontsize=14, fontweight='bold')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('05_influence_score_analysis.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 05_influence_score_analysis.png")
plt.close()

# ============================================================================
# 8. 워드클라우드 (전체 + 플랫폼별)
# ============================================================================
print("\n[8/12] 워드클라우드 생성...")

# 제목에서 텍스트 추출
all_text = ' '.join(df['title'].astype(str))

# 불용어 설정
stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'can', 'this', 'that', 'these', 'those', 'it', 'its', 'as'])

fig, axes = plt.subplots(2, 2, figsize=(20, 16))

# 전체 워드클라우드
wc_all = WordCloud(width=800, height=400, background_color='white', 
                   stopwords=stopwords, colormap='viridis', 
                   max_words=100, relative_scaling=0.5).generate(all_text)
axes[0, 0].imshow(wc_all, interpolation='bilinear')
axes[0, 0].axis('off')
axes[0, 0].set_title('All Posts - Word Cloud', fontsize=16, fontweight='bold', pad=20)

# X (Twitter) 워드클라우드
twitter_text = ' '.join(df[df['platform'] == 'X']['title'].astype(str))
wc_twitter = WordCloud(width=800, height=400, background_color='white',
                      stopwords=stopwords, colormap='Blues',
                      max_words=80, relative_scaling=0.5).generate(twitter_text)
axes[0, 1].imshow(wc_twitter, interpolation='bilinear')
axes[0, 1].axis('off')
axes[0, 1].set_title('X (Twitter) Posts - Word Cloud', fontsize=16, fontweight='bold', pad=20)

# Reddit 워드클라우드
reddit_text = ' '.join(df[df['platform'] == 'Reddit']['title'].astype(str))
wc_reddit = WordCloud(width=800, height=400, background_color='white',
                     stopwords=stopwords, colormap='Oranges',
                     max_words=80, relative_scaling=0.5).generate(reddit_text)
axes[1, 0].imshow(wc_reddit, interpolation='bilinear')
axes[1, 0].axis('off')
axes[1, 0].set_title('Reddit Posts - Word Cloud', fontsize=16, fontweight='bold', pad=20)

# 부정 감정 워드클라우드
negative_text = ' '.join(df[df['sentiment'].isin(['Negative', 'Very_Negative'])]['title'].astype(str))
wc_negative = WordCloud(width=800, height=400, background_color='white',
                       stopwords=stopwords, colormap='Reds',
                       max_words=80, relative_scaling=0.5).generate(negative_text)
axes[1, 1].imshow(wc_negative, interpolation='bilinear')
axes[1, 1].axis('off')
axes[1, 1].set_title('Negative Sentiment - Word Cloud', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('06_wordclouds.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 06_wordclouds.png")
plt.close()

# ============================================================================
# 9. 키워드 히트맵
# ============================================================================
print("\n[9/12] 키워드 히트맵 생성...")

# 키워드 컬럼 추출
keyword_cols = [col for col in df.columns if col.startswith('kw_')]
keyword_data = df[keyword_cols].astype(int)

# 키워드별 출현 빈도
keyword_freq = keyword_data.sum().sort_values(ascending=False)

# 카테고리별 키워드 출현
category_keyword = pd.DataFrame()
for category in df['category'].unique():
    category_data = df[df['category'] == category][keyword_cols].sum()
    category_keyword[category] = category_data

# 정규화 (각 카테고리별 비율)
category_keyword_norm = category_keyword.div(df['category'].value_counts(), axis=1).fillna(0)

# 히트맵
fig, axes = plt.subplots(2, 1, figsize=(16, 14))

# 플랫폼별 키워드 히트맵
platform_keyword = pd.DataFrame()
for platform in df['platform'].unique():
    platform_data = df[df['platform'] == platform][keyword_cols].sum()
    platform_keyword[platform] = platform_data

platform_keyword_norm = platform_keyword.div(df['platform'].value_counts(), axis=1).T
sns.heatmap(platform_keyword_norm, annot=True, fmt='.2f', cmap='YlOrRd', 
           cbar_kws={'label': 'Keyword Frequency per Post'},
           linewidths=0.5, ax=axes[0])
axes[0].set_title('Keyword Frequency by Platform (Normalized)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('')
axes[0].set_yticklabels([col.replace('kw_', '') for col in platform_keyword_norm.index], rotation=0)

# 카테고리별 키워드 히트맵 (상위 8개 카테고리)
top_categories = df['category'].value_counts().head(8).index
category_keyword_top = category_keyword_norm[top_categories].T
sns.heatmap(category_keyword_top, annot=True, fmt='.2f', cmap='viridis',
           cbar_kws={'label': 'Keyword Frequency per Post'},
           linewidths=0.5, ax=axes[1])
axes[1].set_title('Keyword Frequency by Top 8 Categories (Normalized)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Category', fontsize=12)
axes[1].set_yticklabels([col.replace('kw_', '') for col in category_keyword_top.index], rotation=0)

plt.tight_layout()
plt.savefig('07_keyword_heatmap.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 07_keyword_heatmap.png")
plt.close()

# ============================================================================
# 10. 상관관계 히트맵 (키워드 공동 출현)
# ============================================================================
print("\n[10/12] 키워드 공동 출현 히트맵...")

# 키워드 공동 출현 행렬
keyword_cooccurrence = keyword_data.T.dot(keyword_data)

# 대각선 제거 (자기 자신과의 상관관계)
np.fill_diagonal(keyword_cooccurrence.values, 0)

fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(keyword_cooccurrence, annot=True, fmt='d', cmap='coolwarm',
           cbar_kws={'label': 'Co-occurrence Count'},
           linewidths=0.5, ax=ax, square=True)
ax.set_title('Keyword Co-occurrence Matrix', fontsize=14, fontweight='bold')
ax.set_xticklabels([col.replace('kw_', '') for col in keyword_cooccurrence.columns], rotation=45, ha='right')
ax.set_yticklabels([col.replace('kw_', '') for col in keyword_cooccurrence.index], rotation=0)

plt.tight_layout()
plt.savefig('08_keyword_cooccurrence.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 08_keyword_cooccurrence.png")
plt.close()

# ============================================================================
# 11. 네트워크 그래프 (작성자-카테고리 관계)
# ============================================================================
print("\n[11/12] 네트워크 그래프 생성...")

# 상위 작성자 선택 (5회 이상 등장)
author_counts = df['author'].value_counts()
top_authors = author_counts[author_counts >= 3].index[:15]

# 네트워크 생성
G = nx.Graph()

for author in top_authors:
    author_posts = df[df['author'] == author]
    for category in author_posts['category'].unique():
        count = len(author_posts[author_posts['category'] == category])
        G.add_edge(author, category, weight=count)

# 시각화
fig, ax = plt.subplots(figsize=(16, 12))

pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

# 노드 색상 (작성자 vs 카테고리)
node_colors = []
for node in G.nodes():
    if node in top_authors:
        node_colors.append('#1DA1F2')  # Blue for authors
    else:
        node_colors.append('#FF4500')  # Orange for categories

# 노드 크기
node_sizes = []
for node in G.nodes():
    if node in top_authors:
        node_sizes.append(1000)
    else:
        node_sizes.append(800)

# 엣지 두께
edges = G.edges()
weights = [G[u][v]['weight'] for u, v in edges]
max_weight = max(weights) if weights else 1
edge_widths = [3 * w / max_weight for w in weights]

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                       alpha=0.8, ax=ax)
nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)

ax.set_title('Author-Category Network (Top 15 Authors, 3+ Posts)', 
            fontsize=14, fontweight='bold')
ax.axis('off')

# 범례
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#1DA1F2', label='Authors'),
                  Patch(facecolor='#FF4500', label='Categories')]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('09_network_graph.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 09_network_graph.png")
plt.close()

# ============================================================================
# 12. 종합 대시보드
# ============================================================================
print("\n[12/12] 종합 대시보드 생성...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. 플랫폼 분포
ax1 = fig.add_subplot(gs[0, 0])
platform_counts.plot(kind='pie', ax=ax1, colors=colors, autopct='%1.1f%%',
                    startangle=90, textprops={'fontsize': 10})
ax1.set_title('Platform Distribution', fontsize=12, fontweight='bold')
ax1.set_ylabel('')

# 2. 상위 카테고리
ax2 = fig.add_subplot(gs[0, 1:])
top_cats = df['category'].value_counts().head(8)
ax2.barh(range(len(top_cats)), top_cats.values, 
        color=plt.cm.Spectral(np.linspace(0, 1, len(top_cats))),
        edgecolor='black', linewidth=0.8)
ax2.set_yticks(range(len(top_cats)))
ax2.set_yticklabels(top_cats.index, fontsize=9)
ax2.set_xlabel('Count', fontsize=10)
ax2.set_title('Top 8 Categories', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# 3. 감정 분포
ax3 = fig.add_subplot(gs[1, 0])
sentiment_counts.plot(kind='bar', ax=ax3, 
                     color=[colors_sent.get(s, '#333333') for s in sentiment_counts.index],
                     edgecolor='black', linewidth=0.8)
ax3.set_xlabel('')
ax3.set_ylabel('Count', fontsize=10)
ax3.set_title('Sentiment Distribution', fontsize=12, fontweight='bold')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=9)
ax3.grid(axis='y', alpha=0.3)

# 4. 시간대 분포
ax4 = fig.add_subplot(gs[1, 1])
time_counts_top = df['time_period'].value_counts().head(5)
ax4.bar(range(len(time_counts_top)), time_counts_top.values,
       color=plt.cm.viridis(np.linspace(0, 1, len(time_counts_top))),
       edgecolor='black', linewidth=0.8)
ax4.set_xticks(range(len(time_counts_top)))
ax4.set_xticklabels(time_counts_top.index, rotation=45, ha='right', fontsize=8)
ax4.set_ylabel('Count', fontsize=10)
ax4.set_title('Top 5 Time Periods', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# 5. 영향력 분포
ax5 = fig.add_subplot(gs[1, 2])
ax5.hist(df['influence_score'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
ax5.axvline(df['influence_score'].mean(), color='red', linestyle='--', linewidth=2)
ax5.set_xlabel('Influence Score', fontsize=10)
ax5.set_ylabel('Frequency', fontsize=10)
ax5.set_title('Influence Score Distribution', fontsize=12, fontweight='bold')
ax5.grid(alpha=0.3)

# 6. 상위 키워드
ax6 = fig.add_subplot(gs[2, :2])
top_keywords = keyword_freq.head(10)
ax6.barh(range(len(top_keywords)), top_keywords.values,
        color=plt.cm.plasma(np.linspace(0, 1, len(top_keywords))),
        edgecolor='black', linewidth=0.8)
ax6.set_yticks(range(len(top_keywords)))
ax6.set_yticklabels([kw.replace('kw_', '') for kw in top_keywords.index], fontsize=9)
ax6.set_xlabel('Frequency', fontsize=10)
ax6.set_title('Top 10 Keywords', fontsize=12, fontweight='bold')
ax6.grid(axis='x', alpha=0.3)

# 7. 통계 정보
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')
stats_text = f"""
DATASET STATISTICS
{'='*35}

Total Posts: {len(df)}
Unique Authors: {df['author'].nunique()}
Categories: {df['category'].nunique()}

Platform:
  • X (Twitter): {len(df[df['platform']=='X'])} ({len(df[df['platform']=='X'])/len(df)*100:.1f}%)
  • Reddit: {len(df[df['platform']=='Reddit'])} ({len(df[df['platform']=='Reddit'])/len(df)*100:.1f}%)

Sentiment:
  • Negative: {len(df[df['sentiment'].isin(['Negative','Very_Negative'])])} ({len(df[df['sentiment'].isin(['Negative','Very_Negative'])])/len(df)*100:.1f}%)
  • Positive: {len(df[df['sentiment']=='Positive'])} ({len(df[df['sentiment']=='Positive'])/len(df)*100:.1f}%)

Influence Score:
  • Mean: {df['influence_score'].mean():.2f}
  • Max: {df['influence_score'].max():.2f}
  • Min: {df['influence_score'].min():.2f}

Top Keywords:
  1. {keyword_freq.index[0].replace('kw_', '')}: {keyword_freq.values[0]}
  2. {keyword_freq.index[1].replace('kw_', '')}: {keyword_freq.values[1]}
  3. {keyword_freq.index[2].replace('kw_', '')}: {keyword_freq.values[2]}
"""
ax7.text(0.05, 0.95, stats_text, transform=ax7.transAxes,
        fontsize=9, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

fig.suptitle('October 2025 Crypto Crash - Community Data Dashboard', 
            fontsize=16, fontweight='bold', y=0.98)

plt.savefig('10_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
print("✅ 저장: 10_comprehensive_dashboard.png")
plt.close()

# ============================================================================
# 최종 요약
# ============================================================================
print("\n" + "=" * 100)
print("시각화 완료!")
print("=" * 100)

print("\n📁 생성된 파일:")
viz_files = [
    "01_platform_distribution.png",
    "02_category_distribution.png", 
    "03_sentiment_analysis.png",
    "04_time_period_distribution.png",
    "05_influence_score_analysis.png",
    "06_wordclouds.png",
    "07_keyword_heatmap.png",
    "08_keyword_cooccurrence.png",
    "09_network_graph.png",
    "10_comprehensive_dashboard.png"
]

for i, file in enumerate(viz_files, 1):
    print(f"  {i:2d}. {file}")

print("\n✅ 총 10개 시각화 파일 생성 완료")
print("✅ 해상도: 300 DPI (고화질)")
print("✅ 모든 차트 PNG 형식으로 저장")
