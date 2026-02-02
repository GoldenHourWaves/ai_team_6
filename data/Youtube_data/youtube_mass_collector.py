#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 대량 데이터 수집기
October 2025 Crypto Crash 전용

목표: 10,000 - 20,000개 텍스트 데이터
기간: 2025-09-01 ~ 2025-10-31
수집 대상: 영상 메타데이터 + 댓글 + 자막(캡션)

예상 수집량:
- 영상: 500-1,000개
- 댓글: 10,000-15,000개
- 자막: 5,000-10,000개 문장
─────────────────────────
총: 15,000-26,000개 텍스트

소요 시간: 2-4시간
비용: 무료 (할당량 10,000 units/일)
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re

# ============================================================================
# 설정 (여기만 수정하세요!)
# ============================================================================

# YouTube API 키
# 발급 방법: https://console.cloud.google.com/apis/credentials
API_KEY = 'YOUR_YOUTUBE_API_KEY_HERE'  # ← 여기에 붙여넣기!

# 수집 설정
COLLECTION_CONFIG = {
    'date_range': {
        'start': '2025-09-01T00:00:00Z',
        'end': '2025-10-31T23:59:59Z'
    },
    'target_videos': 1000,          # 목표 영상 수
    'target_comments': 15000,       # 목표 댓글 수
    'max_comments_per_video': 100,  # 영상당 최대 댓글
    'target_captions': 10000,       # 목표 자막 문장 수
}

# 검색 키워드 (크립토 크래시 관련)
SEARCH_KEYWORDS = [
    # 핵심 키워드
    'October 2025 crypto crash',
    'crypto crash October 2025',
    '$19 billion liquidation',
    'October 10 2025 crypto',
    'October 11 2025 bitcoin',
    
    # 이벤트
    'Trump tariff crypto crash',
    'Binance crash October 2025',
    'Hyperliquid liquidation',
    'crypto flash crash 2025',
    
    # 분석
    'October 2025 crypto analysis',
    'crypto market crash 2025',
    'bitcoin crash October',
    'ethereum crash October 2025',
    
    # 영향
    'crypto liquidation 2025',
    'whale liquidation October',
    'crypto bloodbath 2025',
    'October crypto dump',
    
    # 반응
    'crypto crash reaction October',
    'October 2025 trading disaster',
    'crypto portfolio destroyed',
    
    # 일반 크립토 (기간 내)
    'bitcoin September 2025',
    'ethereum October 2025',
    'crypto news October 2025',
    'altcoin crash 2025',
]

# 저장 경로
OUTPUT_DIR = './youtube_data_collection'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# YouTube API 초기화
# ============================================================================

print("=" * 100)
print("YouTube 대량 데이터 수집기")
print("=" * 100)
print()

if API_KEY == 'YOUR_YOUTUBE_API_KEY_HERE':
    print("❌ API 키를 설정해주세요!")
    print()
    print("발급 방법:")
    print("1. https://console.cloud.google.com/ 접속")
    print("2. 프로젝트 생성")
    print("3. YouTube Data API v3 활성화")
    print("4. API 키 생성")
    print("5. 위 API_KEY 변수에 붙여넣기")
    print()
    exit(1)

try:
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    print("✅ YouTube API 연결 성공!")
    print()
except Exception as e:
    print(f"❌ YouTube API 연결 실패: {e}")
    exit(1)

# ============================================================================
# 수집 함수들
# ============================================================================

def search_videos(keyword, max_results=50):
    """키워드로 영상 검색"""
    videos = []
    
    try:
        request = youtube.search().list(
            part='snippet',
            q=keyword,
            type='video',
            maxResults=max_results,
            order='relevance',
            publishedAfter=COLLECTION_CONFIG['date_range']['start'],
            publishedBefore=COLLECTION_CONFIG['date_range']['end'],
            relevanceLanguage='en',  # 영어 우선
        )
        
        response = request.execute()
        
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            video_data = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'search_keyword': keyword,
                'url': f'https://www.youtube.com/watch?v={video_id}',
            }
            
            videos.append(video_data)
        
        print(f"    ✓ '{keyword}' → {len(videos)}개 영상")
        
    except HttpError as e:
        print(f"    ✗ 오류: {e}")
    
    return videos

def get_video_details(video_ids):
    """영상 상세 정보 (조회수, 좋아요, 댓글 수 등)"""
    details = {}
    
    try:
        # 50개씩 배치 처리
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            
            request = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(batch)
            )
            
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['id']
                stats = item.get('statistics', {})
                content = item.get('contentDetails', {})
                
                details[video_id] = {
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'duration': content.get('duration', ''),
                }
            
            time.sleep(0.5)  # Rate limit
        
    except HttpError as e:
        print(f"    ✗ 상세 정보 오류: {e}")
    
    return details

def get_video_comments(video_id, max_comments=100):
    """영상 댓글 수집"""
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=min(max_comments, 100),
            order='relevance',
            textFormat='plainText'
        )
        
        while request and len(comments) < max_comments:
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                
                comment_data = {
                    'video_id': video_id,
                    'comment_id': item['snippet']['topLevelComment']['id'],
                    'text': snippet.get('textDisplay', ''),
                    'author': snippet.get('authorDisplayName', ''),
                    'like_count': snippet.get('likeCount', 0),
                    'published_at': snippet.get('publishedAt', ''),
                    'reply_count': item['snippet'].get('totalReplyCount', 0),
                }
                
                comments.append(comment_data)
            
            # 다음 페이지
            if 'nextPageToken' in response and len(comments) < max_comments:
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    maxResults=min(max_comments - len(comments), 100),
                    order='relevance',
                    textFormat='plainText'
                )
            else:
                break
        
    except HttpError as e:
        # 댓글 비활성화된 경우 등
        pass
    
    return comments

def get_video_captions(video_id):
    """영상 자막(캡션) 수집"""
    captions = []
    
    try:
        # 한국어 또는 영어 자막 시도
        for lang in ['ko', 'en']:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                
                for entry in transcript:
                    caption_data = {
                        'video_id': video_id,
                        'text': entry['text'],
                        'start': entry['start'],
                        'duration': entry['duration'],
                        'language': lang,
                    }
                    captions.append(caption_data)
                
                # 성공하면 루프 탈출
                break
                
            except (TranscriptsDisabled, NoTranscriptFound):
                continue
        
    except Exception as e:
        pass
    
    return captions

# ============================================================================
# 메인 수집 프로세스
# ============================================================================

print("수집 시작...")
print(f"  기간: {COLLECTION_CONFIG['date_range']['start'][:10]} ~ {COLLECTION_CONFIG['date_range']['end'][:10]}")
print(f"  목표: 영상 {COLLECTION_CONFIG['target_videos']}개, 댓글 {COLLECTION_CONFIG['target_comments']}개")
print()

all_videos = []
all_comments = []
all_captions = []

start_time = time.time()

# ============================================================================
# Step 1: 영상 검색
# ============================================================================
print("[1/4] 영상 검색 중...")

for i, keyword in enumerate(SEARCH_KEYWORDS, 1):
    print(f"  [{i}/{len(SEARCH_KEYWORDS)}] 검색 중...")
    
    videos = search_videos(keyword, max_results=50)
    all_videos.extend(videos)
    
    time.sleep(1)  # Rate limit
    
    # 목표 달성 체크
    if len(all_videos) >= COLLECTION_CONFIG['target_videos']:
        print(f"  🎯 목표 달성! ({COLLECTION_CONFIG['target_videos']}개)")
        break

# 중복 제거
videos_df = pd.DataFrame(all_videos)
if len(videos_df) > 0:
    videos_df = videos_df.drop_duplicates(subset=['video_id'])
    all_videos = videos_df.to_dict('records')

print(f"\n✅ 총 {len(all_videos)}개 영상 발견 (중복 제거 후)")

# 중간 저장
videos_file = f"{OUTPUT_DIR}/videos_metadata.csv"
videos_df.to_csv(videos_file, index=False, encoding='utf-8-sig')
print(f"💾 저장: {videos_file}")

# ============================================================================
# Step 2: 영상 상세 정보
# ============================================================================
print(f"\n[2/4] 영상 상세 정보 수집 중...")

video_ids = [v['video_id'] for v in all_videos]
details = get_video_details(video_ids)

# 상세 정보 병합
for video in all_videos:
    video_id = video['video_id']
    if video_id in details:
        video.update(details[video_id])

print(f"✅ {len(details)}개 영상 상세 정보 수집")

# ============================================================================
# Step 3: 댓글 수집
# ============================================================================
print(f"\n[3/4] 댓글 수집 중... (영상 {len(all_videos)}개)")

for i, video in enumerate(all_videos, 1):
    video_id = video['video_id']
    
    # 진행 상황
    if i % 50 == 0:
        elapsed = time.time() - start_time
        rate = i / elapsed * 60  # 영상/분
        eta = (len(all_videos) - i) / rate if rate > 0 else 0
        print(f"  진행: {i}/{len(all_videos)} ({i/len(all_videos)*100:.1f}%) | "
              f"댓글: {len(all_comments)}개 | ETA: {eta:.1f}분")
    
    # 댓글 수집
    comments = get_video_comments(video_id, 
                                  max_comments=COLLECTION_CONFIG['max_comments_per_video'])
    all_comments.extend(comments)
    
    time.sleep(0.5)  # Rate limit
    
    # 목표 달성 체크
    if len(all_comments) >= COLLECTION_CONFIG['target_comments']:
        print(f"  🎯 댓글 목표 달성! ({COLLECTION_CONFIG['target_comments']}개)")
        break

print(f"\n✅ 총 {len(all_comments)}개 댓글 수집")

# 중간 저장
if len(all_comments) > 0:
    comments_df = pd.DataFrame(all_comments)
    comments_file = f"{OUTPUT_DIR}/comments_temp.csv"
    comments_df.to_csv(comments_file, index=False, encoding='utf-8-sig')
    print(f"💾 저장: {comments_file}")

# ============================================================================
# Step 4: 자막(캡션) 수집
# ============================================================================
print(f"\n[4/4] 자막 수집 중... (영상 {len(all_videos)}개)")

caption_videos = 0
for i, video in enumerate(all_videos, 1):
    video_id = video['video_id']
    
    if i % 50 == 0:
        print(f"  진행: {i}/{len(all_videos)} | 자막: {len(all_captions)}개 문장 | "
              f"성공: {caption_videos}개 영상")
    
    # 자막 수집
    captions = get_video_captions(video_id)
    
    if len(captions) > 0:
        all_captions.extend(captions)
        caption_videos += 1
    
    time.sleep(0.3)  # Rate limit
    
    # 목표 달성 체크
    if len(all_captions) >= COLLECTION_CONFIG['target_captions']:
        print(f"  🎯 자막 목표 달성! ({COLLECTION_CONFIG['target_captions']}개)")
        break

print(f"\n✅ 총 {len(all_captions)}개 자막 문장 수집 ({caption_videos}개 영상)")

# ============================================================================
# 최종 저장
# ============================================================================

print("\n" + "=" * 100)
print("수집 완료!")
print("=" * 100)

total_time = time.time() - start_time
total_text_items = len(all_videos) + len(all_comments) + len(all_captions)

print(f"\n📊 수집 통계:")
print(f"  영상: {len(all_videos)}개")
print(f"    - 제목: {len(all_videos)}개")
print(f"    - 설명: {len([v for v in all_videos if v.get('description')])}개")
print(f"  댓글: {len(all_comments)}개")
print(f"  자막: {len(all_captions)}개 문장")
print(f"  ─────────────────────────")
print(f"  총 텍스트 항목: {total_text_items:,}개")
print(f"  소요 시간: {total_time/60:.1f}분")

# 텍스트 길이 계산
total_chars = 0
if len(all_videos) > 0:
    total_chars += sum(len(str(v.get('title', ''))) + len(str(v.get('description', ''))) for v in all_videos)
if len(all_comments) > 0:
    total_chars += sum(len(str(c.get('text', ''))) for c in all_comments)
if len(all_captions) > 0:
    total_chars += sum(len(str(c.get('text', ''))) for c in all_captions)

print(f"  총 텍스트 길이: {total_chars:,} 글자")

# 저장
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 1. 영상 메타데이터
if len(all_videos) > 0:
    videos_df = pd.DataFrame(all_videos)
    videos_final = f"{OUTPUT_DIR}/youtube_videos_{timestamp}.csv"
    videos_df.to_csv(videos_final, index=False, encoding='utf-8-sig')
    print(f"\n💾 영상 저장: {videos_final}")
    print(f"   크기: {os.path.getsize(videos_final) / 1024:.1f} KB")

# 2. 댓글
if len(all_comments) > 0:
    comments_df = pd.DataFrame(all_comments)
    comments_final = f"{OUTPUT_DIR}/youtube_comments_{timestamp}.csv"
    comments_df.to_csv(comments_final, index=False, encoding='utf-8-sig')
    print(f"💾 댓글 저장: {comments_final}")
    print(f"   크기: {os.path.getsize(comments_final) / 1024:.1f} KB")

# 3. 자막
if len(all_captions) > 0:
    captions_df = pd.DataFrame(all_captions)
    captions_final = f"{OUTPUT_DIR}/youtube_captions_{timestamp}.csv"
    captions_df.to_csv(captions_final, index=False, encoding='utf-8-sig')
    print(f"💾 자막 저장: {captions_final}")
    print(f"   크기: {os.path.getsize(captions_final) / 1024:.1f} KB")

# 4. 통합 JSON
combined_data = {
    'metadata': {
        'collection_date': timestamp,
        'total_videos': len(all_videos),
        'total_comments': len(all_comments),
        'total_captions': len(all_captions),
        'total_text_items': total_text_items,
        'duration_minutes': total_time / 60,
        'date_range': COLLECTION_CONFIG['date_range'],
    },
    'videos': all_videos,
    'comments': all_comments,
    'captions': all_captions,
}

json_file = f"{OUTPUT_DIR}/youtube_collection_{timestamp}.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False)

print(f"💾 JSON 저장: {json_file}")

# ============================================================================
# 분석 리포트
# ============================================================================

print("\n" + "=" * 100)
print("데이터 분석 리포트")
print("=" * 100)

if len(all_videos) > 0:
    print("\n📹 영상 분석:")
    print(f"  평균 조회수: {videos_df['view_count'].mean():,.0f}")
    print(f"  평균 좋아요: {videos_df['like_count'].mean():,.0f}")
    print(f"  평균 댓글수: {videos_df['comment_count'].mean():,.0f}")
    print(f"\n  상위 채널:")
    for channel, count in videos_df['channel_title'].value_counts().head(5).items():
        print(f"    - {channel}: {count}개")

if len(all_comments) > 0:
    print(f"\n💬 댓글 분석:")
    print(f"  평균 길이: {comments_df['text'].str.len().mean():.0f} 글자")
    print(f"  평균 좋아요: {comments_df['like_count'].mean():.1f}")
    print(f"  답글 있는 댓글: {len(comments_df[comments_df['reply_count'] > 0])}개")

if len(all_captions) > 0:
    print(f"\n📝 자막 분석:")
    print(f"  자막 있는 영상: {caption_videos}개 ({caption_videos/len(all_videos)*100:.1f}%)")
    print(f"  평균 문장 길이: {captions_df['text'].str.len().mean():.0f} 글자")
    print(f"  언어 분포:")
    for lang, count in captions_df['language'].value_counts().items():
        lang_name = 'Korean' if lang == 'ko' else 'English'
        print(f"    - {lang_name}: {count}개")

# 목표 달성 확인
print("\n" + "=" * 100)
print("목표 달성 현황")
print("=" * 100)

target_total = 15000  # 목표 텍스트 수
achieved = total_text_items

print(f"\n🎯 목표: 10,000 - 20,000개 텍스트 데이터")
print(f"✅ 달성: {achieved:,}개")

if achieved >= 10000:
    print(f"🎉 목표 달성! ({achieved/target_total*100:.1f}%)")
else:
    remaining = 10000 - achieved
    print(f"⚠️  {remaining:,}개 더 필요")

print(f"\n📂 저장 위치: {os.path.abspath(OUTPUT_DIR)}")
print("\n✅ 수집 완료! 파일을 확인하세요.")
