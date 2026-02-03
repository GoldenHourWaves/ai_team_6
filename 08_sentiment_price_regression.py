"""
Task 8: 감성-가격 회귀 분석
tone_mean과 커뮤니티 감성 점수를 독립변수로 BTC_Price 예측
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 경로
INTEGRATED_DIR = Path("data/processed/integrated")
OUTPUT_DIR = Path("output/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_and_prepare_data():
    """데이터 로드 및 준비"""
    
    print("\n" + "=" * 80)
    print("📂 데이터 로드 및 준비")
    print("=" * 80)
    
    # 통합 데이터 로드
    master_df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    master_df['date'] = pd.to_datetime(master_df['date'])
    
    # 감성 분석 결과 로드
    sentiment_df = pd.read_csv(OUTPUT_DIR / "sentiment_daily_analysis.csv")
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    
    print(f"✅ 통합 데이터: {master_df.shape}")
    print(f"✅ 감성 데이터: {sentiment_df.shape}")
    
    # 병합
    df = pd.merge(master_df, sentiment_df[['date', 'sentiment_mean', 'sentiment_median', 
                                            'sentiment_std', 'post_count']], 
                  on='date', how='left')
    
    print(f"\n✅ 병합 완료: {df.shape}")
    
    # 결측치 확인
    print(f"\n📊 감성 관련 변수 결측치:")
    sentiment_cols = ['tone_mean', 'tone_pos_share', 'tone_neg_share', 
                     'sentiment_mean', 'sentiment_median']
    for col in sentiment_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            print(f"   {col}: {missing}개 ({missing/len(df)*100:.1f}%)")
    
    # 결측치가 있는 행 제거
    df_clean = df.dropna(subset=['tone_mean', 'sentiment_mean', 'BTC_Price'])
    print(f"\n✅ 결측치 제거 후: {df_clean.shape}")
    
    return df_clean

def perform_simple_regression(df):
    """단순 회귀 분석 (개별 변수)"""
    
    print("\n" + "=" * 80)
    print("📊 단순 회귀 분석")
    print("=" * 80)
    
    # 독립변수 목록
    independent_vars = ['tone_mean', 'tone_pos_share', 'tone_neg_share', 
                       'sentiment_mean', 'sentiment_median', 'sentiment_std']
    
    results = []
    
    for var in independent_vars:
        if var not in df.columns or df[var].isna().all():
            continue
        
        # 데이터 준비
        X = df[[var]].values
        y = df['BTC_Price'].values
        
        # 회귀 모델
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # 평가 지표
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        # 통계적 유의성 검정
        slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
        
        results.append({
            'variable': var,
            'coefficient': model.coef_[0],
            'intercept': model.intercept_,
            'r2': r2,
            'r_value': r_value,
            'p_value': p_value,
            'mae': mae,
            'rmse': rmse
        })
        
        print(f"\n🔹 {var}:")
        print(f"   계수: {model.coef_[0]:+.2f}")
        print(f"   R²: {r2:.4f}")
        print(f"   p-value: {p_value:.4f} {'✅ 유의함' if p_value < 0.05 else '⚠️  유의하지 않음'}")
        print(f"   MAE: ${mae:,.2f}")
        print(f"   RMSE: ${rmse:,.2f}")
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('r2', ascending=False)
    
    return results_df

def perform_multiple_regression(df):
    """다중 회귀 분석 (모든 감성 변수 포함)"""
    
    print("\n" + "=" * 80)
    print("📊 다중 회귀 분석")
    print("=" * 80)
    
    # 독립변수 선택
    feature_cols = ['tone_mean', 'tone_pos_share', 'tone_neg_share', 
                   'sentiment_mean', 'sentiment_median']
    
    # 사용 가능한 변수만 선택
    available_features = [col for col in feature_cols if col in df.columns and not df[col].isna().all()]
    
    X = df[available_features].values
    y = df['BTC_Price'].values
    
    print(f"\n📊 독립변수: {available_features}")
    print(f"   데이터 크기: {X.shape}")
    
    # 표준화
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 회귀 모델
    model = LinearRegression()
    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)
    
    # 평가 지표
    r2 = r2_score(y, y_pred)
    adj_r2 = 1 - (1 - r2) * (len(y) - 1) / (len(y) - X.shape[1] - 1)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    print(f"\n📈 모델 성능:")
    print(f"   R²: {r2:.4f}")
    print(f"   Adjusted R²: {adj_r2:.4f}")
    print(f"   MAE: ${mae:,.2f}")
    print(f"   RMSE: ${rmse:,.2f}")
    
    print(f"\n📊 회귀 계수 (표준화된 변수 기준):")
    for i, feature in enumerate(available_features):
        print(f"   {feature}: {model.coef_[i]:+.2f}")
    print(f"   절편: {model.intercept_:,.2f}")
    
    # F-검정으로 모델 전체 유의성 검정
    n = len(y)
    k = X.shape[1]
    f_stat = (r2 / k) / ((1 - r2) / (n - k - 1))
    f_pvalue = 1 - stats.f.cdf(f_stat, k, n - k - 1)
    
    print(f"\n📊 모델 유의성 검정:")
    print(f"   F-통계량: {f_stat:.4f}")
    print(f"   p-value: {f_pvalue:.6f} {'✅ 유의함' if f_pvalue < 0.05 else '⚠️  유의하지 않음'}")
    
    return model, scaler, available_features, y_pred

def plot_regression_results(df, simple_results, y_pred):
    """회귀 분석 결과 시각화"""
    
    print("\n" + "=" * 80)
    print("📈 회귀 분석 시각화")
    print("=" * 80)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('감성-가격 회귀 분석 결과', fontsize=18, fontweight='bold', y=0.995)
    
    # ===== 그래프 1: 단순 회귀 R² 비교 =====
    ax1 = axes[0, 0]
    
    simple_results_sorted = simple_results.sort_values('r2', ascending=True)
    colors = ['green' if p < 0.05 else 'gray' for p in simple_results_sorted['p_value']]
    
    bars = ax1.barh(range(len(simple_results_sorted)), simple_results_sorted['r2'], 
                    color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax1.set_yticks(range(len(simple_results_sorted)))
    ax1.set_yticklabels(simple_results_sorted['variable'], fontsize=10)
    ax1.set_xlabel('R² (결정계수)', fontsize=11, fontweight='bold')
    ax1.set_title('단순 회귀 분석: 개별 변수 설명력', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # p-value 표시
    for i, (idx, row) in enumerate(simple_results_sorted.iterrows()):
        x_pos = row['r2'] + 0.005
        label = f"p={row['p_value']:.3f}" if row['p_value'] >= 0.001 else "p<0.001"
        ax1.text(x_pos, i, label, va='center', fontsize=8)
    
    # ===== 그래프 2: tone_mean vs BTC_Price 산점도 =====
    ax2 = axes[0, 1]
    
    if 'tone_mean' in df.columns:
        scatter = ax2.scatter(df['tone_mean'], df['BTC_Price'], 
                            c=df['date'].astype('int64'), cmap='viridis',
                            alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
        
        # 회귀선
        X = df['tone_mean'].values.reshape(-1, 1)
        y = df['BTC_Price'].values
        model = LinearRegression()
        model.fit(X, y)
        x_line = np.linspace(X.min(), X.max(), 100)
        y_line = model.predict(x_line.reshape(-1, 1))
        ax2.plot(x_line, y_line, 'r--', linewidth=2, 
                label=f"회귀선 (R²={r2_score(y, model.predict(X)):.3f})")
        
        ax2.set_xlabel('tone_mean (뉴스 감성)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('BTC 가격 (USD)', fontsize=11, fontweight='bold')
        ax2.set_title('뉴스 감성 (tone_mean) vs BTC 가격', fontsize=13, fontweight='bold', pad=10)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax2.legend(loc='best', fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('날짜', fontsize=9)
    
    # ===== 그래프 3: sentiment_mean vs BTC_Price 산점도 =====
    ax3 = axes[1, 0]
    
    if 'sentiment_mean' in df.columns:
        scatter = ax3.scatter(df['sentiment_mean'], df['BTC_Price'], 
                            c=df['date'].astype('int64'), cmap='plasma',
                            alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
        
        # 회귀선
        X = df['sentiment_mean'].values.reshape(-1, 1)
        y = df['BTC_Price'].values
        model = LinearRegression()
        model.fit(X, y)
        x_line = np.linspace(X.min(), X.max(), 100)
        y_line = model.predict(x_line.reshape(-1, 1))
        ax3.plot(x_line, y_line, 'r--', linewidth=2, 
                label=f"회귀선 (R²={r2_score(y, model.predict(X)):.3f})")
        
        ax3.set_xlabel('sentiment_mean (커뮤니티 감성)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('BTC 가격 (USD)', fontsize=11, fontweight='bold')
        ax3.set_title('커뮤니티 감성 vs BTC 가격', fontsize=13, fontweight='bold', pad=10)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax3.legend(loc='best', fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--')
        
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('날짜', fontsize=9)
    
    # ===== 그래프 4: 다중 회귀 예측 vs 실제 =====
    ax4 = axes[1, 1]
    
    y_actual = df['BTC_Price'].values
    
    ax4.scatter(y_actual, y_pred, alpha=0.6, s=100, 
               edgecolors='black', linewidth=0.5, c='steelblue')
    
    # 완벽한 예측선 (y=x)
    min_val = min(y_actual.min(), y_pred.min())
    max_val = max(y_actual.max(), y_pred.max())
    ax4.plot([min_val, max_val], [min_val, max_val], 'r--', 
            linewidth=2, label='완벽한 예측')
    
    ax4.set_xlabel('실제 가격 (USD)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('예측 가격 (USD)', fontsize=11, fontweight='bold')
    ax4.set_title('다중 회귀 모델: 예측 vs 실제', fontsize=13, fontweight='bold', pad=10)
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "10_sentiment_price_regression.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()

def plot_residuals(df, y_pred):
    """잔차 분석"""
    
    print("\n" + "=" * 80)
    print("📊 잔차 분석")
    print("=" * 80)
    
    y_actual = df['BTC_Price'].values
    residuals = y_actual - y_pred
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('회귀 모델 잔차 분석', fontsize=16, fontweight='bold')
    
    # ===== 그래프 1: 잔차 히스토그램 =====
    ax1 = axes[0]
    
    ax1.hist(residuals, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(0, color='red', linestyle='--', linewidth=2)
    ax1.set_xlabel('잔차 (실제 - 예측)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('빈도', fontsize=11, fontweight='bold')
    ax1.set_title('잔차 분포 (정규성 검정)', fontsize=12, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # 통계량 표시
    mean_res = residuals.mean()
    std_res = residuals.std()
    ax1.text(0.05, 0.95, f'평균: ${mean_res:,.2f}\n표준편차: ${std_res:,.2f}', 
            transform=ax1.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # ===== 그래프 2: 잔차 vs 예측값 =====
    ax2 = axes[1]
    
    ax2.scatter(y_pred, residuals, alpha=0.6, s=80, 
               edgecolors='black', linewidth=0.5, c='coral')
    ax2.axhline(0, color='red', linestyle='--', linewidth=2)
    ax2.set_xlabel('예측 가격 (USD)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('잔차 (실제 - 예측)', fontsize=11, fontweight='bold')
    ax2.set_title('잔차 vs 예측값 (등분산성 검정)', fontsize=12, fontweight='bold', pad=10)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "11_regression_residuals.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 잔차 분석 그래프 저장: {output_file}")
    
    plt.show()
    
    # 정규성 검정 (Shapiro-Wilk)
    if len(residuals) < 5000:
        stat, p_value = stats.shapiro(residuals)
        print(f"\n📊 Shapiro-Wilk 정규성 검정:")
        print(f"   통계량: {stat:.4f}")
        print(f"   p-value: {p_value:.4f} {'✅ 정규분포' if p_value > 0.05 else '⚠️  비정규분포'}")

def main():
    print("=" * 80)
    print("Task 8: 감성-가격 회귀 분석")
    print("=" * 80)
    
    # 1. 데이터 로드
    df = load_and_prepare_data()
    
    # 2. 단순 회귀 분석
    simple_results = perform_simple_regression(df)
    
    # 3. 다중 회귀 분석
    model, scaler, features, y_pred = perform_multiple_regression(df)
    
    # 4. 결과 시각화
    plot_regression_results(df, simple_results, y_pred)
    
    # 5. 잔차 분석
    plot_residuals(df, y_pred)
    
    # 6. 결과 저장
    simple_results.to_csv(OUTPUT_DIR / "regression_simple_results.csv", 
                         index=False, encoding='utf-8-sig')
    
    # 다중 회귀 계수 저장
    coef_df = pd.DataFrame({
        'feature': features,
        'coefficient': model.coef_
    })
    coef_df['intercept'] = model.intercept_
    coef_df.to_csv(OUTPUT_DIR / "regression_multiple_coefficients.csv", 
                  index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 8 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '10_sentiment_price_regression.png'}")
    print(f"   2. {OUTPUT_DIR / '11_regression_residuals.png'}")
    print(f"   3. {OUTPUT_DIR / 'regression_simple_results.csv'}")
    print(f"   4. {OUTPUT_DIR / 'regression_multiple_coefficients.csv'}")

if __name__ == "__main__":
    main()
