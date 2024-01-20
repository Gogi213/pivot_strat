from dash import html, dcc, Input, Output, dash_table
import dash
from binance_api import get_top_futures_pairs, get_historical_futures_data
import plot
from analysis import find_pivot_high, find_pivot_low, calculate_ema_osc, emulate_trading
import pandas as pd
import json
import os

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

    # Получение данных о сделках
    trades = emulate_trading(df, 100, 1, 'nATR')

    # Отрисовка графика с маркерами сделок
    graph = plot.plot_support_resistance_with_annotations(df, pivot_highs, pivot_lows, trades, symbol)

    # Расчет статистики торговли
    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    successful_trades = len(trades_df[trades_df['pnl'] > 0])
    unsuccessful_trades = total_trades - successful_trades
    winrate = successful_trades / total_trades if total_trades > 0 else 0
    total_profit = trades_df['pnl'].sum()
    profit_factor = total_profit / -trades_df[trades_df['pnl'] < 0]['pnl'].sum() if unsuccessful_trades > 0 else 'inf'

    # Создание таблицы статистики
    table = html.Div([
        html.Div(f"Всего сделок: {total_trades}", className="table-stat"),
        html.Div(f"Успешных сделок: {successful_trades}", className="table-stat"),
        html.Div(f"Неуспешных сделок: {unsuccessful_trades}", className="table-stat"),
        html.Div(f"Winrate: {winrate:.2%}", className="table-stat"),
        html.Div(f"Доход: {total_profit}", className="table-stat"),
        html.Div(f"Профит фактор: {profit_factor}", className="table-stat")
    ], className="statistics-table")

    return [graph, table]



# def read_and_combine_cached_data(cache_folder_path):
#     combined_df = pd.DataFrame()
#     for filename in os.listdir(cache_folder_path):
#         if filename.endswith('.json'):
#             file_path = os.path.join(cache_folder_path, filename)
#             with open(file_path, 'r') as file:
#                 data = json.load(file)
#                 df = pd.DataFrame(data)
#                 combined_df = pd.concat([combined_df, df], ignore_index=True)
#
#     # Сохранение в JSON
#     combined_df.to_json('combined_data.json', orient='records', lines=True)
#     return combined_df
#
#
# @app.callback(
#     Output('content-tab-2', 'children'),
#     [Input('update-button', 'n_clicks')]
# )
# def update_combined_table(n_clicks):
#     if n_clicks is None:
#         raise dash.exceptions.PreventUpdate
#
#     cache_folder_path = 'C:/Users/Redmi/PycharmProjects/pivot_strat/cache'
#     combined_data = read_and_combine_cached_data(cache_folder_path)
#     all_trades = emulate_trading_for_all(combined_data, 100, 1)
#
#     # Преобразование результатов торговли в DataFrame для отображения в таблице
#     trades_df = pd.DataFrame(all_trades)
#     return dash_table.DataTable(
#         data=trades_df.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in trades_df.columns]
#     )