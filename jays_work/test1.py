import pandas as pd
import folium
from datetime import datetime



file1 = ""
file2 = ""
myKey = ''

df = pd.read_csv(file1)
print(df.head(2))

loc_df = pd.read_csv(file2)
print(loc_df.head(2))

# file1 key colums...
file1_colums = ['', '', '']
file1_df_new = df[[myKey] + file1_colums]

print(file1_df_new)

# file2 key colums...
file2_key = ''
file2_colums = ['', '']
file2_df_new = loc_df[ [file2_key] + file2_colums ]
file2_df_new.columns = [myKey, "LAT", "LONG"]
print(file2_df_new)

merge_data = pd.merge(
    left=file1_df_new,          # 데이터1
    right=file2_df_new,         # 데이터2
    how="left",                 # 취합방법(left, right, inner, outer)
    on=myKey                    # 기준
)
print(merge_data)

today = datetime.now().strftime('%y%m%d')
filename = f"./data/merged_{myKey}_{today}.csv"
merge_data.to_csv(filename, index=False, encoding='utf-8-sig')
print(f"데이터 저장 완료: {filename}")



