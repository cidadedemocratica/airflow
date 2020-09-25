import dash
import dash_core_components as dcc
import dash_html_components as html
from components.comments import CommentsComponent
from components.votes import VotesComponent
from components.analytics import AnalyticsComponent
from dash.dependencies import Input, Output
import time

from dateutil.parser import *
from dateutil.tz import *
import datetime
from datetime import date


app = dash.Dash(__name__)


@app.callback(
    Output("app_loader1", 'children'),
    [Input("app_reload", 'n_clicks')]
)
def callback1(app_reload):
    time.sleep(2)
    return html.Div('result 1')


@app.callback(
    Output("app_loader2", 'children'),
    [Input("app_reload", 'n_clicks')]
)
def callback2(app_reload):
    time.sleep(2)
    return html.Div('result 2')


app.layout = html.Div(children=[

    html.Button('clique aqui', id='app_reload', n_clicks=0),
    dcc.Loading(id="app_loader1", children=[
        html.Div('loader 1')
    ]),
    dcc.Loading(id="app_loader2", children=[
        html.Div('loader 2')
    ])])


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
