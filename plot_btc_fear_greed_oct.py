#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Price와 Fear & Greed Index 시각화 (2025-10-01 ~ 2025-10-11)
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# CSV 파일 읽기
df = pd.read_csv('./data/btc_fear_greed_20250901_20251031.csv')

# date를 문자열로 변환 (CSV에서 int로 읽힐 수 있음)
df['date'] = df['date'].astype(str)

# 기간 필터링 (20251001 ~ 20251011)
df_filtered = df[(df['date'] >= '20251001') & (df['date'] <= '20251011')].copy()

# date를 datetime 형식으로 변환 (X축 표시용)
df_filtered['date_dt'] = pd.to_datetime(df_filtered['date'], format='%Y%m%d')

# 그래프 설정
fig, ax1 = plt.subplots(figsize=(12, 6))

# BTC Price (왼쪽 Y축)
color1 = 'tab:blue'
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('BTC Price (USD)', color=color1, fontsize=12)
line1 = ax1.plot(df_filtered['date_dt'], df_filtered['btc_price_usd'], 
                 color=color1, marker='o', linewidth=2, label='BTC Price')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)

# Fear & Greed Index (오른쪽 Y축)
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel('Fear & Greed Index', color=color2, fontsize=12)
line2 = ax2.plot(df_filtered['date_dt'], df_filtered['fear_greed'], 
                 color=color2, marker='s', linewidth=2, linestyle='--', label='Fear & Greed')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_ylim(0, 100)

# 제목
plt.title('BTC Price vs Fear & Greed Index (Oct 1-11, 2025)', fontsize=14, fontweight='bold')

# 범례 통합
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=10)

# X축 날짜 형식 조정
plt.xticks(rotation=45, ha='right')
fig.tight_layout()

# 저장 및 표시
output_path = './output/visualizations/btc_fear_greed_oct1_11.png'
import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"그래프 저장: {output_path}")

plt.show()
