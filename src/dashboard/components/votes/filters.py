import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from components.votes.service import VotesService
import dash_bootstrap_components as dbc


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter VotesComponent data.
    """

    def __init__(self, app, render_votes):
        """
            app: An instance of App class;
            render_votes: A function to render the votes component visualization. This function
            will be called when a filter is applied.
        """

        self.service = VotesService()
        self.df = self.service.df
        self.render_votes = render_votes
        self.app = app
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []
        self.set_filters_options()
        self.set_filters_callbacks()

    def get_data_to_export(self):
        """
            Returns filtered data to be exported by ExportsComponent
        """
        return self.df

    def render(self):
        """
            Adds filter inputs to VotesComponent.
        """
        return html.Div(children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Div(className="filter-title",
                             children=[
                                 html.Div(children=[
                                     html.Span("Origem do voto", style={
                                         "marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='utm-source')
                                 ]),
                                 dbc.Tooltip(
                                     'Será o valor utm_source (google analytics). Quando definido, será o valor da tag, '
                                     'quando não, será o domínio que o usuário estava antes de ser redirecionado para '
                                     'o componente de votação. Se ele for direto para o componente, o valor será '
                                     '(direct).', target='utm-source')
                             ]),
                    dcc.Dropdown(
                        id='votes_campaign_source',
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
                                     html.Span("Midia do voto", style={
                                         "marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='utm-medium')
                                 ]),
                                 dbc.Tooltip('Será o valor utm_medium(google analytics). Quando definido, será o valor da tag,'
                                             ' quando não, será a engine de busca utilizada pelo usuário. '
                                             'Caso o usuário venha diretamente para a pagina, o valor será (none).',
                                             target='utm-medium')
                             ]),
                    dcc.Dropdown(
                        id='votes_campaign_medium',
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
                                     html.Span("Campanha do voto",
                                               style={"marginRight": 4}),
                                     html.I(className="fa fa-info-circle",
                                            id='utm-campaign')
                                 ]),
                                 dbc.Tooltip(
                                     'Será o valor do utm_campaign (google analytics).'
                                     'Caso não seja definido, seu valor será (not set).', target='utm-campaign')
                             ]),
                    dcc.Dropdown(
                        id='votes_campaign_name',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_campaign_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(className="filter-title",
                              children="Visualizar apenas emails válidos"),
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
                    html.Span(className="filter-title",
                              children="Período"),
                    dcc.DatePickerRange(
                        id='votes_by_date',
                        style={"flexGrow": 1},
                        display_format='DD/MM/YYYY',
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
        @ self.app.callback(
            Output("votes_loader", 'children'),
            [Input('votes_campaign_source', 'value'),
                Input('votes_campaign_name', 'value'),
                Input('votes_campaign_medium', 'value'),
                Input('email', 'value'),
                Input('votes_by_date', 'start_date'),
                Input('votes_by_date', 'end_date'),
                Input('app_reload', 'n_clicks'),
             ])
        def distribution_callback(votes_campaign_source, votes_campaign_name, votes_campaign_medium, email, start_date, end_date, app_reload):
            self.reload_data_from_disk(app_reload)

            if(not self.df.empty):
                self.df = self.service.filter_dataframe_by_date(
                    self.service.df,
                    start_date,
                    end_date
                )
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_source', votes_campaign_source)
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_medium', votes_campaign_medium)
                self.df = self.service.filter_by_utm(
                    self.df, 'analytics_campaign', votes_campaign_name)
                self.df = self.service.filter_by_email(self.df, email)

            return self.render_votes(self.service.groupby(self.df))

    def reload_data_from_disk(self, app_reload):
        if(app_reload != 0):
            self.service.load_data()
            self.df = self.service.df
