import requests
from config import NTFY_TOPIC, TRACKED_COMPANIES


def send_notification(prices: dict, analysis: str) -> None:
    """
    Отправляет уведомление в ntfy.sh с котировками и анализом новостей.
    """
    # Формируем блок котировок
    price_lines = []
    for ticker, name in TRACKED_COMPANIES.items():
        price = prices.get(ticker, "н/д")
        price_lines.append(f"{name}: {price} ₽")

    price_block = "\n".join(price_lines)

    # Итоговое сообщение
    message = f"""📊 Котировки:
{price_block}

📰 Анализ новостей:
{analysis if analysis else 'Важных новостей нет.'}"""

    headers = {
        "Title": "Мониторинг рынка",
        "Priority": "default",
        "Tags": "chart_with_upwards_trend",
    }

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers=headers,
        timeout=15,
    )
