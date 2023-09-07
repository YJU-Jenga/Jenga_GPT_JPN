import os

import speech_recognition as sr
from gtts import gTTS

import GPT_Kinou2


# Speech To Text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("音声コマンドを待機中...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='ja-JP')  # 일본어로 음성 인식
        print("音声コマンド: {}".format(text))
        return text
    except sr.UnknownValueError:
        print("音声を認識できません。")
    except sr.RequestError as e:
        print("Google Speech Recognition サービスでエラーが発生しました; {0}".format(e))

# Text To Speech
def text_to_speech(text):
    file_name = "gtts.mp3"
    tts = gTTS(text=text, lang='ja')
    tts.save(file_name)
    os.system(file_name)

def main():
    text = speech_to_text()
    print(text)
    text_to_speech(text)


if __name__ == '__main__':
    GPT_Kinou2.print_audio_info()
    main()
