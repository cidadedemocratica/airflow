import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ej_comments_all = pd.read_json('/tmp/airflow/comments_only.json')

ej_comments = pd.DataFrame(data=ej_comments_all, columns=['comentário_id', 'comentário', 'concorda', 'discorda', 'pulados'])
ej_comments['concorda'] = ej_comments['concorda'].map(lambda x: x * 100)
ej_comments['discorda'] = ej_comments['discorda'].map(lambda x: x * 100)
ej_comments['pulados'] = ej_comments['pulados'].map(lambda x: x * 100)
ej_comments['compilado'] = ''
for index,value in enumerate(ej_comments['concorda']):
    ej_comments['compilado'][index] = [ej_comments['concorda'][index], ej_comments['discorda'][index], ej_comments['pulados'][index]]
ej_comments
