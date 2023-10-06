import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 상대경로를 절대경로로 변환하는 함수
def convert_to_absolute_url(base_url, relative_path):
    absolute_path = urljoin(base_url, relative_path)
    return absolute_path

# 웹 페이지 URL
url = 'https://www.douwa-douyou.jp/contents/html/douwa/douwa6.shtml'

# 웹 페이지 가져오기
response = requests.get(url)

# 인코딩 설정 (UTF-8)
response.encoding = 'utf-8'

# BeautifulSoup 객체 생성
soup = BeautifulSoup(response.text, 'html.parser')

# 모든 테이블 선택
tables = soup.find_all('table')

# 각 테이블에서 모든 <a> 태그 선택
for table in tables:
    a_tags = table.find_all('a')

    # <a> 태그의 href 속성을 절대경로로 변환하여 출력
    for a in a_tags:
        print(a.text)
        href = a.get('href')
        absolute_href = convert_to_absolute_url(url, href)
        print(absolute_href)

        # 절대경로로 접근하여 내용 크롤링
        response_inner = requests.get(absolute_href)
        response_inner.encoding = 'utf-8'
        soup_inner = BeautifulSoup(response_inner.text, 'html.parser')

        # <p> 태그 중 class="story"인 내용 출력
        story_tags = soup_inner.find_all('p', class_='story')
        for story_tag in story_tags:
            print(story_tag.text)
