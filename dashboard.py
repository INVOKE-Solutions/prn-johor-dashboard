import streamlit as st
st.set_page_config(page_title='JOHOR PRN', page_icon="🗳️", layout='wide')
import pandas as pd
import datetime
import chart_studio.plotly as py
import plotly.graph_objs as go
# import plotly.graph_objs as pg
import plotly.express as px
import numpy as np
import requests
import matplotlib.pyplot as plt
from plotly.graph_objects import Layout
import streamlit.components.v1 as components

# %matplotlib inline



st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)



st.markdown("<h1 style='text-align: center; color: black;'>PRN Johor Dashboard</h1>", unsafe_allow_html=True)

# st.title("PRN Johor Dashboard")

#dun johor geojson
repo_url = 'https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/DUN/Johor_Syor_2_DUN_2017.geojson'
my_regions_geo_dun = requests.get(repo_url).json()

lst_dun = []
lst_dun_no = []
dun_dict = {}
dun_par_dict = {}

for i in range(len(my_regions_geo_dun['features'])):
    lst_dun.append(my_regions_geo_dun['features'][i]['properties']['DUN'])
    final_str = "N" + str(my_regions_geo_dun['features'][i]['properties']['KodDUN'])
    lst_dun_no.append(final_str)

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_dict:
        dun_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = final_str

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_par_dict:
        dun_par_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = my_regions_geo_dun['features'][i]['properties']['Parliament']

# st.write(dun_par_dict)
# st.write(dun_dict)

#parliament johor geojson
repo_url = "https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/PAR/Johor_Syor_2_PAR_2017.geojson"
my_regions_geo_par = requests.get(repo_url).json()

lst_par = []
lst_par_no = []
par_dict = {}

for i in range(len(my_regions_geo_par['features'])):
    lst_par.append(my_regions_geo_par['features'][i]['properties']['Parliament'])
    final_str = "P" + str(my_regions_geo_par['features'][i]['properties']['KodPar'])
    lst_par_no.append(final_str)

    if my_regions_geo_par['features'][i]['properties']['Parliament'] not in par_dict:
        par_dict[my_regions_geo_par['features'][i]['properties']['Parliament']] = final_str


# st.write(lst_par)
# st.write(par_dict)


df = pd.read_excel("Johor PRN.xlsx", sheet_name='transposed')
df['PH'].replace(np.nan, 0, inplace=True)
df['Non-PH'].replace(np.nan, 0, inplace=True)
df['Not Sure/Others'].replace(np.nan, 0, inplace=True)


#recalculate the % to take into acount only the 3 columns
def recalculate_nonph(x):
    non_ph = x['Non-PH']
    not_sure = x['Not Sure/Others']
    ph = x['PH']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_1 = (non_ph*100) / total * 100
    return temp_1

def recalculate_notsure(x):
    non_ph = x['Non-PH']
    not_sure = x['Not Sure/Others']
    ph = x['PH']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_2 = (not_sure*100) / total * 100
    return temp_2

def recalculate_ph(x):
    non_ph = x['Non-PH']
    not_sure = x['Not Sure/Others']
    ph = x['PH']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_3 = (ph*100) / total * 100
    return temp_3



temp_nonph = df.apply(recalculate_nonph, axis=1)
temp_notsure = df.apply(recalculate_notsure, axis=1)
temp_ph = df.apply(recalculate_ph, axis=1)

df['Non-PH'] = temp_nonph
df['Not Sure/Others'] = temp_notsure
df['PH'] = temp_ph

# df = df.drop('Refused to answer', axis=1)
df = df.loc[:, df.columns.drop('Refuse to answer')]


idc = df[df['DUN']=='LAYANG-LAYANG'].index.to_list()
df.loc[idc[0], 'DUN'] = 'LAYANG - LAYANG'

idc = df[df['DUN']=='KOTA ISKANDAR'].index.to_list()
df.loc[idc[0], 'DUN'] = 'ISKANDAR PUTERI'


df['Non-PH'] = round(df['Non-PH'], 2)
df['PH'] = round(df['PH'], 2)
df['Not Sure/Others'] = round(df['Not Sure/Others'], 2)
# st.write(df[df['DUN']=='KOTA ISKANDAR'])

#layang2 ada beza space with the one in geojson file
df['predicted_win'] = df[['Non-PH','Not Sure/Others','PH']].idxmax(axis=1)



#will add the dun no to the df as an extra column
idc = df.index.to_list()
for i in idc:
    df.loc[i, 'DUN No'] = dun_dict[df.loc[i,'DUN']]

#will add parliament
idc = df.index.to_list()
for i in idc:
    df.loc[i, 'Parliament'] = dun_par_dict[df.loc[i, 'DUN']]

#will add parliament no
idc = df.index.to_list()
for i in idc:
    df.loc[i, 'Par No'] = par_dict[df.loc[i,'Parliament']]


#rearrange the columns
df = df[['Parliament','Par No','DUN','DUN No','PH','Non-PH','Not Sure/Others','predicted_win']]
# st.write(df)

st.sidebar.header("Welcome @user")
# st.sidebar.image("meniaga.png", width=200)
choice = st.sidebar.selectbox("Choose by Parliamen/DUN",['Parliament', 'DUN'])



# choice = st.selectbox("Choose one", ['Parliament', 'DUN'])

if choice == "DUN":
    fig = px.choropleth(data_frame=df,
    geojson=my_regions_geo_dun,
    locations='DUN', # name of dataframe column
    featureidkey='properties.DUN',  # path to field in GeoJSON feature object with which to match the values passed in to locations
    color = df['predicted_win'],
    hover_name = 'DUN',
    # hover_data =['DUN','Non-PH','Not Sure/Others','PH'],
    custom_data = ['DUN','Non-PH','Not Sure/Others','PH'],
    labels = {'predicted_win': 'win'},
    # color_discrete_map = {
    # 'PH' : 'lightgray',
    # 'Non PH' : 'mediumseagreen',
    # 'Not Sure/Others': 'mediumseagreen',
    # },
    basemap_visible = False,
    scope="asia",
    # title = "Map of Johor DUN",
    )


    fig.update_geos(fitbounds="locations")

    #<extra></extra> tag remove the secondary box
    fig.update_traces(
    hovertemplate="<br>".join([
    "%{customdata[0]}",
    "PH: %{customdata[3]}%",
    "Non-PH: %{customdata[1]}%",
    "Not Sure/Others: %{customdata[2]}% <extra></extra>",
    ]))


    fig.add_scattergeo(
    geojson=my_regions_geo_dun,
    locations = df['DUN'],
    text = df['DUN No'],
    featureidkey="properties.DUN",
    mode = 'text',
    textfont = dict(size=14, color='white'),
    textposition='middle center',
    )

    fig.update_traces(marker_line_width=0.75, marker_opacity=0.8)

#parliament
else:
    fig = px.choropleth(data_frame=df,
    geojson=my_regions_geo_par,
    locations='Parliament', # name of dataframe column
    featureidkey='properties.Parliament',  # path to field in GeoJSON feature object with which to match the values passed in to locations
    color = df['predicted_win'],
    hover_name = 'Parliament',
    custom_data = ['Parliament','Non-PH','Not Sure/Others','PH'],
    labels = {'predicted_win': 'win'},
    # color_discrete_map = {
    # 'PH' : 'lightgray',
    # 'Non PH' : 'mediumseagreen',
    # 'Not Sure/Others': 'mediumseagreen',
    # },
    basemap_visible = False,
    # projection = 'mercator',
    scope="asia",
    # title = "Map of Johor Parliament",
    )
    fig.update_geos(fitbounds="locations")

    fig.update_traces(hovertemplate="<br>".join([
    "%{customdata[0]}",
    "PH: %{customdata[3]}%",
    "Non-PH: %{customdata[1]}%",
    "Not Sure/Others: %{customdata[2]}% <extra></extra>",
    ]))

    fig.add_trace(go.Scattergeo(
    geojson=my_regions_geo_par,
    locations = df['Parliament'],
    text = df['Par No'],
    featureidkey="properties.Parliament",
    mode = 'text',
    textfont = dict(size=14, color='white'),
    textposition='top left'
    ))

    fig.update_traces(marker_line_width=0.75, marker_opacity=0.8)


# fig.update_layout(plot_bgcolor='rgb(240, 248, 255)')
fig.update_layout(width=1300,height=700)

st.plotly_chart(fig, use_container_width=True)


#
#
# str = "HELLO"
# components.html(
#     """
#     <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
#     <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
#     <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
#     <style>
#     .firstdiv {
#     background-color: lightgrey;
#     width: 1600px;
#     height: 300px;
#     border: 15px solid green;
#     padding: 50px;
#     margin-bottom: 10px;
#     }
#
#     .seconddiv {
#     background-color: lightgrey;
#     width: 1600px;
#     height: 300px;
#     border: 15px solid green;
#     padding: 50px;
#     margin-bottom: 10px;
#     }
#
#     </style>
#     <div>
#         <div class='firstdiv'>
#         Hello world!
#         </div>
#
#         <div class='seconddiv'>
#         WHta
#         </div>
#     </div>
#
#     """,
#     height=1000,
# )
#

#will add a tick that shows which won
#to create a widget automatically
# @st.cache(suppress_st_warning=True)
def custom_expander_dun(df):
    idc = df.index.to_list()
    with st.expander(df.loc[idc[0], 'DUN No'] + " " + str(df.loc[idc[0], 'DUN'])):

            col1, col2 = st.columns(2)
            with col1:

                st.subheader('PH ' + str(df.loc[idc[0], 'PH']) + "%")
                st.subheader('Non-PH ' + str(df.loc[idc[0], 'Non-PH']) + "%")
                st.subheader('Not Sure/Others ' + str(df.loc[idc[0], 'Not Sure/Others']) + "%")

            with col2:
                st.info("Demographics")

#need to take into accoun that a parliament has several duns under it --> will need to divide properly
def custom_expander_par(df):
    idc = df.index.to_list()
    with st.expander(df.loc[idc[0], 'Par No'] + " " + str(df.loc[idc[0], 'Parliament'])):

        col1, col2 = st.columns(2)
        with col1:

            st.subheader('PH ' + str(df.loc[idc[0], 'PH']) + "%")
            st.subheader('Non-PH ' + str(df.loc[idc[0], 'Non-PH']) + "%")
            st.subheader('Not Sure/Others ' + str(df.loc[idc[0], 'Not Sure/Others']) + "%")

            with col2:
                st.info("Demographics")



#customizing the show all button
# m = st.markdown("""
# <style>
# div.stButton > button:first-child {
#     color: #FFFFFF;
#     border-radius: 20%;
#     background-color: #B22222;
#     height: 1.5em;
#     width: 5em;
#     position:relative;left:90%;
#     font-size:20px
# }
# </style>""", unsafe_allow_html=True)
#
# b = st.button("Show All")
# if b and (choice == 'DUN'):
if (choice == 'DUN'):
    for d in lst_dun:
        custom_expander_dun(df[df['DUN']==d])

elif (choice == 'Parliament'):
    for p in lst_par:
        custom_expander_par(df[df['Parliament']==p])
