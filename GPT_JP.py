import os
import openai

from gtts import gTTS

import GPT_Kinou2

import pyaudio
import wave
import audioop

import config


def record_audio_with_silence_detection(output_filename, silence_threshold=2000, max_silence_duration=5):
    # 오디오 설정
    FORMAT = pyaudio.paInt16  # 오디오 포맷 설정
    CHANNELS = 1  # 모노 오디오
    RATE = 44100  # 샘플링 레이트
    CHUNK = 1024  # 버퍼 사이즈

    audio = pyaudio.PyAudio()

    # 오디오 입력 스트림 열기
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("음성 녹음을 시작합니다...")

    frames = []

    # 오디오 데이터 읽기 및 저장
    silence_counter = 0  # 연속적인 조용한 프레임 수를 계산하기 위한 카운터
    for _ in range(0, int(RATE / CHUNK) * max_silence_duration):
        data = stream.read(CHUNK)
        frames.append(data)

        # 오디오 데이터에서 에너지 값 계산
        energy = audioop.rms(data, 2)

        # 에너지 값이 일정 임계값 미만이면 조용한 상태로 간주하고 카운터 증가
        if energy < silence_threshold:
            silence_counter += 1
        else:
            silence_counter = 0

        # 연속적인 조용한 프레임이 max_silence_duration 이상이면 녹음 종료
        if silence_counter > max_silence_duration * (RATE / CHUNK):
            break

    print("음성 녹음을 종료합니다.")

    # 오디오 스트림 닫기
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 오디오 파일로 저장
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"{output_filename} 파일로 저장되었습니다.")


# Text To Speech
def text_to_speech(text):
    file_name = "gtts.mp3"
    tts = gTTS(text=text, lang='ja')
    tts.save(file_name)
    os.system(file_name)


def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    return transcription['text']


def main():
    # 녹음 함수 호출 (원하는 파일 이름과 녹음 시간을 설정할 수 있습니다.)
    record_audio_with_silence_detection("my_audio.wav", silence_threshold=2000, max_silence_duration=5)
    # Speech To Text
    audio_file = open("my_audio.wav", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)


if __name__ == '__main__':
    openai.api_key = config.openai_api_key
    # transcribe_audio("gtts.mp3")
    GPT_Kinou2.print_audio_info()
    main()
