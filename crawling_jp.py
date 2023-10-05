import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 웹 페이지 URL
url = "https://www.douwa-douyou.jp/contents/html/douwastory/douwastory1_02.shtml"

# 웹 페이지 가져오기
response = requests.get(url)

if response.status_code == 200:
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(response.text, "html.parser")

    # audio 태그 찾기
    audio_tag = soup.find("audio")

    if audio_tag:
        # 상대경로 추출
        relative_path = audio_tag["src"]

        # 절대 URL로 변환
        absolute_url = urljoin(url, relative_path)

        # MP3 파일 다운로드
        mp3_response = requests.get(absolute_url)

        if mp3_response.status_code == 200:
            # MP3 파일 저장
            with open("2kasajizou.mp3", "wb") as mp3_file:
                mp3_file.write(mp3_response.content)
            print("MP3 파일을 다운로드했습니다.")
        else:
            print("MP3 파일을 다운로드하는 중 문제가 발생했습니다.")
    else:
        print("audio 태그를 찾을 수 없습니다.")
else:
    print("웹 페이지를 가져오는 중 문제가 발생했습니다.")
