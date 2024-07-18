# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Blibliotecas Necessárias
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import datetime as dt
from PIL import Image
import folium as fm

st.set_page_config( page_title='Visão Entregadores', layout='wide' )


def clean_code( df01 ):
    # Removendo os espaços dentro de texto/string/object com o Comando strip
    # for i in range(len(df01)):
    df01.loc[:, 'ID'] = df01.loc[:, 'ID'].str.strip()
    df01.loc[:, 'Delivery_person_ID'] = df01.loc[:, 'Delivery_person_ID'].str.strip()
    df01.loc[:, 'Road_traffic_density'] = df01.loc[:, 'Road_traffic_density'].str.strip()
    df01.loc[:, 'Type_of_vehicle'] = df01.loc[:, 'Type_of_vehicle'].str.strip()
    df01.loc[:, 'City'] = df01.loc[:, 'City'].str.strip()
    df01.loc[:, 'Festival'] = df01.loc[:, 'Festival'].str.strip()

    #0 Desconciderar as linhas com 'NaN ' das Colunas
    df01 = df01.loc[df01['Delivery_person_Age'] != 'NaN ', :]
    df01 = df01.loc[df01['multiple_deliveries'] != 'NaN ', :]
    df01 = df01.loc[df01['Weatherconditions'] != 'conditions NaN', :]
    df01 = df01.loc[df01['City'] != 'NaN ']

    # Converter a coluna Delivery_person_Age de texto (object/string) para números (inteiros)
    df01['Delivery_person_Age'] = df01['Delivery_person_Age'].astype(int)

    # Converter a coluna Delivery_person_Ratings de texto (object/string) para número decimal (float)
    df01['Delivery_person_Ratings'] = df01['Delivery_person_Ratings'].astype(float)

    # Converter a coluna Order_Date de texto (object/string) para Data
    df01['Order_Date'] = pd.to_datetime(df01['Order_Date'], format='%d-%m-%Y')

    # Converter a coluna multiple_deliveries de texto (object/string) para número inteiro (int)
    df01['multiple_deliveries'] = df01['multiple_deliveries'].astype(int)
    return df01

def to_ent_len( df01 ):
    dfCity = (  df01.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                    .groupby( ['City', 'Delivery_person_ID'] ).min()
                    .sort_values( ['City', 'Time_taken(min)'], ascending=False ).reset_index() )

    dfCity01 = dfCity.loc[dfCity['City'] == 'Metropolitian', : ].head(10)
    dfCity02 = dfCity.loc[dfCity['City'] == 'Urban', : ].head(10)
    dfCity03 = dfCity.loc[dfCity['City'] == 'Semi-Urban', : ].head(10)
    mais_lentos = pd.concat([dfCity01, dfCity02, dfCity03])
    return mais_lentos

def top_mais_rap( df01 ):
    dfCity = (  df01.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                    .groupby( ['City', 'Delivery_person_ID'] ).min()
                    .sort_values( ['City', 'Time_taken(min)'], ascending=True ).reset_index() )

    dfCity01 = dfCity.loc[dfCity['City'] == 'Metropolitian', : ].head(10)
    dfCity02 = dfCity.loc[dfCity['City'] == 'Urban', : ].head(10)
    dfCity03 = dfCity.loc[dfCity['City'] == 'Semi-Urban', : ].head(10)

    mais_rapidos = pd.concat([dfCity01, dfCity02, dfCity03])
    return mais_rapidos

def avaliacao_media_transito( def01 ):
    media_desvio = ( df01.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                         .groupby('Road_traffic_density')
                         .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
            # Renomear Colunas
    media_desvio.columns = ['Delivery_Mean', 'Delivery_Std']
    avaliacao_transito = media_desvio.reset_index()
    return avaliacao_transito

def avaliacao_media_clima( df01 ):
    media_desvio = ( df01.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                         .groupby('Weatherconditions')
                         .agg({'Delivery_person_Ratings':['mean','std']}) )

    media_desvio.columns = ['Delivery_Mean','Delivery_Std']
    avaliacao_clima = media_desvio.reset_index()
    return avaliacao_clima


#---------------------------- Inicio da Estrutura Lógica do Código ----------------------------

#------------------------------------------
# Import dataset
#------------------------------------------ 
df = pd.read_csv('dataset/train.csv')

#------------------------------------------
# Limpando Dados
#------------------------------------------ 
df01 = clean_code( df )

# ============================================
# Barra Lateral
# ============================================

st.markdown('# Marketplace - Visão Entregadores')

# Adicionar Imgem
#image_path = 'C:/Users/9SAMJUNI/Documents/ComunidadeDS/img/img-python.png'
image = Image.open('img-python.png')
st.sidebar.image(image, width=50)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma Data Limite')

date_slider = st.sidebar.slider(
    'Até qual Valor?',
     value = dt.datetime(2022, 4, 13), 
     min_value = dt.datetime(2022, 2, 11),
     max_value = dt.datetime(2022, 4, 6),
     format = 'DD-MM-YYYY')

# st.dataframe(df01)
#st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do Trânsito ?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")

# Filtro de Datas
linhas_selecionadas = df01['Order_Date'] < date_slider
df01 = df01.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df01['Road_traffic_density'].isin( traffic_options )
df01 = df01.loc[linhas_selecionadas, :]

# ============================================
# Layout no Streamlit
# ============================================

tab01, tab02, tab03 = st.tabs(['VISÃO GENRENCIAL', ' - ', ' - '])

with tab01:
    with st.container():
        st.title('Overall Metrics')
        col01, col02, col03, col04 = st.columns(4, gap='large')

        with col01:
            maior_idade = df01.loc[:, "Delivery_person_Age"].max()
            col01.metric('Maior Idade', maior_idade)

        with col02:
            menor_idade = df01.loc[:, "Delivery_person_Age"].min()
            col02.metric('Menor Idade', menor_idade)

        with col03:
            melhor_condicao = df01.loc[:, 'Vehicle_condition'].max()
            col03.metric('Melhor Condições', melhor_condicao)

        with col04:
           pior_condicao = df01.loc[:, 'Vehicle_condition'].min()
           col04.metric('Pior Condições', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.markdown('## Avaliações')

        col01, col02 = st.columns(2)
        with col01:
            st.markdown('Avaliações Médias por Entregadores')
            avalicoes_entregadores = ( df01.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                           .groupby('Delivery_person_ID').mean().reset_index() )
            st.dataframe(avalicoes_entregadores)

        with col02:
            avaliacao_transito = avaliacao_media_transito( df01 )
            st.markdown('Avaliação Média por Transito')
            st.dataframe(avaliacao_transito)
            
            avaliacao_clima = avaliacao_media_clima( df01 )
            st.markdown('Avaliação Média por Clima')
            st.dataframe(avaliacao_clima)
            

    with st.container():
        st.markdown("""---""")
        st.markdown('## Velocidade de Entragas')
        col01, col02 = st.columns(2)

        with col01:
            mais_rapidos = top_mais_rap( df01 )
            st.markdown('Top Entregadores mais Rápidos')
            st.dataframe(mais_rapidos)

        with col02:
            mais_lentos = to_ent_len( df01 )
            st.markdown('Top Entregadores mais Lentos')
            st.dataframe(mais_lentos)

        
