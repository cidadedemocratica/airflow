import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dash_html_components as html

ej_comments_all = pd.read_json('/tmp/airflow/comments_only.json')

ej_comments = pd.DataFrame(data=ej_comments_all, columns=['comentário_id', 'comentário', 'autor', 'concorda', 'discorda', 'pulados', 'participação', 'convergência'])
ej_comments['concorda'] = ej_comments['concorda'].map(lambda x: x * 100)
ej_comments['discorda'] = ej_comments['discorda'].map(lambda x: x * 100)
ej_comments['pulados'] = ej_comments['pulados'].map(lambda x: x * 100)
ej_comments['convergência'] = ej_comments['convergência'].map(lambda x: round(x * 100))
ej_comments['geral'] = ''
for index,value in enumerate(ej_comments['concorda']):
    ej_comments['geral'][index] = [ej_comments['concorda'][index], ej_comments['discorda'][index], ej_comments['pulados'][index]]



def generate_table_body(dataframe):
    trs = []
    for index in range(len(dataframe)):
        tds = []
        for col in dataframe.columns:
            if(col == "convergência"):
                tds.append(html.Td(str(dataframe.iloc[index][col]) + '%'))
            if(col == "geral"):
                bar = html.Div(
                    style={},
                    children=[
                        html.Div(style={'borderStyle': 'solid', 'borderColor': 'grey', 'width': '100px', 'height': 20, 'display': 'flex'}, children=[
                            html.Div(style={'backgroundColor': 'green', 'width': dataframe.iloc[index]['concorda'], 'height': 20}),
                            html.Div(style={'backgroundColor': 'red', 'width': dataframe.iloc[index]['discorda'], 'height': 20}),
                            html.Div(style={'backgroundColor': 'yellow', 'width': dataframe.iloc[index]['pulados'], 'height': 20})
                        ]),
                        html.Div(style={}, children=[
                            html.Span(style={'color': 'green', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['concorda'])) + '%'),
                            html.Span(style={'color': 'red', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['discorda'])) + '%'),
                            html.Span(style={'color': 'yellow', 'fontSize': '11px', 'marginRight': '5px'}, children=str(round(dataframe.iloc[index]['pulados'])) + '%'),
                        ]),
                    ],
                )
                tds.append(html.Td(bar))
            elif((col != "concorda") and (col != "discorda") and (col != "pulados") and (col != 'participação') and (col != 'convergência')):
                tds.append(html.Td(dataframe.iloc[index][col]))
        trs.append(html.Tr(tds))
    return trs;

def generate_table(dataframe):
    ths = []
    trs = []
    for col in dataframe.columns:
        if((col != 'concorda') and (col != 'discorda') and (col != 'pulados') and (col != 'participação')):
            ths.append(html.Th(col))
    trs = generate_table_body(dataframe)
    return html.Table([
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                trs, id="table_body"
            )
        ])
