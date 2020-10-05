import datetime
import pandas as pd
from dash.dependencies import Input, Output
from components.utils.date_picker import dataframe_between_dates


class CallbacksComponent():

    def __init__(self, analytics_component, export_component):
        self.component = analytics_component
        self.app = analytics_component.app
        self.df = analytics_component.df
        self.service = analytics_component.service
        self.export = export_component

    def create(self):
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
            if(app_reload != 0):
                self.service.load_data()
                self.df = self.service.df

            if(self.df.empty):
                return

            start_date = datetime.datetime.fromisoformat(start_date).date()
            end_date = datetime.datetime.fromisoformat(end_date).date()

            df = dataframe_between_dates(
                self.component.df,
                start_date,
                end_date
            )

            self.set_date_range_filter(df, start_date, end_date)
            self.set_campaign_source_filter(df,
                                            campaign_source, start_date, end_date)
            self.set_campaign_name_filter(
                df, campaign_name, start_date, end_date)
            self.set_campaign_medium_filter(df,
                                            campaign_medium, start_date, end_date)
            self.set_export_data(start_date, end_date)
            return self.component.get_figure()

    def set_export_data(self, start_date, end_date):
        data = [{'page_visits': self.component.analytics_users_count,
                 'ej_participants': self.component.ej_users_count,
                 'start_date': start_date,
                 'end_date': end_date}]
        self.export.df = pd.DataFrame(data)

    def set_date_range_filter(self, df, start_date, end_date):
        if(start_date and end_date):
            analytics_filter = self.service.get_date_filter(
                start_date, end_date)
            self.count_users(df, analytics_filter)

    def set_campaign_medium_filter(self, df, campaign_medium, start_date, end_date):
        if(campaign_medium and len(campaign_medium) >= 3):
            df = df[df['analytics_medium'] == campaign_medium]

            analytics_filter = self.service.get_medium_filter(
                campaign_medium, start_date, end_date)
            self.count_users(df, analytics_filter)

    def set_campaign_name_filter(self, df, campaign_name, start_date, end_date):
        if(campaign_name and len(campaign_name) >= 3):
            df = df[df['analytics_campaign'] == campaign_name]
            analytics_filter = self.service.get_name_filter(
                campaign_name, start_date, end_date)
            self.count_users(df, analytics_filter)

    def set_campaign_source_filter(self, df, campaign_source, start_date, end_date):
        if(campaign_source and len(campaign_source) >= 3):
            df = df[df['analytics_source']
                    == campaign_source]

            analytics_filter = self.service.get_campaign_filter(
                campaign_source, start_date, end_date)
            self.count_users(df, analytics_filter)

    def count_users(self, df, analytics_filter):
        self.component.analytics_users_count = self.service.filter_by_analytics(
            analytics_filter)
        self.component.ej_users_count = int(len(df['email'].value_counts()))
