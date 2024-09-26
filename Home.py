import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)

#image_path = '/Users/macdamaripimenta/Documents/repos/ftc_python/'
image = Image.open( 'target_loc.png' )
st.sidebar.image( image, width=240 )

st.sidebar.markdown( '# Curry Company')
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.write( '# Curry Company Grouth Dashboard' )

st.markdown(
    """
    Este Dashboard foi constituído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes cadastrados na empresa de delivery Curry Company.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
        mariana.heitzp@gmail.com
    """ )