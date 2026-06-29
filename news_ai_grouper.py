from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import json

from db_news import (
    get_unclassified_news,
    update_representative_news_id
)

llm = ChatOllama(model="qwen3:8b")


def normalize_groups(groups):
    normalized = []

    # 1. LLM이 dict 형태로 준 경우
    # 예: {"56": [56, 57], "76": [76, 77]}
    if isinstance(groups, dict):
        for _, news_ids in groups.items():

            if isinstance(news_ids, int):
                news_ids = [news_ids]

            news_ids = [int(news_id) for news_id in news_ids]

            normalized.append({
                "representative_news_id": min(news_ids),
                "id": news_ids
            })

        return normalized

    # 2. LLM이 배열 안의 배열로 준 경우
    # 예: [[56, 57], [58, 78]]
    if isinstance(groups, list) and all(isinstance(group, list) for group in groups):
        for news_ids in groups:
            news_ids = [int(news_id) for news_id in news_ids]

            normalized.append({
                "representative_news_id": min(news_ids),
                "id": news_ids
            })

        return normalized

    # 3. LLM이 객체 배열로 준 경우
    # 예: [{"representative_news_id": 56, "id": [56, 57]}]
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                print("잘못된 그룹:", group)
                continue

            news_ids = (
                group.get("id")
                or group.get("ids")
                or group.get("news_ids")
                or group.get("news_id")
            )

            if news_ids is None:
                print("뉴스 ID 없음:", group)
                continue

            if isinstance(news_ids, int):
                news_ids = [news_ids]

            news_ids = [int(news_id) for news_id in news_ids]

            normalized.append({
                "representative_news_id": min(news_ids),
                "id": news_ids
            })

        return normalized

    print("알 수 없는 그룹 형식:", groups)

    return normalized


def group_news_by_llm(news_list):
    print("연관 뉴스 분류 시작")

    news_text = ""
    news_ids =[]

    for news_id, content in news_list:
        news_ids.append(news_id)
        news_text += f"""
[{news_id}]
요약: {content}
"""

    print(news_text)

    messages = [
        SystemMessage(
            content=f"""
너는 뉴스 그룹핑 AI다. 
반드시 JSON만 출력한다. 
설명 문장은 절대 출력하지 않는다. 
마크다운을 사용하지 않는다. 
뉴스 ID 그룹만 출력한다.

"""
        ),
      HumanMessage(
    content=f"""
뉴스 목록:
{news_text}

모든 뉴스 ID 목록: {news_ids}

뉴스 목록에 [숫자]는 뉴스 ID를 뜻한다.
위 뉴스들을 같은 이슈끼리 묶어라.

중요 분류 기준:
- 각 요약은 보통 다음 구조를 가진다.
  1. 기사 핵심 이슈
  2. 기사에서 확인된 로이킴 언급
  3. 로이킴 관점 핵심 요약

- 그룹핑할 때는 1번 '기사 핵심 이슈'보다
  2번 '기사에서 확인된 로이킴 언급'과
  3번 '로이킴 관점 핵심 요약'을 가장 중요하게 본다.

- 기사 전체 주제가 달라도,
  로이킴 관련 언급이 같은 방송, 같은 발언, 같은 차트, 같은 행사, 같은 공연, 같은 순위, 같은 인물 관계를 다루면 같은 이슈로 묶는다.

- 예를 들어 어떤 기사는 정규민 중심이고 다른 기사는 이수근 중심이어도,
  둘 다 '민호가 해병대 후임 로이킴에게 밥을 사줬고 로이킴이 방송에서 언급하지 않았다'는 내용이면 같은 이슈다.

규칙:
- 모든 뉴스 ID는 한 번만 포함한다.
- 입력된 모든 뉴스 ID를 반드시 출력에 포함한다. 하나라도 누락하면 안 된다.
- 설명 문장은 출력하지 않는다.
- 마크다운을 사용하지 않는다.
- JSON 배열만 출력한다.
- 각 배열은 같은 이슈다.

출력 예시:
[
  [1,2,5,6,8],
  [3,4,7,9],
  [10],
  [11,12]
]
"""
)
    ]

    response = llm.invoke(messages)

    result_text = response.content.strip()

    print("LLM 원본 응답:")
    print(result_text)

    result_text = (
        result_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # LLM이 [1,2], [3,4] 형태로 준 경우
    # [[1,2], [3,4]] 형태로 보정
    if "], [" in result_text and not result_text.startswith("[["):
        result_text = "[" + result_text + "]"


    try:
        groups = json.loads(result_text)

        print("JSON 변환 결과:")
        print(groups)

        groups = normalize_groups(groups)

        print("정규화 결과:")
        print(groups)

        return groups

    except json.JSONDecodeError:
        print("JSON 변환 실패")
        print("LLM 응답 내용:")
        print(result_text)
        return []

def classify_unclassified_news(start_date=None, end_date=None):
    news = get_unclassified_news(
        start_date=start_date,
        end_date=end_date
    )

    if not news:
        print("분류할 뉴스가 없습니다.")
        return []

    representatives = group_news_by_llm(news)

    if not representatives:
        print("분류 결과가 없습니다.")
        return []
    
    input_news_ids = [news_id for news_id, _ in news]

    if not validate_group_result(input_news_ids, representatives):
        print("검증 실패로 DB 업데이트를 중단합니다.")
        return []

    for group in representatives:
        representative_news_id = group["representative_news_id"]
        news_ids = group["id"]

        for news_id in news_ids:
            update_representative_news_id(
                news_id,
                representative_news_id
            )

    print("연관 뉴스 분류 완료")

    return representatives

def validate_group_result(input_news_ids, groups):
    input_ids = set(input_news_ids)
    output_ids = []

    for group in groups:
        output_ids.extend(group["id"])

    output_id_set = set(output_ids)

    duplicated_ids = {
        news_id
        for news_id in output_ids
        if output_ids.count(news_id) > 1
    }

    missing_ids = input_ids - output_id_set
    unknown_ids = output_id_set - input_ids

    if duplicated_ids or missing_ids or unknown_ids:
        print("LLM 그룹핑 결과 검증 실패")
        print("중복 ID:", duplicated_ids)
        print("누락 ID:", missing_ids)
        print("존재하지 않는 ID:", unknown_ids)

        return False

    return True
