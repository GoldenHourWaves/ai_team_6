import pandas as pd 
import folium

def get_top_locations_by_distance(df, group_col, value_col, top_n=None):
    """
    대여소별 평균 이동거리 상위 N개를 반환하는 함수
    
    Args:
        df: 데이터프레임
        group_col: 그룹화할 컬럼명 (예: '대여소명')
        value_col: 평균을 계산할 컬럼명 (예: '건당 이동거리(M)') - 문자열 또는 리스트
        top_n: 반환할 상위 개수 (기본값: None - 전체 반환)
    
    Returns:
        상위 N개 대여소의 평균 이동거리 데이터프레임 (top_n이 None이면 전체 반환)
    """
    # value_col이 리스트인 경우 첫 번째 요소만 사용
    if isinstance(value_col, list):
        value_col = value_col[0]
    
    result = df.groupby(group_col)[value_col].mean().sort_values(ascending=False)
    if top_n is not None:
        result = result.head(top_n)
    result = result.reset_index()
    return result

file1 = "./data/따릉이_월별정보_전처리_데이터(25_7_12).csv"
file2 = "./data/공공자전거 대여소 정보.csv"
df = pd.read_csv(file1)
print(df.head(2))

loc_df = pd.read_csv(file2)
print(loc_df.head(2))


# file1 key colums...
file1_key = '대여소명'
file1_colums = ['건당 이동거리(M)', 'RENT_NO']
file1_df_new = get_top_locations_by_distance(df, file1_key, file1_colums)
print(file1_df_new)

# file2 key colums...
file2_key = 'RENT_ID_NM'
file2_colums = ['STA_LAT', 'STA_LONG']
file2_df_new = loc_df[ [file2_key, "STA_LAT", "STA_LONG"] ]
file2_df_new.columns = ["대여소명", "LAT", "LONG"]
print(file2_df_new)

merge_data = pd.merge(
    left=file1_df_new,          # 데이터1
    right=file2_df_new,                   # 데이터2
    how="left",                         # 취합방법(left, right, inner, outer)
    on="대여소명"                       # 기준
)
print(merge_data)

merge_data.to_csv(
    "./data/따릉이Merged_0202.csv", # "/content/appreply2.csv"
)