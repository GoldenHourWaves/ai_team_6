"""
Streamlit Dashboard: Bitcoin Market Crash Analysis
비트코인 급락 분석 대시보드
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title="Bitcoin Crash Analysis Dashboard",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")

@st.cache_data
def load_data():
    """데이터 로드 (캐싱)"""
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_sentiment_data():
    """감성 분석 데이터 로드"""
    try:
        df = pd.read_csv(OUTPUT_DIR / "sentiment_daily_analysis.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return None

def main():
    # 제목
    st.title("📉 Bitcoin Market Crash Analysis Dashboard")
    st.markdown("### 2025년 10월 비트코인 급락 분석")
    st.markdown("---")
    
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        df = load_data()
        sentiment_df = load_sentiment_data()
    
    # 사이드바
    st.sidebar.header("⚙️ 설정")
    
    # 날짜 범위 선택
    st.sidebar.subheader("📅 날짜 범위")
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # 타임스탬프를 날짜로 변환
    min_date_val = pd.Timestamp(min_date).date()
    max_date_val = pd.Timestamp(max_date).date()
    
    date_range = st.sidebar.date_input(
        "날짜 선택",
        value=(min_date_val, max_date_val),
        min_value=min_date_val,
        max_value=max_date_val
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        # 타임스탬프로 변환하여 비교
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)
        mask = (df['date'] >= start_ts) & (df['date'] <= end_ts)
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
    
    # 급락일 표시
    crash_date = pd.Timestamp('2025-10-10')
    
    # 메트릭 카드
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 주요 지표")
    
    if len(filtered_df) > 0:
        avg_price = filtered_df['BTC_Price'].mean()
        max_price = filtered_df['BTC_Price'].max()
        min_price = filtered_df['BTC_Price'].min()
        
        col1, col2 = st.sidebar.columns(2)
        col1.metric("평균 가격", f"${avg_price:,.0f}")
        col2.metric("최고가", f"${max_price:,.0f}")
        
        col3, col4 = st.sidebar.columns(2)
        col3.metric("최저가", f"${min_price:,.0f}")
        col4.metric("변동폭", f"${max_price - min_price:,.0f}")
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 가격 분석", 
        "💬 감성 분석", 
        "🌍 거시경제", 
        "📊 상관관계",
        "🔍 종합 분석"
    ])
    
    # ===== 탭 1: 가격 분석 =====
    with tab1:
        st.header("📈 비트코인 가격 분석")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 가격 차트
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['BTC_Price'],
                mode='lines+markers',
                name='BTC Price',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=5)
            ))
            
            # 급락일 표시
            if crash_date in filtered_df['date'].values:
                crash_row = filtered_df[filtered_df['date'] == crash_date].iloc[0]
                
                # 수직선 추가 (shapes 사용)
                fig.add_shape(
                    type="line",
                    x0=crash_date,
                    x1=crash_date,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="red", width=2, dash="dash")
                )
                
                # 주석 추가
                fig.add_annotation(
                    x=crash_date,
                    y=1,
                    yref="paper",
                    text="10/10 Crash",
                    showarrow=False,
                    font=dict(color="red", size=12),
                    yshift=10
                )
                
                fig.add_trace(go.Scatter(
                    x=[crash_date],
                    y=[crash_row['BTC_Price']],
                    mode='markers',
                    name='Crash Point',
                    marker=dict(color='red', size=15, symbol='x')
                ))
            
            fig.update_layout(
                title="BTC 가격 추이",
                xaxis_title="날짜",
                yaxis_title="가격 (USD)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 가격 통계")
            
            if len(filtered_df) > 0:
                # 가격 변화율 계산
                filtered_df['price_change_pct'] = filtered_df['BTC_Price'].pct_change() * 100
                
                st.metric("평균 가격", f"${filtered_df['BTC_Price'].mean():,.2f}")
                st.metric("표준편차", f"${filtered_df['BTC_Price'].std():,.2f}")
                st.metric("변동계수", f"{(filtered_df['BTC_Price'].std() / filtered_df['BTC_Price'].mean() * 100):.2f}%")
                
                st.markdown("---")
                st.metric("최대 상승", f"+{filtered_df['price_change_pct'].max():.2f}%")
                st.metric("최대 하락", f"{filtered_df['price_change_pct'].min():.2f}%")
                
                # 급락일 정보
                if crash_date in filtered_df['date'].values:
                    crash_row = filtered_df[filtered_df['date'] == crash_date].iloc[0]
                    st.markdown("---")
                    st.markdown("**🔴 급락일 (2025-10-10)**")
                    st.metric("가격", f"${crash_row['BTC_Price']:,.2f}")
                    st.metric("변화율", f"{crash_row['price_change_pct']:.2f}%")
        
        # Open Interest
        st.subheader("📊 Open Interest vs 가격")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['Open_Interest'],
            mode='lines',
            name='Open Interest',
            yaxis='y',
            line=dict(color='#FF6B6B', width=2)
        ))
        
        fig2.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['BTC_Price'],
            mode='lines',
            name='BTC Price',
            yaxis='y2',
            line=dict(color='#4ECDC4', width=2)
        ))
        
        if crash_date in filtered_df['date'].values:
            fig2.add_shape(
                type="line",
                x0=crash_date, x1=crash_date,
                y0=0, y1=1, yref="paper",
                line=dict(color="red", width=2, dash="dash")
            )
        
        fig2.update_layout(
            title="Open Interest와 BTC 가격 비교",
            xaxis_title="날짜",
            yaxis=dict(title="Open Interest", side="left"),
            yaxis2=dict(title="BTC Price (USD)", overlaying="y", side="right"),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # ===== 탭 2: 감성 분석 =====
    with tab2:
        st.header("💬 뉴스 및 커뮤니티 감성 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 뉴스 감성
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['tone_mean'],
                mode='lines+markers',
                name='뉴스 감성 (tone_mean)',
                line=dict(color='#FFD93D', width=3),
                fill='tozeroy',
                fillcolor='rgba(255, 217, 61, 0.3)'
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            if crash_date in filtered_df['date'].values:
                fig.add_shape(
                    type="line",
                    x0=crash_date, x1=crash_date,
                    y0=0, y1=1, yref="paper",
                    line=dict(color="red", width=2, dash="dash")
                )
            
            fig.update_layout(
                title="뉴스 감성 추이 (tone_mean)",
                xaxis_title="날짜",
                yaxis_title="감성 점수",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 커뮤니티 감성
            if sentiment_df is not None:
                # 날짜 필터링
                if len(date_range) == 2:
                    start_ts = pd.Timestamp(start_date)
                    end_ts = pd.Timestamp(end_date)
                    mask = (sentiment_df['date'] >= start_ts) & (sentiment_df['date'] <= end_ts)
                    filtered_sentiment = sentiment_df[mask].copy()
                else:
                    filtered_sentiment = sentiment_df.copy()
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=filtered_sentiment['date'],
                    y=filtered_sentiment['sentiment_mean'],
                    mode='lines+markers',
                    name='커뮤니티 감성',
                    line=dict(color='#FF6B6B', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(255, 107, 107, 0.3)'
                ))
                
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                if crash_date in filtered_sentiment['date'].values:
                    fig.add_shape(
                        type="line",
                        x0=crash_date, x1=crash_date,
                        y0=0, y1=1, yref="paper",
                        line=dict(color="red", width=2, dash="dash")
                    )
                
                fig.update_layout(
                    title="커뮤니티 감성 추이",
                    xaxis_title="날짜",
                    yaxis_title="감성 점수",
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("커뮤니티 감성 데이터가 없습니다.")
        
        # 감성 비교
        st.subheader("📊 감성 지표 비교")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_tone = filtered_df['tone_mean'].mean()
            st.metric("평균 뉴스 감성", f"{avg_tone:.3f}", 
                     delta="긍정" if avg_tone > 0 else "부정")
        
        with col2:
            avg_pos = filtered_df['tone_pos_share'].mean()
            st.metric("평균 긍정 비율", f"{avg_pos*100:.1f}%")
        
        with col3:
            avg_neg = filtered_df['tone_neg_share'].mean()
            st.metric("평균 부정 비율", f"{avg_neg*100:.1f}%")
    
    # ===== 탭 3: 거시경제 =====
    with tab3:
        st.header("🌍 거시경제 지표")
        
        # 변수 선택
        macro_vars = ['M2SL', 'Yield_10Y', 'USD_Index']
        available_vars = [v for v in macro_vars if v in filtered_df.columns]
        
        selected_var = st.selectbox("지표 선택", available_vars)
        
        if selected_var:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 선택된 변수와 가격
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=filtered_df['date'],
                    y=filtered_df[selected_var],
                    mode='lines+markers',
                    name=selected_var,
                    yaxis='y',
                    line=dict(width=3)
                ))
                
                fig.add_trace(go.Scatter(
                    x=filtered_df['date'],
                    y=filtered_df['BTC_Price'],
                    mode='lines',
                    name='BTC Price',
                    yaxis='y2',
                    line=dict(color='gray', width=2, dash='dash')
                ))
                
                if crash_date in filtered_df['date'].values:
                    fig.add_shape(
                        type="line",
                        x0=crash_date, x1=crash_date,
                        y0=0, y1=1, yref="paper",
                        line=dict(color="red", width=2, dash="dash")
                    )
                
                fig.update_layout(
                    title=f"{selected_var} vs BTC 가격",
                    xaxis_title="날짜",
                    yaxis=dict(title=selected_var, side="left"),
                    yaxis2=dict(title="BTC Price", overlaying="y", side="right"),
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 통계")
                
                st.metric("평균", f"{filtered_df[selected_var].mean():.2f}")
                st.metric("표준편차", f"{filtered_df[selected_var].std():.2f}")
                st.metric("최소", f"{filtered_df[selected_var].min():.2f}")
                st.metric("최대", f"{filtered_df[selected_var].max():.2f}")
                
                # 상관관계
                corr = filtered_df[[selected_var, 'BTC_Price']].corr().iloc[0, 1]
                st.markdown("---")
                st.metric("BTC 가격과 상관계수", f"{corr:+.4f}")
        
        # 모든 거시경제 지표 한눈에
        st.subheader("📊 전체 거시경제 지표")
        
        fig = go.Figure()
        
        for var in available_vars:
            # 정규화 (0-1 범위)
            normalized = (filtered_df[var] - filtered_df[var].min()) / (filtered_df[var].max() - filtered_df[var].min())
            
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=normalized,
                mode='lines',
                name=var,
                line=dict(width=2)
            ))
        
        if crash_date in filtered_df['date'].values:
            fig.add_shape(
                type="line",
                x0=crash_date, x1=crash_date,
                y0=0, y1=1, yref="paper",
                line=dict(color="red", width=2, dash="dash")
            )
        
        fig.update_layout(
            title="거시경제 지표 추이 (정규화)",
            xaxis_title="날짜",
            yaxis_title="정규화 값 (0-1)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== 탭 4: 상관관계 =====
    with tab4:
        st.header("📊 변수 간 상관관계 분석")
        
        # 주요 변수 선택
        key_vars = ['BTC_Price', 'tone_mean', 'tone_neg_share', 
                   'M2SL', 'Yield_10Y', 'USD_Index', 'Open_Interest']
        available_key_vars = [v for v in key_vars if v in filtered_df.columns]
        
        # 상관관계 행렬
        corr_matrix = filtered_df[available_key_vars].corr()
        
        # Plotly 히트맵
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="상관계수")
        ))
        
        fig.update_layout(
            title="주요 변수 상관관계 히트맵",
            height=600,
            width=800
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 강한 상관관계 Top 10
        st.subheader("🔝 강한 상관관계 Top 10")
        
        # 상관관계를 리스트로 변환
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                var1 = corr_matrix.columns[i]
                var2 = corr_matrix.columns[j]
                corr_val = corr_matrix.iloc[i, j]
                corr_pairs.append({
                    'Variable 1': var1,
                    'Variable 2': var2,
                    'Correlation': corr_val,
                    'Abs Correlation': abs(corr_val)
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df = corr_df.sort_values('Abs Correlation', ascending=False).head(10)
        
        # 표시
        st.dataframe(
            corr_df[['Variable 1', 'Variable 2', 'Correlation']].style.format({'Correlation': '{:+.4f}'}),
            use_container_width=True
        )
    
    # ===== 탭 5: 종합 분석 =====
    with tab5:
        st.header("🔍 종합 분석")
        
        st.markdown("""
        ### 📊 주요 발견사항
        
        #### 1. 가격 변동성
        - 2025년 10월 10일 급락 발생 (-7.22%)
        - 가격 범위: $106,443 ~ $124,725 (17.17% 변동)
        - 급락 전 최고가: $124,725 (10/7)
        - 급락 후 최저가: $106,443 (10/15)
        
        #### 2. 거시경제 영향
        - **M2 통화량**: 양의 영향 (+4,241 표준화 계수)
        - **달러 인덱스**: 음의 영향 (-3,740 표준화 계수)
        - **10년물 금리**: 양의 영향 (+2,223 표준화 계수)
        - 거시경제 변수 설명력: 44.5% (R²)
        
        #### 3. 감성 분석
        - 전반적으로 부정적 감성 우세 (평균 -0.190)
        - 급락 전 3일: 정치 테마 급증 (+17.4%)
        - 부정 뉴스 비율(tone_neg_share)이 가격과 유의한 상관관계
        
        #### 4. Open Interest 패턴
        - 급락 전: 평균 OI 103.95 (최고치)
        - 급락 후: 평균 OI 71.74 (-31% 감소)
        - 10/11 OI 급감 -32% (청산 신호)
        
        #### 5. 네트워크 분석
        - SNS 활동(sns_post_count)이 최고 연결 중심성 (0.667)
        - 부정 뉴스 비율(tone_neg_share)이 네트워크 허브 역할
        - OI와 가격 강한 양의 상관관계 (r = +0.684)
        """)
        
        st.markdown("---")
        
        # 데이터 테이블
        st.subheader("📋 필터링된 데이터")
        
        display_cols = ['date', 'BTC_Price', 'tone_mean', 'M2SL', 
                       'Yield_10Y', 'USD_Index', 'Open_Interest']
        available_display = [c for c in display_cols if c in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_display].style.format({
                'BTC_Price': '${:,.2f}',
                'tone_mean': '{:.3f}',
                'M2SL': '{:,.2f}',
                'Yield_10Y': '{:.2f}',
                'USD_Index': '{:.2f}',
                'Open_Interest': '{:.0f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # 다운로드 버튼
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"bitcoin_analysis_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
