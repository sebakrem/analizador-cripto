import pandas as pd
import numpy as np
import talib
from binance_client_web import BinanceClient

class TechnicalAnalyzer:
    def __init__(self, df, symbol=None):
        self.df = self._clean_data(df)
        self.symbol = symbol

    def _clean_data(self, df):
        if df is None or df.empty:
            return pd.DataFrame()
        df_clean = df.replace([np.inf, -np.inf], np.nan).dropna()
        return df_clean

    def _check_sufficient_data(self, min_periods=50):
        available = len(self.df)
        if available >= 80:
            return True
        elif available >= 50:
            return True
        elif available >= 20:
            return True
        else:
            return False

    def _get_default_analysis(self):
        current_price = float(self.df['close'].iloc[-1]) if not self.df.empty else 0
        return {
            'current_price': current_price,
            'rsi': 50.0,
            'moving_averages': {
                'ema_10': current_price, 'ema_55': current_price, 'sma_20': current_price,
                'ema_cross_status': 'INDETERMINADO', 'trend_direction': 'NEUTRAL',
                'price_vs_ema55': 0, 'price_vs_ema55_percent': 0
            },
            'volume_analysis': {'volume_trend': 'NEUTRO', 'volume_ratio': 1.0},
            'trend': 'INDETERMINADA', 'trend_percentage': 0.0, 'trend_strength': 'DATOS_INSUFICIENTES',
            'squeeze_momentum': {
                'squeeze_value': 0, 'squeeze_status': 'NO_SQUEEZE',
                'momentum_trend': 'NEUTRO'
            },
            'adx': {
                'adx': 0, 'plus_di': 0, 'minus_di': 0, 'trend_strength': 'DEBIL',
                'above_key_level': False, 'trend_direction': 'NEUTRAL'
            },
            'data_quality': f'INSUFICIENTE ({len(self.df)} registros)'
        }

    def calculate_rsi(self, period=14):
        if not self._check_sufficient_data(period + 20):
            return 50.0
        try:
            close_prices = self.df['close'].astype(float).values
            rsi_values = talib.RSI(close_prices, timeperiod=period)
            valid_rsi = rsi_values[~np.isnan(rsi_values)]
            if len(valid_rsi) == 0:
                return 50.0
            last_rsi = float(valid_rsi[-1])
            return last_rsi
        except Exception as e:
            return 50.0

    def calculate_moving_averages(self):
        if not self._check_sufficient_data(55):
            current_price = float(self.df['close'].iloc[-1]) if not self.df.empty else 0
            return {
                'ema_10': current_price, 'ema_55': current_price, 'sma_20': current_price,
                'ema_cross_status': 'INDETERMINADO', 'trend_direction': 'NEUTRAL',
                'price_vs_ema55': 0, 'price_vs_ema55_percent': 0
            }
        try:
            close_prices = self.df['close'].astype(float).values
            current_price = float(self.df['close'].iloc[-1])

            ema_10 = talib.EMA(close_prices, timeperiod=10)
            ema_55 = talib.EMA(close_prices, timeperiod=55)
            sma_20 = talib.SMA(close_prices, timeperiod=20)

            ema_10_valid = ema_10[~np.isnan(ema_10)]
            ema_55_valid = ema_55[~np.isnan(ema_55)]
            sma_20_valid = sma_20[~np.isnan(sma_20)]

            mas = {}
            mas['ema_10'] = float(ema_10_valid[-1]) if len(ema_10_valid) > 0 else current_price
            mas['ema_55'] = float(ema_55_valid[-1]) if len(ema_55_valid) > 0 else current_price
            mas['sma_20'] = float(sma_20_valid[-1]) if len(sma_20_valid) > 0 else current_price

            ema_10_val = mas['ema_10']
            ema_55_val = mas['ema_55']

            if ema_10_val > ema_55_val:
                mas['ema_cross_status'] = "CRUCE_ALCISTA"
                mas['trend_direction'] = "ALCISTA"
            elif ema_10_val < ema_55_val:
                mas['ema_cross_status'] = "CRUCE_BAJISTA"
                mas['trend_direction'] = "BAJISTA"
            else:
                mas['ema_cross_status'] = "CRUCE_NEUTRO"
                mas['trend_direction'] = "NEUTRAL"

            mas['price_vs_ema55'] = current_price - ema_55_val
            mas['price_vs_ema55_percent'] = ((current_price - ema_55_val) / ema_55_val) * 100

            return mas
        except Exception as e:
            current_price = float(self.df['close'].iloc[-1]) if not self.df.empty else 0
            return {
                'ema_10': current_price, 'ema_55': current_price, 'sma_20': current_price,
                'ema_cross_status': 'ERROR', 'trend_direction': 'NEUTRAL',
                'price_vs_ema55': 0, 'price_vs_ema55_percent': 0
            }

    def calculate_volume_analysis(self):
        if not self._check_sufficient_data(20):
            return {'volume_trend': 'NEUTRO', 'volume_ratio': 1.0}
        try:
            volumes = self.df['volume'].astype(float).values
            volume_sma = talib.SMA(volumes, timeperiod=20)
            volume_sma_valid = volume_sma[~np.isnan(volume_sma)]

            if len(volume_sma_valid) == 0:
                return {'volume_trend': 'NEUTRO', 'volume_ratio': 1.0}

            current_volume = volumes[-1]
            avg_volume = volume_sma_valid[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            if volume_ratio > 2.0:
                volume_trend = "MUY ALTO"
            elif volume_ratio > 1.5:
                volume_trend = "ALTO"
            elif volume_ratio < 0.5:
                volume_trend = "BAJO"
            else:
                volume_trend = "NORMAL"

            return {'volume_trend': volume_trend, 'volume_ratio': volume_ratio}
        except Exception as e:
            return {'volume_trend': 'NEUTRO', 'volume_ratio': 1.0}

    def analyze_trend(self):
        if not self._check_sufficient_data(50):
            return "INDETERMINADA", 0.0, "DATOS INSUFICIENTES"
        try:
            closes = self.df['close'].astype(float)
            medium_trend = ((closes.iloc[-1] - closes.iloc[-20]) / closes.iloc[-20]) * 100 if len(closes) >= 20 else 0
            long_trend = ((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100

            if medium_trend > 5 and long_trend > 2:
                trend = "FUERTE ALCISTA"
                strength = "ALTA"
            elif medium_trend < -5 and long_trend < -2:
                trend = "FUERTE BAJISTA"
                strength = "ALTA"
            elif long_trend > 2:
                trend = "ALCISTA"
                strength = "MEDIA"
            elif long_trend < -2:
                trend = "BAJISTA"
                strength = "MEDIA"
            else:
                trend = "LATERAL"
                strength = "BAJA"

            return trend, long_trend, strength
        except Exception as e:
            return "ERROR", 0.0, "ERROR"

    def calculate_squeeze_momentum(self, bb_length=20, bb_mult=2.0, kc_length=20, kc_mult=1.5):
        if not self._check_sufficient_data(max(bb_length, kc_length) + 20):
            return {'squeeze_value': 0, 'squeeze_status': 'NO_SQUEEZE', 'momentum_trend': 'NEUTRO'}
        try:
            close_prices = self.df['close'].astype(float).values
            high_prices = self.df['high'].astype(float).values
            low_prices = self.df['low'].astype(float).values

            basis = talib.SMA(close_prices, timeperiod=bb_length)
            dev = bb_mult * talib.STDDEV(close_prices, timeperiod=bb_length)
            upper_bb = basis + dev
            lower_bb = basis - dev

            kc_ma = talib.SMA(close_prices, timeperiod=kc_length)
            tr = talib.TRANGE(high_prices, low_prices, close_prices)
            range_ma = talib.SMA(tr, timeperiod=kc_length)
            upper_kc = kc_ma + range_ma * kc_mult
            lower_kc = kc_ma - range_ma * kc_mult

            squeeze_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
            squeeze_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)

            hl_avg = (talib.MAX(high_prices, kc_length) + talib.MIN(low_prices, kc_length)) / 2
            price_avg = (close_prices + hl_avg) / 2
            momentum = talib.LINEARREG(close_prices - price_avg, timeperiod=kc_length)

            momentum_valid = momentum[~np.isnan(momentum)]
            squeeze_on_valid = squeeze_on[~np.isnan(squeeze_on)]

            if len(momentum_valid) == 0:
                return {'squeeze_value': 0, 'squeeze_status': 'NO_SQUEEZE', 'momentum_trend': 'NEUTRO'}

            current_momentum = float(momentum_valid[-1])
            prev_momentum = float(momentum_valid[-2]) if len(momentum_valid) > 1 else current_momentum

            if current_momentum > 0:
                if current_momentum > prev_momentum:
                    momentum_trend = "ALCISTA_FUERTE"
                else:
                    momentum_trend = "ALCISTA_DEBIL"
            else:
                if current_momentum < prev_momentum:
                    momentum_trend = "BAJISTA_FUERTE"
                else:
                    momentum_trend = "BAJISTA_DEBIL"

            if squeeze_on_valid[-1]:
                squeeze_status = "SQUEEZE_ON"
            elif squeeze_off[-1]:
                squeeze_status = "SQUEEZE_OFF"
            else:
                squeeze_status = "NO_SQUEEZE"

            return {
                'squeeze_value': current_momentum,
                'squeeze_status': squeeze_status,
                'momentum_trend': momentum_trend
            }
        except Exception as e:
            return {'squeeze_value': 0, 'squeeze_status': 'ERROR', 'momentum_trend': 'NEUTRO'}

    def calculate_adx(self, di_length=14, adx_length=14, key_level=23):
        if not self._check_sufficient_data(max(di_length, adx_length) + 20):
            return {
                'adx': 0, 'plus_di': 0, 'minus_di': 0, 'trend_strength': 'DEBIL',
                'above_key_level': False, 'trend_direction': 'NEUTRAL'
            }
        try:
            high_prices = self.df['high'].astype(float).values
            low_prices = self.df['low'].astype(float).values
            close_prices = self.df['close'].astype(float).values

            adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=adx_length)
            plus_di = talib.PLUS_DI(high_prices, low_prices, close_prices, timeperiod=di_length)
            minus_di = talib.MINUS_DI(high_prices, low_prices, close_prices, timeperiod=di_length)

            adx_valid = adx[~np.isnan(adx)]
            plus_di_valid = plus_di[~np.isnan(plus_di)]
            minus_di_valid = minus_di[~np.isnan(minus_di)]

            if len(adx_valid) == 0:
                return {
                    'adx': 0, 'plus_di': 0, 'minus_di': 0, 'trend_strength': 'DEBIL',
                    'above_key_level': False, 'trend_direction': 'NEUTRAL'
                }

            current_adx = float(adx_valid[-1])
            current_plus_di = float(plus_di_valid[-1]) if len(plus_di_valid) > 0 else 0
            current_minus_di = float(minus_di_valid[-1]) if len(minus_di_valid) > 0 else 0

            if current_adx > 50:
                trend_strength = "MUY_FUERTE"
            elif current_adx > 25:
                trend_strength = "FUERTE"
            elif current_adx > 20:
                trend_strength = "MODERADA"
            else:
                trend_strength = "DEBIL"

            if current_plus_di > current_minus_di:
                trend_direction = "ALCISTA"
            elif current_plus_di < current_minus_di:
                trend_direction = "BAJISTA"
            else:
                trend_direction = "NEUTRAL"

            return {
                'adx': current_adx,
                'plus_di': current_plus_di,
                'minus_di': current_minus_di,
                'trend_strength': trend_strength,
                'above_key_level': current_adx > key_level,
                'trend_direction': trend_direction
            }
        except Exception as e:
            return {
                'adx': 0, 'plus_di': 0, 'minus_di': 0, 'trend_strength': 'DEBIL',
                'above_key_level': False, 'trend_direction': 'NEUTRAL'
            }

    def full_analysis(self):
        if not self._check_sufficient_data(100):
            return self._get_default_analysis()
        try:
            current_price = float(self.df['close'].iloc[-1])
            rsi = self.calculate_rsi()
            mas = self.calculate_moving_averages()
            volume = self.calculate_volume_analysis()
            trend, trend_percentage, trend_strength = self.analyze_trend()
            squeeze = self.calculate_squeeze_momentum()
            adx = self.calculate_adx()

            return {
                'current_price': current_price,
                'rsi': rsi,
                'moving_averages': mas,
                'volume_analysis': volume,
                'trend': trend,
                'trend_percentage': trend_percentage,
                'trend_strength': trend_strength,
                'squeeze_momentum': squeeze,
                'adx': adx,
                'data_quality': f"EXCELENTE ({len(self.df)} registros)" if len(self.df) >= 100 else f"BUENA ({len(self.df)} registros)"
            }
        except Exception as e:
            return self._get_default_analysis()