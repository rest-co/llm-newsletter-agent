import traceback
import os
from datetime import datetime, timedelta
from pathlib import Path
from naver_news import search_naver_news
from naver_article import get_article
from db_news import save_news_to_db, get_unsummarized_news, update_news_content, has_news_by_date
from news_ai_analyzer import summarize_roy_kim_news
from news_ai_grouper import classify_unclassified_news
from make_news_letter import create_newsletter
from send_mail import send_email
from dotenv import load_dotenv
# .env 파일 로드
load_dotenv()

test = False
def write_error_log():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / datetime.now().strftime("error_%Y%m%d.log")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("=" * 80)
        f.write("\n")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("\n")
        f.write(traceback.format_exc())
        f.write("\n")


try:
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    start_date = yesterday.strftime("%Y-%m-%d 00:00:00")
    end_date = today.strftime("%Y-%m-%d 00:00:00")

    if has_news_by_date(start_date, end_date):
        print("이미 해당 날짜 뉴스가 DB에 있습니다. 네이버 검색을 건너뜁니다.")
    else:
        news = search_naver_news(
            "로이킴",
            start_date,
            end_date
        )

        print(f"뉴스 개수: {len(news)}")

        save_news_to_db(news)

    unsummarized_news = get_unsummarized_news(
        start_date=start_date,
        end_date=end_date
    )

    if not unsummarized_news:
        print("요약할 뉴스가 없습니다.")
    else:
        for news_id, title, link in unsummarized_news:
            try:
                print("처리 중:", title)

                article = get_article(link)
                if test == True:
                    print(article) 

                if not article or article.strip() == "":
                    print("본문 없음:", link)
                    continue

                summary = summarize_roy_kim_news(article)

                if not summary or summary.strip() == "":
                    print("요약 결과 없음:", title)
                    continue

                print(summary)

                update_news_content(news_id, summary)

                print("DB 저장 완료")

            except Exception as e:
                print("처리 중 에러 발생:", title)
                print("에러 내용:", e)

            print("-" * 50)

    classify_unclassified_news(
        start_date=start_date,
        end_date=end_date
    )

    newsletter_file, html_content = create_newsletter(
        start_date,
        end_date
    )

    subject_date = today.strftime("%Y-%m-%d")
    
    if test == False:
        send_email(
        to_emails=[
            email.strip()
            for email in os.getenv("MAIL_TO").split(",")
        
        ],
        subject=f"로이킴 뉴스 클립 ({subject_date})",
        html_content=html_content
    )



except Exception:
    write_error_log()
    print("전체 실행 중 에러 발생. logs 폴더에 기록했습니다.")

