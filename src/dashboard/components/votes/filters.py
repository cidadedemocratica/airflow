import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter VotesComponent data.
    """

    def __init__(self, service, app, votes_component, export_component):
        self.service = service
        self.app = app
        self.df = self.service.df
        self.votes_component = votes_component
        self.export_component = export_component
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []
        self.set_filters_options()
        self.set_filters_callbacks()

    def render(self):
        """
            Main entrypoint to add filters to VotesComponent.
        """
        return html.Div(children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_source:"),
                    dcc.Dropdown(
                        id='analytics_campaign_source',
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
                        id='analytics_campaign_medium',
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
                        id='analytics_campaign_name',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_campaign_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="visualizar apenas emails válidos"),
                    dcc.Checklist(
                        id='email',
                        options=[
                            {'label':  '', 'value': 'is_valid'}],
                        value=['is_valid'],
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Período"),
                    dcc.DatePickerRange(
                        id='votes_by_date',
                        clearable=True,
                        style={"flexGrow": 1},
                         end_date=self.service.get_default_end_date(),
                         start_date=self.service.get_default_start_date(),
                         ),
                ])
                ]),
            ]),
        ],
        )

    def set_filters_options(self):
        if(not self.df.empty):
            self.utm_source_options = self.df['analytics_source'].value_counts(
            ).keys()
            self.utm_medium_options = self.df['analytics_medium'].value_counts(
            ).keys()
            self.utm_campaign_options = self.df['analytics_campaign'].value_counts(
            ).keys()

    def set_filters_callbacks(self):
        @self.app.callback(
            Output("votes_loader", 'children'),
            [Input('analytics_campaign_source', 'value'),
                Input('analytics_campaign_name', 'value'),
                Input('analytics_campaign_medium', 'value'),
                Input('email', 'value'),
                Input('votes_by_date', 'start_date'),
                Input('votes_by_date', 'end_date'),
                Input('app_reload', 'n_clicks'),
             ])
        def distribution_callback(analytics_campaign_source, analytics_campaign_name, analytics_campaign_medium, email, start_date, end_date, app_reload):
            self.reload_data_from_disk(app_reload)

            if(not self.df.empty):
                self.df = self.service.filter_dataframe_by_date(
                    self.service.df,
                    start_date,
                    end_date
                )
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_source', analytics_campaign_source)
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_medium', analytics_campaign_medium)
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_campaign', analytics_campaign_name)
                self.df = self.service.filter_by_email(self.df, email)
                self.export_component.df = self.df
                self.votes_component.df = self.df

            return self.votes_component.get_figure()

    def reload_data_from_disk(self, app_reload):
        if(app_reload != 0):
            self.service.load_data()
            self.df = self.service.df
            self.votes_component.df = self.service.df
