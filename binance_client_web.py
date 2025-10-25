import ccxt
import pandas as pd

class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': '',
            'secret': '',
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.connection_ok = self.test_connection()

    def test_connection(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            print("✅ Conexión a Binance exitosa")
            return True
        except Exception as e:
            print(f"❌ Error de conexión a Binance: {e}")
            return False

    def get_ohlcv_data(self, symbol, timeframe, limit=5000):
        if not self.connection_ok:
            print("❌ No hay conexión a Binance")
            return None
        try:
            adjusted_limit = self._get_adjusted_limit(timeframe, limit)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=adjusted_limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.dropna()
            df = df.drop_duplicates()
            print(f"✅ Datos obtenidos para {symbol} - {len(df)} registros")
            return df
        except Exception as e:
            print(f"❌ Error obteniendo datos para {symbol}: {e}")
            return None

    def _get_adjusted_limit(self, timeframe, original_limit):
        long_timeframes = ['1M', '1w', '3d']
        if timeframe in long_timeframes:
            return min(original_limit, 100)
        else:
            return original_limit

    def get_current_price(self, symbol):
        try:
            binance_symbol = symbol.replace("/", "")
            ticker = self.exchange.fetch_ticker(binance_symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error obteniendo precio de {symbol}: {e}")
            return None