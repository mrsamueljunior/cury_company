import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home'
)

#image_path = 'C:/Users/9SAMJUNI/Documents/ComunidadeDS/img/img-python.png'
image = Image.open('img-python.png')
st.sidebar.image(image, width=50)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write( "# Curry Company Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como Utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de Geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
        - @meigarom    

    """

)