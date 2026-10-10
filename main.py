from datetime import datetime, time, timezone, timedelta
from config import TRACKED_COMPANIES
from market_data import get_last_prices
from news_fetcher import fetch_tbank_news, fetch_rss_news
from analyzer import analyze_news
from notifier import send_notification

MSK = timezone(timedelta(hours=3))


def is_active_time() -> bool:
    """Проверяет, что сейчас активное время (06:00–24:00 МСК)."""
    now = datetime.now(MSK)
    return now.time() >= time(6, 0)


def main():
    if not is_active_time():
        print("Неактивное время. Пропускаем.")
        return

    print(f"Запуск мониторинга в {datetime.now(MSK).strftime('%H:%M')} МСК")

    # 1. Получаем котировки
    try:
        prices = get_last_prices()
        print(f"Котировки: {prices}")
    except Exception as e:
        print(f"Ошибка получения котировок: {e}")
        prices = {}

    # 2. Собираем новости
    try:
        tbank_news = fetch_tbank_news()
        rss_news = fetch_rss_news(hours_back=1)
        all_news = tbank_news + rss_news
        print(f"Собрано новостей: {len(all_news)}")
    except Exception as e:
        print(f"Ошибка сбора новостей: {e}")
        all_news = []

    # 3. Анализируем через Yandex GPT (только если есть новости)
    analysis = ""
    if all_news:
        try:
            analysis = analyze_news(all_news)
        except Exception as e:
            print(f"Ошибка анализа: {e}")
            analysis = "Не удалось проанализировать новости."

    # 4. Отправляем уведомление
    try:
        send_notification(prices, analysis)
        print("Уведомление отправлено.")
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")


if __name__ == "__main__":
    main()
