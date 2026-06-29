import requests
from bs4 import BeautifulSoup


def get_article(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    selectors = [
        "._article_content",          # 네이버 연예
        "#article-view-content-div", #id명
        "#article_txt",
        ".gmv2c_con01.detailCont", # class명
        ".col-12",
        ".viewConts",
        ".view_contents",
        ".view_news",
        ".main-news-article",
        ".newsCont",
        ".content_left_wrap",
        "#news_body_area",
        ".read_body",
        "#articleBody",
        ".articleBody",
        "#article",
        ".contents",
        ".content",
    ]

    article = None

    for selector in selectors:
        article = soup.select_one(selector)

        if article:
            print(f"선택된 selector : {selector}")
            print("텍스트 미리보기:")
            print(article.get_text(strip=True)[:200])
            break

    if article is None:
        print("본문 선택자 못 찾음:", url)
        return None

    return article.get_text(
        separator="\n",
        strip=True
    )
