from t_tech.invest import Client
from config import TBANK_TOKEN, TRACKED_COMPANIES

def get_last_prices() -> dict:
    prices = {}
    try:
        with Client(TBANK_TOKEN) as client:
            # Получаем список FIGI для наших тикеров
            figi_map = {}
            for ticker in TRACKED_COMPANIES:
                response = client.instruments.share_by(
                    id_type=1, # 1 = TICKER
                    id=f"{ticker}_TQBR",
                    class_code="TQBR"
                )
                figi_map[ticker] = response.instrument.figi
            
            if not figi_map:
                return {}

            # Запрашиваем цены по FIGI
            last_prices = client.market_data.get_last_prices(figi=list(figi_map.values()))
            
            # Сопоставляем FIGI обратно с тикерами
            figi_to_ticker = {v: k for k, v in figi_map.items()}
            
            for price in last_prices.last_prices:
                ticker = figi_to_ticker.get(price.figi)
                if ticker:
                    # Цена в SDK возвращается как объект Quotation
                    value = price.price.units + price.price.nano / 1e9
                    prices[ticker] = round(value, 2)
                    
    except Exception as e:
        print(f"Ошибка в SDK при получении котировок: {e}")
        return {}
        
    return prices
