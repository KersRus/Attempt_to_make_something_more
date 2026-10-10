import requests
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, TRACKED_COMPANIES


def analyze_news(news_items: list[dict]) -> str:
    """
    Отправляет новости в Yandex GPT и возвращает краткую информационную сводку.
    Формулировка промпта намеренно избегает слов «анализ», «прогноз», «совет»,
    чтобы не срабатывали фильтры безопасности модели.
    """
    if not news_items:
        return ""

    news_text = "\n".join(
        f"- [{item['source']}] {item['title']}"
        for item in news_items[:30]
    )

    company_list = ", ".join(TRACKED_COMPANIES.values())

    system_prompt = (
        "Ты — информационный ассистент, который делает краткие сводки новостей "
        "для личного дневника наблюдений. Ты не даёшь советов, не делаешь прогнозов "
        "и не рекомендуешь покупать или продавать. Ты только пересказываешь факты "
        "из предоставленных заголовков."
    )

    user_prompt = f"""Ниже — список заголовков новостей за последний час, 
собранных из открытых источников. Компании, которые я отслеживаю: {company_list}.

Заголовки:
{news_text}

Сделай краткую фактическую сводку: перечисли, какие события упоминаются 
в этих заголовках и какие компании они касаются. Опиши только то, что прямо 
написано в заголовках, не добавляй собственных выводов и оценок.

Если в заголовках нет ничего существенного по моим компаниям — 
напиши «Существенных новостей нет».

Формат ответа: 3–5 предложений или короткий список. Без вступлений и заключений."""

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": 800,
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
    if alternatives:
        return alternatives[0].get("message", {}).get("text", "")
    return ""
