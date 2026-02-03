"""
Task 14: PDF 분석 리포트 자동 생성
Bitcoin Market Crash Analysis Report Generator
"""

import pandas as pd
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import os

# 경로 설정
OUTPUT_DIR = Path("output/visualizations")
REPORT_DIR = Path("output/reports")
INTEGRATED_DIR = Path("data/processed/integrated")

# 리포트 디렉토리 생성
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 한글 폰트 등록 (Windows 환경)
try:
    font_path = "C:/Windows/Fonts/malgun.ttf"
    pdfmetrics.registerFont(TTFont('Malgun', font_path))
    KOREAN_FONT = 'Malgun'
except:
    # 폰트 로드 실패시 기본 폰트 사용
    KOREAN_FONT = 'Helvetica'
    print("Warning: 한글 폰트를 로드하지 못했습니다. 영문 폰트를 사용합니다.")

def load_data():
    """데이터 로드"""
    df = pd.read_csv(INTEGRATED_DIR / "master_data_integrated.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

def create_custom_styles():
    """커스텀 스타일 생성"""
    styles = getSampleStyleSheet()
    
    # 제목 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=KOREAN_FONT,
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        leading=30
    )
    
    # 부제목 스타일
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName=KOREAN_FONT,
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=12,
        leading=20
    )
    
    # 섹션 제목 스타일
    section_style = ParagraphStyle(
        'CustomSection',
        parent=styles['Heading3'],
        fontName=KOREAN_FONT,
        fontSize=14,
        textColor=colors.HexColor('#2980B9'),
        spaceAfter=10,
        spaceBefore=15,
        leading=18
    )
    
    # 본문 스타일
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=11,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        leading=14,
        alignment=TA_LEFT
    )
    
    # 강조 스타일
    emphasis_style = ParagraphStyle(
        'CustomEmphasis',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=12,
        textColor=colors.HexColor('#E74C3C'),
        spaceAfter=10,
        leading=16,
        alignment=TA_LEFT
    )
    
    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'section': section_style,
        'body': body_style,
        'emphasis': emphasis_style
    }

def create_cover_page(story, styles):
    """표지 페이지 생성"""
    # 제목
    title = Paragraph("Bitcoin Market Crash Analysis", styles['title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # 부제목
    subtitle = Paragraph("2025년 10월 비트코인 급락 분석 리포트", styles['subtitle'])
    story.append(subtitle)
    story.append(Spacer(1, 0.5*inch))
    
    # 날짜 정보
    date_info = Paragraph(f"분석 기간: 2025-09-01 ~ 2025-10-31", styles['body'])
    story.append(date_info)
    
    crash_date_info = Paragraph(f"급락 발생일: 2025-10-10", styles['emphasis'])
    story.append(crash_date_info)
    story.append(Spacer(1, 0.5*inch))
    
    # 생성 날짜
    generation_date = Paragraph(f"보고서 생성: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['body'])
    story.append(generation_date)
    
    story.append(PageBreak())

def create_executive_summary(story, styles, df):
    """주요 요약 페이지"""
    story.append(Paragraph("Executive Summary", styles['title']))
    story.append(Spacer(1, 0.3*inch))
    
    # 급락 정보
    crash_date = pd.Timestamp('2025-10-10')
    crash_row = df[df['date'] == crash_date].iloc[0]
    prev_row = df[df['date'] == crash_date - pd.Timedelta(days=1)].iloc[0]
    
    crash_price = crash_row['BTC_Price']
    prev_price = prev_row['BTC_Price']
    crash_pct = ((crash_price - prev_price) / prev_price) * 100
    
    summary_text = f"""
    <b>1. 가격 변동 개요</b><br/>
    • 급락일 (2025-10-10) 가격: ${crash_price:,.2f}<br/>
    • 변화율: {crash_pct:.2f}%<br/>
    • 분석 기간 최고가: ${df['BTC_Price'].max():,.2f} ({df[df['BTC_Price'] == df['BTC_Price'].max()]['date'].iloc[0].strftime('%Y-%m-%d')})<br/>
    • 분석 기간 최저가: ${df['BTC_Price'].min():,.2f} ({df[df['BTC_Price'] == df['BTC_Price'].min()]['date'].iloc[0].strftime('%Y-%m-%d')})<br/>
    <br/>
    <b>2. 거시경제 영향 (R² = 0.4448)</b><br/>
    • M2 통화량: 양의 영향 (+4,241 표준화 계수)<br/>
    • 달러 인덱스: 음의 영향 (-3,740 표준화 계수)<br/>
    • 10년물 금리: 양의 영향 (+2,223 표준화 계수)<br/>
    <br/>
    <b>3. 감성 분석 결과</b><br/>
    • 전반적 감성: 부정 우세 (평균 tone_mean = {df['tone_mean'].mean():.3f})<br/>
    • 부정 뉴스 비율(tone_neg_share)이 가격과 유의한 상관관계 (p=0.040)<br/>
    • 급락 전 3일간 정치 테마 17.4% 급증<br/>
    <br/>
    <b>4. Open Interest 패턴</b><br/>
    • 급락 전 평균 OI: 103.95 (최고치)<br/>
    • 급락 후 평균 OI: 71.74 (-31% 감소)<br/>
    • OI와 가격 강한 양의 상관관계 (r = +0.684)<br/>
    <br/>
    <b>5. 네트워크 분석</b><br/>
    • SNS 활동(sns_post_count)이 최고 연결 중심성 (0.667)<br/>
    • 부정 뉴스 비율이 네트워크 허브 역할 (betweenness = 0.229)<br/>
    """
    
    summary = Paragraph(summary_text, styles['body'])
    story.append(summary)
    story.append(PageBreak())

def add_chart_section(story, styles, chart_path, title, description):
    """차트 섹션 추가"""
    story.append(Paragraph(title, styles['section']))
    story.append(Spacer(1, 0.1*inch))
    
    if description:
        desc = Paragraph(description, styles['body'])
        story.append(desc)
        story.append(Spacer(1, 0.1*inch))
    
    if chart_path.exists():
        # 이미지 크기 조정 (A4 용지에 맞게)
        img = Image(str(chart_path), width=6.5*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 0.2*inch))
    else:
        no_chart = Paragraph(f"차트를 찾을 수 없습니다: {chart_path.name}", styles['body'])
        story.append(no_chart)
        story.append(Spacer(1, 0.2*inch))

def create_analysis_sections(story, styles):
    """분석 섹션들 생성"""
    
    # 가격 분석
    story.append(Paragraph("1. 가격 추이 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "01_price_trend.png",
        "비트코인 가격 추이",
        "2025년 9월-10월 비트코인 가격 변동 추이. 10월 10일 급락이 명확히 표시되어 있습니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "02_price_trend_with_speed.png",
        "가격 및 변화 속도",
        "가격의 1차 및 2차 미분을 통한 변화 속도 분석입니다."
    )
    
    story.append(PageBreak())
    
    # 상관관계 분석
    story.append(Paragraph("2. 상관관계 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "03_correlation_heatmap_full.png",
        "전체 변수 상관관계 히트맵",
        "모든 변수 간의 상관관계를 시각화한 히트맵입니다."
    )
    
    story.append(PageBreak())
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "04_correlation_heatmap_high.png",
        "강한 상관관계 히트맵",
        "절대값 0.5 이상의 강한 상관관계만 표시한 히트맵입니다."
    )
    
    story.append(PageBreak())
    
    # 정치 테마 분석
    story.append(Paragraph("3. 정치 테마 영향 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "06_political_themes_timeseries.png",
        "정치 테마 시계열",
        "뉴스에서 정치 관련 테마의 등장 빈도 추이입니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "07_political_price_correlation.png",
        "정치 테마와 가격 상관관계",
        "정치 테마 빈도와 비트코인 가격 간의 시차별 상관관계 분석입니다."
    )
    
    story.append(PageBreak())
    
    # 감성 분석
    story.append(Paragraph("4. 감성-가격 회귀 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "08_sentiment_regression_scatter.png",
        "감성 vs 가격 산점도",
        "뉴스 감성 점수와 비트코인 가격 간의 관계를 나타낸 산점도입니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "09_sentiment_regression_residuals.png",
        "회귀 분석 잔차 플롯",
        "회귀 모델의 잔차 분포를 통한 모델 적합도 평가입니다."
    )
    
    story.append(PageBreak())
    
    # 거시경제 분석
    story.append(Paragraph("5. 거시경제 지표 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "10_macro_regression_scatter.png",
        "거시경제 회귀 분석",
        "M2, 10년물 금리, 달러 인덱스와 가격의 관계입니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "11_macro_regression_residuals.png",
        "거시경제 모델 잔차",
        "거시경제 변수 회귀 모델의 잔차 분석입니다."
    )
    
    story.append(PageBreak())
    
    # Open Interest 분석
    story.append(Paragraph("6. Open Interest 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "12_open_interest_price.png",
        "Open Interest vs 가격",
        "선물 미결제약정과 비트코인 가격의 관계입니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "13_open_interest_crash_analysis.png",
        "급락 전후 OI 분석",
        "급락 전후 Open Interest의 급격한 변화를 보여줍니다."
    )
    
    story.append(PageBreak())
    
    # 워드클라우드
    story.append(Paragraph("7. 감성 워드클라우드", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "14_wordcloud_overall.png",
        "전체 키워드 워드클라우드",
        "전체 기간의 주요 키워드를 시각화한 워드클라우드입니다."
    )
    
    story.append(PageBreak())
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "15_wordcloud_negative.png",
        "부정 감성 워드클라우드",
        "부정적 감성을 가진 키워드들의 빈도를 나타냅니다."
    )
    
    story.append(PageBreak())
    
    # 네트워크 분석
    story.append(Paragraph("8. 네트워크 관계 분석", styles['subtitle']))
    story.append(Spacer(1, 0.2*inch))
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "17_network_full.png",
        "전체 변수 네트워크",
        "모든 변수 간의 연결 관계를 네트워크로 표현했습니다."
    )
    
    add_chart_section(
        story, styles,
        OUTPUT_DIR / "18_network_simplified.png",
        "핵심 변수 네트워크",
        "높은 중심성을 가진 핵심 변수들의 네트워크입니다."
    )

def create_conclusion(story, styles):
    """결론 페이지"""
    story.append(PageBreak())
    story.append(Paragraph("결론 및 시사점", styles['title']))
    story.append(Spacer(1, 0.3*inch))
    
    conclusion_text = """
    <b>주요 발견사항</b><br/>
    <br/>
    1. <b>거시경제 변수의 높은 설명력</b><br/>
       • M2 통화량, 10년물 금리, 달러 인덱스가 가격 변동의 44.5%를 설명<br/>
       • 감성 변수(19.7%)보다 2배 이상 높은 설명력<br/>
    <br/>
    2. <b>Open Interest의 선행 지표 가능성</b><br/>
       • OI와 가격의 강한 양의 상관관계 (r = +0.684)<br/>
       • 급락 다음날 OI 32% 급감 → 대규모 청산 발생<br/>
    <br/>
    3. <b>정치 테마의 시차 효과</b><br/>
       • 정치 관련 뉴스가 가격에 1일 선행<br/>
       • 급락 전 3일간 정치 테마 17.4% 급증<br/>
    <br/>
    4. <b>SNS 활동의 중심 역할</b><br/>
       • sns_post_count가 최고 연결 중심성 (0.667)<br/>
       • 커뮤니티 활동이 시장 전반의 허브 역할<br/>
    <br/>
    5. <b>부정 감성의 유의한 영향</b><br/>
       • tone_neg_share가 가격과 유의한 관계 (p = 0.040)<br/>
       • 네트워크에서 허브 역할 (betweenness = 0.229)<br/>
    <br/>
    <b>투자 시사점</b><br/>
    <br/>
    • 거시경제 지표(M2, 금리, 달러)를 주요 모니터링 지표로 활용<br/>
    • Open Interest 급감 시 청산 위험 증가 신호로 해석<br/>
    • 정치 관련 뉴스 급증 시 1일 후 변동성 증가 대비<br/>
    • SNS 커뮤니티 활동 지표를 시장 심리 판단에 활용<br/>
    • 부정 뉴스 비율 증가 시 가격 하락 가능성 고려<br/>
    """
    
    conclusion = Paragraph(conclusion_text, styles['body'])
    story.append(conclusion)

def generate_report():
    """PDF 리포트 생성"""
    print("=" * 60)
    print("PDF 분석 리포트 생성 시작")
    print("=" * 60)
    
    # 데이터 로드
    print("\n[1/4] 데이터 로딩...")
    df = load_data()
    print(f"  ✓ 데이터 로드 완료: {len(df)} rows")
    
    # PDF 문서 생성
    print("\n[2/4] PDF 문서 생성...")
    report_path = REPORT_DIR / f"Bitcoin_Crash_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 스토리 생성
    story = []
    styles = create_custom_styles()
    
    print("\n[3/4] 리포트 컨텐츠 생성...")
    print("  • 표지 페이지")
    create_cover_page(story, styles)
    
    print("  • 요약 페이지")
    create_executive_summary(story, styles, df)
    
    print("  • 분석 섹션들")
    create_analysis_sections(story, styles)
    
    print("  • 결론 페이지")
    create_conclusion(story, styles)
    
    # PDF 빌드
    print("\n[4/4] PDF 파일 생성 중...")
    doc.build(story)
    
    print("\n" + "=" * 60)
    print("✓ PDF 리포트 생성 완료!")
    print(f"  파일 위치: {report_path}")
    print(f"  파일 크기: {report_path.stat().st_size / 1024:.2f} KB")
    print("=" * 60)
    
    return report_path

if __name__ == "__main__":
    try:
        report_path = generate_report()
        print(f"\n성공: {report_path}")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
