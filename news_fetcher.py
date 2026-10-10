import feedparser
from datetime import datetime, timedelta, timezone
from t_tech.invest import Client
from config import (
    TBANK_TOKEN,
    RSS_FEEDS,
    TRACKED_COMPANIES,
)

MSK = timezone(timedelta(hours=3))


def fetch_tbank_news(limit: int = 50) -> list[dict]:
    """
    Получает новости из T-Bank Invest API через официальный SDK.
    Возвращает только новости, релевантные отслеживаемым компаниям.
    """
    news_items = []
    try:
        with Client(TBANK_TOKEN) as client:
            response = client.instruments.news(limit=limit)

            for item in response.news:
                # Оставляем только новости, привязанные к нашим тикерам
                tickers = [
                    inst.ticker
                    for inst in item.instruments
                    if inst.ticker in TRACKED_COMPANIES
                ]
                if not tickers:
                    continue

                # ts в SDK — это datetime с таймзоной UTC
                ts = item.ts
                if isinstance(ts, datetime):
                    ts_str = ts.isoformat()
                else:
                    ts_str = str(ts)

                news_items.append({
                    "title": item.title,
                    "content": item.content,
                    "source": item.source or "T-Bank",
                    "priority": bool(item.priority),
                    "ts": ts_str,
                    "tickers": tickers,
                })

    except Exception as e:
        print(f"Ошибка в SDK при получении новостей: {e}")
        return []

    return news_items


def fetch_rss_news(hours_back: int = 1) -> list[dict]:
    """
    Собирает новости из RSS-лент внешних СМИ.
    Фильтрует по времени (за последние `hours_back` часов) и по упоминанию компаний.
    """
    cutoff = datetime.now(MSK) - timedelta(hours=hours_back)
    all_news = []

    company_names = list(TRACKED_COMPANIES.values())
    tickers = list(TRACKED_COMPANIES.keys())

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"Ошибка чтения RSS {source_name}: {e}")
            continue

        for entry in feed.entries:
            # Проверяем дату публикации
            published = entry.get("published_parsed")
            if published:
                try:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc).astimezone(MSK)
                except Exception:
                    pub_dt = datetime.now(MSK)
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
                    # Ищем тикер как отдельное слово, чтобы избежать ложных срабатываний
                    # (например, "T" не должен совпадать с "инвестиции")
                    if f" {ticker.lower()} " in f" {text} ":
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
