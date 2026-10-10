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


def fetch_tbank_news(limit: int = 50) -> list[dict]:
    """
    Получает новости из T-Bank Invest API.
    Возвращает список словарей с полями: title, content, source, priority, ts, tickers.
    """
    payload = {"limit": limit}
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
    news_items = []

    for item in data.get("items", []):
        # Извлекаем тикеры, к которым привязана новость
        tickers = []
        for inst in item.get("instrumentId", []):
            instrument = inst.get("instrument", {})
            ticker = instrument.get("ticker")
            if ticker:
                tickers.append(ticker)

        news_items.append({
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "source": item.get("source", "T-Bank"),
            "priority": item.get("priority", False),
            "ts": item.get("ts", ""),
            "tickers": tickers,
        })

    return news_items


def fetch_rss_news(hours_back: int = 1) -> list[dict]:
    """
    Собирает новости из RSS-лент.
    Фильтрует по времени (за последние `hours_back` часов) и по упоминанию компаний.
    """
    cutoff = datetime.now(MSK) - timedelta(hours=hours_back)
    all_news = []

    company_names = list(TRACKED_COMPANIES.values())
    tickers = list(TRACKED_COMPANIES.keys())

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in feed.entries:
            # Проверяем дату публикации
            published = entry.get("published_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc).astimezone(MSK)
                if pub_dt < cutoff:
                    continue
            else:
                pub_dt = datetime.now(MSK)

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            # Проверяем, упоминается ли хотя бы одна из компаний или тикеров
            matched = False
            for name in company_names:
                if name.lower() in text:
                    matched = True
                    break
            if not matched:
                for ticker in tickers:
                    if ticker.lower() in text:
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
