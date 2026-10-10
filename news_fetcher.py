import re
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from config import (
    TBANK_TOKEN,
    TBANK_API_URL,
    RSS_FEEDS,
    TRACKED_COMPANIES,
)

MSK = timezone(timedelta(hours=3))

# Варианты написания названий компаний для поиска в RSS.
# Ключи должны совпадать с ключами TRACKED_COMPANIES.
COMPANY_ALIASES = {
    "OZON": ["ozon", "озон"],
    "T": ["т-технологии", "тинькофф", "т-банк", "t-технологии", "тcs group"],
    "YDEX": ["яндекс", "yandex"],
    "POSI": ["positive technologies", "позитив", "positive tech"],
}


def fetch_tbank_news(minutes_back: int = 10) -> list[dict]:
    """
    Получает новости из T-Bank Invest API.
    Оставляет только те, что относятся к отслеживаемым компаниям
    и опубликованы за последние `minutes_back` минут.
    """
    payload = {"limit": 50}
    headers = {
        "Authorization": f"Bearer {TBANK_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{TBANK_API_URL}/tinkoff.public.invest.api.contract.v1.InstrumentsService/News",
        json=payload,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    cutoff = datetime.now(MSK) - timedelta(minutes=minutes_back)
    tracked_tickers = set(TRACKED_COMPANIES.keys())
    news_items = []

    for item in data.get("items", []):
        # 1. Фильтр по времени
        ts_raw = item.get("ts", "")
        try:
            pub_dt = datetime.fromisoformat(
                ts_raw.replace("Z", "+00:00")
            ).astimezone(MSK)
        except Exception:
            continue

        if pub_dt < cutoff:
            continue

        # 2. Фильтр по тикерам: собираем только те, что есть в нашем списке
        matched_tickers = []
        for inst in item.get("instrumentId", []):
            instrument = inst.get("instrument", {})
            ticker = instrument.get("ticker", "")
            if ticker in tracked_tickers:
                matched_tickers.append(ticker)

        # 3. Если ни одного из наших тикеров нет — пропускаем новость
        if not matched_tickers:
            continue

        news_items.append({
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "source": item.get("source", "T-Bank"),
            "priority": item.get("priority", False),
            "ts": pub_dt.isoformat(),
            "tickers": matched_tickers,
        })

    return news_items


def fetch_rss_news(minutes_back: int = 10) -> list[dict]:
    """
    Собирает новости из RSS-лент за последние `minutes_back` минут.
    Фильтрует по упоминанию компаний (по имени или алиасу).
    Тикеры не используем — они слишком короткие и дают ложные срабатывания.
    """
    cutoff = datetime.now(MSK) - timedelta(minutes=minutes_back)
    all_news = []

    # Собираем все алиасы в один список нижним регистром
    all_aliases = []
    for aliases in COMPANY_ALIASES.values():
        all_aliases.extend(aliases)

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in feed.entries:
            published = entry.get("published_parsed")
            if published:
                pub_dt = datetime(
                    *published[:6], tzinfo=timezone.utc
                ).astimezone(MSK)
                if pub_dt < cutoff:
                    continue
            else:
                continue

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text_lower = f"{title} {summary}".lower()

            # Проверяем, есть ли в тексте хотя бы один алиас
            matched = False
            for alias in all_aliases:
                # Ищем алиас как отдельную фразу (на границе слов)
                pattern = (
                    rf"(?<![a-zA-Zа-яА-Я])"
                    rf"{re.escape(alias)}"
                    rf"(?![a-zA-Zа-яА-Я])"
                )
                if re.search(pattern, text_lower):
                    matched = True
                    break

            if matched:
                all_news.append({
                    "title": title,
                    "content": summary,
                    "source": source_name,
                    "priority": False,
                    "ts": pub_dt.isoformat(),
                    "tickers": [],
                })

    return all_news
