# Visão Geral

Repositório contendo um DAG do airflow, responsável por coletar dados
de voto (via api) na EJ, dados de contato (via api) na plataforma Mautic
e dados de comportamento via api do google analytics. Além de coletar
os dados, o DAG também consolida tais dados em uma estrutura única, utilizando tanto o identificador gerado pelo Analytics (`ga`), quanto o identificador de um contato no Mautic (`mtc_id`). Quando um voto é feito na EJ, via
web component de coleta, o usuário criado pela api terá o `mtc_id` compondo
o campo email. 

Além do DAG, também mantemos um notebook do Jupyter, responsável por
gerar as visualizações e correlações dos dados coletados pelo DAG.

# Execução

Para a coleta, precisamos que EJ, Mautic e Analytics estejam configurados
para trabalhar em conjunto. No EJ, a coleta tem de ser feita via [web 
component](https://github.com/cidadedemocratica/ej-components) de coleta. O Mautic deverá ter seu script de tracking configurado
na mesma página do componente da EJ. O Analytics terá que ter uma property
configurada para a pagina em que o web component da EJ foi instalado. Para
o cruzamento funcionar, utilizamos um [script customizado](https://github.com/cidadedemocratica/ej-server/issues/105) do Mautic, para
salvar, no contato do Mautic, o `_ga` do Analytics, via campo customizado.

Para configurar o ambiente apontando para o EJ, Mautic e Analytics configurados localmente, execute:

	make prepare env=local
	airflow scheduler
	airflow webserver -p 8080


