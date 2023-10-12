import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pymysql
import config


# 상대경로를 절대경로로 변환하는 함수
def convert_to_absolute_url(base_url, relative_path):
    absolute_path = urljoin(base_url, relative_path)
    return absolute_path


# 데이터베이스 연결 설정
def connect_to_database():
    db = pymysql.Connect(
        host='localhost',
        user='jenga',
        password=config.database_password,
        database='jenga',
        charset='utf8',
    )
    return db


# 데이터베이스에 데이터 추가
def insert_data_to_db(cursor, db, title, content):
    sql = "INSERT INTO book (title, detail) VALUES (%s, %s)"
    cursor.execute(sql, (title, content))
    db.commit()


# Clear book table in database
def clear_table(cursor):
    sql = "TRUNCATE TABLE book"
    cursor.execute(sql)


def scrape_and_store_data(url):
    db = connect_to_database()
    cursor = db.cursor()

    # Clear existing data
    clear_table(cursor)

    # 웹 페이지 가져오기
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    title_content_pairs = []

    # 모든 테이블 선택
    tables = soup.find_all('table')

    # 각 테이블에서 모든 <a> 태그 선택
    for table in tables:
        a_tags = table.find_all('a')

        for a in a_tags:
            title = a.text
            href = a.get('href')
            absolute_href = convert_to_absolute_url(url, href)

            # 절대경로로 접근하여 내용 크롤링
            response_inner = requests.get(absolute_href)
            response_inner.encoding = 'utf-8'
            soup_inner = BeautifulSoup(response_inner.text, 'html.parser')

            # <p> 태그 중 class="story"인 내용 추가
            story_tags = soup_inner.find_all('p', class_='story')
            content_list = [p.text for p in story_tags]
            content = ' '.join(content_list)

            title_content_pairs.append((title, content))

    for title, content in title_content_pairs:
        print(f'Title: {title}')
        print(f'Content: {content}')

    # 데이터베이스에 추가
    for (title, content) in title_content_pairs:
        insert_data_to_db(cursor, db, title, content)

    # 데이터베이스 연결 종료
    db.close()


# 호출
if __name__ == '__main__':
    url = 'https://www.douwa-douyou.jp/contents/html/douwa/douwa6.shtml'
    scrape_and_store_data(url)
