## Terá que utilizar a biblioteca Pandas para plotar os gráficos
## pip install streamlit yfinance pandas
## pip install plotly
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

## Função de cálculo de MACD
def calc_macd(df):
    rapidaMME = df['Close'].ewm(span=12).mean()
    lentaMME = df['Close'].ewm(span=26).mean()
    MACD = rapidaMME - lentaMME
    sinal = MACD.ewm(span=9).mean()
    return MACD , sinal

## Função para plotar gráfico
def plotar_grafico(df, acao):
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        name='Preço fechamento',
        line_color='#FECB52',
        text=df.index.strftime('%d/%m'),
        hovertemplate='%{text}<br>Preço: %{y}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['preco_compra'],
        name='Compra',
        mode='markers',
        marker=dict(color='#00CC96', size=10),
        text=df.index.strftime('%d/%m'),
        hovertemplate='%{text}<br>Preço Compra: %{y}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['preco_venda'],
        name='Venda',
        mode='markers',
        marker=dict(color='#EF553B', size=10),
        text=df.index.strftime('%d/%m'),
        hovertemplate='%{text}<br>Preço Venda: %{y}<extra></extra>'
    ))

    st.plotly_chart(fig)

## Configuração da interface no Streamlit
st.title('Análise de ações')
st.sidebar.header('Parâmetros')

acao = st.sidebar.text_input('Digite a sigla da ação. OBS: Sempre usar ".SA" no final', 'PETR4.SA')
analise = st.sidebar.selectbox('Selecione o tipo de análise', ['MACD'])
executar = st.sidebar.button('Executar')

if executar:
    ## Obter dados da ação
    ticket = yf.Ticker(acao)
    df = ticket.history(period='1mo').reset_index()

    if df.empty:
        st.error("Não foi possível obter os dados da ação. Verifique o código e tente novamente.")
    else:
        ## Cálculo do MACD
        df['MACD'], df['sinal'] = calc_macd(df)

        ## Identificação de sinais de compra e venda
        df['flag'] = ''
        df['preco_compra'] = np.nan
        df['preco_venda'] = np.nan

        for i in range(1, len(df)):
            if df['MACD'][i] > df['sinal'][i]:
                if df['flag'][i - 1] != 'C':
                    df['flag'][i] = 'C'
                    df['preco_compra'][i] = df['Close'][i]
                else:
                    df['flag'][i] = 'C'
            elif df['MACD'][i] < df['sinal'][i]:
                if df['flag'][i - 1] != 'V':
                    df['flag'][i] = 'V'
                    df['preco_venda'][i] = df['Close'][i]
                else:
                    df['flag'][i] = 'V'

        ## Plotar gráfico
        plotar_grafico(df, acao)
