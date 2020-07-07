import dash
import dash_core_components as dcc
import dash_html_components as html
from comments import Comments
from votes import Votes
from dash.dependencies import Input, Output


class App():

    def __init__(self):
        self.votes = Votes()
        self.comments = Comments()
        self.votes.read()
        self.comments.read()
        self.app = dash.Dash(
            __name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

    def create(self):
        self.app.layout = html.Div(style={'background-color': '#DBDDDF'}, children=[
            html.Div(style={'background': 'white', 'height': '5rem', 'fontSize': '3rem'},
                     children="Dashboard"),
            html.Div(style={"width": "90%", "margin": "30px auto", 'background-color': '#DBDDDF'}, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
                    self.votes.get_html(),
                    self.votes.get_html()
                ]),
                self.comments.get_html()
            ])])

    def callbacks(self):
        @self.app.callback(
            Output("table_body", 'children'),
            [Input('_filter', 'value'), Input('participation', 'value')])
        def table_callback(_filter, participation):
            df = self.comments.df
            if(participation):
                df = df[df['participação'] >= int(participation) / 100]
            if(_filter in self.comments.order_options):
                df = df.sort_values(by=_filter, ascending=False)
                return self.comments.generate_table_body(df)
            return self.comments.generate_table_body(df)
