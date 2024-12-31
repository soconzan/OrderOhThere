import sqlite3
import pandas as pd

# 데이터베이스 파일 경로
db_path = r"D:\Class\3-1\MachineLearning\SQLite\miniai-db"

# 데이터베이스 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# DataFrame 변환
categories_df = pd.read_sql_query("SELECT * FROM categories", conn)
menus_df = pd.read_sql_query("SELECT * FROM menus", conn)
options_df = pd.read_sql_query("SELECT * FROM options", conn)

# 연결 종료
conn.close()

# 데이터 확인
print(categories_df.head())  # DataFrame의 처음 몇 줄을 출력
print(menus_df)  # DataFrame의 처음 몇 줄을 출력
print(options_df)  # DataFrame의 처음 몇 줄을 출력

menu_names = menus_df['menu_name'].tolist()

print(menu_names)

