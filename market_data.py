import requests
from config import TBANK_TOKEN, TBANK_API_URL, TRACKED_COMPANIES, TBANK_CA_BUNDLE


def get_last_prices() -> dict:
    """
    Возвращает словарь {тикер: цена} для всех отслеживаемых компаний.
    """
    instrument_ids = [f"{ticker}_TQBR" for ticker in TRACKED_COMPANIES]

    payload = {
        "instrumentId": instrument_ids,
        "lastPriceType": "LAST_PRICE_EXCHANGE",
    }

    headers = {
        "Authorization": f"Bearer {TBANK_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{TBANK_API_URL}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices",
        json=payload,
        headers=headers,
        timeout=15,
        verify=TBANK_CA_BUNDLE,
    )
    response.raise_for_status()

    data = response.json()
    prices = {}

    for item in data.get("lastPrices", []):
        ticker = item.get("ticker", "UNKNOWN")
        price_obj = item.get("price", {})
        units = int(price_obj.get("units", 0))
        nano = int(price_obj.get("nano", 0))
        price = units + nano / 1e9
        prices[ticker] = round(price, 2)

    return prices
