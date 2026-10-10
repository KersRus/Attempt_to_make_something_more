import re
import requests
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, TRACKED_COMPANIES


def analyze_news(news_items: list[dict]) -> str:
    """
    Отправляет новости в Yandex GPT и возвращает только те заголовки,
    где явно упомянута одна из отслеживаемых компаний.
    """
    if not news_items:
        return ""

    # Убираем дубли по заголовку
    seen = set()
    unique = []
    for item in news_items:
        title = item.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            unique.append(item)

    if not unique:
        return ""

    news_text = "\n".join(
        f"{i}. [{item['source']}] {item['title']}"
        for i, item in enumerate(unique[:40], start=1)
    )

    company_list = ", ".join(TRACKED_COMPANIES.values())

    system_prompt = (
        "Ты — редактор новостной ленты. Ты просматриваешь заголовки и выбираешь "
        "только те, где явно упомянута одна из указанных компаний. "
        "Ты не пишешь комментариев, не даёшь оценок и не интерпретируешь события."
    )

    user_prompt = f"""Ниже — список новостных заголовков.

Отслеживаемые компании: {company_list}.

Заголовки:
{news_text}

Выбери только те заголовки, в которых ПРЯМО упомянута хотя бы одна 
из отслеживаемых компаний (по названию). Заголовки, где упоминаются другие 
компании, отрасли, чиновники, макроэкономика или события без связи с этими 
компаниями — НЕ выбирай.

Верни только номера выбранных заголовков через запятую. Например: 2, 5, 11.
Если ни в одном заголовке нет упоминания этих компаний — верни слово "нет".

Не добавляй пояснений. Только номера или слово "нет"."""

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.0,
            "maxTokens": 200,
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_prompt},
        ],
    }

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    alternatives = result.get("result", {}).get("alternatives", [])
    if not alternatives:
        return ""

    raw = alternatives[0].get("message", {}).get("text", "").strip()
    print(f"YandexGPT ответил: {raw}")

    if "нет" in raw.lower() and not any(c.isdigit() for c in raw):
        return ""

    numbers = [int(n) for n in re.findall(r"\d+", raw)]

    selected = []
    for n in numbers:
        if 1 <= n <= len(unique):
            item = unique[n - 1]
            selected.append(f"• [{item['source']}] {item['title']}")

    return "\n".join(selected)
