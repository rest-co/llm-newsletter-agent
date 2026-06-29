
import os
import requests

# 날짜와 시간 처리를 위한 라이브러리
from datetime import datetime, timezone, timedelta

# .env 파일의 환경변수를 읽어오기 위한 라이브러리
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


# -----------------------------
# 네이버 API 정보
# -----------------------------

CLIENT_ID = os.getenv("NAVER_API_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_API_CLIENT_SECRET")

# 네이버 뉴스 검색 API 주소
API_URL = "https://openapi.naver.com/v1/search/news.json"


# -----------------------------
# 한국 시간대(KST)
# -----------------------------
# 네이버 뉴스 시간은 +0900(KST) 기준
# 비교할 날짜도 동일하게 맞춰줘야 함

KST = timezone(timedelta(hours=9))


def search_naver_news(query, start_date, end_date):

    # 최종 뉴스 저장 리스트
    all_news = []

    # 네이버 API 페이지 시작 번호
    start = 1

    # 한 번에 가져올 뉴스 개수
    # 최대 100
    display = 100

    print("입력 시작:", start_date)
    print("입력 종료:", end_date)

    # -----------------------------
    # 시작 날짜 처리
    # -----------------------------

    if isinstance(start_date, datetime):

        # 이미 datetime 객체면 그대로 사용
        start_datetime = start_date

    else:

        # 문자열이면 datetime 객체로 변환
        start_datetime = datetime.strptime(
            start_date,
            "%Y-%m-%d %H:%M:%S"
        )

    # -----------------------------
    # 종료 날짜 처리
    # -----------------------------

    if isinstance(end_date, datetime):

        end_datetime = end_date

    else:

        end_datetime = datetime.strptime(
            end_date,
            "%Y-%m-%d %H:%M:%S"
        )

    # -----------------------------
    # timezone 맞추기
    # -----------------------------
    # 네이버 뉴스는 +0900(KST)
    # 입력 날짜도 KST로 맞춤

    if start_datetime.tzinfo is None:

        start_datetime = start_datetime.replace(
            tzinfo=KST
        )

    if end_datetime.tzinfo is None:

        end_datetime = end_datetime.replace(
            tzinfo=KST
        )

    print("비교 시작:", start_datetime)
    print("비교 종료:", end_datetime)

    # -----------------------------
    # 뉴스 API 반복 호출
    # -----------------------------
    # 네이버 API는 한 번에 최대 100개
    # 최대 1000개까지 조회 가능

    while start <= 1000:

        # API 요청 헤더
        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET,
            "Content-Type": "application/json"
        }

        # API 요청 파라미터
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": "date"  # 최신순
        }

        # API 호출
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        # -----------------------------
        # 호출 실패
        # -----------------------------

        if response.status_code != 200:

            print(
                f"Error {response.status_code}: {response.text}"
            )

            break

        # JSON 변환
        results = response.json()

        # 뉴스 목록
        items = results.get("items", [])

        # 뉴스 없으면 종료
        if not items:
            break

        # -----------------------------
        # 뉴스 하나씩 처리
        # -----------------------------

        for item in items:

            pub_date = item.get("pubDate", "")

            try:

                # 예시
                # Sat, 21 Jun 2026 18:22:00 +0900

                pub_datetime = datetime.strptime(
                    pub_date,
                    "%a, %d %b %Y %H:%M:%S %z"
                )

            except ValueError:

                # 날짜 파싱 실패
                continue

            # -----------------------------
            # 날짜 범위 필터링
            # -----------------------------
            #
            # 예시
            #
            # 시작:
            # 2026-06-21 00:00:00
            #
            # 종료:
            # 2026-06-22 00:00:00
            #
            # 결과:
            # 6월 21일 뉴스만 포함
            #
            # 종료 시각은 포함하지 않음
            # (< end_datetime)
            #
            # 그래서
            # 2026-06-22 00:33 뉴스는 제외됨
            #

            if (
                start_datetime
                <= pub_datetime
                < end_datetime
            ):

                all_news.append(item)

            # -----------------------------
            # 최적화
            # -----------------------------
            # 최신순 정렬이라
            # 시작일보다 과거 뉴스가 나오면
            # 더 조회할 필요 없음

            if pub_datetime < start_datetime:

                print(
                    "시작일 이전 뉴스 발견 → 조회 종료"
                )

                return all_news

        # 다음 페이지
        start += display

    # 최종 뉴스 반환
    return all_news
