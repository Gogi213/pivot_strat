# analysis.py
import pandas as pd

# Функции для расчета точек разворота
def find_pivot_high(df, left_bars, right_bars):
    highs = []
    for i in range(left_bars, len(df) - right_bars):
        high_range = df['High'][i-left_bars:i+right_bars+1]
        current_high = df['High'][i]
        if current_high == max(high_range) and (high_range == current_high).sum() == 1:
            highs.append((df.index[i], current_high))
        else:
            highs.append((df.index[i], None))
    return highs

def find_pivot_low(df, left_bars, right_bars):
    lows = []
    for i in range(left_bars, len(df) - right_bars):
        low_range = df['Low'][i-left_bars:i+right_bars+1]
        current_low = df['Low'][i]
        if current_low == min(low_range) and (low_range == current_low).sum() == 1:
            lows.append((df.index[i], current_low))
        else:
            lows.append((df.index[i], None))
    return lows


def calculate_ema_osc(df):
    short_ema = df['Volume'].ewm(span=5, adjust=False).mean()
    long_ema = df['Volume'].ewm(span=10, adjust=False).mean()
    df['osc'] = 100 * (short_ema - long_ema) / long_ema


def plot_breaks(df, fig, pivot_highs, pivot_lows, volume_thresh):
    for i in range(len(df)):
        if df['Close'][i] > pivot_highs[i][1] and df['osc'][i] > volume_thresh:
            # Добавить метку пробоя сопротивления
            fig.add_annotation(x=df.index[i], y=df['Close'][i],
                               text="Break", showarrow=True,
                               arrowhead=1, yshift=10)
        elif df['Close'][i] < pivot_lows[i][1] and df['osc'][i] > volume_thresh:
            # Добавить метку пробоя поддержки
            fig.add_annotation(x=df.index[i], y=df['Close'][i],
                               text="Break", showarrow=True,
                               arrowhead=1, yshift=-10)
    return fig

def calculate_tp(price, nATR):
    return price + (price * 2 * nATR)

def calculate_sl(price, nATR):
    return price - (price * (nATR / 2))


def emulate_trading(df, left_bars, right_bars, nATR_column='nATR'):
    trades = []
    pivot_highs = find_pivot_high(df, left_bars, right_bars)
    pivot_lows = find_pivot_low(df, left_bars, right_bars)

    for i in range(2, len(df)):
        # Проверка условий для входа в позицию
        if pivot_highs[i - 2][1] is not None and df['Close'][i - 1] < df['Open'][i - 1]:
            # Логика для шорт позиции
            entry_price = df['Open'][i]  # Вход по открытию следующей свечи
            tp = calculate_sl(entry_price, df[nATR_column][i - 2])  # Используем SL как TP для шорта
            sl = calculate_tp(entry_price, df[nATR_column][i - 2])  # Используем TP как SL для шорта

        elif pivot_lows[i - 2][1] is not None and df['Close'][i - 1] > df['Open'][i - 1]:
            # Логика для лонг позиции
            entry_price = df['Open'][i]  # Вход по открытию следующей свечи
            tp = calculate_tp(entry_price, df[nATR_column][i - 2])
            sl = calculate_sl(entry_price, df[nATR_column][i - 2])

        else:
            continue

        # Отслеживание позиции и определение выхода
        for j in range(i + 1, len(df)):
            if df['High'][j] >= tp or df['Low'][j] <= sl:
                exit_price = df['Close'][j]  # Выход по закрытию свечи
                profit_or_loss = exit_price - entry_price
                trades.append({'entry': entry_price, 'exit': exit_price, 'pnl': profit_or_loss})
                break

    return trades



