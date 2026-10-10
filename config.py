import os

# T-Bank Invest API — токен только для чтения
TBANK_TOKEN = os.environ["TBANK_TOKEN"]

# Yandex GPT API
YANDEX_API_KEY = os.environ["YANDEX_API_KEY"]
YANDEX_FOLDER_ID = os.environ["YANDEX_FOLDER_ID"]

# ntfy.sh — топик для уведомлений
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

# Список отслеживаемых компаний: тикер -> отображаемое имя
TRACKED_COMPANIES = {
    "OZON": "Ozon",
    "T": "Т-Технологии",
    "YDEX": "Яндекс",
    "POSI": "Positive Technologies",
    "MOEX": "Московская биржа",
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

# Путь к CA-бандлу для T-Bank API
# GitHub Actions запускает код из корня репозитория, поэтому путь относительный
TBANK_CA_BUNDLE = os.path.join(os.path.dirname(__file__), "tbank_ca_bundle.pem")
