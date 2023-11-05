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
from pydub import AudioSegment

from gtts import gTTS
from config import db_config

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


# Speech To Text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("음성 명령을 기다리는 중...")
        try:
            audio = r.listen(source)  # 5초 동안 음성을 대기하고 자동으로 종료
            text = r.recognize_google(audio, language='ja-JP')
            print("음성 명령: {}".format(text))
            return text
        except sr.WaitTimeoutError:
            print("시간 초과: 음성 입력이 없습니다.")
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print("Google Speech Recognition 서비스에서 오류 발생; {0}".format(e))


def split_text(text, n):
    # 긴 텍스트를 n글자씩 분할하여 리스트로 반환
    return [text[i:i + n] for i in range(0, len(text), n)]


def tts_threads(text, n=200, delay=0.5):
    # 긴 텍스트를 n글자씩 분할
    text_list = split_text(text, n)

    # 각각의 분할된 텍스트를 음성으로 변환하고 파일로 저장
    threads = []
    for i, t in enumerate(text_list):
        thread = threading.Thread(target=text_to_speech, args=t)
        threads.append(thread)
        thread.start()
        time.sleep(delay)

    # 모든 쓰레드가 종료될 때까지 대기
    for thread in threads:
        thread.join()

    # 저장된 음성 파일을 연속으로 재생
    for i in range(len(text_list)):
        file_name = "gtts.mp3"
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file, format="wav")
        pygame.mixer.Sound(wav_file).play()
        os.remove(file_name)


# Text To Speech
def text_to_speech(text):
    file_name = "gtts.mp3"
    tts = gTTS(text=text, lang='ja')
    tts.save(file_name)
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")
    tts_sound = pygame.mixer.Sound(wav_file)
    tts_sound.play()

# 데이터베이스에 존재하는 동화를 읽어주는 함수
def play_fairy_tale(database_list):
    text_to_speech("どんな童話を聞かせてくれるかな？ ")
    time.sleep(3)
    try:
        text = speech_to_text()
        for tale_title, tale_content in database_list:
            if tale_title == text:
                text_to_speech(text + "童話を聞かせてあげるよ。")
                text_to_speech(tale_content)
                break
        else:
            text_to_speech("そんな童話はない。")
    except sr.UnknownValueError:
        text_to_speech("ごめん、聞いてなかった。")