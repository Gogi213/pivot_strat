# dash_app.py
from dash import html, dcc, Input, Output
import dash
from binance_api import get_top_futures_pairs, get_historical_futures_data
import plot
from analysis import find_pivot_high, find_pivot_low, calculate_ema_osc, emulate_trading
import pandas as pd
import os
import json

app = dash.Dash(__name__, suppress_callback_exceptions=True)

volume_threshold = 100000000
symbols = get_top_futures_pairs(volume_threshold=volume_threshold)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Чарт', children=[
            plot.create_layout_with_graph_and_list(symbols, symbols[0]),
            html.Div(id='breakout-statistics-table')  # Место для таблицы статистики
        ]),
        dcc.Tab(label='Сводка таблиц', children=[
            html.Button('Обновить данные', id='update-button'),
            html.Div(id='content-tab-2')  # Контейнер для общей таблицы статистики
        ])
    ])
])


@app.callback(
    [Output('currency-pair-graph', 'figure'),
     Output('breakout-statistics-table', 'children')],
    [Input(symbol, 'n_clicks') for symbol in symbols]
)
def update_graph_and_table(*args):
    ctx = dash.callback_context

    if not ctx.triggered:
        symbol = symbols[0]
    else:
        symbol = ctx.triggered[0]['prop_id'].split('.')[0]

    df = get_historical_futures_data(symbol)
    calculate_ema_osc(df)
    pivot_highs = find_pivot_high(df, left_bars=100, right_bars=1)
    pivot_lows = find_pivot_low(df, left_bars=100, right_bars=1)

    graph = plot.plot_support_resistance_with_annotations(df, pivot_highs, pivot_lows, symbol)

    # Вызов функции эмуляции торговли и расчет статистики
    trades = emulate_trading(df, 100, 1, 'nATR')
    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    successful_trades = len(trades_df[trades_df['pnl'] > 0])
    unsuccessful_trades = total_trades - successful_trades
    winrate = successful_trades / total_trades if total_trades > 0 else 0
    total_profit = trades_df['pnl'].sum()
    profit_factor = total_profit / -trades_df[trades_df['pnl'] < 0]['pnl'].sum() if unsuccessful_trades > 0 else 'inf'

    # Создание компактной таблицы статистики
    table = html.Div([
        html.Div(f"Всего сделок: {total_trades}", className="table-stat"),
        html.Div(f"Успешных сделок: {successful_trades}", className="table-stat"),
        html.Div(f"Неуспешных сделок: {unsuccessful_trades}", className="table-stat"),
        html.Div(f"Winrate: {winrate:.2%}", className="table-stat"),
        html.Div(f"Доход: {total_profit}", className="table-stat"),
        html.Div(f"Профит фактор: {profit_factor}", className="table-stat")
    ], className="statistics-table")

    return [graph, table]



# Функция для чтения и объединения данных из JSON файлов
def read_and_combine_json_data(cache_folder):
    all_files = [os.path.join(cache_folder, file) for file in os.listdir(cache_folder) if file.endswith('.json')]
    df_list = []
    for file in all_files:
        with open(file, 'r') as f:
            data = json.load(f)
            df_list.append(pd.DataFrame(data))
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

# Callback для обновления второй вкладки
@app.callback(
    Output('content-tab-2', 'children'),
    [Input('update-button', 'n_clicks')]
)
def update_overall_statistics(n_clicks):
    cache_folder = 'C:/Users/Redmi/PycharmProjects/pivot_strat/cache'
    combined_df = read_and_combine_json_data(cache_folder)

    # Расчет статистики для combined_df
    total_trades = len(combined_df)
    successful_trades = len(combined_df[combined_df['pnl'] > 0])
    unsuccessful_trades = total_trades - successful_trades
    winrate = successful_trades / total_trades if total_trades > 0 else 0
    total_profit = combined_df['pnl'].sum()
    profit_factor = total_profit / -combined_df[combined_df['pnl'] < 0]['pnl'].sum() if unsuccessful_trades > 0 else 'inf'

    # Создание таблицы статистики
    overall_table = html.Div([
        html.Div(f"Всего сделок: {total_trades}", className="table-stat"),
        html.Div(f"Успешных сделок: {successful_trades}", className="table-stat"),
        html.Div(f"Неуспешных сделок: {unsuccessful_trades}", className="table-stat"),
        html.Div(f"Winrate: {winrate:.2%}", className="table-stat"),
        html.Div(f"Доход: {total_profit}", className="table-stat"),
        html.Div(f"Профит фактор: {profit_factor}", className="table-stat")
    ], className="overall-statistics-table")

    return overall_table


