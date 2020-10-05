import dash_html_components as html
import dash_core_components as dcc
from components.utils.date_picker import *


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter AnalyticsComponent data.
    """

    def __init__(self):
        self.utm_source_options = []
        self.utm_medium_options = []
        self.utm_campaign_options = []

    def render(self, dataframe, service):
        """
            Main entrypoint to add filters to AnalyticsComponent.
        """
        service.set_filters_options(self, dataframe)
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
                         end_date=get_default_end_date(),
                         start_date=get_default_start_date(),
                         ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children=f"Paginas analisadas: {(service.page_path).replace('ga:pagePath=@', ' ')}"),
                ])
                ]),
            ])
        ],
        )
