# dash_app.py
from dash import html, dcc, Input, Output
import dash
from binance_api import get_top_futures_pairs, get_historical_futures_data
import plot
from analysis import find_pivot_high, find_pivot_low, calculate_ema_osc

app = dash.Dash(__name__)

volume_threshold = 150000000
symbols = get_top_futures_pairs(volume_threshold=volume_threshold)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Чарт', children=[
            plot.create_layout_with_graph_and_list(symbols, symbols[0]),
            # Убрана таблица статистики, так как соответствующая функция закомментирована
            # html.Div(id='breakout-statistics-table')
        ]),
        dcc.Tab(label='Сводка таблиц', children=[
            html.Div(id='content-tab-2')
        ])
    ])
])

@app.callback(
    [Output('currency-pair-graph', 'figure')],
    [Input(symbol, 'n_clicks') for symbol in symbols]
)
def update_graph(*args):
    ctx = dash.callback_context

    if not ctx.triggered:
        symbol = symbols[0]
    else:
        symbol = ctx.triggered[0]['prop_id'].split('.')[0]

    df = get_historical_futures_data(symbol)
    calculate_ema_osc(df)  # Расчёт EMA и осциллятора объёма
    pivot_highs = find_pivot_high(df, left_bars=100, right_bars=1)
    pivot_lows = find_pivot_low(df, left_bars=100, right_bars=1)

    # Создание графика
    graph = plot.plot_support_resistance_with_annotations(df, pivot_highs, pivot_lows, symbol)

    return [graph]  # Оборачиваем график в список


