### 1. 메뉴 준비 ###
import sqlite3
import pandas as pd

# DB 연결
db_path = r"D:\Class\3-1\MachineLearning\SQLite\miniai-db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 카테고리, 메뉴, 옵션 df로 변환
categories_df = pd.read_sql_query("SELECT * FROM categories", conn)
menus_df = pd.read_sql_query("SELECT * FROM menus", conn)
options_df = pd.read_sql_query("SELECT * FROM options", conn)

# DB 종료
conn.close()

menu_names = menus_df['menu_name'].tolist()

print("\n😊 { 어서오세요! 메뉴를 고르신 후 저에게 주문해주세요! ]")

# 메뉴판 출력
print("\n▀▄▀▄▀▄▀▄▀ 메뉴판 ▀▄▀▄▀▄▀▄▀")
for index, row in categories_df.iterrows():
    ctgr_id = row['ctgr_id']
    ctgr_name = row['ctgr_name']
    print("\n %s -----" % ctgr_name)

    menus = menus_df[menus_df['ctgr_id'] == ctgr_id]
    for index, row in menus.iterrows():
        print("\t%s %s원" % (row['menu_name'], row['menu_price']))
print("\n▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀")

### 2. 음성 인식하여 텍스트로 변환하기 ###
import sounddevice as sd
from scipy.io.wavfile import write
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


# 음성 녹음
def record_audio(seconds=10, samplerate=44100, channels=2, filename='order.wav'):
    print("\n👂··· 주문을 듣고 있어요!")
    recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()
    write(filename, samplerate, recording)
    print("\n👀··· 주문을 확인하고 있어요 잠시만 기다려주세요!")


# STT 변환
def audio_to_text(filename):
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text


# 주문 받기
if __name__ == "__main__":
    seconds = 5
    audio_filename = 'order.wav'
    record_audio(seconds, 44100, 2, audio_filename)
    order_text = audio_to_text(audio_filename)
    print("\n🎙️: %s" % order_text)

### 3. 주문 확인 ###
import json

system_role = '너는 카페의 주문 받는 로봇이다. 손님의 요청을 듣고 각 메뉴마다 메뉴명, 온도, 수량, 추가 요청 사항 목록을 json 형식으로 작성하여 리스트로 반환해준다. key는 menu, temp, count, options로 고정한다. 메뉴명에 아이스나 핫이 들어갈 경우 해당 단어는 제외힌다. 메뉴가 음료인 경우 temp의 값은 손님의 요청대로 입력한다. ice, hot 중 하나만 들어갈 수 있으며 고르지 않은 경우 none을 입력한다. 예외로 메뉴가 디저트인 경우 temp의 값은 dessert이다. options 예시로는 size up, 연하게, 덜 달게, 시럽 추가, 헤이즐넛 시럽 추가, 휘핑 크림 추가 등이 있으며 중복 선택이 가능하다. 또 손님이 원하는 다른 요청사항도 options에 추가할 수 있다. 요청사항이 없다면 options는 빈 리스트로 입력한다. 같은 메뉴명이라도 temp 값이나 options 값이 다른 경우 다른 메뉴로 구분한다.'
prompt = order_text
top = 0.9
temp = 1.0

completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_role,
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    model="gpt-3.5-turbo",
    top_p=top,
    temperature=temp,
)

order_list = json.loads(completion.choices[0].message.content.replace("'", '"'))


### 3-1. 음료 주문 수정 ###

def reorderTemp():
    seconds = 5
    audio_filename = 'order.wav'
    record_audio(seconds, 44100, 2, audio_filename)
    order_text = audio_to_text(audio_filename)
    print("\n🎙️: %s" % order_text)

    system_role = "너는 카페의 주문 받는 로봇이다. 손님의 요청을 듣고 다음 보기에서 알맞는 단어만 출력한다. 보기 : ice, hot"
    prompt = order_text
    top = 0.9
    temp = 1.0

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_role,
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo",
        top_p=top,
        temperature=temp,
    )

    return completion.choices[0].message.content


### 3-2. 추가 요청
def reorder(order_list):
    seconds = 5
    audio_filename = 'order.wav'
    record_audio(seconds, 44100, 2, audio_filename)
    order_text = audio_to_text(audio_filename)
    print("\n🎙️: %s" % order_text)

    system_role = '너는 카페의 주문 받는 로봇이다. 직전에 손님에게 더 필요한 것이 있는지 물었다. 손님이 더 요청하는 게 없다면 null을 반환한다. 손님이 주문을 추가하거나 수정한다면 기존 주문 내역을 알맞게 수정하여 json 형태로 반환한다. key는 menu, temp, count, options로 고정한다. 메뉴가 음료인 경우 temp의 값은 손님의 요청대로 입력한다. ice, hot 중 하나만 들어갈 수 있으며 고르지 않은 경우 none을 입력한다. 예외로 메뉴가 디저트인 경우 temp의 값은 dessert이다. 메뉴가 디저트인 경우 temp의 값은 dessert이다. options 예시로는 size up, 연하게, 덜 달게, 시럽 추가, 헤이즐넛 시럽 추가, 휘핑 크림 추가 등이 있으며 중복 선택이 가능하다. 또 손님이 원하는 다른 요청사항도 options에 추가할 수 있다. 요청사항이 없다면 options는 빈 리스트로 입력한다. 같은 메뉴명이라도 temp 값이나 options 값이 다른 경우 다른 메뉴로 구분한다. 기존 주문 내역 : %s' % str(order_list)
    prompt = order_text
    top = 0.9
    temp = 1.0

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_role,
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo",
        top_p=top,
        temperature=temp,
    )

    reorder_list = json.loads(completion.choices[0].message.content.replace("'", '"'))
    return reorder_list


### 4. 주문 확인 ###

def check():
    # 음료 확인
    for item in order_list:
        if item['temp'] in ('none', 'null'):
            print("\n🤓 { %s는 따뜻한 걸로 드릴까요? 아이스로 드릴까요? ]" % item["menu"])
            item["temp"] = reorderTemp()

    # 주문 확인
    order_price = 0
    print("\n🤓 { 주문 확인 도와드리겠습니다! ]")
    print("\n========== 주문 내역 ==========")
    for item in order_list:
        price = menus_df.loc[menus_df['menu_name'] == item['menu'], 'menu_price'].values[0]
        print("\n%s [%s]\t%s원\t%s개" % (item['menu'], item['temp'], price, item['count']), end='')

        option_price = 0
        for option in item["options"]:

            option_price = '0'
            if options_df['option_name'].isin([option]).any():
                option_price = options_df.loc[options_df['option_name'] == option, 'option_price'].values[0]
            print("\n\t└ %s" % option, end='')
            if int(option_price) > 0:
                option_price += int(option_price)
                print("\t %s원" % option_price, end='')

        order_price += (int(price) + int(option_price)) * int(item["count"])
    print("\n------------------------------")
    print("총 %d원" % order_price)
    print("==============================")
    print("\n☺️ { 더 필요한 게 있으신가요? ]")
    return reorder(order_list)


reorder_list = check()
while reorder_list is not None:
    order_list = reorder_list
    reorder_list = check()

print("\n🥰 { 주문이 완료되었습니다. 잠시만 기다려주세요~ ]")
