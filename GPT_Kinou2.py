import os
import openai
import pyaudio
import pygame
import time
import speech_recognition as sr
import pymysql
import re
from pydub import AudioSegment
from gtts import gTTS

# Database 연결 설정
db_config = {
    "host": 'localhost',
    "user": 'jenga',
    "password": 'your_password',
    "database": 'jenga',
    "charset": 'utf8',
}

# 동화 Database 연결
def connect_database(config):
    with pymysql.connect(**config) as db:
        with db.cursor() as cursor:
            sql = "SELECT title, detail FROM jenga.book"
            cursor.execute(sql)
            database_list = cursor.fetchall()
    return database_list

# 마이크와 스피커의 정보 출력
def print_audio_info():
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        print("Index: {0}, Name: {1}, Channels: {2}, Max Input Channels: {3}".format(i, info['name'],
                                                                                     info['maxInputChannels'],
                                                                                     info['maxOutputChannels']))
    audio.terminate()

# 음성 인식
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("음성 명령을 기다리는 중...")
        try:
            audio = r.listen(source, timeout=5)  # 5초 동안 음성을 대기하고 자동으로 종료
            text = r.recognize_google(audio, language='ja-JP')
            print("음성 명령: {}".format(text))
            return text
        except sr.WaitTimeoutError:
            print("시간 초과: 음성 입력이 없습니다.")
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print("Google Speech Recognition 서비스에서 오류 발생; {0}".format(e))

# 긴 텍스트를 분할
def split_text(text, n):
    return [text[i:i + n] for i in range(0, len(text), n)]

# 긴 텍스트를 음성으로 출력
def tts_threads(text, n=200, delay=0.5):
    text_list = split_text(text, n)
    for t in text_list:
        text_to_speech(t)
        time.sleep(delay)

# Text To Speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='ja')
    tts.save("gtts.mp3")
    audio = AudioSegment.from_mp3("gtts.mp3")
    audio.export("gtts.wav", format="wav")
    tts_sound = pygame.mixer.Sound("gtts.wav")
    tts_sound.play()

# 받은 문자열에서 한글만 추출
def get_cleaned_text(text):
    cleaned_text = re.sub(r"[^가-힣]", "", text)
    return cleaned_text

# 데이터베이스에 존재하는 동화를 읽어주는 함수
def play_fairy_tale(database_list):
    text_to_speech("どんな童話を聞かせてくれるかな？ ")
    time.sleep(3)
    try:
        text = speech_to_text()
        text = get_cleaned_text(text)
        for tale_title, tale_content in database_list:
            if tale_title == text:
                text_to_speech(text + "童話を聞かせてあげるよ。")
                tts_threads(tale_content)
                break
        else:
            text_to_speech("そんな童話はない。")
    except sr.UnknownValueError:
        text_to_speech("ごめん、聞いてなかった.")

# 메인 함수
def main():
    openai.api_key = 'your_openai_api_key'
    pygame.mixer.init()

    database_list = connect_database(db_config)

    while True:
        try:
            text = speech_to_text()
            if "いちご" in text:
                if pygame.mixer.get_busy():
                    pygame.mixer.stop()
                print("네")
                pygame.mixer.Sound("start.wav").play()
                text = speech_to_text()
                if '童話' in text:
                    print("童話")
                    play_fairy_tale(database_list)
                else:
                    print("GPT")
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=text,
                        temperature=0.9,
                        max_tokens=2048,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.6,
                    )
                    message = response.choices[0].text.strip()
                    print("message: ", message)
                    text_to_speech(message)
        except sr.UnknownValueError:
            print("음성을 인식할 수 없음")
        except sr.RequestError as e:
            print("Google 음성 인식 서비스에서 결과를 요청할 수 없음; {0}".format(e))
        except Exception as e:
            print("음성 명령을 처리하는 동안 오류가 발생; {0}".format(e))

if __name__ == "__main__":
    print_audio_info()
    dall_name = "いちご"
    main()
