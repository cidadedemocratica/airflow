import dash_html_components as html
import dash_core_components as dcc
from components.utils.date_picker import *
from dash.dependencies import Input, Output
import pandas as pd


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter AnalyticsComponent data.
    """

    def __init__(self, service, app, analytics_component, export_component):
        self.service = service
        self.app = app
        self.df = self.service.df
        self.analytics_component = analytics_component
        self.export_component = export_component
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []
        self.start_date = None
        self.end_date = None
        self.set_filters_options()
        self.set_filters_callbacks()

    def render(self):
        """
            Main entrypoint to add filters to AnalyticsComponent.
        """
        return html.Div(children=[
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
                        clearable=True,
                        style={"flexGrow": 1},
                         end_date=self.end_date[0],
                         start_date=self.start_date[0]
                         ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children=f"Paginas analisadas: {(self.service.page_path).replace('ga:pagePath=@', ' ')}"),
                ])
                ]),
            ])
        ],
        )

    def set_filters_options(self):
        self.end_date = self.service.get_default_end_date(),
        self.start_date = self.service.get_default_start_date(),
        self.utm_source_options = self.df['analytics_source'].value_counts(
        ).keys()
        self.utm_medium_options = self.df['analytics_medium'].value_counts(
        ).keys()
        self.utm_campaign_options = self.df['analytics_campaign'].value_counts(
        ).keys()

    def set_filters_callbacks(self):
        @self.app.callback(
            Output("analytics_loader", 'children'),
            [Input('campaign_source', 'value'),
                Input('campaign_name', 'value'),
                Input('campaign_medium', 'value'),
                Input('by_date', 'start_date'),
                Input('by_date', 'end_date'),
                Input('app_reload', 'n_clicks'),
             ])
        def filter_callbacks(campaign_source,
                             campaign_name,
                             campaign_medium,
                             start_date,
                             end_date,
                             app_reload):

            if(self.df.empty):
                return

            self.start_date = start_date
            self.end_date = end_date
            self.reload_data_from_disk(app_reload)
            self.set_aquisition_by_date()
            self.set_aquisition_by_utm_source(campaign_source)
            self.set_aquisition_by_utm_name(campaign_name)
            self.set_aquisition_by_utm_medium(campaign_medium)
            self.set_export_data()
            return self.analytics_component.get_figure()

    def reload_data_from_disk(self, app_reload):
        if(app_reload != 0):
            self.service.load_data()
            self.df = self.service.df

    def set_aquisition_by_date(self):
        self.df = self.service.filter_dataframe_by_date(
            self.df,
            self.start_date,
            self.end_date
        )
        self.analytics_component.analytics_users_count = self.service.filter_analytics_users_by_date(
            self.df, self.start_date, self.end_date)
        self.analytics_component.ej_users_count = len(
            self.df.email.value_counts())

    def set_aquisition_by_utm_source(self, campaign_source):
        if(campaign_source and len(campaign_source) >= 3):
            self.analytics_component.analytics_users_count = self.service.filter_analytics_users_by_utm_source(
                self.df, campaign_source, self.start_date, self.end_date)
            self.analytics_component.ej_users_count = len(
                self.df[self.df.analytics_source == campaign_source].email.value_counts())

    def set_aquisition_by_utm_name(self, campaign_name):
        if(campaign_name and len(campaign_name) >= 3):
            self.analytics_component.analytics_users_count = self.service.filter_analytics_users_by_utm_name(
                self.df, campaign_name, self.start_date, self.end_date)
            self.analytics_component.ej_users_count = len(
                self.df[self.df.analytics_name == campaign_name].email.value_counts())

    def set_aquisition_by_utm_medium(self, campaign_medium):
        if(campaign_medium and len(campaign_medium) >= 3):
            self.analytics_component.analytics_users_count = self.service.filter_analytics_users_by_utm_medium(
                self.df, campaign_medium, self.start_date, self.end_date)
            self.analytics_component.ej_users_count = len(
                self.df[self.df.analytics_medium == campaign_medium].email.value_counts())

    def set_export_data(self):
        data = [{'page_visits': self.analytics_component.analytics_users_count,
                 'ej_participants': self.analytics_component.ej_users_count,
                 'start_date': self.start_date,
                 'end_date': self.end_date}]
        self.export_component.df = pd.DataFrame(data)
