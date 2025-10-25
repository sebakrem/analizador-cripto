import streamlit as st
import pandas as pd
from datetime import datetime
from binance_client_web import BinanceClient
from technical_analyzer_web import TechnicalAnalyzer

# Configuración idéntica a tu config.py
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT",
    "SOL/USDT", "DOT/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT",
    "LTC/USDT", "LINK/USDT", "GALA/USDT", "ATOM/USDT", "UNI/USDT",
    "XLM/USDT", "ALGO/USDT", "VET/USDT", "FIL/USDT", "ETC/USDT"
]

TIMEFRAMES = {
    "15min": "15m",
    "1 hora": "1h",
    "4 horas": "4h",
    "1 día": "1d",
    "1 semana": "1w",
    "1 mes": "1M"
}


def main():
    st.title("📊 Analizador de Criptomonedas - Binance")

    if 'binance' not in st.session_state:
        st.session_state.binance = BinanceClient()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "analysis"

    # Sidebar
    with st.sidebar:
        st.header("Configuración de Análisis")
        selected_crypto = st.selectbox("Criptomoneda:", CRYPTO_SYMBOLS)
        selected_timeframe = st.selectbox("Timeframe:", list(TIMEFRAMES.keys()))

        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("🔍 Analizar Cripto", use_container_width=True)
        with col2:
            entry_btn = st.button("📈 Entrada", use_container_width=True)

    # Navegación entre páginas
    if analyze_btn:
        st.session_state.current_page = "analysis"
        perform_analysis(selected_crypto, selected_timeframe)

    if entry_btn:
        st.session_state.current_page = "entry"
        show_entry_management()

    # Mostrar página actual
    if st.session_state.current_page == "entry":
        show_entry_management()


def perform_analysis(symbol, timeframe):
    st.header(f"Análisis de {symbol} - {timeframe}")

    with st.spinner("Obteniendo datos de Binance..."):
        binance_timeframe = TIMEFRAMES[timeframe]
        df = st.session_state.binance.get_ohlcv_data(symbol, binance_timeframe, limit=100)

    if df is None or df.empty:
        st.error("❌ No se pudieron obtener datos de Binance")
        return

    if len(df) < 20:
        st.error(f"❌ Datos insuficientes ({len(df)} registros)")
        return

    analyzer = TechnicalAnalyzer(df, symbol)
    analysis = analyzer.full_analysis()

    # DISEÑO DE DOS COLUMNAS IDÉNTICO A TU PROGRAMA
    col1, col2 = st.columns(2)

    with col1:
        show_personal_recommendation(analysis, symbol, timeframe)

    with col2:
        display_analysis_exact(analysis, symbol, timeframe)


def display_analysis_exact(analysis, symbol, timeframe):
    """RÉPLICA EXACTA de tu función display_analysis"""

    # ENCABEZADO
    st.write("=" * 60)
    st.write(f"**ANÁLISIS {symbol}**")
    st.write(f"**Timeframe: {timeframe}**")
    st.write(f"**Actualizado: {datetime.now().strftime('%H:%M:%S')}**")
    st.write("=" * 60)
    st.write("")

    # INFORMACIÓN BÁSICA
    st.write("**INFORMACIÓN BÁSICA**")
    st.write("-" * 40)
    current_price = analysis['current_price']
    price_str = f"${current_price:,.0f}" if current_price >= 1000 else f"${current_price:.2f}"
    st.write(f"Precio actual: {price_str}")
    st.write(f"Tendencia: {analysis['trend']}")
    st.write("")

    # MEDIAS MÓVILES
    st.write("**MEDIAS MÓVILES - ESTRATEGIA JAIME**")
    st.write("-" * 40)
    mas = analysis['moving_averages']
    ema_10_vs_price = "POR DEBAJO" if mas['ema_10'] < analysis['current_price'] else "POR ARRIBA"
    ema_55_vs_price = "POR DEBAJO" if mas['ema_55'] < analysis['current_price'] else "POR ARRIBA"

    st.write(f"• EMA 10: {ema_10_vs_price} del precio")
    st.write(f"• EMA 55: {ema_55_vs_price} del precio")
    st.write(f"• EMA 10 vs EMA 55: {mas['ema_cross_status'].replace('CRUCE_', '')}")

    # RETROCESO
    price_vs_ema55 = mas['price_vs_ema55_percent']
    if abs(price_vs_ema55) < 2.0:
        st.write(f"• RETROCESO: CERCA de EMA 55")
    elif price_vs_ema55 > 0:
        st.write(f"• RETROCESO: SOBRE EMA 55")
    else:
        st.write(f"• RETROCESO: DEBAJO EMA 55")
    st.write("")

    # SQUEEZE MOMENTUM
    st.write("**SQUEEZE MOMENTUM**")
    st.write("-" * 40)
    squeeze = analysis['squeeze_momentum']

    if squeeze['squeeze_status'] == "SQUEEZE_ON":
        st.write(f"• STATUS: MERCADO COMPRIMIDO")
    elif squeeze['squeeze_status'] == "SQUEEZE_OFF":
        st.write(f"• STATUS: MERCADO EXPANDIÉNDOSE")
    else:
        st.write(f"• STATUS: MERCADO NORMAL")

    momentum_trend = squeeze['momentum_trend']
    if "ALCISTA" in momentum_trend:
        st.write(f"• MOMENTUM: VALLE VERDE (Alcista)")
    elif "BAJISTA" in momentum_trend:
        st.write(f"• MOMENTUM: VALLE ROJO (Bajista)")
    else:
        st.write(f"• MOMENTUM: NEUTRO")
    st.write("")

    # ADX
    st.write("**ADX - FUERZA DE TENDENCIA**")
    st.write("-" * 40)
    adx = analysis['adx']
    st.write(f"• ADX: {adx['adx']:.1f} (Fuerza: {adx['trend_strength']})")
    st.write(f"• Dirección: {adx['trend_direction']}")

    if adx['above_key_level']:
        st.write(f"• NIVEL: Por encima de 23 (Fuerte)")
    else:
        st.write(f"• NIVEL: Por debajo de 23 (Débil)")
    st.write("")

    # RSI
    st.write("**RSI - MOMENTUM**")
    st.write("-" * 40)
    rsi = analysis['rsi']
    st.write(f"• RSI: {rsi:.1f}")
    if rsi < 30:
        st.write("• NIVEL: SOBREVENTA")
    elif rsi > 70:
        st.write("• NIVEL: SOBRECOMPRA")
    else:
        st.write("• NIVEL: NEUTRO")
    st.write("")

    # RECOMENDACIÓN
    show_single_recommendation_exact(analysis)


def show_single_recommendation_exact(analysis):
    """RÉPLICA EXACTA de tu generate_single_recommendation"""
    st.write("**RECOMENDACIÓN**")
    st.write("=" * 50)

    mas = analysis['moving_averages']
    squeeze = analysis['squeeze_momentum']
    adx = analysis['adx']
    rsi = analysis['rsi']

    # Calcular puntuaciones EXACTAMENTE igual
    buy_signals = 0
    total_buy_criteria = 5

    if mas['ema_cross_status'] == "CRUCE_ALCISTA":
        buy_signals += 1
    if abs(mas['price_vs_ema55_percent']) <= 3.0:
        buy_signals += 1
    if "ALCISTA" in squeeze['momentum_trend']:
        buy_signals += 1
    if adx['trend_direction'] == "ALCISTA":
        buy_signals += 1
    if rsi < 65:
        buy_signals += 1

    sell_signals = 0
    total_sell_criteria = 5

    if mas['ema_cross_status'] == "CRUCE_BAJISTA":
        sell_signals += 1
    if mas['price_vs_ema55_percent'] > 5.0:
        sell_signals += 1
    if "BAJISTA" in squeeze['momentum_trend']:
        sell_signals += 1
    if adx['trend_direction'] == "BAJISTA":
        sell_signals += 1
    if rsi > 70:
        sell_signals += 1

    buy_score = (buy_signals / total_buy_criteria) * 100
    sell_score = (sell_signals / total_sell_criteria) * 100

    # LÓGICA IDÉNTICA
    if buy_score >= 70 and buy_score > sell_score + 15 and mas['ema_cross_status'] == "CRUCE_ALCISTA":
        st.success("**SEÑAL LONG FUERTE**")
        st.write("")
        st.write("**CRITERIOS CUMPLIDOS:**")
        if mas['ema_cross_status'] == "CRUCE_ALCISTA":
            st.write("• EMA 10 > EMA 55 ✓")
        if abs(mas['price_vs_ema55_percent']) <= 3.0:
            st.write("• Retroceso ideal ✓")
        if "ALCISTA" in squeeze['momentum_trend']:
            st.write("• Momentum alcista ✓")
        if adx['trend_direction'] == "ALCISTA":
            st.write("• ADX alcista ✓")
        if rsi < 65:
            st.write(f"• RSI {rsi:.1f} ✓")
        st.write("")
        st.write(f"**PUNTUACIÓN: {buy_score:.0f}%**")

    elif sell_score >= 70 and sell_score > buy_score + 15 and mas['ema_cross_status'] == "CRUCE_BAJISTA":
        st.error("**SEÑAL SHORT FUERTE**")
        st.write("")
        st.write("**CRITERIOS CUMPLIDOS:**")
        if mas['ema_cross_status'] == "CRUCE_BAJISTA":
            st.write("• EMA 10 < EMA 55 ✓")
        if mas['price_vs_ema55_percent'] > 5.0:
            st.write("• Precio extendido ✓")
        if "BAJISTA" in squeeze['momentum_trend']:
            st.write("• Momentum bajista ✓")
        if adx['trend_direction'] == "BAJISTA":
            st.write("• ADX bajista ✓")
        if rsi > 70:
            st.write(f"• RSI {rsi:.1f} ✓")
        st.write("")
        st.write(f"**PUNTUACIÓN: {sell_score:.0f}%**")
    else:
        st.warning("**MERCADO EN EQUILIBRIO**")
        st.write("")
        st.write("**ESPERAR SEÑAL MÁS CLARA**")
        st.write("")
        if mas['ema_cross_status'] != "CRUCE_ALCISTA" and buy_score > 50:
            st.write(f"• Falta: EMA 10 > EMA 55")
        elif mas['ema_cross_status'] != "CRUCE_BAJISTA" and sell_score > 50:
            st.write(f"• Falta: EMA 10 < EMA 55")
        st.write("")
        if buy_score > sell_score:
            st.write(f"(Sesgo alcista: {buy_score:.0f}%)")
        else:
            st.write(f"(Sesgo bajista: {sell_score:.0f}%)")


def show_personal_recommendation(analysis, symbol, timeframe):
    """RÉPLICA EXACTA de tu generate_personal_recommendation"""

    mas = analysis['moving_averages']
    rsi = analysis['rsi']
    squeeze = analysis['squeeze_momentum']
    adx = analysis['adx']
    current_price = analysis['current_price']

    recommendation = "Hola Sebastián,\n\n"
    recommendation += f"Análisis {symbol}:\n\n"

    # SEÑALES PRINCIPALES
    recommendation += "SEÑALES PRINCIPALES:\n\n"

    if mas['ema_cross_status'] == "CRUCE_ALCISTA":
        recommendation += "EMA: Tendencia alcista\n"
    else:
        recommendation += "EMA: Tendencia bajista\n"

    if "ALCISTA" in squeeze['momentum_trend']:
        recommendation += "SQUEEZE: Valle verde\n"
    else:
        recommendation += "SQUEEZE: Valle rojo\n"

    recommendation += f"RSI: {rsi:.1f}\n"
    recommendation += f"ADX: {adx['adx']:.1f}\n\n"

    # INTERPRETACIÓN
    recommendation += "INTERPRETACIÓN:\n"

    momentum_fuerte = (adx['adx'] > 23 and
                       "ALCISTA" in squeeze['momentum_trend'] and
                       rsi < 65)

    momentum_moderado = (adx['adx'] > 18 and
                         "ALCISTA" in squeeze['momentum_trend'] and
                         rsi < 70)

    if momentum_fuerte:
        recommendation += "MOMENTUM FUERTE ALCISTA\n"
        recommendation += "Tendencia bien establecida\n"
    elif momentum_moderado:
        recommendation += "MOMENTO ALCISTA CONFIRMADO\n"
        recommendation += "Buena dirección\n"
    else:
        recommendation += "MOMENTUM DÉBIL\n"
        recommendation += "Falta fuerza\n"

    # ACCIÓN
    recommendation += "\nACCIÓN:\n"

    if mas['ema_cross_status'] == "CRUCE_ALCISTA" and "ALCISTA" in squeeze['momentum_trend']:

        # Calcular niveles de entrada
        entrada_conservadora = mas['ema_55'] * 0.995
        entrada_media = min(current_price, mas['ema_10'] * 0.998)
        entrada_agresiva = current_price

        # Lógica inteligente de entrada
        if momentum_fuerte:
            if current_price <= mas['ema_55'] * 1.02:
                mejor_entrada = entrada_agresiva
                recomendacion_entrada = "ENTRADA INMEDIATA - Momentum fuerte + Precio ideal"
            elif current_price <= mas['ema_10'] * 1.01:
                mejor_entrada = entrada_agresiva
                recomendacion_entrada = "ENTRADA AHORA - Momentum fuerte + Buen nivel"
            else:
                mejor_entrada = entrada_media
                recomendacion_entrada = "ENTRADA CONVIENE - Momentum fuerte compensa precio"

        elif momentum_moderado:
            if current_price <= mas['ema_55'] * 1.01:
                mejor_entrada = entrada_agresiva
                recomendacion_entrada = "ENTRADA RECOMENDADA - Precio ideal"
            elif current_price <= mas['ema_10']:
                mejor_entrada = entrada_agresiva
                recomendacion_entrada = "ENTRADA BUENA - Nivel aceptable"
            else:
                mejor_entrada = entrada_conservadora
                recomendacion_entrada = "ESPERAR RETROCESO - Precio alto"

        else:
            if current_price <= mas['ema_55'] * 1.005:
                mejor_entrada = entrada_agresiva
                recomendacion_entrada = "ENTRADA CAUTELOSA - Solo si precio ideal"
            else:
                mejor_entrada = entrada_conservadora
                recomendacion_entrada = "ESPERAR MEJOR PRECIO - Momentum débil"

        recommendation += f"Considerar LONG\n"
        recommendation += f"Mejor entrada: ${mejor_entrada:.0f}\n"
        recommendation += f"Recomendación: {recomendacion_entrada}\n"

        # Mostrar diferencia si hay oportunidad de entrada actual
        diferencia_porcentaje = abs(current_price - mejor_entrada) / current_price * 100
        if diferencia_porcentaje > 2 and mejor_entrada < current_price:
            recommendation += f"Precio actual: ${current_price:.0f} (+{diferencia_porcentaje:.1f}%)\n"
        elif current_price <= mejor_entrada * 1.01:
            recommendation += f"Precio actual ES buena entrada\n"

        # Gestión de riesgo
        stop_loss = mas['ema_55'] * 0.98
        target_1 = current_price * 1.02
        target_2 = current_price * 1.04

        recommendation += f"Stop: ${stop_loss:.0f}\n"
        recommendation += f"Target 1: ${target_1:.0f}\n"
        recommendation += f"Target 2: ${target_2:.0f}\n"

        # Explicación simple del riesgo/beneficio
        riesgo = current_price - stop_loss
        beneficio_1 = target_1 - current_price

        if beneficio_1 > 0:
            rr_1 = beneficio_1 / riesgo
            if rr_1 >= 2.0:
                recommendation += f"Relación: Ganas el DOBLE de lo que arriesgas\n"
            elif rr_1 >= 1.5:
                recommendation += f"Relación: Ganas MÁS de lo que arriesgas\n"
            elif rr_1 >= 1.0:
                recommendation += f"Relación: Ganas lo MISMO que arriesgas\n"
            else:
                recommendation += f"Relación: Arriesgas MÁS de lo que ganas\n"

    elif mas['ema_cross_status'] == "CRUCE_BAJISTA" and "BAJISTA" in squeeze['momentum_trend'] and rsi > 70:
        recommendation += "Considerar SHORT\n"
        recommendation += f"Entrada: ${current_price:.0f}\n"
        recommendation += f"Stop: ${current_price * 1.02:.0f}\n"
        recommendation += f"Target: ${current_price * 0.96:.0f}\n"

        # Explicación simple para SHORT
        riesgo_short = (current_price * 1.02) - current_price
        beneficio_short = current_price - (current_price * 0.96)
        rr_short = beneficio_short / riesgo_short

        if rr_short >= 2.0:
            recommendation += f"Relación: Ganas el DOBLE de lo que arriesgas\n"
        elif rr_short >= 1.5:
            recommendation += f"Relación: Ganas MÁS de lo que arriesgas\n"
        elif rr_short >= 1.0:
            recommendation += f"Relación: Ganas lo MISMO que arriesgas\n"
        else:
            recommendation += f"Relación: Arriesgas MÁS de lo que ganas\n"

    else:
        recommendation += "Esperar mejor señal\n"
        if mas['ema_cross_status'] != "CRUCE_ALCISTA":
            recommendation += "Falta: EMA 10 > EMA 55\n"
        elif "ALCISTA" not in squeeze['momentum_trend']:
            recommendation += "Falta: Momentum alcista\n"
        elif rsi > 65:
            recommendation += "RSI muy alto, esperar\n"
        else:
            recommendation += "Condiciones no óptimas\n"

    # GESTIÓN DE TIEMPO SOLO SI HAY OPERACIÓN
    if "Considerar LONG" in recommendation or "Considerar SHORT" in recommendation:
        recommendation += "\n⏰ GESTIÓN DE TIEMPO:\n"
        recommendation += "----------------------------------------\n"

        timeframe_advice = {
            "15min": "• DURACIÓN: 15-90 min (1-6 velas)\n• MÁXIMO: 2 horas sin avance\n• TIPO: Scalping rápido",
            "1 hora": "• DURACIÓN: 2-8 horas (2-8 velas)\n• MÁXIMO: 12 horas operación\n• TIPO: Intradía",
            "4 horas": "• DURACIÓN: 1-5 días (6-30 velas)\n• REEVALUAR: A los 3 días\n• TIPO: Swing corto",
            "1 día": "• DURACIÓN: 3-15 días\n• REVISAR: Semanalmente\n• TIPO: Swing medio",
            "1 semana": "• DURACIÓN: 2-8 semanas\n• ANÁLISIS: Mensual\n• TIPO: Medio plazo",
            "1 mes": "• DURACIÓN: 1-6 meses\n• REVISAR: Trimestral\n• TIPO: Largo plazo"
        }

        if timeframe in timeframe_advice:
            recommendation += timeframe_advice[timeframe] + "\n"
        else:
            recommendation += "• DURACIÓN: 1-5 días (6-30 velas)\n• REEVALUAR: A los 3 días\n• TIPO: Swing corto\n"

    # EXPLICACIONES FIJAS
    recommendation += "\n" + "=" * 40 + "\n"
    recommendation += "RECUERDA:\n"
    recommendation += "MEDIAS MÓVILES: DIRECCIÓN DE TENDENCIA\n"
    recommendation += "SQUEEZE MOMENTUM: COMPRESIÓN/EXPLOSIÓN\n"
    recommendation += "ADX: QUÉ TAN FUERTE ES LA TENDENCIA\n"
    recommendation += "RSI: QUÉ TAN FUERTE ES EL MOVIMIENTO\n"

    # Mostrar en Streamlit
    st.subheader("🎯 RECOMENDACIÓN PERSONAL")
    st.text(recommendation)


def show_entry_management():
    """Gestión de operaciones activas - RÉPLICA de tu open_entry_analysis()"""
    st.header("📈 Gestión de Operación Activa")

    with st.form("entry_form"):
        col1, col2 = st.columns(2)

        with col1:
            symbol = st.selectbox("Moneda:", CRYPTO_SYMBOLS, key="entry_symbol")
            timeframe = st.selectbox("Timeframe de entrada:", list(TIMEFRAMES.keys()), key="entry_timeframe")
            entry_price = st.text_input("Precio de entrada:", placeholder="Ej: 110816 para BTC o 0.0114 para GALA")

        with col2:
            operation_type = st.radio("Tipo de operación:", ["LONG", "SHORT", "SPOT"], horizontal=True)
            analyze_btn = st.form_submit_button("📊 ANALIZAR OPERACIÓN")

    if analyze_btn:
        analyze_active_operation(symbol, timeframe, entry_price, operation_type)


def analyze_active_operation(symbol, timeframe, entry_price_str, operation_type):
    """Análisis de operación activa - RÉPLICA de tu analyze_active_operation()"""
    if not entry_price_str:
        st.error("❌ Ingresa el precio de entrada")
        return

    try:
        entry_price = float(entry_price_str.replace(',', '.'))
    except ValueError:
        st.error("❌ Precio inválido. Usa números (ej: 110816 o 0.0114)")
        return

    # Obtener precio actual
    current_price = st.session_state.binance.get_current_price(symbol)
    if current_price is None:
        st.error("❌ Error: No se pudo obtener el precio actual")
        return

    # Calcular resultado
    if operation_type == "LONG":
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price) * 100
    elif operation_type == "SHORT":
        pnl = entry_price - current_price
        pnl_percent = (pnl / entry_price) * 100
    else:  # SPOT
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price) * 100

    # Mostrar información
    st.subheader("📊 Resultado de la Operación")

    col1, col2, col3 = st.columns(3)

    with col1:
        price_fmt = f"${entry_price:,.0f}" if entry_price >= 1000 else f"${entry_price:.2f}" if entry_price >= 1 else f"${entry_price:.6f}"
        st.metric("Precio Entrada", price_fmt)
    with col2:
        current_fmt = f"${current_price:,.0f}" if current_price >= 1000 else f"${current_price:.2f}" if current_price >= 1 else f"${current_price:.6f}"
        st.metric("Precio Actual", current_fmt)
    with col3:
        st.metric("Resultado", f"${pnl:+.2f}", f"{pnl_percent:+.2f}%")

    # Obtener análisis técnico para recomendación
    binance_timeframe = TIMEFRAMES.get(timeframe, "1h")
    df = st.session_state.binance.get_ohlcv_data(symbol, binance_timeframe, limit=100)

    if df is not None and len(df) >= 20:
        analyzer = TechnicalAnalyzer(df, symbol)
        analysis = analyzer.full_analysis()
        show_operation_recommendation(analysis, entry_price, current_price, operation_type, pnl, pnl_percent, timeframe)
    else:
        st.warning("No se pudo obtener análisis técnico para recomendación")


def show_operation_recommendation(analysis, entry_price, current_price, operation_type, pnl, pnl_percent, timeframe):
    """Recomendación de operación activa - RÉPLICA de tu show_operation_recommendation()"""
    st.subheader("🎯 Recomendación de Gestión")

    mas = analysis['moving_averages']
    squeeze = analysis['squeeze_momentum']

    if operation_type == "LONG":
        if "ALCISTA" in mas['ema_cross_status'] and "ALCISTA" in squeeze['momentum_trend']:
            if pnl > 0:
                st.success("✅ MANTENER POSICIÓN")
                st.write("Señales alcistas fuertes")
                if pnl_percent > 2:
                    st.write(f"🎯 SUBIR STOP a ${entry_price * 1.01:.0f}")
                st.write(f"📈 TARGET: ${current_price * 1.03:.0f}")
            else:
                st.warning("⚠️ MANTENER CON CAUTELA")
                st.write("En pérdida pero señales positivas")
        else:
            st.error("🔴 CERRAR POSICIÓN")
            st.write("Señales bajistas detectadas")

    elif operation_type == "SHORT":
        if "BAJISTA" in mas['ema_cross_status'] and "BAJISTA" in squeeze['momentum_trend']:
            if pnl > 0:
                st.success("✅ MANTENER POSICIÓN")
                st.write("Señales bajistas fuertes")
                if pnl_percent > 2:
                    st.write(f"🎯 BAJAR STOP a ${entry_price * 0.99:.0f}")
                st.write(f"📉 TARGET: ${current_price * 0.97:.0f}")
            else:
                st.warning("⚠️ MANTENER CON CAUTELA")
                st.write("En pérdida pero señales negativas")
        else:
            st.error("🔴 CERRAR POSICIÓN")
            st.write("Señales alcistas detectadas")

    else:  # SPOT
        if "ALCISTA" in mas['ema_cross_status'] and pnl_percent < -5:
            st.success("✅ MANTENER SPOT")
            st.write("Tendencia mejorando, esperar recuperación")
            precio_venta_sugerido = entry_price * 0.99
            st.write(f"💰 Considerar vender en: ${precio_venta_sugerido:.4f}")
        elif "BAJISTA" in mas['ema_cross_status'] and pnl_percent < -10:
            st.error("🔴 CONSIDERAR VENDER")
            st.write("Tendencia bajista fuerte, puede empeorar")
            precio_venta_urgente = current_price * 1.02
            st.write(f"🚨 Vender si llega a: ${precio_venta_urgente:.4f}")
        elif pnl_percent < -20:
            st.error("🚨 VENDER PARCIAL")
            st.write("Pérdida significativa, reducir riesgo")
            st.write(f"💸 Vender 50% ahora: ${current_price:.4f}")
        else:
            st.warning("🟡 MANTENER SPOT")
            st.write("Esperar mejores condiciones")
            precio_objetivo = entry_price * 1.05
            st.write(f"🎯 Objetivo venta: ${precio_objetivo:.4f}")


if __name__ == "__main__":
    main()
