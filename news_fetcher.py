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


def fetch_tbank_news(minutes_back: int = 10) -> list[dict]:
    """
    Получает новости из T-Bank Invest API и оставляет только те,
    что опубликованы за последние `minutes_back` минут.
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
    news_items = []

    for item in data.get("items", []):
        ts_raw = item.get("ts", "")
        try:
            pub_dt = datetime.fromisoformat(
                ts_raw.replace("Z", "+00:00")
            ).astimezone(MSK)
        except Exception:
            continue

        if pub_dt < cutoff:
            continue

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
            "ts": pub_dt.isoformat(),
            "tickers": tickers,
        })

    return news_items


def fetch_rss_news(minutes_back: int = 10) -> list[dict]:
    """
    Собирает новости из RSS-лент за последние `minutes_back` минут.
    Фильтрует по упоминанию компаний.
    """
    cutoff = datetime.now(MSK) - timedelta(minutes=minutes_back)
    all_news = []

    company_names = list(TRACKED_COMPANIES.values())
    tickers = list(TRACKED_COMPANIES.keys())

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

            matched = False
            for name in company_names:
                if name.lower() in text_lower:
                    matched = True
                    break
            if not matched:
                for ticker in tickers:
                    pattern = (
                        rf"(?<![a-zA-Zа-яА-Я])"
                        rf"{re.escape(ticker.lower())}"
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
