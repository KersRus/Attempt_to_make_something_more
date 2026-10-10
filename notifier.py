import json
import requests
from config import NTFY_TOPIC, TRACKED_COMPANIES


def send_notification(prices: dict, analysis: str) -> None:
    """
    Отправляет уведомление в ntfy.sh с котировками и анализом новостей.
    Использует JSON-тело для поддержки кириллицы в заголовке.
    """
    price_lines = []
    for ticker, name in TRACKED_COMPANIES.items():
        price = prices.get(ticker, "н/д")
        price_lines.append(f"{name}: {price} ₽")

    price_block = "\n".join(price_lines)

    message = f"""📊 Котировки:
{price_block}

📰 Анализ новостей:
{analysis if analysis else 'Важных новостей нет.'}"""

    # Отправляем метаданные через JSON-тело, а не через HTTP-заголовки
    payload = {
        "topic": NTFY_TOPIC,
        "message": message,
        "title": "Мониторинг рынка",
        "priority": 3,          # default
        "tags": ["chart_with_upwards_trend"],
    }

    requests.post(
        "https://ntfy.sh",
        json=payload,           # <-- JSON-тело вместо data и headers
        timeout=15,
    )
