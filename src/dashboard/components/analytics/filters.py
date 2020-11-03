import dash_html_components as html
import dash_core_components as dcc
from components.utils.date_picker import *
from dash.dependencies import Input, Output
import pandas as pd
from components.analytics.service import AnalyticsService
import dash_bootstrap_components as dbc


class BubleData():

    def __init__(self, ej_users=0, analytics_users=0):
        self.ej_users = ej_users
        self.analytics_users = analytics_users

    def dataframe(self):
        return pd.DataFrame(
            [{'analytics_users': self.analytics_users, 'ej_users': self.ej_users}])


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter AnalyticsComponent data.
    """

    def __init__(self, app, render_analytics):
        """
            app: An instance of App class;
            render_analytics: A function to render the analytics component visualization. This function
            will be called when a filter is applied.
        """
        self.service = AnalyticsService()
        self.df = self.service.df
        self.app = app
        self.render_analytics = render_analytics
        self.end_date = self.service.get_default_end_date(),
        self.start_date = self.service.get_default_start_date(),
        self.bubble_data = BubleData().dataframe()
        self.set_filters_options()
        self.set_filters_callbacks()

    def get_data_to_export(self):
        """
            Returns filtered data to be exported by ExportsComponent
        """
        data = [{'page_visits': self.bubble_data.analytics_users,
                 'ej_participants': self.bubble_data.ej_users,
                 'start_date': self.start_date,
                 'end_date': self.end_date}]
        return pd.DataFrame(data)

    def render(self):
        """
            Adds filter inputs to AnalyticsComponent.
        """
        return html.Div(children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Div(className="filter-title",
                             children=[
                                 html.Div(children=[
                                     html.Span("Origem do participante", style={
                                         "marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='analytics-utm-source')
                                 ]),
                                 dbc.Tooltip(
                                     'Será o valor utm_source (google analytics). Quando definido, será o valor da tag, '
                                     'quando não, será o domínio que o usuário estava antes de ser redirecionado para '
                                     'o componente de votação. Se ele for direto para o componente, o valor será '
                                     '(direct).', target='analytics-utm-source')
                             ]),
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
                    html.Div(className="filter-title",
                             children=[
                                 html.Div(children=[
                                     html.Span("Midia do participante", style={
                                         "marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='analytics-utm-medium')
                                 ]),
                                 dbc.Tooltip('Será o valor utm_medium(google analytics). Quando definido, será o valor da tag,'
                                             ' quando não, será a engine de busca utilizada pelo usuário. '
                                             'Caso o usuário venha diretamente para a pagina, o valor será (none).',
                                             target='analytics-utm-medium')
                             ]),
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
                    html.Div(className="filter-title",
                             children=[
                                 html.Div(children=[
                                     html.Span("Campanha do participante",
                                               style={"marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='analytics-utm-campaign')
                                 ]),
                                 dbc.Tooltip(
                                     'Será o valor do utm_campaign (google analytics).'
                                     'Caso não seja definido, seu valor será (not set).', target='analytics-utm-campaign')
                             ]),
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
                    html.Span(className="filter-title",
                              children="Período:"),
                    dcc.DatePickerRange(
                        id='by_date',
                        style={"flexGrow": 1},
                        display_format='DD/MM/YYYY',
                        end_date=self.end_date[0],
                        start_date=self.start_date[0]
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(className="filter-title",
                              children=f"Paginas analisadas:"),
                    html.Span(
                        children=f"{(self.service.page_path).replace('ga:pagePath=@', ' ')}"),
                ])
                ]),
            ])
        ],
        )

    def set_filters_options(self):
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []
        if(not self.df.empty):
            self.utm_source_options = self.df['analytics_source'].value_counts(
            ).keys()
            self.utm_medium_options = self.df['analytics_medium'].value_counts(
            ).keys()
            self.utm_campaign_options = self.df['analytics_campaign'].value_counts(
            ).keys()

    def set_filters_callbacks(self):
        @self.app.callback(
            Output("analytics_loader", 'children'),
            [Input('analytics_campaign_source', 'value'),
                Input('analytics_campaign_name', 'value'),
                Input('analytics_campaign_medium', 'value'),
                Input('by_date', 'start_date'),
                Input('by_date', 'end_date'),
                Input('app_reload', 'n_clicks'),
             ])
        def filter_callbacks(analytics_campaign_source,
                             analytics_campaign_name,
                             analytics_campaign_medium,
                             start_date,
                             end_date,
                             app_reload):

            self.start_date = start_date
            self.end_date = end_date
            self.reload_data_from_disk(app_reload)
            if(not self.df.empty):
                self.set_aquisition_by_date()
                self.set_aquisition_by_utm_source(
                    analytics_campaign_source)
                self.set_aquisition_by_utm_name(analytics_campaign_name)
                self.set_aquisition_by_utm_medium(
                    analytics_campaign_medium)
            return self.render_analytics(self.bubble_data)

    def reload_data_from_disk(self, app_reload):
        if(app_reload != 0):
            self.service.load_data()
            self.df = self.service.df

    def set_aquisition_by_date(self):
        self.df = self.service.filter_dataframe_by_date(
            self.service.df,
            self.start_date,
            self.end_date
        )
        analytics_users = self.service.filter_analytics_users_by_date(self.start_date, self.end_date)
        ej_users = len(self.df.email.value_counts())
        self.bubble_data = BubleData(ej_users, analytics_users).dataframe()

    def set_aquisition_by_utm_source(self, analytics_campaign_source):
        if(analytics_campaign_source and len(analytics_campaign_source) >= 3):
            analytics_users = self.service.filter_analytics_users_by_utm_source(
                self.df, analytics_campaign_source, self.start_date, self.end_date)
            ej_users = len(
                self.df[self.df.analytics_source == analytics_campaign_source].email.value_counts())
            self.bubble_data = BubleData(
                ej_users, analytics_users).dataframe()

    def set_aquisition_by_utm_name(self, analytics_campaign_name):
        if(analytics_campaign_name and len(analytics_campaign_name) >= 3):
            analytics_users = self.service.filter_analytics_users_by_utm_name(
                self.df, analytics_campaign_name, self.start_date, self.end_date)
            ej_users = len(
                self.df[self.df.analytics_name == analytics_campaign_name].email.value_counts())
            self.bubble_data = BubleData(
                ej_users, analytics_users).dataframe()

    def set_aquisition_by_utm_medium(self, analytics_campaign_medium):
        if(analytics_campaign_medium and len(analytics_campaign_medium) >= 3):
            analytics_users = self.service.filter_analytics_users_by_utm_medium(
                self.df, analytics_campaign_medium, self.start_date, self.end_date)
            ej_users = len(
                self.df[self.df.analytics_medium == analytics_campaign_medium].email.value_counts())
            self.bubble_data = BubleData(
                ej_users, analytics_users).dataframe()
