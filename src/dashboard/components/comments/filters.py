import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from components.comments.service import CommentsService


class FiltersComponent():
    """
        FiltersComponent adds inputs to filter CommentsComponent data.
    """

    def __init__(self, app, render_comments):
        self.service = CommentsService()
        self.comments = self.service.comments
        self.clusters = self.service.clusters
        self.app = app
        self.render_comments = render_comments
        self.order_options = ['concorda',
                              'discorda', 'pulados', 'convergência']
        self.set_filters_callbacks()

    def get_data_to_export(self):
        """
            Returns filtered data to be exported by ExportsComponent
        """
        return self.comments

    def render(self):
        """
            Main entrypoint to add filters to commentsComponent.
        """
        return html.Div(children=[
            html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center', 'width': '30%'}, children=[
                html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                          children="Participação acima de:"),
                dcc.Input(
                        id='participation',
                        type='number',
                        value='50',
                        debounce=True,
                        style={"flexGrow": 1, 'color': '#aaa', 'padding': '6px', 'opacity': '60%'}),
            ]),
            html.Div(style={'display': 'flex', 'marginTop': '10px', 'marginBottom': '18px', 'alignItems': 'center', 'width': '30%'}, children=[
                html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                          children="Ordenar por:"),
                dcc.Dropdown(
                    id='_filter',
                    options=[{'label': i, 'value': i}
                             for i in self.order_options],
                    value='',
                    style={"flexGrow": 1}
                ),
            ]),
        ])

    def set_filters_callbacks(self):
        @self.app.callback(
            Output("table_body", 'children'),
            [Input('_filter', 'value'),
             Input('app_reload', 'n_clicks'),
             Input('participation', 'value')])
        def table_callback(_filter, app_reload, participation):
            self.reload_data_from_disk(app_reload)
            if(not self.comments.empty):
                if(participation):
                    self.comments = self.service.comments
                    self.comments = self.comments[
                        self.comments['participação'] >= int(participation) / 100]
                if(_filter in self.order_options):
                    self.comments = self.comments.sort_values(
                        by=_filter, ascending=False)
            return self.render_comments(self.comments, self.clusters)

    def reload_data_from_disk(self, app_reload):
        if(app_reload != 0):
            self.service.load_data()
            self.comments = self.service.comments
