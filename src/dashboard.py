import pandas as pd
import numpy as np
import plotly.express as px
import sqlalchemy
import psycopg2
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_option_menu import option_menu

# Configurar página em wide
st.set_page_config(layout='wide')

# Retirar o menu
st.markdown("""
<style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Cria o gráfico do valor por categoria
def valor_categoria(data):
    aux = data.groupby('categoria', as_index=False)['valor_venda'].sum().sort_values('valor_venda', ascending=False)
    fig = px.bar(x='categoria', y='valor_venda', data_frame=aux, title='Total do Valor de Venda por Categoria')

    return fig

# Cria o gráfico do valor por marca
def valor_marca(data):
    aux = data.groupby('marca', as_index=False)['valor_venda'].sum().sort_values('valor_venda', ascending=False)
    fig = px.bar(x='marca', y='valor_venda', data_frame=aux, title='Total do Valor de Venda por Marca')

    return fig

# Cria o gráfico de venda por ano
def venda_ano(data):
    aux = data.groupby('ano', as_index=False)['valor_venda'].sum().sort_values('valor_venda', ascending=True)
    aux['ano'] = aux['ano'].astype(str)
    aux['avg'] = aux['valor_venda'].mean()

    bars = go.Bar(y=aux['ano'], x =aux['valor_venda'],  orientation='h', showlegend= False)

    line = go.Scatter(y= [0, 1], x= aux['avg'], mode= 'lines', showlegend= False, hoverinfo='none')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(bars, 1, 1, secondary_y=False)
    fig.add_trace(line, 1, 1, secondary_y=True)

    fig.update_layout(yaxis2= dict(fixedrange= True, range= [0, 1], visible= False), title_text='Total de Valor por Ano')

    return fig

# Cria o gráfico de média por segmento
def media_segmento(data):
    aux = data.groupby('segmento', as_index=False)['valor_venda'].mean().sort_values('valor_venda', ascending=False)
    fig = px.bar(x='segmento', y='valor_venda', data_frame=aux, title='Média de Valor de Venda por Segmento')

    return fig


# Conectando banco de dados
engine = sqlalchemy.create_engine('postgresql://postgres:triforce@localhost/vendas')

# Unindo as tabelas
query = """SELECT * 

FROM mkt."TB_VENDAS" v INNER JOIN mkt."TB_PRODUTO" P on v."ID_PRODUTO" = P."ID_PRODUTO" 
                        INNER JOIN mkt."TB_DATA" d on v."DATA_COMPLETA" = d."DATA_COMPLETA"

"""
df = pd.read_sql(query, engine)

# Excluindo colunas duplicadas
df = df.loc[:,~df.columns.duplicated()]

# Renomeando as colunas
aux = df.columns

for e in aux:
    col = e.casefold()
    df.rename(columns={e:col}, inplace=True)

# Alterando a coluna data para o tipo datetime
df['data_completa'] = pd.to_datetime(df['data_completa'], format='%d/%m/%Y')

# Separando a data completa em dia, mês e ano
df['dia'] = df['data_completa'].dt.day
df['mes'] = df['data_completa'].dt.month
df['ano'] = df['data_completa'].dt.year

# Menus
selected = option_menu(None, ['Página Inicial', 'Dashboard'], 
    icons=['house', 'file-bar-graph'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

# Página Inicial
if selected == 'Página Inicial':
    st.write('A empresa *PowerMasterLearning*, uma rede varejista que vende produtos eletrônicos e eletrodomésticos com lojas espalhadas em várias cidades do Brasil. A empresa começou sua operação em 2012 e atua nos quatro estados da região sudeste mais os estados do Paraná e Bahia.')
    st.write('Montando sua estratégia de vendas para o próximo ano, a PowerMasterLearning precisa saber qual dos fabricantes dos produtos vendido apresenta o melhor desempenho de vendas.')
    st.write('Em paralelo a isso, a empresa gostaria de ter diferentes visões das vendas realizadas nos últimos 4 anos (período de 2012 a 2015), por isso será necessário responder as seguintes perguntas:')
    st.write('1 - Qual o total do valor de vendas por categoria?')
    st.write('2 - Qual o total do valor de vendas por marca?')
    st.write('3 - Qual o total do valor de vendas por ano?')
    st.write('4 - Qual a média de valor de venda por segmento?')
    st.write('5 - Qual o total do valor de venda?')
    st.write('6 - Qual a média do valor de venda?')
    st.write('Para responder essas perguntas, foi montado um Dashboard que é apresentado na próxima página.')

# Dashboard
if selected == 'Dashboard':
    col1, col2, col3 = st.columns(3)
    # Título
    col2.header('Dashboard de Vendas')
    # Valores totais e médias de venda
    st.write('Valor total de venda: $', df['valor_venda'].sum())
    st.write('Média do valor de venda: $', np.round(df['valor_venda'].mean(), 2))
    # Gráficos
    col4, col5 = st.columns(2)
    col4.plotly_chart(valor_categoria(df))
    col4.plotly_chart(venda_ano(df))
    col5.plotly_chart(valor_marca(df))
    col5.plotly_chart(media_segmento(df))

