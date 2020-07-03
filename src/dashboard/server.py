# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output

from comments import ej_comments, generate_table_body, generate_table
from votes import Votes

votes = Votes()
votes.get()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


order_options = ['comentário_id', 'concorda', 'discorda', 'pulados']
visualization = html.Div(
    children=[
        html.Div(style={"display": "flex", "width": "20%"}, children=[
            html.Span(style={"marginRight": 8},
                      children="Participação acima de:"),
            dcc.Input(
                id='participation',
                value='50',
                style={"flexGrow": 1}
            ),
        ]),
        html.Div(style={"display": "flex", "width": "30%"}, children=[
            html.Span(style={"marginRight": 8},  children="Ordenar por:"),
            dcc.Dropdown(
                id='_filter',
                options=[{'label': i, 'value': i} for i in order_options],
                value='Fertility rate, total (births per woman)',
                style={"flexGrow": 1}
            ),
        ]),
        generate_table(ej_comments)
    ])


@app.callback(
    Output("table_body", 'children'),
    [Input('_filter', 'value'), Input('participation', 'value')])
def order_table(_filter, participation):
    print(_filter, participation)
    df = None
    if(participation):
        df = ej_comments[ej_comments['participação']
                         >= int(participation) / 100]
    else:
        df = ej_comments

    if(_filter in order_options):
        ordered_df = df.sort_values(by=_filter, ascending=False)
        return generate_table_body(ordered_df)
    else:
        return generate_table_body(df)


app.layout = html.Div(style={'background-color': '#DBDDDF'}, children=[
    html.Div(style={'background': 'white', 'height': '5rem', 'fontSize': '3rem'},
             children="Dashboard"),
    html.Div(style={"width": "90%", "margin": "30px auto", 'background-color': '#DBDDDF'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
            html.Div(style={'width': '49%'}, children=[
                html.Div(style={"textAlign": "center", "backgroundColor": "#042a46", "color": "white", "height": "40px"},
                         children=[html.Div(style={"position": "relative", "top": "20%"}, children=[
                                            'Aquisição Qualificada'])]),
                html.Div(children=[
                    html.Div(style={'flexGrow': 1, 'background-color': 'white'}, children=[
                        dcc.Graph(figure=votes.get_figure())
                    ]),
                ])
            ]),
            html.Div(style={'width': '49%'}, children=[
                html.Div(style={"textAlign": "center", "backgroundColor": "#042a46", "color": "white", "height": "40px"},
                         children=[html.Div(style={"position": "relative", "top": "20%"}, children=[
                             'Visitas x Aquisição EJ (Taxa de aquisição)'])]),
                html.Div(children=[
                    html.Div(style={'flexGrow': 1, 'background-color': 'white'}, children=[
                        dcc.Graph(figure=votes.get_figure())
                    ]),
                ])
            ]),
        ]),
        html.Div(style={'background-color': 'white', 'marginTop': '15px'}, children=[
            html.Div(style={"textAlign": "center", "backgroundColor": "#042a46", "color": "white", "height": "40px"},
                     children=[html.Div(style={"position": "relative", "top": "20%"}, children=[
                         'Votos e participação em todos os comentários, excluíndo os comentários que foram rejeitados para moderação.'])]),
            html.Div(style={'width': '90%', 'margin': '20px auto'}, children=[
                visualization
            ])
        ]),
    ])])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')