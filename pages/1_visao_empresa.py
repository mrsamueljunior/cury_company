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

st.set_page_config( page_title='Visão Empresa', layout='wide' )

# -----------------------------------------
#  Funções
#------------------------------------------

def clean_code(df01):
    """ 
        Está Função tem a responsabilidade de limpar o dataFrame
        Tipo de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de coluna de Dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação de coluna de Datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: DataFrame
        OutPut: DataFrame
    """
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

# Order Metric
def order_metric(df01):    
    colunas = ['ID', 'Order_Date']
    barras = df01.loc[:, colunas].groupby('Order_Date').count().reset_index()
    fig_bar = px.bar( barras, x='Order_Date', y='ID' )
    return fig_bar

# Traffic Order Share
def traffic_order_share (df01):
    pizza = df01.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    # Converter para Percentual
    pizza['Entregas_%'] = pizza["ID"] / pizza['ID'].sum()
    fig_pie = px.pie( pizza, values='Entregas_%', names='Road_traffic_density' )
    return fig_pie

# Traffic Order City
def traffic_order_city( df01 ):
    bolhas  = df01.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    # Gráfico de Bolha
    fig_bolhas = px.scatter( bolhas, x='City', y= 'Road_traffic_density', size= 'ID', color='City' )    
    return fig_bolhas

# Order By Week
def order_by_week( df01 ):
    df01['Week_of_Year'] = df01['Order_Date'].dt.strftime( '%U' )
    lines = df01.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    fig_lines = px.line( lines, x='Week_of_Year', y='ID' )
    return fig_lines

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

st.markdown('# Marketplace - Visão Cliente')

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
df01 = df01 = df01.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df01['Road_traffic_density'].isin( traffic_options )
df01 = df01.loc[linhas_selecionadas, :]

# st.dataframe(df01)

# ============================================
# Layout no Streamlit
# ============================================

#  Abas (TABS)
tab01, tab02, tab03 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geografica'])
with tab01:
    with st.container():
        # Order Matric
        fig_bar = order_metric( df01 )
        st.plotly_chart(fig_bar, use_container_width=True)        
        
    with st.container():
        col01, col02, = st.columns(2)
        with col01:
            fig_pie = traffic_order_share( df01 )
            st.markdown('Traffic Order Share')
            st.plotly_chart(fig_pie, use_container_width=True)            
        
        with col02:
            fig_bolhas = traffic_order_city( df01 )
            st.markdown('Traffic Order City')
            st.plotly_chart(fig_bolhas, use_container_width=True)

with tab02:
    with st.container():
        fig_lines = order_by_week( df01 )
        st.markdown('Order by Week')
        st.plotly_chart(fig_lines, use_container_width=True)

    with st.container():
        st.markdown('Order Share By Week')
        entregasWeek = df01.loc[:,['ID', 'Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
        entregadorWeek = df01.loc[:,['Delivery_person_Age', 'Week_of_Year']].groupby(['Week_of_Year']).nunique().reset_index()
        
        # Juntar dois Dataframes com a Função MERGE da Biblioteca Pandas
        df01_aux = pd.merge(entregasWeek, entregadorWeek, how='inner')
        df01_aux['Order_by_Deliver'] = entregasWeek['ID'] / entregadorWeek['Delivery_person_Age']
        fig_lines = px.line(df01_aux, x='Week_of_Year', y='Order_by_Deliver')
        st.plotly_chart(fig_lines, use_container_width=True)

with tab03:
    st.markdown('Country Maps')
    localizacao = ( df01.loc[:, ['City', 'Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']]
                        .groupby(['City', 'Road_traffic_density']).median().reset_index() )
    localizacao = localizacao.head()
    # Desenhar Mapas com a Biblioteca folium
    mapa = fm.Map()
    #Função Marker (Pino)
    for index, location_info in localizacao.iterrows():
        fm.Marker([location_info['Delivery_location_latitude'],
                 location_info['Delivery_location_longitude']],
                 popup=location_info[['City', 'Road_traffic_density']]).add_to(mapa)

    folium_static(mapa, width = 800, height = 600)



















































































