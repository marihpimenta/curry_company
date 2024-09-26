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
import numpy as np

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

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

# LEMBRAR DE LIMPAR A COLUNA WEATHER (tirar o condition)


# =========================================
# BARRA LATERAL NO STREAMLIT
# =========================================

st.header( 'Marketplace - Visão Restaurantes' )

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

city_options = st.sidebar.multiselect(
    'Cidades',
    [ 'Metropolitian', 'Semi-Urban', 'Urban' ],
    default=[ 'Metropolitian', 'Semi-Urban', 'Urban' ] )

st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
    'Condições do trânsito',
    [ 'Low', 'Medium', 'High', 'Jam' ],
    default=[ 'Low', 'Medium', 'High', 'Jam' ] )

#st.sidebar.markdown( """___""" )

#weather_conditions = st.sidebar.multiselect(
#    'Condições do clima',
#    [ 'conditions Sunny', 'conditions Cloudy', 'conditions Windy', 'conditions Fog', 'conditions Stormy', 'conditions Sandstorms' ],
#    default=[ 'conditions Sunny', 'conditions Cloudy', 'conditions Windy', 'conditions Fog', 'conditions Stormy', 'conditions Sandstorms' ] )

st.sidebar.markdown( """___""" )

st.sidebar.markdown( '***Powered by Mariana Heitz***' )

# filtro de data
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

# filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]

# filtro de clima
#linhas_selecionadas = df1[ 'Weatherconditions' ].isin( weather_conditions )
#df1 = df1.loc[ linhas_selecionadas, : ]

# =========================================
# LAYOUT NO STREAMLIT
# =========================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', '' ] )

with tab1:
    with st.container():
        st.title( 'Informações Gerais' )

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )

        with col1:
            delivery_unique = len( df1.loc[ :, 'Delivery_person_ID'].unique())
            col1.metric( 'Entregadores', delivery_unique )

        with col2:
            cols = [ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply( lambda x:
                            haversine(
                                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = np.round( df1['distance'].mean(), 2 )

            col2.metric( 'Distância média', avg_distance )
            

        with col3:
            df_avr_std_time = ( df1.loc[ :, [ 'Time_taken(min)', 'Festival' ]  ]
                                .groupby('Festival')
                                .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            df_avr_std_time = np.round( df_avr_std_time.loc[df_avr_std_time['Festival'] == 'Yes', 'Time_means'], 2 )
            col3.metric( 'Tempo médio durante os Festivais', df_avr_std_time )
            
        with col4:
            df_avr_std_time = ( df1.loc[ :, [ 'Time_taken(min)', 'Festival' ]  ]
                                .groupby('Festival')
                                .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            df_avr_std_time = np.round( df_avr_std_time.loc[df_avr_std_time['Festival'] == 'Yes', 'Time_std'], 2 )
            col4.metric( 'Desvio padrão durante os Festivais', df_avr_std_time )

        with col5:
            df_avr_std_time = ( df1.loc[ :, [ 'Time_taken(min)', 'Festival' ]  ]
                                .groupby('Festival')
                                .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            df_avr_std_time = np.round( df_avr_std_time.loc[df_avr_std_time['Festival'] == 'No', 'Time_means'], 2 )
            col5.metric( 'Tempo médio fora dos Festivais', df_avr_std_time )

        with col6:
            df_avr_std_time = ( df1.loc[ :, [ 'Time_taken(min)', 'Festival' ]  ]
                                .groupby('Festival')
                                .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            df_avr_std_time = np.round( df_avr_std_time.loc[df_avr_std_time['Festival'] == 'No', 'Time_std'], 2 )
            col6.metric( 'Desvio padrão fora dos Festivais', df_avr_std_time )

    with st.container():
        st.markdown( """___""" )
        st.title( 'Distribuição por Tempo e Distância' )
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Tempo médio e o desvio padrão de entrega por cidade' )
            df_avr_std_time = df1.loc[ :, [ 'City', 'Time_taken(min)' ] ].groupby('City').agg( {'Time_taken(min)' : ['mean', 'std']})
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            
            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control', 
                                    x=df_avr_std_time['City'], 
                                    y=df_avr_std_time[ 'Time_means'],
                                    error_y=dict( type='data', array=df_avr_std_time['Time_std'])))
            
            fig.update_layout( barmode='group')
            st.plotly_chart( fig )

        with col2:
            st.markdown( '##### Tempo médio e desvio padrão de entrega por cidade e tipo de pedido' )
            df_avr_std_time = ( df1.loc[ :,  ['City', 'Time_taken(min)', 'Type_of_order' ]]
                                .groupby(['City', 'Type_of_order' ])
                                .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
    
            st.dataframe( df_avr_std_time )

    with st.container():
        
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '##### Tempo médio de entrega por cidade' )
            cols = [ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    
            df1['distance'] = df1.loc[:, cols].apply( lambda x:
                                        haversine(
                                                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
            
            avg_distance = df1.loc[ :, ['City', 'distance' ]].groupby( 'City' ).mean().reset_index()
            fig = go.Figure( data=[ go.Pie( labels=avg_distance[ 'City' ], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart( fig )
            
        with col2:
            st.markdown( '##### Tempo médio e desvio padrão de entrega por cidade e condição de tráfego' )
            cols = [ 'City', 'Time_taken(min)', 'Road_traffic_density' ]
            df_avr_std_time = ( df1.loc[ :, [ 'City', 'Time_taken(min)', 'Road_traffic_density' ] ]
                                   .groupby(['City', 'Road_traffic_density' ])
                                   .agg( {'Time_taken(min)' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_time.columns = ['Time_means', 'Time_std']
            #reset do index
            df_avr_std_time = df_avr_std_time.reset_index()
            
            fig = px.sunburst( df_avr_std_time, path=['City', 'Road_traffic_density'], values='Time_means', color='Time_std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_avr_std_time['Time_std']))
            
            st.plotly_chart( fig )

 