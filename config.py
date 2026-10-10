import os

# T-Bank Invest API — токен только для чтения
TBANK_TOKEN = os.environ["TBANK_TOKEN"]

# ntfy.sh — топик для уведомлений
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

# Список отслеживаемых компаний: тикер -> отображаемое имя
TRACKED_COMPANIES = {
    "OZON": "Ozon",
    "T": "Т-Технологии",
    "YDEX": "Яндекс",
    "POSI": "Positive Technologies",
}

# RSS-ленты новостных источников
RSS_FEEDS = {
    "Finam": "https://www.finam.ru/analysis/conews/rsspoint/",
    "ProFinance": "https://www.profinance.ru/fond.xml",
    "SmartLab": "https://smart-lab.ru/allnews/rss/",
    "Kommersant": "https://www.kommersant.ru/RSS/news.xml",
}

# T-Bank Invest API endpoint
TBANK_API_URL = "https://invest-public-api.tbank.ru/rest"
