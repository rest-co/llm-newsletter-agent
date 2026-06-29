from datetime import datetime
from collections import defaultdict
import html
import re


def make_newsletter_html(news_list, start_date, end_date):
    today = datetime.now().strftime("%Y-%m-%d")

    # representative_news_id 기준으로 뉴스 묶기
    grouped_news = defaultdict(list)

    for row in news_list:
        representative_news_id = row[0]
        grouped_news[representative_news_id].append(row)

    html_text = f"""
<table cellpadding="0" cellspacing="0" style="
width:100%;
max-width:1000px;
border-collapse:collapse;
border:0;
margin:0 auto;
font-family:'Noto Sans KR','Malgun Gothic',Arial,sans-serif;
">
<tbody>
<tr>
<td>

<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;border:0;">
<tbody>

<tr>
<td style="font-size:28px;letter-spacing:-1px;color:#111;font-weight:700;">
<p style="padding:0;margin:0;line-height:1.4;"> {today} 로이킴 네이버 검색 결과 </p>
</td>
</tr>

<tr>
<td style="font-size:14px;color:#777;padding-top:4px;padding-bottom:20px;">
{start_date} ~ {end_date}
</td>
</tr>
"""

    group_number = 0
    news_number = 0

    for representative_news_id, articles in grouped_news.items():
        group_number += 1
        similar_count = len(articles)

        html_text += f"""
<tr>
<td style="
background-color:#f7f8fa;
border-radius:12px;
padding:16px;
">

<div style="
font-size:14px;
font-weight:700;
color:#2f80ed;
margin-bottom:10px;
">
연관 뉴스 {group_number}번 · {similar_count}건
</div>

<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;border:0;">
<tbody>
"""

        for row in articles:
            representative_news_id, news_id, title, content, link, pub_date = row

            news_number += 1

            safe_title = html.escape(title or "")
            safe_content = html.escape(content or "")
            safe_content = re.sub(r"\n\s*\n+", "\n", safe_content)
            safe_link = html.escape(link or "#")

            html_text += f"""
<tr>
<td style="width:36px;vertical-align:top;font-size:15px;font-weight:700;color:#999;">
{news_number}
</td>

<td style="vertical-align:top;padding-bottom:12px;">
<a href="{safe_link}" target="_blank" style="text-decoration:none;display:block;">

<div style="
font-size:15px;
font-weight:700;
color:#111;
line-height:1.5;
letter-spacing:-0.3px;
word-break:keep-all;
">{safe_title}</div>
<div style="
font-size:15px;
font-weight:400;
color:#616161;
letter-spacing:-0.3px;
line-height:1.5;
margin-top:0px;
word-break:keep-all;
white-space: pre-line;
">{safe_content}</div>

</a>
</td>

<td style="width:24px;text-align:right;vertical-align:middle;">
<span style="font-size:22px;color:#222;">›</span>
</td>
</tr>
"""

        html_text += """
</tbody>
</table>

</td>
</tr>

<tr>
<td style="font-size:0;line-height:0;height:18px;">&nbsp;</td>
</tr>
"""

    html_text += """
</tbody>
</table>

</td>
</tr>
</tbody>
</table>
"""

    return html_text
