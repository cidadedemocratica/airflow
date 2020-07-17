import dash
import dash_core_components as dcc
import dash_html_components as html
from components.comments import CommentsComponent
from components.votes import VotesComponent
from components.analytics import AnalyticsComponent
from dash.dependencies import Input, Output

from dateutil.parser import *
from dateutil.tz import *
import datetime
from datetime import date


class App():

    def __init__(self):
        self.app = dash.Dash(
            __name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        self.votes_component = VotesComponent(self.app)
        self.comments_component = CommentsComponent(self.app)
        self.analytics_component = AnalyticsComponent(self.app)

    def render(self):
        self.app.layout = html.Div(style={'background-color': '#DBDDDF'}, children=[
            html.Div(style={'background': 'white', 'height': '5rem', 'fontSize': '3rem'},
                     children="Dashboard"),
            html.Div(style={"width": "90%", "margin": "30px auto", 'background-color': '#DBDDDF'}, children=[
                html.Div(style={}, children=[
                    self.analytics_component.render(),
                ]),
                html.Div(style={}, children=[
                    self.votes_component.render(),
                ]),
                self.comments_component.render()
            ])])
