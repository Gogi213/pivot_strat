# plot.py
import logging
from dash import html, dcc
from plotly.subplots import make_subplots
logging.basicConfig(level=logging.INFO)
import plotly.graph_objects as go

def plot_support_resistance_with_annotations(df, pivot_highs, pivot_lows, trades, symbol):

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(symbol, 'sub'),
                        row_heights=[0.7, 0.3])

    # Добавление свечного графика
    candlestick = go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'])
    fig.add_trace(candlestick, row=1, col=1)

    # Отображение горизонтальных линий для pivot highs и pivot lows
    for high in pivot_highs:
        if high[1] is not None:
            fig.add_shape(type='line',
                          x0=high[0], y0=high[1], x1=df.index[min(len(df)-1, df.index.get_loc(high[0]) + 5)], y1=high[1],
                          line=dict(color='Green',),
                          xref='x', yref='y',
                          row=1, col=1)

    for low in pivot_lows:
        if low[1] is not None:
            fig.add_shape(type='line',
                          x0=low[0], y0=low[1], x1=df.index[min(len(df)-1, df.index.get_loc(low[0]) + 5)], y1=low[1],
                          line=dict(color='Red',),
                          xref='x', yref='y',
                          row=1, col=1)

    # Добавление маркеров для сделок
    for trade in trades:
        entry_color = 'blue'  # Цвет маркера входа в сделку
        exit_color = 'red' if trade['is_profitable'] else 'green'  # Цвет маркера выхода из сделки

        # Маркер входа
        fig.add_trace(go.Scatter(
            x=[df.index[trade['entry_index']]],
            y=[trade['entry']],
            marker=dict(color=entry_color, size=10),
            mode='markers',
            name='Вход в позицию'
        ))

        # Маркер выхода
        fig.add_trace(go.Scatter(
            x=[df.index[trade['exit_index']]],
            y=[trade['exit']],
            marker=dict(color=exit_color, size=10),
            mode='markers',
            name='Выход из позиции'
        ))

    # Обновление макета графика
    fig.update_layout(
        height=800, width=1200, title_text="График",
        showlegend=False,
        margin=dict(l=50, r=50, b=100, t=100, pad=4)
    )
    fig.update_xaxes(title_text="Дата")
    fig.update_yaxes(title_text="Цена")

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