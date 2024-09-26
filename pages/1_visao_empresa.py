
# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image


# biblioteca necessaria
import folium
import pandas as pd
import streamlit as st

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

df = pd.read_csv( '../dataset/train.csv' )

df1 = df.copy()

# 1. Convertendo a coluna Age de texto para número
linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['City'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Festival'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

# 2. Convertendo a coluna Ratings de texto para número decimal (float)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

# 3. Convertendo a coluna Order_data de texto para data
df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

# 4. Convertendo Multiple_deliveries de texto para número inteiro
linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

# 5. Removendo espaços dentro de strings/textos/objects (com for)
#df1 = df1.reset_index( drop=True )
#for i in range( len( df1 ) ):
#  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

# 6. Removendo espaços dentro de strings/textos/objects
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

# 7. Limpando a coluna Time_taken(min) por engano alterei no df
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )


# =========================================
# BARRA LATERAL NO STREAMLIT
# =========================================

st.header( 'Marketplace - Visão Empresa' )

#image_path = '/Users/macdamaripimenta/Documents/repos/ftc_python/target_loc.png'
image = Image.open( 'target_loc.png' )
st.sidebar.image( image, width=240 )

st.sidebar.markdown( '# Curry Company')
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

#st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Selecione uma data',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
    'Condições do trânsito',
    [ 'Low', 'Medium', 'High', 'Jam' ],
    default=[ 'Low', 'Medium', 'High', 'Jam' ] )

st.sidebar.markdown( """___""" )

st.sidebar.markdown( '***Powered by Comunidade DS***' )

# filtro de data
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

# filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]


# =========================================
# LAYOUT NO STREAMLIT
# =========================================

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ] )

with tab1:
    with st.container():
# 1. Quantidade de pedidos por dia - Order Metric
        st.markdown( '# Orders by Day' )
    
# Lista de colunas
        cols = ['ID', 'Order_Date']

# selecao de linhas - reseta o index para mudar o Order_Date de linhas para coluna
        df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()

# Desenhando o gráfico de colunas
        fig = px.bar( df_aux, x='Order_Date', y='ID')
        st.plotly_chart( fig, use_container_width=True )

# Segunda linha de gráficos
    col1, col2 = st.columns( 2 )
    with col1:
        st.header( 'Traffic Order Share' )
    # Distribuicao dos pedidos por tipo de tráfego
        df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
    
    # limpar dados
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    
    # criar coluna com porcentagem
        df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    # Desenhando gráfico de pizza
        fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
        st.plotly_chart( fig, use_container_width=True )
            
    with col2:
        st.header( 'Traffic Order City' )
    # Volume de pedido por cidade e tipo de tráfego
        # calcular volume de pedidos
        df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    
    # Limpando dados
        df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    # Desenhando gráfico de bolhas
        fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )
        st.plotly_chart( fig, use_container_width=True )    

with tab2:
    with st.container():
        st.markdown( '# Order by Week' )
        # criar coluna de semana
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
        
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        
        # Desenhando gráfico de linhas
        fig = px.line( df_aux, x='week_of_year', y='ID')
        st.plotly_chart( fig, use_container_width=True )
    with st.container():
        st.markdown( '# Order Share by Week' )
        # Quantidade de pedidos por semana / Número único de entregadires por semana

        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year' ).nunique().reset_index()
        
        # Como juntar 2 data frames
        df_aux = pd.merge( df_aux01, df_aux02, how='inner')
        
        # criando nova coluna com resultado da divisão dos data frames
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        
        # Desenhndo gráfico de linhas
        fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
        st.plotly_chart( fig, use_container_width=True )
        
with tab3:
    st.markdown( '# Country Maps' ) 
# Localização central de cada cidade por tipo de tráfego
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City', 'Road_traffic_density']).median().reset_index()
    
    # Limpando dados
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    # Desenhando gráfico de mapa na biblioteca Folium
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'], 
                      location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']]).add_to( map )
    
    folium_static( map, width=1024, height=600 )
    
    
    
    






    


