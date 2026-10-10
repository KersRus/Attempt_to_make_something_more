import requests
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, TRACKED_COMPANIES


def analyze_news(news_items: list[dict]) -> str:
    """
    Отправляет новости в Yandex GPT и возвращает только те заголовки,
    которые модель сочла значимыми. Без интерпретаций и оценок.
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
        "Ты — новостной редактор. Твоя задача — просмотреть список заголовков "
        "и выбрать те, которые сообщают о значимых событиях. Ты не пишешь "
        "собственных комментариев и не даёшь оценок."
    )

    user_prompt = f"""Ниже — список новостных заголовков за последний час.
Я отслеживаю события, связанные с компаниями: {company_list}.

Заголовки:
{news_text}

Выбери из списка те заголовки, которые сообщают о существенных событиях: 
отчётность, сделки, кадровые изменения в руководстве, регуляторные решения, 
крупные контракты, судебные разбирательства.

Верни только номера выбранных заголовков через запятую. Например: 2, 5, 11.
Если ничего существенного нет — верни слово "нет".

Не добавляй никаких пояснений, только номера."""

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
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

    # Парсим номера из ответа
    if "нет" in raw.lower() and not any(c.isdigit() for c in raw):
        return ""

    import re
    numbers = [int(n) for n in re.findall(r"\d+", raw)]

    selected = []
    for n in numbers:
        if 1 <= n <= len(unique):
            item = unique[n - 1]
            selected.append(f"• [{item['source']}] {item['title']}")

    return "\n".join(selected)
