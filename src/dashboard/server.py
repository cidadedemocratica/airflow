# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from comments import ej_comments

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def generate_table(dataframe, max_rows=10):
    ths = []
    trs = []
    for col in dataframe.columns:
        ths.append(html.Th(col))
    for index in range(min(len(dataframe), max_rows)):
        tds = []
        for col in dataframe.columns:
            if(col == "compilado"):
                bar = html.Div(style={'border-style': 'solid', 'border-color': 'black', 'width': '100px', 'height': 30, 'display': 'flex'}, children=[html.Div(style={'background-color': 'green', 'width': dataframe.iloc[index]['concorda'], 'height': 30}), html.Div(style={'background-color': 'red', 'width': dataframe.iloc[index]['discorda'], 'height': 30}), html.Div(style={'background-color': 'yellow', 'width': dataframe.iloc[index]['pulados'], 'height': 30})])
                tds.append(html.Td(bar))
            else:
                tds.append(html.Td(dataframe.iloc[index][col]))
        trs.append(html.Tr(tds))


    print(trs)
    return html.Table([
        html.Thead(
            html.Tr(ths)
        ),
        html.Tbody(
            trs
        )
    ])

app.layout = html.Div(children=[
    html.Span(children='Votos e participação em todos os comentários, excluíndo os comentários que foram rejeitados para moderação.'),
    generate_table(ej_comments)
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
