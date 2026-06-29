from db_news import get_news_for_newsletter
from news_letter import make_newsletter_html


def create_newsletter(
    start_date=None,
    end_date=None,
    output_file="roykim_newsletter.html"
):
    # 뉴스 조회
    news = get_news_for_newsletter(
        start_date=start_date,
        end_date=end_date
    )

    # HTML 생성
    html_text = make_newsletter_html(news, start_date, end_date)

    # 파일 저장
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_text)

    print(f"HTML 뉴스레터 생성 완료: {output_file}")

    return output_file, html_text
