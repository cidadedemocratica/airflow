import datetime
import urllib.parse
from datetime import date

import pandas as pd
from dateutil.parser import *
from dateutil.tz import *

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from services.analytics import AnalyticsService
from components.utils.export import ExportsComponent


class AnalyticsComponent():
    """
        AnalyticsComponent represents a Dash component. This component will
        show a bubble Chart with some analytics filters.
    """

    def __init__(self, app):
        self.app = app
        self.service = AnalyticsService()
        self.export_component = ExportsComponent("analytics")
        self.df = self.service.df
        self.ej_users_count = 1
        self.analytics_users_count = 1
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []
        self.prepare()

    def prepare(self):
        try:
            self.set_default_filter()
            self.register_callbacks()
        except Exception as err:
            print(f"Error: {err}")

    def render(self):
        """
            Main entrypoint to create a Dash visualization.
            render will show a plotly figure and the figure's filters.
        """
        if(not self.df.empty):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Engajamento vs Aquisição (EJ)']),
                        html.Div(className="card-body", children=[
                            html.Div(style={"display": "flex"}, children=[
                                html.Div(children=[
                                    self.get_filters_ui(self.df),
                                    html.Hr(),
                                    self.export_component.render(),
                                ]),
                                html.Div(id="filters",
                                         style={"flexGrow": 1, "width": "60%"}, children=[
                                            self.get_figure(self.df)
                                         ])
                            ])
                        ])
                    ])
                ])
            ])
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                    html.Div(className="card-header", children=[
                        'Engajamento vs Aquisição (EJ)']),
                    html.Div(className="card-body",
                             children=["Não há dados para apresentar"])
                ])
            ])
        ])

    def get_filters_ui(self, new_df):
        self.service.set_filters_options(self, new_df)
        return html.Div(style={"flexGrow": "2"}, children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_source:"),
                    dcc.Dropdown(
                        id='campaign_source',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_source_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_medium:"),
                    dcc.Dropdown(
                        id='campaign_medium',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_medium_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_campaign:"),
                    dcc.Dropdown(
                        id='campaign_name',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_campaign_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Período:"),
                    dcc.DatePickerRange(
                        id='by_date',
                        style={"flexGrow": 1},
                    ),
                ])
                ]),
            ])
        ],
        )

    def get_figure(self, df=pd.DataFrame({})):
        if(df.empty):
            df = self.df
        fig = go.Figure(layout={'title': {'text': '', 'x': 0.5,
                                          'font': {'size': 16, 'color': '#ff3e72', 'family': 'Times New Roman'}},
                                'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'plot_bgcolor': "#ffffff",
                                'legend': {
            'font': {'size': 15, 'color': '#000'},
                                    'y': 0.8
        },
            'annotations': [
            {
                'x': '-50',
                'y': '50',
                'text': f'<b>{round((self.ej_users_count/self.analytics_users_count) * 100,2) }%</b>',
                'font': {'color': '#fff', 'size': 15},
                'align': 'center',
                'showarrow': False
            },
            {
                'x': '-50',
                'y': '50',
                'yshift': 90,
                'text': f'<b>{self.analytics_users_count} visitantes</b>',
                'font': {'color': '#fff', 'size': 15},
                'showarrow': False
            }
        ]
        }
        )
        fig.add_trace(go.Scatter(
            x=[-50], y=[50],
            mode='markers',
            marker=dict(
                size=[300],
                color='#30bfd3',
                sizeref=1.1,
            ),
            name="Visitas na pagina da conversa (/opiniao)")
        )
        fig.add_trace(go.Scatter(
            x=[-50], y=[50],
            mode='markers',
            marker=dict(
                size=[(300 / self.analytics_users_count)
                      * self.ej_users_count],
                color='#C4F2F4',
                sizeref=1.1,
                maxdisplayed=1),
            name="Visitas que participaram da conversa",
        )
        )
        return html.Div(children=[
            dcc.Graph(figure=fig)
        ])

    def register_callbacks(self):
        @self.app.callback(
            Output("analytics_download_export", 'href'),
            [Input('analytics_exports_df', 'n_clicks')]
        )
        def export_callback(export_df):
            return self.export_component.export(self.df)

        @self.app.callback(
            Output("filters", 'children'),
            [Input('campaign_source', 'value'),
                Input('campaign_name', 'value'),
                Input('campaign_medium', 'value'),
                Input('by_date', 'start_date'),
                Input('by_date', 'end_date'),
             ])
        def filter_callbacks(campaign_source,
                             campaign_name,
                             campaign_medium,
                             start_date,
                             end_date):
            if(self.df.empty):
                return
            if(not campaign_source and
               not campaign_name and
               not campaign_medium and
               not start_date and not end_date):
                self.set_default_filter()
            if(campaign_source and len(campaign_source) >= 3):
                self.set_campaign_source_filter(
                    campaign_source)
            elif(campaign_name and len(campaign_name) >= 3):
                self.set_campaign_name_filter(
                    campaign_name)
            elif(campaign_medium and len(campaign_medium) >= 3):
                self.set_campaign_medium_filter(
                    campaign_medium)
            elif(start_date and end_date):
                self.set_campaign_date_range_filter(datetime.datetime.fromisoformat(start_date).date(),
                                                    datetime.datetime.fromisoformat(end_date).date())
            return self.get_figure(self.df)

    def set_default_filter(self):
        self.ej_users_count = len(self.df['email'].value_counts())
        self.analytics_users_count = self.service.filter_by_analytics({})

    def set_campaign_source_filter(self, campaign):
        analytics_filter = self.service.get_campaign_filter(campaign)
        self.df = self.df[self.df['analytics_source'] == campaign]
        self.count_users(analytics_filter)

    def set_campaign_name_filter(self, campaign):
        analytics_filter = self.service.get_name_filter(campaign)
        self.df = self.df[self.df['analytics_campaign'] == campaign]
        self.count_users(analytics_filter)

    def set_campaign_medium_filter(self, campaign):
        analytics_filter = self.service.get_medium_filter(campaign)
        self.df = self.df[self.df['analytics_medium'] == campaign]
        self.count_users(analytics_filter)

    def count_users(self, analytics_filter):
        self.analytics_users_count = self.service.filter_by_analytics(
            analytics_filter)
        self.ej_users_count = int(
            len(self.df['email'].value_counts()))

    def set_campaign_date_range_filter(self, start_date, end_date):
        analytics_filter = self.service.get_date_filter(start_date, end_date)
        self.analytics_users_count = self.service.filter_by_analytics(
            analytics_filter)
        self.ej_users_count = int(len(self.service.dataframe_between_dates(
            self.df, start_date, end_date)))
