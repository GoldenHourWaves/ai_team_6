"""
Task 9: 거시경제 지표 다중 회귀 분석
M2, CPI, Gold, Yield_10Y, USD_Index가 BTC 가격에 미치는 영향 정량화
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

def load_data():
    """데이터 로드"""
    
    print("\n" + "=" * 80)
    print("📂 데이터 로드")
    print("=" * 80)
    
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"✅ 데이터 로드 완료: {df.shape}")
    print(f"   기간: {df['date'].min().date()} ~ {df['date'].max().date()}")
    
    return df

def analyze_macro_variables(df):
    """거시경제 변수 분석"""
    
    print("\n" + "=" * 80)
    print("📊 거시경제 변수 분석")
    print("=" * 80)
    
    # 거시경제 변수 목록
    macro_vars = ['M2SL', 'CPI', 'Gold_Price', 'Yield_10Y', 'USD_Index']
    
    # 존재하는 변수 확인
    available_vars = [var for var in macro_vars if var in df.columns]
    print(f"\n📊 분석할 거시경제 변수: {len(available_vars)}개")
    
    for var in available_vars:
        missing = df[var].isna().sum()
        mean_val = df[var].mean()
        std_val = df[var].std()
        min_val = df[var].min()
        max_val = df[var].max()
        
        print(f"\n🔹 {var}:")
        print(f"   결측치: {missing}개 ({missing/len(df)*100:.1f}%)")
        print(f"   평균: {mean_val:,.2f}")
        print(f"   표준편차: {std_val:,.2f}")
        print(f"   범위: {min_val:,.2f} ~ {max_val:,.2f}")
    
    # BTC_Price 정보
    print(f"\n🔹 BTC_Price:")
    print(f"   평균: ${df['BTC_Price'].mean():,.2f}")
    print(f"   표준편차: ${df['BTC_Price'].std():,.2f}")
    print(f"   범위: ${df['BTC_Price'].min():,.2f} ~ ${df['BTC_Price'].max():,.2f}")
    
    return available_vars

def perform_individual_regression(df, macro_vars):
    """개별 거시경제 변수별 단순 회귀"""
    
    print("\n" + "=" * 80)
    print("📊 단순 회귀 분석 (개별 변수)")
    print("=" * 80)
    
    results = []
    
    for var in macro_vars:
        # 결측치 제거
        mask = ~(df[var].isna() | df['BTC_Price'].isna())
        X = df.loc[mask, var].values.reshape(-1, 1)
        y = df.loc[mask, 'BTC_Price'].values
        
        if len(X) < 3:
            print(f"\n⚠️  {var}: 데이터 부족")
            continue
        
        # 회귀 모델
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # 평가 지표
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        # 통계적 유의성
        slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
        
        results.append({
            'variable': var,
            'coefficient': model.coef_[0],
            'intercept': model.intercept_,
            'r2': r2,
            'r_value': r_value,
            'p_value': p_value,
            'std_err': std_err,
            'mae': mae,
            'rmse': rmse
        })
        
        print(f"\n🔹 {var}:")
        print(f"   계수: {model.coef_[0]:+,.4f}")
        print(f"   절편: ${model.intercept_:,.2f}")
        print(f"   R²: {r2:.4f} ({r2*100:.1f}% 설명력)")
        print(f"   상관계수: {r_value:+.4f}")
        print(f"   p-value: {p_value:.6f} {'✅ 유의함' if p_value < 0.05 else '⚠️  유의하지 않음'}")
        print(f"   MAE: ${mae:,.2f}")
        print(f"   RMSE: ${rmse:,.2f}")
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('r2', ascending=False)
    
    print(f"\n" + "=" * 80)
    print("📊 단순 회귀 결과 요약 (R² 순)")
    print("=" * 80)
    for idx, row in results_df.iterrows():
        sig = "✅" if row['p_value'] < 0.05 else "⚠️ "
        print(f"{sig} {row['variable']:15s} | R²={row['r2']:.4f} | p={row['p_value']:.6f}")
    
    return results_df

def perform_multiple_regression(df, macro_vars):
    """다중 회귀 분석 (모든 거시경제 변수)"""
    
    print("\n" + "=" * 80)
    print("📊 다중 회귀 분석 (전체 모델)")
    print("=" * 80)
    
    # 결측치 제거
    cols = macro_vars + ['BTC_Price']
    df_clean = df[cols].dropna()
    
    print(f"\n📊 사용 데이터:")
    print(f"   변수: {macro_vars}")
    print(f"   샘플 수: {len(df_clean)}개 (결측치 제거 후)")
    
    if len(df_clean) < 10:
        print("\n⚠️  데이터가 부족하여 다중 회귀 분석을 수행할 수 없습니다.")
        return None, None, None, None, None
    
    X = df_clean[macro_vars].values
    y = df_clean['BTC_Price'].values
    
    # 표준화
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 회귀 모델
    model = LinearRegression()
    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)
    
    # 평가 지표
    r2 = r2_score(y, y_pred)
    n = len(y)
    k = X.shape[1]
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    print(f"\n📈 모델 성능:")
    print(f"   R²: {r2:.4f} ({r2*100:.1f}% 설명력)")
    print(f"   Adjusted R²: {adj_r2:.4f}")
    print(f"   MAE: ${mae:,.2f}")
    print(f"   RMSE: ${rmse:,.2f}")
    
    print(f"\n📊 회귀 계수 (표준화된 변수 기준):")
    coef_importance = []
    for i, var in enumerate(macro_vars):
        print(f"   {var:15s}: {model.coef_[i]:+,.2f}")
        coef_importance.append({'variable': var, 'coefficient': model.coef_[i]})
    print(f"   {'절편':15s}: ${model.intercept_:,.2f}")
    
    # 원래 스케일 계수 계산
    print(f"\n📊 회귀 계수 (원래 스케일):")
    original_coefs = model.coef_ / scaler.scale_
    for i, var in enumerate(macro_vars):
        print(f"   {var:15s}: {original_coefs[i]:+,.6f}")
    
    # F-검정
    f_stat = (r2 / k) / ((1 - r2) / (n - k - 1))
    f_pvalue = 1 - stats.f.cdf(f_stat, k, n - k - 1)
    
    print(f"\n📊 모델 유의성 검정 (F-test):")
    print(f"   F-통계량: {f_stat:.4f}")
    print(f"   p-value: {f_pvalue:.6f} {'✅ 모델 유의함' if f_pvalue < 0.05 else '⚠️  모델 유의하지 않음'}")
    
    # 계수 중요도 정렬
    coef_importance_df = pd.DataFrame(coef_importance)
    coef_importance_df['abs_coef'] = coef_importance_df['coefficient'].abs()
    coef_importance_df = coef_importance_df.sort_values('abs_coef', ascending=False)
    
    print(f"\n📊 변수 중요도 (표준화 계수 절대값 순):")
    for idx, row in coef_importance_df.iterrows():
        print(f"   {row['variable']:15s}: {row['abs_coef']:,.2f}")
    
    return model, scaler, macro_vars, y_pred, df_clean

def plot_macro_regression_results(df_clean, macro_vars, simple_results, y_pred):
    """거시경제 회귀 결과 시각화"""
    
    print("\n" + "=" * 80)
    print("📈 거시경제 회귀 시각화")
    print("=" * 80)
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('거시경제 지표와 비트코인 가격 회귀 분석', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    # ===== 그래프 1: 단순 회귀 R² 비교 =====
    ax1 = fig.add_subplot(gs[0, 0])
    
    simple_results_sorted = simple_results.sort_values('r2', ascending=True)
    colors = ['green' if p < 0.05 else 'gray' for p in simple_results_sorted['p_value']]
    
    bars = ax1.barh(range(len(simple_results_sorted)), simple_results_sorted['r2'], 
                    color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax1.set_yticks(range(len(simple_results_sorted)))
    ax1.set_yticklabels(simple_results_sorted['variable'], fontsize=10)
    ax1.set_xlabel('R² (결정계수)', fontsize=11, fontweight='bold')
    ax1.set_title('단순 회귀: 개별 변수 설명력', fontsize=12, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # p-value 표시
    for i, (idx, row) in enumerate(simple_results_sorted.iterrows()):
        x_pos = row['r2'] + 0.01
        label = f"p={row['p_value']:.3f}" if row['p_value'] >= 0.001 else "p<0.001"
        ax1.text(x_pos, i, label, va='center', fontsize=8)
    
    # ===== 그래프 2-6: 개별 변수 산점도 =====
    for i, var in enumerate(macro_vars[:5]):  # 최대 5개만 표시
        row = i // 2
        col = i % 2 + 1
        ax = fig.add_subplot(gs[row, col])
        
        if var in df_clean.columns:
            # 산점도
            scatter = ax.scatter(df_clean[var], df_clean['BTC_Price'], 
                               c=df_clean.index, cmap='viridis',
                               alpha=0.6, s=80, edgecolors='black', linewidth=0.5)
            
            # 회귀선
            X = df_clean[var].values.reshape(-1, 1)
            y = df_clean['BTC_Price'].values
            model = LinearRegression()
            model.fit(X, y)
            x_line = np.linspace(X.min(), X.max(), 100)
            y_line = model.predict(x_line.reshape(-1, 1))
            
            r2 = r2_score(y, model.predict(X))
            ax.plot(x_line, y_line, 'r--', linewidth=2, 
                   label=f"R²={r2:.3f}")
            
            ax.set_xlabel(var, fontsize=10, fontweight='bold')
            ax.set_ylabel('BTC 가격 (USD)', fontsize=10, fontweight='bold')
            ax.set_title(f'{var} vs BTC 가격', fontsize=11, fontweight='bold', pad=8)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3, linestyle='--')
    
    # ===== 그래프 7: 다중 회귀 예측 vs 실제 =====
    ax7 = fig.add_subplot(gs[2, 0])
    
    y_actual = df_clean['BTC_Price'].values
    
    ax7.scatter(y_actual, y_pred, alpha=0.6, s=100, 
               edgecolors='black', linewidth=0.5, c='steelblue')
    
    # 완벽한 예측선
    min_val = min(y_actual.min(), y_pred.min())
    max_val = max(y_actual.max(), y_pred.max())
    ax7.plot([min_val, max_val], [min_val, max_val], 'r--', 
            linewidth=2, label='완벽한 예측')
    
    r2 = r2_score(y_actual, y_pred)
    ax7.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax7.transAxes, 
            fontsize=11, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    ax7.set_xlabel('실제 가격 (USD)', fontsize=11, fontweight='bold')
    ax7.set_ylabel('예측 가격 (USD)', fontsize=11, fontweight='bold')
    ax7.set_title('다중 회귀: 예측 vs 실제', fontsize=12, fontweight='bold', pad=10)
    ax7.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax7.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax7.legend(loc='best', fontsize=9)
    ax7.grid(True, alpha=0.3, linestyle='--')
    
    # ===== 그래프 8: 잔차 히스토그램 =====
    ax8 = fig.add_subplot(gs[2, 1])
    
    residuals = y_actual - y_pred
    
    ax8.hist(residuals, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
    ax8.axvline(0, color='red', linestyle='--', linewidth=2)
    ax8.set_xlabel('잔차 (실제 - 예측)', fontsize=11, fontweight='bold')
    ax8.set_ylabel('빈도', fontsize=11, fontweight='bold')
    ax8.set_title('잔차 분포', fontsize=12, fontweight='bold', pad=10)
    ax8.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # 통계량 표시
    mean_res = residuals.mean()
    std_res = residuals.std()
    ax8.text(0.95, 0.95, f'평균: ${mean_res:,.0f}\nStd: ${std_res:,.0f}', 
            transform=ax8.transAxes, fontsize=9, verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    # ===== 그래프 9: 잔차 vs 예측값 =====
    ax9 = fig.add_subplot(gs[2, 2])
    
    ax9.scatter(y_pred, residuals, alpha=0.6, s=80, 
               edgecolors='black', linewidth=0.5, c='coral')
    ax9.axhline(0, color='red', linestyle='--', linewidth=2)
    ax9.set_xlabel('예측 가격 (USD)', fontsize=11, fontweight='bold')
    ax9.set_ylabel('잔차', fontsize=11, fontweight='bold')
    ax9.set_title('잔차 vs 예측값', fontsize=12, fontweight='bold', pad=10)
    ax9.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax9.grid(True, alpha=0.3, linestyle='--')
    
    output_file = OUTPUT_DIR / "12_macroeconomic_regression.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 그래프 저장: {output_file}")
    
    plt.show()

def analyze_variable_importance(model, scaler, macro_vars):
    """변수 중요도 분석 및 시각화"""
    
    print("\n" + "=" * 80)
    print("📊 변수 중요도 분석")
    print("=" * 80)
    
    # 표준화된 계수 (중요도)
    importance_df = pd.DataFrame({
        'variable': macro_vars,
        'coefficient': model.coef_,
        'abs_coefficient': np.abs(model.coef_)
    })
    importance_df = importance_df.sort_values('abs_coefficient', ascending=False)
    
    print("\n📊 변수 중요도 (표준화 계수 기준):")
    for idx, row in importance_df.iterrows():
        direction = "↑ 양의 영향" if row['coefficient'] > 0 else "↓ 음의 영향"
        print(f"   {row['variable']:15s}: {row['coefficient']:+8.2f} ({direction})")
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['green' if c > 0 else 'red' for c in importance_df['coefficient']]
    bars = ax.barh(range(len(importance_df)), importance_df['coefficient'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax.set_yticks(range(len(importance_df)))
    ax.set_yticklabels(importance_df['variable'], fontsize=11)
    ax.set_xlabel('표준화 회귀 계수', fontsize=12, fontweight='bold')
    ax.set_title('거시경제 변수의 BTC 가격 영향도\n(양수: 가격 상승 요인, 음수: 가격 하락 요인)', 
                fontsize=14, fontweight='bold', pad=15)
    ax.axvline(0, color='black', linewidth=2)
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # 계수 값 표시
    for i, (idx, row) in enumerate(importance_df.iterrows()):
        x_pos = row['coefficient'] + (50 if row['coefficient'] > 0 else -50)
        ha = 'left' if row['coefficient'] > 0 else 'right'
        ax.text(x_pos, i, f"{row['coefficient']:+.1f}", 
               va='center', ha=ha, fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "13_macro_variable_importance.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 변수 중요도 그래프 저장: {output_file}")
    
    plt.show()
    
    return importance_df

def main():
    print("=" * 80)
    print("Task 9: 거시경제 지표 다중 회귀 분석")
    print("=" * 80)
    
    # 1. 데이터 로드
    df = load_data()
    
    # 2. 거시경제 변수 분석
    macro_vars = analyze_macro_variables(df)
    
    # 3. 개별 변수 단순 회귀
    simple_results = perform_individual_regression(df, macro_vars)
    
    # 4. 다중 회귀 분석
    model, scaler, features, y_pred, df_clean = perform_multiple_regression(df, macro_vars)
    
    if model is not None:
        # 5. 결과 시각화
        plot_macro_regression_results(df_clean, macro_vars, simple_results, y_pred)
        
        # 6. 변수 중요도 분석
        importance_df = analyze_variable_importance(model, scaler, features)
        
        # 7. 결과 저장
        simple_results.to_csv(OUTPUT_DIR / "macro_simple_regression.csv", 
                             index=False, encoding='utf-8-sig')
        importance_df.to_csv(OUTPUT_DIR / "macro_variable_importance.csv", 
                            index=False, encoding='utf-8-sig')
        
        # 다중 회귀 계수 저장
        coef_df = pd.DataFrame({
            'variable': features,
            'standardized_coefficient': model.coef_,
            'original_coefficient': model.coef_ / scaler.scale_
        })
        coef_df['intercept'] = model.intercept_
        coef_df.to_csv(OUTPUT_DIR / "macro_regression_coefficients.csv", 
                      index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("Task 9 완료! ✅")
    print("=" * 80)
    print(f"\n✅ 생성된 파일:")
    print(f"   1. {OUTPUT_DIR / '12_macroeconomic_regression.png'}")
    print(f"   2. {OUTPUT_DIR / '13_macro_variable_importance.png'}")
    print(f"   3. {OUTPUT_DIR / 'macro_simple_regression.csv'}")
    print(f"   4. {OUTPUT_DIR / 'macro_variable_importance.csv'}")
    print(f"   5. {OUTPUT_DIR / 'macro_regression_coefficients.csv'}")

if __name__ == "__main__":
    main()
