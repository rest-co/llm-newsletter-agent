from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOllama(model="qwen3:8b",temperature=0)

import re

def extract_roy_kim_context(article_text, keyword="로이킴", window=300):
    if keyword not in article_text:
        return ""

    contexts = []

    for match in re.finditer(keyword, article_text):
        start = max(match.start() - window, 0)
        end = min(match.end() + window, len(article_text))

        contexts.append(article_text[start:end])

    return "\n\n---\n\n".join(contexts)

def summarize_roy_kim_news(content):
    roy_context = extract_roy_kim_context(content)
    
    messages = [
    SystemMessage(
        content="""
너는 엔터테인먼트 뉴스 분석 AI다.

"로이킴" 단어를 찾는다. 단어가 있다면 '로이킴 관련 내용 없음'이라고 작성해서는 안 된다.

목적은 기사의 핵심 이슈를 먼저 요약한 뒤,
기사 안에서 확인되는 로이킴 관련 언급을 별도로 정리하는 것이다.

반드시 기사에 적혀 있는 사실만 사용한다.
추론, 상식, 해석, 전망을 추가하지 않는다.
기사에 없는 관계를 만들어서는 안 된다.

로이킴이 단순히 순위, 명단, 라인업, 출연진, 차트, 브랜드평판 순위에 이름만 포함된 경우도
반드시 로이킴 관련 언급으로 작성한다.

기사에 명시되지 않았다면 다음과 같은 문장은 절대 작성하지 않는다.
- 로이킴이 소속된 ○○
- ○○가 로이킴에게 영향을 준다
- 로이킴과 ○○가 관련 있다
- 로이킴의 활동이 확대됐다
- 로이킴의 인기가 상승했다

만약 기사에 로이킴이 전혀 등장하지 않는다면
정확히 아래 한 줄만 출력한다.

로이킴 관련 내용 없음
"""
    ),
    HumanMessage(
        content=f"""

기사 전체:

{content}

로이킴이 언급된 주변 문맥:

{roy_context if roy_context else "로이킴 언급 없음"}

아래 형식을 반드시 따른다.

1. 기사 핵심 이슈
- 기사 전체의 핵심 내용을 2~3문장으로 요약한다.

2. 기사에서 확인된 로이킴 언급
- 기사 전체 에서 "로이킴" 이라는 단어가 등장한 내용을 작성한다.
- 단순 순위, 명단, 라인업, 차트 포함도 작성한다.
- 로이킴에 대한 별도 설명이 없다면 "별도 설명은 없다"고 작성한다.
- 기사에 적혀 있는 사실만 작성한다.

3. 로이킴 관점 핵심 요약
- 기사 전체 맥락 속에서 로이킴이 어떤 방식으로 언급되었는지 1~2문장으로 정리한다.
- 로이킴이 단순히 명단이나 순위에 포함된 경우, 그 사실만 작성한다.
- 기사에 없는 의미나 해석은 추가하지 않는다.

규칙
- 2번과 3번에는 로이킴과 무관한 다른 인물이나 그룹의 상세 내용을 쓰지 않는다.
- 기사에 없는 추론은 하지 않는다.
- 반드시 위 1, 2, 3번 형식을 유지한다.
"""
    )
]

    response = llm.invoke(messages)

    return response.content
