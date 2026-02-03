"""
Task 12: 네트워크 관계도 생성
뉴스 테마, 가격, 감성, OI 간의 상관관계 네트워크 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """데이터 로드"""
    
    print("\n" + "=" * 80)
    print("📂 데이터 로드")
    print("=" * 80)
    
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"✅ 데이터 로드 완료: {df.shape}")
    
    return df

def select_key_variables(df):
    """주요 변수 선택"""
    
    print("\n" + "=" * 80)
    print("🔍 주요 변수 선택")
    print("=" * 80)
    
    # 주요 변수 카테고리
    key_vars = {
        '가격': ['BTC_Price', 'BTC_Price_Speed'],
        '거시경제': ['M2SL', 'Yield_10Y', 'USD_Index'],
        '뉴스 감성': ['tone_mean', 'tone_pos_share', 'tone_neg_share'],
        '정치 테마': ['theme_cnt__EPU_POLICY', 'theme_cnt__LEADER', 
                     'theme_cnt__GENERAL_GOVERNMENT'],
        '경제 테마': ['theme_cnt__ECON_BITCOIN', 'theme_cnt__ECON_STOCKMARKET'],
        '파생상품': ['Open_Interest'],
        'SNS 감성': ['sns_engagement_total', 'sns_post_count']
    }
    
    # 존재하는 변수만 선택
    available_vars = {}
    for category, vars_list in key_vars.items():
        available = [v for v in vars_list if v in df.columns]
        if available:
            available_vars[category] = available
    
    print(f"\n📊 선택된 변수 카테고리:")
    total_vars = 0
    for category, vars_list in available_vars.items():
        print(f"   {category}: {len(vars_list)}개")
        for var in vars_list:
            print(f"      - {var}")
        total_vars += len(vars_list)
    
    print(f"\n✅ 총 {total_vars}개 변수 선택됨")
    
    return available_vars

def calculate_correlation_matrix(df, variables_dict):
    """상관관계 행렬 계산"""
    
    print("\n" + "=" * 80)
    print("📊 상관관계 행렬 계산")
    print("=" * 80)
    
    # 모든 변수를 하나의 리스트로
    all_vars = []
    var_categories = {}
    for category, vars_list in variables_dict.items():
        all_vars.extend(vars_list)
        for var in vars_list:
            var_categories[var] = category
    
    # 상관관계 계산
    corr_df = df[all_vars].corr()
    
    print(f"\n✅ 상관관계 행렬 크기: {corr_df.shape}")
    print(f"   변수 수: {len(all_vars)}")
    
    return corr_df, var_categories

def create_network_from_correlation(corr_df, var_categories, threshold=0.3):
    """상관관계 기반 네트워크 생성"""
    
    print("\n" + "=" * 80)
    print("🌐 네트워크 생성")
    print("=" * 80)
    
    print(f"\n📊 설정:")
    print(f"   상관관계 임계값: {threshold} (절대값)")
    
    # 네트워크 그래프 생성
    G = nx.Graph()
    
    # 노드 추가
    for var in corr_df.index:
        category = var_categories.get(var, '기타')
        G.add_node(var, category=category)
    
    print(f"   노드 수: {G.number_of_nodes()}개")
    
    # 엣지 추가 (임계값 이상의 상관관계)
    edge_count = 0
    for i, var1 in enumerate(corr_df.index):
        for j, var2 in enumerate(corr_df.columns):
            if i < j:  # 중복 방지
                corr_value = corr_df.loc[var1, var2]
                if abs(corr_value) >= threshold:
                    G.add_edge(var1, var2, weight=abs(corr_value), 
                             correlation=corr_value)
                    edge_count += 1
    
    print(f"   엣지 수: {edge_count}개")
    print(f"   평균 연결도: {2*edge_count/G.number_of_nodes():.2f}")
    
    return G

def analyze_network_centrality(G):
    """네트워크 중심성 분석"""
    
    print("\n" + "=" * 80)
    print("📊 네트워크 중심성 분석")
    print("=" * 80)
    
    # Degree Centrality (연결 중심성)
    degree_centrality = nx.degree_centrality(G)
    
    # Betweenness Centrality (매개 중심성)
    betweenness_centrality = nx.betweenness_centrality(G)
    
    # Closeness Centrality (근접 중심성)
    closeness_centrality = nx.closeness_centrality(G)
    
    # 결과를 DataFrame으로
    centrality_df = pd.DataFrame({
        'node': list(degree_centrality.keys()),
        'degree': list(degree_centrality.values()),
        'betweenness': list(betweenness_centrality.values()),
        'closeness': list(closeness_centrality.values())
    })
    
    centrality_df = centrality_df.sort_values('degree', ascending=False)
    
    print(f"\n🔝 연결 중심성(Degree Centrality) Top 10:")
    print("-" * 80)
    for idx, row in centrality_df.head(10).iterrows():
        print(f"   {row['node']:40s} | Degree: {row['degree']:.4f} | "
              f"Betweenness: {row['betweenness']:.4f}")
    
    print(f"\n🔝 매개 중심성(Betweenness Centrality) Top 5:")
    print("-" * 80)
    top_betweenness = centrality_df.nlargest(5, 'betweenness')
    for idx, row in top_betweenness.iterrows():
        print(f"   {row['node']:40s} | {row['betweenness']:.4f}")
    
    return centrality_df

def visualize_network(G, var_categories, centrality_df, output_file):
    """네트워크 시각화"""
    
    print("\n" + "=" * 80)
    print("📈 네트워크 시각화")
    print("=" * 80)
    
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # 카테고리별 색상
    category_colors = {
        '가격': '#FF6B6B',
        '거시경제': '#4ECDC4',
        '뉴스 감성': '#FFD93D',
        '정치 테마': '#95E1D3',
        '경제 테마': '#F38181',
        '파생상품': '#AA96DA',
        'SNS 감성': '#FCBAD3',
        '기타': '#A8E6CF'
    }
    
    # 노드 색상
    node_colors = [category_colors.get(var_categories.get(node, '기타'), '#gray') 
                   for node in G.nodes()]
    
    # 노드 크기 (중심성에 비례)
    centrality_dict = dict(zip(centrality_df['node'], centrality_df['degree']))
    node_sizes = [centrality_dict.get(node, 0) * 5000 + 300 for node in G.nodes()]
    
    # 레이아웃
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 엣지 그리기
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    correlations = [G[u][v]['correlation'] for u, v in edges]
    
    # 양의 상관관계와 음의 상관관계 분리
    positive_edges = [(u, v) for u, v in edges if G[u][v]['correlation'] > 0]
    negative_edges = [(u, v) for u, v in edges if G[u][v]['correlation'] < 0]
    
    positive_weights = [G[u][v]['weight'] for u, v in positive_edges]
    negative_weights = [G[u][v]['weight'] for u, v in negative_edges]
    
    # 양의 상관관계 (초록색)
    nx.draw_networkx_edges(G, pos, edgelist=positive_edges, 
                          width=[w*3 for w in positive_weights],
                          alpha=0.5, edge_color='green', ax=ax)
    
    # 음의 상관관계 (빨간색)
    nx.draw_networkx_edges(G, pos, edgelist=negative_edges, 
                          width=[w*3 for w in negative_weights],
                          alpha=0.5, edge_color='red', ax=ax)
    
    # 노드 그리기
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='black', linewidths=2, ax=ax)
    
    # 라벨 (주요 노드만)
    top_nodes = centrality_df.head(15)['node'].tolist()
    labels = {node: node for node in G.nodes() if node in top_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, 
                           font_weight='bold', ax=ax)
    
    # 범례
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color, markersize=12, 
                                 label=category, markeredgecolor='black', 
                                 markeredgewidth=1.5)
                      for category, color in category_colors.items()]
    
    legend_elements.append(plt.Line2D([0], [0], color='green', linewidth=3, 
                                     label='양의 상관관계', alpha=0.7))
    legend_elements.append(plt.Line2D([0], [0], color='red', linewidth=3, 
                                     label='음의 상관관계', alpha=0.7))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
             framealpha=0.9, edgecolor='black')
    
    ax.set_title('비트코인 급락 요인 네트워크 분석\n(변수 간 상관관계 기반)', 
                fontsize=20, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ 네트워크 그래프 저장: {output_file}")
    
    plt.show()

def create_simplified_network(df, output_file):
    """단순화된 네트워크 (주요 변수만)"""
    
    print("\n" + "=" * 80)
    print("📊 단순화 네트워크 생성")
    print("=" * 80)
    
    # 핵심 변수만 선택
    core_vars = {
        'BTC_Price': '가격',
        'tone_mean': '뉴스 감성',
        'tone_neg_share': '뉴스 부정',
        'M2SL': 'M2 통화량',
        'Yield_10Y': '10년물 금리',
        'USD_Index': '달러 인덱스',
        'Open_Interest': 'Open Interest',
        'theme_cnt__EPU_POLICY': '정책 테마',
        'theme_cnt__ECON_BITCOIN': '비트코인 테마'
    }
    
    available_core = {k: v for k, v in core_vars.items() if k in df.columns}
    
    print(f"\n📊 핵심 변수: {len(available_core)}개")
    for var, label in available_core.items():
        print(f"   - {var} ({label})")
    
    # 상관관계 계산
    corr_df = df[list(available_core.keys())].corr()
    
    # 네트워크 생성
    G = nx.Graph()
    
    # 노드 추가 (레이블 사용)
    for var, label in available_core.items():
        G.add_node(label, original=var)
    
    # 엣지 추가 (강한 상관관계만)
    threshold = 0.4
    for i, var1 in enumerate(corr_df.index):
        for j, var2 in enumerate(corr_df.columns):
            if i < j:
                corr_value = corr_df.loc[var1, var2]
                if abs(corr_value) >= threshold:
                    label1 = available_core[var1]
                    label2 = available_core[var2]
                    G.add_edge(label1, label2, weight=abs(corr_value), 
                             correlation=corr_value)
    
    print(f"\n✅ 단순화 네트워크:")
    print(f"   노드: {G.number_of_nodes()}개")
    print(f"   엣지: {G.number_of_edges()}개")
    
    # 시각화
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 레이아웃
    pos = nx.spring_layout(G, k=3, iterations=100, seed=42)
    
    # 노드 색상 (카테고리별)
    node_colors = {
        '가격': '#FF6B6B',
        '뉴스 감성': '#FFD93D',
        '뉴스 부정': '#FFA500',
        'M2 통화량': '#4ECDC4',
        '10년물 금리': '#95E1D3',
        '달러 인덱스': '#5DADE2',
        'Open Interest': '#AA96DA',
        '정책 테마': '#F8B500',
        '비트코인 테마': '#F38181'
    }
    
    colors = [node_colors.get(node, '#gray') for node in G.nodes()]
    
    # 중심성 계산
    degree_cent = nx.degree_centrality(G)
    node_sizes = [degree_cent[node] * 4000 + 500 for node in G.nodes()]
    
    # 엣지 분리
    positive_edges = [(u, v) for u, v in G.edges() if G[u][v]['correlation'] > 0]
    negative_edges = [(u, v) for u, v in G.edges() if G[u][v]['correlation'] < 0]
    
    pos_weights = [G[u][v]['weight'] for u, v in positive_edges]
    neg_weights = [G[u][v]['weight'] for u, v in negative_edges]
    
    # 엣지 그리기
    nx.draw_networkx_edges(G, pos, edgelist=positive_edges, 
                          width=[w*5 for w in pos_weights],
                          alpha=0.6, edge_color='green', ax=ax,
                          style='solid')
    
    nx.draw_networkx_edges(G, pos, edgelist=negative_edges, 
                          width=[w*5 for w in neg_weights],
                          alpha=0.6, edge_color='red', ax=ax,
                          style='dashed')
    
    # 노드 그리기
    nx.draw_networkx_nodes(G, pos, node_color=colors, 
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='black', linewidths=3, ax=ax)
    
    # 라벨
    nx.draw_networkx_labels(G, pos, font_size=12, 
                           font_weight='bold', font_family='Malgun Gothic', ax=ax)
    
    # 엣지 라벨 (상관계수)
    edge_labels = {(u, v): f"{G[u][v]['correlation']:+.2f}" 
                   for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=9, ax=ax)
    
    # 범례
    legend_elements = [
        plt.Line2D([0], [0], color='green', linewidth=4, 
                  label='양의 상관관계 (|r| ≥ 0.4)', alpha=0.7),
        plt.Line2D([0], [0], color='red', linewidth=4, linestyle='--',
                  label='음의 상관관계 (|r| ≥ 0.4)', alpha=0.7)
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
             framealpha=0.9, edgecolor='black')
    
    ax.set_title('핵심 변수 간 상관관계 네트워크\n(노드 크기: 연결 중심성)', 
                fontsize=18, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ 단순화 네트워크 저장: {output_file}")
    
    plt.show()
    
    return G

def main():
    print("=" * 80)
    print("Task 12: 네트워크 관계도 생성")
    print("=" * 80)
    
    # 1. 데이터 로드
    df = load_data()
    
    # 2. 주요 변수 선택
    variables_dict = select_key_variables(df)
    
    # 3. 상관관계 행렬 계산
    corr_df, var_categories = calculate_correlation_matrix(df, variables_dict)
    
    # 4. 네트워크 생성 (임계값 0.3)
    G = create_network_from_correlation(corr_df, var_categories, threshold=0.3)
    
    # 5. 중심성 분석
    centrality_df = analyze_network_centrality(G)
    
    # 6. 전체 네트워크 시각화
    visualize_network(G, var_categories, centrality_df, 
                     OUTPUT_DIR / "17_network_full.png")
    
    # 7. 단순화 네트워크 생성
    G_simple = create_simplified_network(df, OUTPUT_DIR / "18_network_simplified.png")
    
    # 8. 결과 저장
    centrality_df.to_csv(OUTPUT_DIR / "network_centrality.csv", 
                        index=False, encoding='utf-8-sig')
    
    # 상관관계 저장
    corr_df.to_csv(OUTPUT_DIR / "correlation_matrix.csv", encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 12 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '17_network_full.png'}")
    print(f"   2. {OUTPUT_DIR / '18_network_simplified.png'}")
    print(f"   3. {OUTPUT_DIR / 'network_centrality.csv'}")
    print(f"   4. {OUTPUT_DIR / 'correlation_matrix.csv'}")

if __name__ == "__main__":
    main()
