import requests
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, TRACKED_COMPANIES


def analyze_news(news_items: list[dict]) -> str:
    """
    Отправляет новости в Yandex GPT и возвращает текстовый анализ:
    какие новости важны и как они могут повлиять на котировки.
    """
    if not news_items:
        return ""

    # Формируем компактный список для промпта
    news_text = "\n".join(
        f"- [{item['source']}] {item['title']}"
        for item in news_items[:30]  # ограничиваем контекст
    )

    company_list = ", ".join(TRACKED_COMPANIES.values())

    prompt = f"""Ты — финансовый аналитик. Проанализируй следующие новости за последний час 
для компаний: {company_list}.

Новости:
{news_text}

Определи:
1. Какие новости действительно важны (влияют на цену акций, дивиденды, отчётность, регуляторику).
2. Для каждой важной новости укажи компанию и короткий вывод (1-2 предложения).
3. Если важных новостей нет — напиши "Важных новостей нет".

Отвечай на русском языке, структурированно и кратко."""

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 1000,
        },
        "messages": [
            {"role": "system", "text": "Ты — финансовый аналитик."},
            {"role": "user", "text": prompt},
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
