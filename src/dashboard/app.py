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
        self.app = dash.Dash(__name__)

    def render(self):
        self.votes_component = VotesComponent(self.app)
        self.comments_component = CommentsComponent(self.app)
        self.analytics_component = AnalyticsComponent(self.app)
        self.app.layout = html.Div(children=[
            html.Nav(
                className="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow", children=[
                    html.Img(src="./assets/logo-ej-mini.png"),
                    html.Div(style={"marginLeft": "5px"},
                             children=[html.Span("Bem vinda!")])
                ]),
            html.Div(style={"width": "90%", "margin": "auto"}, children=[
                html.Div(style={}, children=[
                    self.analytics_component.render(),
                ]),
                html.Div(style={}, children=[
                    self.votes_component.render(),
                ]),
                self.comments_component.render()
            ])])
