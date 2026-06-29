import psycopg2
import os
from datetime import datetime
import re
from html import unescape
# .env 파일의 환경변수를 읽어오기 위한 라이브러리
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
password=os.getenv("DB_PASSWORD")

def save_news_to_db(news_items):

    # PostgreSQL DB에 연결
    conn = psycopg2.connect(
        host="localhost",      # DB 서버 주소
        database="news",       # 사용할 DB 이름
        user="postgres",       # DB 계정
        password=password      # DB 비밀번호
    )

    # SQL을 실행하기 위한 Cursor 객체 생성
    cur = conn.cursor()

    # 뉴스 목록을 하나씩 반복
    for item in news_items:

        # 뉴스 제목

        title = item.get("title", "")
        title = re.sub(r"<[^>]+>", "", title) # 특수 문자 제거
        title = unescape(title)
        
        # 뉴스 설명
        description = item.get("description", "")
        description = re.sub(r"<[^>]+>", "", description) # 특수 문자 제거
        title = unescape(title)
        description = unescape(description)
      
        # 네이버 뉴스 링크
        link = item.get("link")

        # 원본 기사 링크
        original_link = item.get("originallink")

        # 뉴스 발행 시간
        pub_date = item.get("pubDate")

        # 아직 기사 본문 수집 전
        # 나중에 AI 요약 결과를 저장할 예정
        content = None

        # 문자열 형태의 날짜를 datetime 객체로 변환
        #
        # 예:
        # Mon, 08 Jun 2026 09:00:00 +0900
        #
        # ↓
        #
        # datetime 객체
        pub_datetime = datetime.strptime(
            pub_date,
            "%a, %d %b %Y %H:%M:%S %z"
        )

        # DB에 저장할 SQL 작성
        sql = """
        INSERT INTO news_articles (
            title,
            description,
            link,
            original_link,
            content,
            pub_date
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        -- 이미 같은 link가 있으면 저장하지 않음
        ON CONFLICT (link)
        DO NOTHING;
        """

        # SQL 실행
        #
        # %s 자리에 아래 값들이 순서대로 들어감
        cur.execute(
            sql,
            (
                title,
                description,
                link,
                original_link,
                content,
                pub_datetime
            )
        )

    # 반복문이 끝난 후
    # 모든 INSERT 내용을 DB에 최종 반영
    conn.commit()

    # Cursor 종료
    cur.close()

    # DB 연결 종료
    conn.close()

    print("DB 저장 완료")

def get_unsummarized_news(start_date=None, end_date=None):
    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )

    cur = conn.cursor()

    sql = """
    SELECT id, title, link
    FROM news_articles
    WHERE content IS NULL
    """

    params = []

    if start_date:
        sql += " AND pub_date >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND pub_date < %s"
        params.append(end_date)

    sql += " ORDER BY pub_date ASC;"

    cur.execute(sql, params)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def update_news_content(id, content):

    # PostgreSQL DB에 연결
    conn = psycopg2.connect(
        host="localhost",      # DB 서버 주소
        database="news",       # 사용할 DB 이름
        user="postgres",       # DB 계정
        password=password      # DB 비밀번호
    )

    # SQL 실행을 위한 Cursor 생성
    cur = conn.cursor()

    # UPDATE SQL 작성
    #
    # news_articles 테이블에서
    # id가 news_id인 행을 찾아
    # content 컬럼을 content 값으로 변경
    sql = """
    UPDATE news_articles
    SET content = %s
    WHERE id = %s;
    """

    # SQL 실행
    #
    # 첫 번째 %s → content
    # 두 번째 %s → news_id
    #
    # 예:
    # UPDATE news_articles
    # SET content = 'AI 요약 결과'
    # WHERE id = 5;
    cur.execute(
        sql,
        (
            content,
            id
        )
    )

    # 변경사항을 DB에 최종 반영
    conn.commit()

    # 저장 완료 메시지 출력
    print(f"{id}번 뉴스 요약 저장 완료")

    # Cursor 종료
    cur.close()

    # DB 연결 종료
    conn.close()

from difflib import SequenceMatcher


def update_representative_news_id(news_id, representative_news_id):

    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )

    cur = conn.cursor()

    sql = """
    UPDATE news_articles
    SET representative_news_id = %s
    WHERE id = %s;
    """

    cur.execute(
        sql,
        (
            representative_news_id,
            news_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

def get_unclassified_news(start_date=None, end_date=None):
    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )

    cur = conn.cursor()

    sql = """
    SELECT
        id,
        content
    FROM news_articles
    WHERE content IS NOT NULL
      AND representative_news_id IS NULL
    """

    params = []

    if start_date:
        sql += " AND pub_date >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND pub_date < %s"
        params.append(end_date)

    sql += " ORDER BY id ASC;"

    cur.execute(sql, params)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def update_representative_news_id(id, representative_news_id):

    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )

    cur = conn.cursor()

    sql = """
    UPDATE news_articles
    SET representative_news_id = %s
    WHERE id = %s;
    """

    cur.execute(
        sql,
        (
            representative_news_id,
            id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

def get_news_for_newsletter(start_date=None, end_date=None):
    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )
    cur = conn.cursor()

    sql = """
    SELECT
        representative_news_id,
        id,
        title,
        content,
        link,
        pub_date
    FROM news_articles
    WHERE representative_news_id IS NOT NULL
    """

    params = []

    if start_date:
        sql += " AND DATE(pub_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(pub_date) < %s"
        params.append(end_date)

    sql += """
    ORDER BY representative_news_id ASC, id ASC
    """

    cur.execute(sql, params)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def has_news_by_date(start_date, end_date):
    conn = psycopg2.connect(
        host="localhost",
        database="news",
        user="postgres",
        password=password
    )

    cur = conn.cursor()

    sql = """
    SELECT EXISTS (
        SELECT 1
        FROM news_articles
        WHERE pub_date >= %s
          AND pub_date < %s
    );
    """

    cur.execute(sql, (start_date, end_date))

    exists = cur.fetchone()[0]

    cur.close()
    conn.close()

    return exists
