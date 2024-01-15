# plot.py
import logging
from dash import html, dcc
from plotly.subplots import make_subplots
logging.basicConfig(level=logging.INFO)
import plotly.graph_objects as go

def plot_support_resistance_with_annotations(df, pivot_highs, pivot_lows, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(symbol, 'nATR'),
                        row_heights=[0.7, 0.3])

    # Добавление свечного графика
    candlestick = go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'])
    fig.add_trace(candlestick, row=1, col=1)

    # Добавление графика nATR
    fig.add_trace(go.Bar(x=df.index, y=df['nATR'], marker_color='blue'), row=2, col=1)

    # Отображение горизонтальных линий для pivot highs
    last_high = None
    for high in pivot_highs:
        if high[1] is not None and high[1] != last_high:
            fig.add_shape(type='line',
                          x0=high[0], y0=high[1], x1=df.index[min(len(df)-1, df.index.get_loc(high[0]) + 35)], y1=high[1],
                          line=dict(color='Green',),
                          xref='x', yref='y',
                          row=1, col=1)
            last_high = high[1]

    # Отображение горизонтальных линий для pivot lows
    last_low = None
    for low in pivot_lows:
        if low[1] is not None and low[1] != last_low:
            fig.add_shape(type='line',
                          x0=low[0], y0=low[1], x1=df.index[min(len(df)-1, df.index.get_loc(low[0]) + 35)], y1=low[1],
                          line=dict(color='Red',),
                          xref='x', yref='y',
                          row=1, col=1)
            last_low = low[1]

    # Обновление макета графика
    fig.update_layout(
        height=800, width=1200, title_text="График с nATR",
        showlegend=False,
        margin=dict(l=50, r=50, b=100, t=100, pad=4)
    )
    fig.update_xaxes(title_text="Дата", row=2, col=1)
    fig.update_yaxes(title_text="Цена", row=1, col=1)
    fig.update_yaxes(title_text="nATR", row=2, col=1)

    return fig


def create_layout_with_graph_and_list(symbols, selected_symbol):
    graph = dcc.Graph(id='currency-pair-graph', style={'height': '100vh'})  # Задаем высоту графика
    symbol_list = html.Ul(
        [html.Li(symbol, id=symbol, className='symbol-item', n_clicks=0) for symbol in symbols],
        style={'list-style-type': 'none', 'padding': '0'}  # Убираем маркеры списка и отступы
    )

    layout = html.Div([
        html.Div(graph, style={'width': '90%', 'display': 'inline-block'}),
        html.Div(symbol_list, style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '100px'})
    ], style={'display': 'flex', 'height': '100vh'})

    return layout

# def create_breakout_statistics_table(df, breakout_candles, symbol):
#     # Получение результатов эмуляции
#     # results = emulate_position_tracking(df, breakout_candles)
#
#     # Сбор статистики
#     total_breakouts = len(results)
#     successful_breakouts = sum(1 for result in results if result['outcome'] == 'Successful')
#     unsuccessful_breakouts = total_breakouts - successful_breakouts
#     win_rate = successful_breakouts / total_breakouts if total_breakouts > 0 else 0
#     sum_nATR_successful = sum(result['profit_loss'] for result in results if result['outcome'] == 'Successful')
#     sum_nATR_unsuccessful = sum(result['profit_loss'] for result in results if result['outcome'] == 'Unsuccessful')
#     total_sum = sum_nATR_successful + sum_nATR_unsuccessful
#
#     # Создание таблицы
#     fig = go.Figure(data=[go.Table(
#         header=dict(values=['Валютная пара', 'Количество пробоев', 'Успешные', 'Неуспешные', 'Винрейт', 'Сумма nATR успешных', 'Сумма nATR/2 неуспешных', 'Сумма двух предыдущих пунктов']),
#         cells=dict(values=[[symbol], [total_breakouts], [successful_breakouts], [unsuccessful_breakouts], [f"{win_rate:.2%}"], [sum_nATR_successful], [sum_nATR_unsuccessful], [total_sum]])
#     )])
#
#     return fig