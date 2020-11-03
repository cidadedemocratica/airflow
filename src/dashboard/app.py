import dash
import dash_core_components as dcc
import dash_html_components as html
from components.comments.component import CommentsComponent
from components.votes.component import VotesComponent
from components.analytics.component import AnalyticsComponent
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
                className="navbar navbar-light bg-white topbar mb-4 static-top shadow", children=[
                    html.Img(src="./assets/logo-ej-mini.png"),
                    html.Button(className='dash-icon', children=[html.I(className='fa fa-repeat')],
                                id='app_reload', n_clicks=0),
                ]),
            html.Div(id="app",
                     style={"width": "90%", "margin": "auto"},
                     children=[
                         html.Div(id="app_loader",
                                  children=self._app_root(self.analytics_component,
                                                          self.votes_component, self.comments_component))

                     ])
        ])

    def _app_root(self, analytics_component, votes_component, comments_component):
        return [html.Div(style={}, children=[
            analytics_component.render(),
        ]),
            html.Div(style={}, children=[
                votes_component.render(),
            ]), comments_component.render()]
