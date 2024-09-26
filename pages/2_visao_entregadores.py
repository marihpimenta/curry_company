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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )

df = pd.read_csv( 'dataset/train.csv' )

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

st.header( 'Marketplace - Visão Entregadores' )

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

weather_conditions = st.sidebar.multiselect(
    'Condições do clima',
    [ 'conditions Sunny', 'conditions Cloudy', 'conditions Windy', 'conditions Fog', 'conditions Stormy', 'conditions Sandstorms' ],
    default=[ 'conditions Sunny', 'conditions Cloudy', 'conditions Windy', 'conditions Fog', 'conditions Stormy', 'conditions Sandstorms' ] )

st.sidebar.markdown( """___""" )

st.sidebar.markdown( '***Powered by Comunidade DS***' )

# filtro de data
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

# filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]

# filtro de clima
linhas_selecionadas = df1[ 'Weatherconditions' ].isin( weather_conditions )
df1 = df1.loc[ linhas_selecionadas, : ]

# =========================================
# LAYOUT NO STREAMLIT
# =========================================

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '', '' ] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[ :, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade )

        with col2:
            menor_idade = df1.loc[ :, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            melhor_condicao_veiculo = df1.loc[ :, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição de veículo', melhor_condicao_veiculo )

        with col4:
            pior_condicao_veiculo = df1.loc[ :, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição de veículo', pior_condicao_veiculo )

    with st.container():
        st.markdown( """___""" )
        st.title( 'Avaliações' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por entregador' )
            df_avr_ratings_person = ( df1.loc[ :, [ 'Delivery_person_ID', 'Delivery_person_Ratings' ]].groupby( 'Delivery_person_ID' ).mean().reset_index() )
            st.dataframe( df_avr_ratings_person )
            
        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            df_avr_std_ratings_by_traffic = (df1.loc[ :, ['Delivery_person_Ratings', 'Road_traffic_density' ]]
                                                 .groupby('Road_traffic_density')
                                                 .agg( {'Delivery_person_Ratings' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_ratings_by_traffic.columns = ['Delivery_means', 'Delivery_std']
            #reset do index
            df_avr_std_ratings_by_traffic.reset_index()

            st.dataframe( df_avr_std_ratings_by_traffic ) 
            
            st.markdown( '##### Avaliação média por clima' )
            df_avr_std_ratings_by_weather = (df1.loc[ :, ['Delivery_person_Ratings', 'Weatherconditions' ]]
                                                 .groupby('Weatherconditions')
                                                 .agg( {'Delivery_person_Ratings' : ['mean', 'std']}))
            # mudança de nome das colunas
            df_avr_std_ratings_by_weather.columns = ['Delivery_means', 'Delivery_std']
            #reset do index
            df_avr_std_ratings_by_weather.reset_index()

            st.dataframe( df_avr_std_ratings_by_weather ) 

    with st.container():
        st.markdown( """___""" )
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Top Entregadores Mais Rápidos' )
            df2 = ( df1.loc[ :, [ 'Delivery_person_ID', 'City', 'Time_taken(min)' ] ]
                        .groupby( ['City', 'Delivery_person_ID'])
                        .min()
                        .sort_values(['City', 'Time_taken(min)'], ascending=True)
                        .reset_index() )

            df_aux01 = df2.loc[df2[ 'City' ] == 'Metropolitian', : ].head(10)
            df_aux02 = df2.loc[df2[ 'City' ] == 'Urban', : ].head(10)
            df_aux03 = df2.loc[df2[ 'City' ] == 'Semi-Urban', : ].head(10)

            df3 = pd.concat( [ df_aux01, df_aux02, df_aux03]).reset_index( drop=True )
            st.dataframe( df3 ) 

        with col2:
            st.markdown( '##### Top Entregadores Mais Lentos' )
            df2 = ( df1.loc[ :, [ 'Delivery_person_ID', 'City', 'Time_taken(min)' ] ]
                       .groupby( ['City', 'Delivery_person_ID'] )
                       .max()
                       .sort_values( ['City', 'Time_taken(min)'], ascending=False )
                       .reset_index() )

            df_aux01 = df2.loc[df2[ 'City' ] == 'Metropolitian', : ].head(10)
            df_aux02 = df2.loc[df2[ 'City' ] == 'Urban', : ].head(10)
            df_aux03 = df2.loc[df2[ 'City' ] == 'Semi-Urban', : ].head(10)
            
            df3 = pd.concat( [ df_aux01, df_aux02, df_aux03]).reset_index( drop=True )
            st.dataframe( df3 )
            
