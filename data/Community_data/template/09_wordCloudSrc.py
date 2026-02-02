#데이터 불러오기
import pandas as pd
from konlpy.tag import Okt 
import re 
from collections import Counter 
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
import koreanize_matplotlib

df_new = pd.read_csv(
    "./data/appreply2_보충.csv", #./data/appreply2_보충.csv
    index_col=0
)

okt = Okt()
# 반복문
word_list = []
stopwords = ["진짜", "카톡", "로그인"]

# 패턴: [^0-9가-힣a-zA-Z\s]
for sent in df_new["text"]: # sent: 문장
    # print("STEP1. 문장을 전처리합니다.")
    # 리뷰 텍스트 전처리
    clean_sent = re.sub("[^0-9가-힣a-zA-Z\s]", "", sent)
    # print("STEP2. 문장을 형태소분석기로 토크나이징합니다.")
    # 토크나이징(형태소 분석기: Okt)
    result = okt.pos(clean_sent)
    # result를 하나씩 뽑는다. 
    # print("STEP3. 새로운 리스트를 만듭니다.")
    sub_list = []
    # print("\t탐색을 시작합니다.")
    for res in result: # res : (단어, 품사)
        word = res[0]
        pos = res[1]
        # word가 stopwords에 있으면 건너뛰기
        if word in stopwords:
            # print("\t건너뛰어!", res)
            continue

        # sub_list 만들기: 조건 pos == "Noun" and len(word) > 1
        if pos == "Noun" and len(word) > 1:
            sub_list.append(word)
word_list.extend(sub_list)
print(f"\t[WORD LIST] {word_list}")
print("="*100)
    

counter = Counter(word_list)
wc = WordCloud(
    font_path = "C:\Windows\Fonts\malgun.ttf", # "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    background_color="white",
    width=800,
    height=400
)

wc.generate_from_frequencies(counter)

plt.figure(figsize=(5,5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("배달의 민족 워드 클라우드(명사)", fontsize=15)
plt.show()
