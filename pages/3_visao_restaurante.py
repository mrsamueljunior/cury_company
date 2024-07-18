# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Blibliotecas Necessárias
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import datetime as dt
from PIL import Image
import folium as fm
import re

st.set_page_config( page_title='Visão Restaurantes', layout='wide' )

def clean_dataset( df ):
    # Removendo os espaços dentro de texto/string/object com o Comando strip
    # for i in range(len(df)):
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()

    #0 Desconciderar as linhas com 'NaN ' das Colunas
    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]
    df = df.loc[df['multiple_deliveries'] != 'NaN ', :]
    df = df.loc[df['Weatherconditions'] != 'conditions NaN', :]
    df = df.loc[df['City'] != 'NaN ']

    # Comando para Remover o Texto de Numeros
    df['Time_taken(min)'] = df['Time_taken(min)'].str.replace('(min) ', '')

    # Converter a coluna Delivery_person_Age de texto (object/string) para números (inteiros)
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # Converter a coluna Delivery_person_Age de texto (object/string) para números (inteiros)
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # Converter a coluna Delivery_person_Ratings de texto (object/string) para número decimal (float)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # Converter a coluna Order_Date de texto (object/string) para Data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    # Converter a coluna multiple_deliveries de texto (object/string) para número inteiro (int)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    return df

# Distancia Média
def distancia_media( df01 ):    
    colunas = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df01['distance'] = df01.loc[:, colunas].apply( lambda x:
                            haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
    avg_distance = np.round(df01['distance'].mean(), 2)
    col02.metric('Distancia Média', avg_distance)
    return df01

# Tempo Médio com Festival
def tempo_medio( df01 ):    
    tempo_medio = ( df01.loc[:, ['Time_taken(min)', 'Festival']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} ) )
    tempo_medio.columns = ['avg_time', 'std_time']
    tempo_medio = tempo_medio.reset_index()
    tempo_medio = np.round(tempo_medio.loc[tempo_medio['Festival'] == 'Yes', 'avg_time'], 2)
    col03.metric('Tempo Médio', tempo_medio)
    return df01

# Desvio Padrão
def desvio_padrao( df01 ):    
    desvio_padrao = ( df01.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby('Festival')
                          .agg( {'Time_taken(min)' : ['mean', 'std']} ) )
    desvio_padrao.columns = ['avg_time', 'std_time']
    desvio_padrao = desvio_padrao.reset_index()
    desvio_padrao = np.round(desvio_padrao.loc[desvio_padrao['Festival'] == 'Yes', 'std_time' ], 2)
    col04.metric('Desvio Padrão', desvio_padrao)
    return df01

# Tempo Medio sem Festival
def tempo_media_sf( df01 ):    
    tempo_medio = ( df01.loc[:, ['Time_taken(min)', 'Festival']]
                        .groupby('Festival')
                        .agg( {'Time_taken(min)': ['mean', 'std']} ) )
    tempo_medio.columns = ['avg_time', 'std_time']
    tempo_medio = tempo_medio.reset_index()
    tempo_medio = np.round(tempo_medio.loc[tempo_medio['Festival'] == 'No', 'avg_time'], 2)
    col05.metric('Tempo Médio', tempo_medio)
    return df01

# Import dataset
df = pd.read_csv('dataset/train.csv')

df01 = clean_dataset ( df )



#print(df01['Time_taken(min)'])

# df01.to_csv('dataset/train.csv')

# ============================================
# Barra Lateral
# ============================================

st.markdown('# Marketplace - Visão Restaurantes')

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

tab01, tab02, tab03, tab04 = st.tabs(['VISÃO', ' - ', ' - ', ' - '])

with tab01:
    with st.container():
        st.subheader('Overal Metrics')
        
        col01, col02, col03, col04, col05, col06 = st.columns(6)
        with col01:
            delivery_unique = len( df01.loc[:, 'Delivery_person_ID'].unique() )
            col01.metric('Entregadores Únicos', delivery_unique)

        with col02:
            df01 = distancia_media( df01 )

        with col03:
            df01 = tempo_medio( df01 )

        with col04:
            df01 = desvio_padrao( df01 )

        with col05:
            df01 = tempo_media_sf( df01 )
        
        with col06:                    
            desvio_padrao = ( df01.loc[:, ['Time_taken(min)', 'Festival']]
                                  .groupby('Festival')
                                  .agg( {'Time_taken(min)' : ['mean', 'std']} ) )
            desvio_padrao.columns = ['avg_time', 'std_time']
            desvio_padrao = desvio_padrao.reset_index()
            desvio_padrao = np.round(desvio_padrao.loc[desvio_padrao['Festival'] == 'No', 'std_time' ], 2)
            col06.metric('Desvio Padrão', desvio_padrao)

    st.markdown("""___""")            

    with st.container():
        tempo_md = df01.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg( {'Time_taken(min)' : ['mean','std']} )
        tempo_md.columns = ['avg_time', 'std_time']
        tempo_md = tempo_md.reset_index()
        fig = go.Figure()
        fig.add_trace( go.Bar( name='Control', x=tempo_md['City'],y=tempo_md['avg_time'], error_y=dict( type='data', array=tempo_md['std_time'] ) ) )
        fig.update_layout(barmode='group')
        st.plotly_chart( fig )

    with st.container():
        st.subheader('Distrinuição do Tempo')
        col01, col02 = st.columns (2)

        with col01:
            #st.subheader('Tempo Médio de Entrega por Cidade')
            colunas = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df01['Distancia'] = df01.loc[:, colunas].apply( lambda x:
                                    haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
            avg_distance = df01.loc[:, ['City', 'Distancia']].groupby('City').mean().reset_index()
            fig = go.Figure( data = [go.Pie( labels=avg_distance['City'], values=avg_distance['Distancia'], pull=[0, 0.05, 0])] )
            st.plotly_chart( fig )

        with col02:
            cityTime = ( df01.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                             .groupby( ['City', 'Road_traffic_density'] )
                             .agg( {'Time_taken(min)' : ['mean', 'std']} ) )
            cityTime.columns = ['avg_time', 'std_time']
            cityTime = cityTime.reset_index()
            fig = px.sunburst( cityTime, path=['City', 'Road_traffic_density'], values='avg_time', 
                               color='std_time', color_continuous_scale='RdBu', 
                               color_continuous_midpoint=np.average( cityTime['std_time'] ) )
            st.plotly_chart( fig )

    with st.container():
        distancia = ( df01.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)' : ['mean', 'std']} ) )
        distancia.columns = ['avg_time', 'std_time']
        distancia = distancia.reset_index()
        st.dataframe( distancia )