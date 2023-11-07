from __future__ import print_function

import os
import threading

import openai
import pyaudio
import pygame
import time
import speech_recognition as sr
import subprocess
import pymysql
import re
import config
import ex1_kwstest as kws
from pydub import AudioSegment

from gtts import gTTS

from config import db_config

# 동화 Database 생성
# subprocess.run(['python', 'crawling.py'])

# Button Stop
os.system('cd /home/pi/blockcoding/kt_ai_makers_kit_block_coding_driver/blockDriver/ && ./buttonStop.sh')

mp3_file = "gtts.mp3"
wav_file = "gtts.wav"


# 동화 Database 연결
def connect_database(config):
    with pymysql.connect(**config) as db:
        with db.cursor() as cursor:
            sql = "SELECT title, detail FROM jenga.book"
            cursor.execute(sql)
            database_list = cursor.fetchall()
    return database_list


# 마이크와 스피커의 정보를 알려주는 함수
def print_audio_info():
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        print("Index: {0}, Name: {1}, Channels: {2}, Max Input Channels: {3}".format(i, info['name'],
                                                                                     info['maxInputChannels'],
                                                                                     info['maxOutputChannels']))
    audio.terminate()


# Speech To Text
def continuous_speech_to_text(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("음성 명령을 기다리는 중...")

        # 음성 인식을 시작하기 전에 잠시 정지한 후 소음을 기록합니다.
        r.adjust_for_ambient_noise(source)

        try:
            audio = r.listen(source, timeout=timeout)
            text = r.recognize_google(audio, language='ja-JP')
            print("음성 명령: {}".format(text))
            return text
        except sr.WaitTimeoutError:
            print("시간 초과: 음성 입력이 없습니다.")
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print("Google Speech Recognition 서비스에서 오류 발생: {0}".format(e))


def tts_threads(text, n=200, delay=0.5):
    text_list = [text[i:i + n] for i in range(0, len(text), n)]

    for t in text_list:
        text_to_speech(t)
        time.sleep(delay)

def split_text(text, n):
    # 긴 텍스트를 n글자씩 분할하여 리스트로 반환
    return [text[i:i + n] for i in range(0, len(text), n)]


# Text To Speech
def text_to_speech(text):
    file_name = "gtts.mp3"
    tts = gTTS(text=text, lang='ja')
    tts.save(file_name)
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")
    tts_sound = pygame.mixer.Sound(wav_file)
    tts_sound.play()


# 받은 문자열에서 한글만 추출하고 공백과 특수문자를 제거하는 함
def get_cleaned_text(text):
    cleaned_text = re.sub(r"[^가-힣]", "", text)
    return cleaned_text


# 데이터베이스에 존재하는 동화를 읽어주는 함수
def play_fairy_tale(database_list):
    text_to_speech("どんな童話を聞かせてくれるかな？ ")
    time.sleep(3)

    try:
        text = continuous_speech_to_text()
        print(text)

        # "桃太郎"가 입력되면 "ももたろう"으로 변환
        if text == "桃太郎":
            text = "ももたろう"

        # 입력된 텍스트가 database_list에 있는 동화와 일치하는지 확인
        matching_tale = next((tale_content for tale_title, tale_content in database_list if tale_title == text), None)

        if matching_tale:
            pygame.mixer.Sound("momotarou.wav").play()
        else:
            text_to_speech("そんな童話はない。")

    except sr.UnknownValueError:
        text_to_speech("ごめん、聞いてなかった。")


def main():
    while True:
        recog = kws.btn_test()
        if recog == 200:
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
            print("Button On")
            pygame.mixer.Sound("start.wav").play()

            # 일정 시간 동안 음성 인식을 시도
            timeout = time.time() + 5  # 예: 5초 동안 시도
            text = None
            while time.time() < timeout:
                text = continuous_speech_to_text()
                if text:
                    break  # 음성이 인식되면 루프 탈출

            if text:
                if "童話" in text or "東和" in text or "動画" in text or "とは" in text or "とうは" in text or "お話し" in text:
                    print("童話")
                    play_fairy_tale(database_list)
                else:
                    print("GPT")
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "You are a helpful assistant."},
                                  {"role": "user", "content": text}],
                    )
                    message = response.choices[0].message['content'].strip()
                    print("response: ", response)
                    print("message: ", message)
                    text_to_speech(message)
            else:
                print("음성 인식 실패. 다시 시도하세요.")


if __name__ == "__main__":
    openai.api_key = config.openai_api_key
    dall_name = "いちご"

    print_audio_info()  # 마이크와 스피커의 정보를 알려주는 함수
    pygame.mixer.init()

    database_list = connect_database(db_config)

    main()