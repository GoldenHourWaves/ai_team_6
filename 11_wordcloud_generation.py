"""
Task 11: 워드클라우드 생성
감성 점수 기준으로 긍정/부정 댓글 분리 후 워드클라우드 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from wordcloud import WordCloud
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
COMMUNITY_DIR = Path("data/Community_data")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 감성 매핑
SENTIMENT_MAP = {
    'Positive': 1.0,
    'Hopeful': 0.7,
    'Optimistic': 0.8,
    'Neutral': 0.0,
    'Skeptical': -0.3,
    'Skeptic': -0.3,
    'Fear': -0.8,
    'Panic': -0.9,
    'Negative': -1.0,
    'Bearish': -0.6,
    'Bullish': 0.6,
    'Worried': -0.5,
    'Anxious': -0.7,
    'Excited': 0.8,
    'FOMO': 0.5,
    'FUD': -0.7,
    'Anger': -0.8,
    'Analytical': 0.0
}

def load_community_data():
    """커뮤니티 데이터 로드"""
    
    print("\n" + "=" * 80)
    print("📂 커뮤니티 데이터 로드")
    print("=" * 80)
    
    file_path = COMMUNITY_DIR / "FINAL_10K_RECORDS.csv"
    df = pd.read_csv(file_path)
    
    # 감성 점수 변환
    df['sentiment_score'] = df['sentiment'].map(SENTIMENT_MAP)
    df['sentiment_score'].fillna(0, inplace=True)
    
    print(f"\n✅ 데이터 로드 완료: {df.shape}")
    print(f"   평균 감성 점수: {df['sentiment_score'].mean():.3f}")
    
    return df

def extract_keywords_by_sentiment(df):
    """감성별로 키워드 추출"""
    
    print("\n" + "=" * 80)
    print("🔍 감성별 키워드 추출")
    print("=" * 80)
    
    # 긍정 댓글 (sentiment_score > 0.3)
    positive_df = df[df['sentiment_score'] > 0.3]
    
    # 부정 댓글 (sentiment_score < -0.3)
    negative_df = df[df['sentiment_score'] < -0.3]
    
    # 중립 댓글
    neutral_df = df[(df['sentiment_score'] >= -0.3) & (df['sentiment_score'] <= 0.3)]
    
    print(f"\n📊 감성 분포:")
    print(f"   긍정 댓글: {len(positive_df)}개 ({len(positive_df)/len(df)*100:.1f}%)")
    print(f"   부정 댓글: {len(negative_df)}개 ({len(negative_df)/len(df)*100:.1f}%)")
    print(f"   중립 댓글: {len(neutral_df)}개 ({len(neutral_df)/len(df)*100:.1f}%)")
    
    # 키워드 추출
    def extract_keywords(data_df):
        keywords = []
        for idx, row in data_df.iterrows():
            if pd.notna(row['keywords']):
                kw_list = [k.strip() for k in str(row['keywords']).split(',')]
                keywords.extend(kw_list)
        return keywords
    
    positive_keywords = extract_keywords(positive_df)
    negative_keywords = extract_keywords(negative_df)
    neutral_keywords = extract_keywords(neutral_df)
    
    print(f"\n📊 추출된 키워드 수:")
    print(f"   긍정: {len(positive_keywords)}개")
    print(f"   부정: {len(negative_keywords)}개")
    print(f"   중립: {len(neutral_keywords)}개")
    
    return positive_keywords, negative_keywords, neutral_keywords

def analyze_keyword_frequency(keywords, sentiment_type):
    """키워드 빈도 분석"""
    
    print(f"\n📊 {sentiment_type} 키워드 빈도 분석:")
    print("-" * 80)
    
    keyword_counts = Counter(keywords)
    top_20 = keyword_counts.most_common(20)
    
    for i, (keyword, count) in enumerate(top_20, 1):
        print(f"   {i:2d}. {keyword:30s} : {count:4d}회")
    
    return keyword_counts

def create_wordcloud(keywords, title, output_filename, colormap='viridis'):
    """워드클라우드 생성"""
    
    print(f"\n📈 '{title}' 워드클라우드 생성 중...")
    
    if len(keywords) == 0:
        print(f"⚠️  키워드가 없어 워드클라우드를 생성할 수 없습니다.")
        return None
    
    # 키워드를 텍스트로 결합
    text = ' '.join(keywords)
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color='white',
        colormap=colormap,
        max_words=100,
        relative_scaling=0.5,
        min_font_size=10,
        collocations=False  # 단어 조합 방지
    ).generate(text)
    
    # 시각화
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    
    plt.tight_layout(pad=0)
    
    output_file = OUTPUT_DIR / output_filename
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 워드클라우드 저장: {output_file}")
    
    plt.show()
    
    return wordcloud

def create_combined_wordcloud(positive_kw, negative_kw, neutral_kw):
    """전체/긍정/부정 3개 워드클라우드를 한 화면에"""
    
    print("\n" + "=" * 80)
    print("📈 통합 워드클라우드 생성")
    print("=" * 80)
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('커뮤니티 감성별 워드클라우드', fontsize=20, fontweight='bold', y=0.98)
    
    # ===== 전체 키워드 워드클라우드 =====
    ax1 = axes[0, 0]
    all_keywords = positive_kw + negative_kw + neutral_kw
    if len(all_keywords) > 0:
        text = ' '.join(all_keywords)
        wc = WordCloud(width=800, height=600, background_color='white', 
                      colormap='viridis', max_words=80, 
                      collocations=False).generate(text)
        ax1.imshow(wc, interpolation='bilinear')
    ax1.axis('off')
    ax1.set_title('전체 키워드', fontsize=16, fontweight='bold', pad=10)
    
    # ===== 긍정 키워드 워드클라우드 =====
    ax2 = axes[0, 1]
    if len(positive_kw) > 0:
        text = ' '.join(positive_kw)
        wc = WordCloud(width=800, height=600, background_color='white', 
                      colormap='Greens', max_words=80,
                      collocations=False).generate(text)
        ax2.imshow(wc, interpolation='bilinear')
    else:
        ax2.text(0.5, 0.5, '긍정 키워드 없음', ha='center', va='center',
                fontsize=16, transform=ax2.transAxes)
    ax2.axis('off')
    ax2.set_title(f'긍정 키워드 ({len(positive_kw):,}개)', 
                 fontsize=16, fontweight='bold', pad=10, color='green')
    
    # ===== 부정 키워드 워드클라우드 =====
    ax3 = axes[1, 0]
    if len(negative_kw) > 0:
        text = ' '.join(negative_kw)
        wc = WordCloud(width=800, height=600, background_color='white', 
                      colormap='Reds', max_words=80,
                      collocations=False).generate(text)
        ax3.imshow(wc, interpolation='bilinear')
    else:
        ax3.text(0.5, 0.5, '부정 키워드 없음', ha='center', va='center',
                fontsize=16, transform=ax3.transAxes)
    ax3.axis('off')
    ax3.set_title(f'부정 키워드 ({len(negative_kw):,}개)', 
                 fontsize=16, fontweight='bold', pad=10, color='red')
    
    # ===== 중립 키워드 워드클라우드 =====
    ax4 = axes[1, 1]
    if len(neutral_kw) > 0:
        text = ' '.join(neutral_kw)
        wc = WordCloud(width=800, height=600, background_color='white', 
                      colormap='Blues', max_words=80,
                      collocations=False).generate(text)
        ax4.imshow(wc, interpolation='bilinear')
    else:
        ax4.text(0.5, 0.5, '중립 키워드 없음', ha='center', va='center',
                fontsize=16, transform=ax4.transAxes)
    ax4.axis('off')
    ax4.set_title(f'중립 키워드 ({len(neutral_kw):,}개)', 
                 fontsize=16, fontweight='bold', pad=10, color='blue')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "15_wordcloud_combined.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ 통합 워드클라우드 저장: {output_file}")
    
    plt.show()

def analyze_sentiment_keywords(df):
    """감성별 대표 키워드 분석"""
    
    print("\n" + "=" * 80)
    print("🔍 감성별 대표 키워드 분석")
    print("=" * 80)
    
    # 키워드별 평균 감성 점수 계산
    keyword_sentiment = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['keywords']):
            keywords = [k.strip() for k in str(row['keywords']).split(',')]
            for keyword in keywords:
                keyword_sentiment.append({
                    'keyword': keyword,
                    'sentiment_score': row['sentiment_score']
                })
    
    keyword_df = pd.DataFrame(keyword_sentiment)
    
    # 키워드별 평균 감성 및 빈도
    keyword_summary = keyword_df.groupby('keyword').agg({
        'sentiment_score': ['mean', 'count']
    }).reset_index()
    
    keyword_summary.columns = ['keyword', 'avg_sentiment', 'count']
    keyword_summary = keyword_summary[keyword_summary['count'] >= 5]  # 최소 5회 이상
    
    # 가장 긍정적 키워드
    most_positive = keyword_summary.nlargest(10, 'avg_sentiment')
    print(f"\n🟢 가장 긍정적 키워드 (Top 10):")
    for idx, row in most_positive.iterrows():
        print(f"   {row['keyword']:30s} | 감성: {row['avg_sentiment']:+.3f} | {row['count']:3.0f}회")
    
    # 가장 부정적 키워드
    most_negative = keyword_summary.nsmallest(10, 'avg_sentiment')
    print(f"\n🔴 가장 부정적 키워드 (Top 10):")
    for idx, row in most_negative.iterrows():
        print(f"   {row['keyword']:30s} | 감성: {row['avg_sentiment']:+.3f} | {row['count']:3.0f}회")
    
    # 특정 키워드 확인
    target_keywords = ['buying the dip', 'panic selling', 'crash', 'dump', 
                      'liquidation', 'whale', 'manipulation']
    
    print(f"\n🎯 주요 키워드 감성 점수:")
    for keyword in target_keywords:
        matches = keyword_summary[keyword_summary['keyword'].str.lower() == keyword.lower()]
        if len(matches) > 0:
            row = matches.iloc[0]
            emoji = "😊" if row['avg_sentiment'] > 0.2 else "😟" if row['avg_sentiment'] < -0.2 else "😐"
            print(f"   {emoji} {keyword:30s} | 감성: {row['avg_sentiment']:+.3f} | {row['count']:3.0f}회")
        else:
            print(f"   ❌ {keyword:30s} | 데이터 없음")

def create_keyword_frequency_chart(positive_counts, negative_counts):
    """키워드 빈도 비교 차트"""
    
    print("\n" + "=" * 80)
    print("📊 키워드 빈도 비교 차트 생성")
    print("=" * 80)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('감성별 Top 15 키워드 빈도', fontsize=18, fontweight='bold')
    
    # ===== 긍정 키워드 Top 15 =====
    ax1 = axes[0]
    if len(positive_counts) > 0:
        top_positive = positive_counts.most_common(15)
        keywords = [k for k, v in top_positive]
        counts = [v for k, v in top_positive]
        
        y_pos = np.arange(len(keywords))
        ax1.barh(y_pos, counts, color='green', alpha=0.7, edgecolor='black')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(keywords, fontsize=10)
        ax1.invert_yaxis()
        ax1.set_xlabel('빈도', fontsize=12, fontweight='bold')
        ax1.set_title('긍정 키워드 Top 15', fontsize=14, fontweight='bold', 
                     pad=10, color='green')
        ax1.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        # 값 표시
        for i, v in enumerate(counts):
            ax1.text(v + max(counts)*0.01, i, str(v), va='center', fontsize=9)
    
    # ===== 부정 키워드 Top 15 =====
    ax2 = axes[1]
    if len(negative_counts) > 0:
        top_negative = negative_counts.most_common(15)
        keywords = [k for k, v in top_negative]
        counts = [v for k, v in top_negative]
        
        y_pos = np.arange(len(keywords))
        ax2.barh(y_pos, counts, color='red', alpha=0.7, edgecolor='black')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(keywords, fontsize=10)
        ax2.invert_yaxis()
        ax2.set_xlabel('빈도', fontsize=12, fontweight='bold')
        ax2.set_title('부정 키워드 Top 15', fontsize=14, fontweight='bold', 
                     pad=10, color='red')
        ax2.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        # 값 표시
        for i, v in enumerate(counts):
            ax2.text(v + max(counts)*0.01, i, str(v), va='center', fontsize=9)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "16_keyword_frequency_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 키워드 빈도 차트 저장: {output_file}")
    
    plt.show()

def main():
    print("=" * 80)
    print("Task 11: 워드클라우드 생성")
    print("=" * 80)
    
    # 1. 데이터 로드
    df = load_community_data()
    
    # 2. 감성별 키워드 추출
    positive_kw, negative_kw, neutral_kw = extract_keywords_by_sentiment(df)
    
    # 3. 키워드 빈도 분석
    positive_counts = analyze_keyword_frequency(positive_kw, "긍정")
    negative_counts = analyze_keyword_frequency(negative_kw, "부정")
    neutral_counts = analyze_keyword_frequency(neutral_kw, "중립")
    
    # 4. 개별 워드클라우드 생성
    if len(positive_kw) > 0:
        create_wordcloud(positive_kw, '긍정 키워드 워드클라우드', 
                        'wordcloud_positive.png', colormap='Greens')
    
    if len(negative_kw) > 0:
        create_wordcloud(negative_kw, '부정 키워드 워드클라우드', 
                        'wordcloud_negative.png', colormap='Reds')
    
    # 5. 통합 워드클라우드
    create_combined_wordcloud(positive_kw, negative_kw, neutral_kw)
    
    # 6. 감성별 대표 키워드 분석
    analyze_sentiment_keywords(df)
    
    # 7. 키워드 빈도 비교 차트
    create_keyword_frequency_chart(positive_counts, negative_counts)
    
    # 8. 결과 저장
    keyword_freq_df = pd.DataFrame([
        {'sentiment': 'positive', 'keyword': k, 'count': v} 
        for k, v in positive_counts.most_common(50)
    ] + [
        {'sentiment': 'negative', 'keyword': k, 'count': v} 
        for k, v in negative_counts.most_common(50)
    ])
    keyword_freq_df.to_csv(OUTPUT_DIR / "keyword_frequency_by_sentiment.csv", 
                           index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 11 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '15_wordcloud_combined.png'}")
    print(f"   2. {OUTPUT_DIR / '16_keyword_frequency_comparison.png'}")
    print(f"   3. {OUTPUT_DIR / 'wordcloud_positive.png'}")
    print(f"   4. {OUTPUT_DIR / 'wordcloud_negative.png'}")
    print(f"   5. {OUTPUT_DIR / 'keyword_frequency_by_sentiment.csv'}")

if __name__ == "__main__":
    main()
