# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output

from comments import ej_comments

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def generate_table_body(dataframe):
    trs = []
    for index in range(len(dataframe)):
        tds = []
        for col in dataframe.columns:
            if(col == "compilado"):
                bar = html.Div(
                    style={},
                    children=[
                        html.Div(style={'borderStyle': 'solid', 'borderColor': 'black', 'width': '100px', 'height': 30, 'display': 'flex'}, children=[
                            html.Div(style={'backgroundColor': 'green', 'width': dataframe.iloc[index]['concorda'], 'height': 30}),
                            html.Div(style={'backgroundColor': 'red', 'width': dataframe.iloc[index]['discorda'], 'height': 30}),
                            html.Div(style={'backgroundColor': 'yellow', 'width': dataframe.iloc[index]['pulados'], 'height': 30})
                        ]),
                        html.Div(style={}, children=[
                            html.Span(style={'color': 'green', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['concorda'])) + '%'),
                            html.Span(style={'color': 'red', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['discorda'])) + '%'),
                            html.Span(style={'color': 'yellow', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['pulados'])) + '%'),
                        ]),
                    ],
                )
                tds.append(html.Td(bar))
            elif((col != "concorda") and (col != "discorda") and (col != "pulados")):
                tds.append(html.Td(dataframe.iloc[index][col]))
        trs.append(html.Tr(tds))
    return trs;

def generate_table(dataframe):
    ths = []
    trs = []
    for col in dataframe.columns:
        if((col != 'concorda') and (col != 'discorda') and (col != 'pulados')):
            ths.append(html.Th(col))
    trs = generate_table_body(dataframe)
    return html.Table([
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                trs, id="table_body"
            )
        ])


order_options = ['comentário_id', 'concorda', 'discorda', 'pulados']
visualization = html.Div(
    children=[
            dcc.Dropdown(
            id='filter',
            options=[{'label': i, 'value': i} for i in order_options],
            value='Fertility rate, total (births per woman)'
        ),
        generate_table(ej_comments)
    ])

@app.callback(
    Output("table_body", component_property='children'),
    [Input('filter', 'value')])
def order_table(value):
    if(value in order_options):
        ordered_df = ej_comments.sort_values(by=value, ascending=False)
        return generate_table_body(ordered_df)
    else:
        return generate_table_body(ej_comments)

app.layout = html.Div(children=[
    html.Span(children='Votos e participação em todos os comentários, excluíndo os comentários que foram rejeitados para moderação.'),
    visualization
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
