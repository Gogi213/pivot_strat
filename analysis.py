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









# Функция для отслеживания позиции (закомментирована для будущего использования)
# def emulate_position_tracking(df, breakout_candles, nATR_column='nATR'):
#     results = []
#     for pair, breakout_idx in breakout_candles:
#         test_price = pair[1][1]  # Цена нижнего теста
#         nATR_value = df.at[breakout_idx, nATR_column]
#         tp = test_price + test_price * nATR_value
#         sl = test_price - test_price * (nATR_value / 2)
#         outcome = None
#         profit_loss = 0
#         for i in range(breakout_idx + 1, len(df)):
#             high_price = df.at[i, 'High']
#             low_price = df.at[i, 'Low']
#             if high_price >= tp:
#                 outcome = 'Successful'
#                 profit_loss = nATR_value * 100
#                 break
#             elif low_price <= sl:
#                 outcome = 'Unsuccessful'
#                 profit_loss = (-nATR_value / 2) * 100
#                 break
#         results.append({
#             'setup': pair,
#             'breakout_idx': breakout_idx,
#             'outcome': outcome,
#             'profit_loss': profit_loss
#         })
#     return results
