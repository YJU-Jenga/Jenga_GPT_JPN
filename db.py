import pymysql
import config

db = pymysql.Connect(
    host='localhost',
    user='jenga',
    password=config.database_password,
    database='jenga',
    charset='utf8',
)

cursor = db.cursor()

create_table_query = """
CREATE TABLE book (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    detail TEXT
)
"""

cursor.execute(create_table_query)
