import streamlit as st
st.set_page_config(page_title='JOHOR PRN', page_icon="🗳️")
import pandas as pd
import datetime
import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import requests
import matplotlib.pyplot as plt
from plotly.graph_objects import Layout
import streamlit.components.v1 as components
import collections
import pyautogui



#to be commented
#to hide the menu bar on the streamlit page
# st.markdown(""" <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style> """, unsafe_allow_html=True)

st.markdown("""
<link href='http://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
""", unsafe_allow_html=True)

#the header with the line
st.markdown("<h2 style='height: 2em;overflow:auto;color: #4682B4;font-size:25px;border-bottom: 1px solid #ccc;font-family: Lato, sans-serif;font-weight:900;padding-top: 0%'>PRN Johor Dashboard</h2>", unsafe_allow_html=True)


#import the dun johor geojson file to plot the coordinates for dun border
repo_url = 'https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/DUN/Johor_Syor_2_DUN_2017.geojson'
my_regions_geo_dun = requests.get(repo_url).json()

dun_dict = {}
dun_par_dict = {}

for i in range(len(my_regions_geo_dun['features'])):
    final_str = str(my_regions_geo_dun['features'][i]['properties']['KodDUN'])

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_dict:
        dun_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = final_str

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_par_dict:
        dun_par_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = my_regions_geo_dun['features'][i]['properties']['Parliament']



#import the results from the model
df = pd.read_excel("Johor PRN.xlsx", sheet_name='transposed')
df = df.rename({'PH': 'PH_1', 'Non-PH': 'Non-PH_1', 'Not Sure/Others': 'Not Sure/Others_1'}, axis=1)

df['PH_1'].replace(np.nan, 0, inplace=True)
df['Non-PH_1'].replace(np.nan, 0, inplace=True)
df['Not Sure/Others_1'].replace(np.nan, 0, inplace=True)


#recalculate the % to take into acount only the 3 columns
#because in the original sample data the % include PH, non PH, fence sitter and refused to answer
#the new model will only output % for PH and Non PH---------------------------------------------can remove from this point onwards
def recalculate_nonph(x):
    non_ph = x['Non-PH_1']
    not_sure = x['Not Sure/Others_1']
    ph = x['PH_1']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_1 = (non_ph*100) / total * 100
    return temp_1

def recalculate_notsure(x):
    non_ph = x['Non-PH_1']
    not_sure = x['Not Sure/Others_1']
    ph = x['PH_1']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_2 = (not_sure*100) / total * 100
    return temp_2

def recalculate_ph(x):
    non_ph = x['Non-PH_1']
    not_sure = x['Not Sure/Others_1']
    ph = x['PH_1']

    total = (non_ph*100) + (not_sure*100) + (ph*100)
    temp_3 = (ph*100) / total * 100
    return temp_3



temp_nonph = df.apply(recalculate_nonph, axis=1)
temp_notsure = df.apply(recalculate_notsure, axis=1)
temp_ph = df.apply(recalculate_ph, axis=1)

df['Non-PH_1'] = temp_nonph
df['Not Sure/Others_1'] = temp_notsure
df['PH_1'] = temp_ph

df = df.loc[:, df.columns.drop('Refuse to answer')]
#-------------------------------------------------------------------------------


#the goejson file contains error on the iskandar puteri side --> need to fix on the geojson file
idc = df[df['DUN']=='LAYANG-LAYANG'].index.to_list()
df.loc[idc[0], 'DUN'] = 'LAYANG - LAYANG'

idc = df[df['DUN']=='KOTA ISKANDAR'].index.to_list()
df.loc[idc[0], 'DUN'] = 'ISKANDAR PUTERI'

#round up the % value
df['Non-PH_1'] = round(df['Non-PH_1'])
df['PH_1'] = round(df['PH_1'])
df['Not Sure/Others_1'] = round(df['Not Sure/Others_1'])


#get the party that will win between PH and Non PH
df['predicted_win'] = df[['Non-PH_1','PH_1']].idxmax(axis=1)



#will add the dun no to the df as an extra column
idc = df.index.to_list()
for i in idc:
    df.loc[i, 'DUN No'] = dun_dict[df.loc[i,'DUN']]




#rearrange the columns
df = df[['DUN','DUN No','PH_1','Non-PH_1','predicted_win']]

#combine for header when hover over each dun
def combine_dun(x):
    return "N" + str(x['DUN No']) + " " + str(x['DUN'])

def combine_percent(x):
    return str(round(x)) + "%"


#this contain the % to be included in the map
df['DUN_str'] = df.apply(combine_dun, axis=1)
df['PH'] = df['PH_1'].apply(combine_percent)
df['Non-PH'] = df['Non-PH_1'].apply(combine_percent)
# df['Not Sure/Others'] = df['Not Sure/Others_1'].apply(combine_percent)


#experimenting wiht a better map --> px mapbox
st.cache(suppress_st_warning=True)
def create_map():
    fig = px.choropleth_mapbox(df, geojson=my_regions_geo_dun,
    locations='DUN',
    featureidkey="properties.DUN",
    mapbox_style="carto-positron",
    opacity=0.5,
    zoom=7,
    center = {"lat": 2.0301, "lon": 103.3185},
    color = df["predicted_win"],
    color_discrete_map = {
    'PH_1' : '#D0312D',
    'Non-PH_1' : '#0000CD',
    },
    hover_name='DUN_str',
    hover_data={'DUN No': False, 'predicted_win': False, 'DUN': False,'PH': True, 'Non-PH': True},
    )

    fig.update_geos(fitbounds="locations",visible=False)

    fig.add_scattergeo(
    geojson=my_regions_geo_dun,
    locations = df['DUN'],
    text = df['DUN No'],
    featureidkey="properties.DUN",
    mode = 'text')

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)



create_map()




# if (choice == 'DUN'):
#     fig = px.choropleth_mapbox(df, geojson=my_regions_geo_dun,
#     locations='DUN',
#     featureidkey="properties.DUN",
#     mapbox_style="carto-positron",
#     opacity=0.5,
#     zoom=7,
#     center = {"lat": 2.0301, "lon": 103.3185},
#     color = 'DUN',
#     # color_discrete_map = {
#     # 'PH' : '#00BFFF',
#     # 'Non PH' : '#000080',
#     # 'Not Sure/Others': '#DC143C',
#     # },
#     hover_name='DUN',
#     hover_data={'DUN No': False, 'predicted_win': False, 'DUN': False, 'PH': True, 'Non-PH': True, 'Not Sure/Others': True},
#     )
#
#     fig.add_scattergeo(
#         geojson=my_regions_geo_dun,
#         locations = df['DUN'],
#         text = 'DUN No',
#         featureidkey="properties.DUN",
#         mode = 'text',
#         textfont = dict(size=14, color='white'),
#         textposition='middle center',
#         )
#
#
# else:
#     fig = px.choropleth_mapbox(df, geojson=my_regions_geo_par,
#     locations='Parliament',
#     featureidkey="properties.Parliament",
#     mapbox_style="carto-positron",
#     opacity=0.5,
#     zoom=7,
#     center = {"lat": 2.0301, "lon": 103.3185},
#     # color = 'predicted_win',
#     # color_discrete_map = {
#     # 'PH' : 'red',
#     # 'Non PH' : 'yello',
#     # 'Not Sure/Others': 'green',
#     # },
#     hover_name='Parliament',
#     hover_data={'Par No': False, 'predicted_win': False, 'Parliament': False, 'PH': True, 'Non-PH': True, 'Not Sure/Others': True},
#     )
#
#     fig.add_scattergeo(
#         geojson=my_regions_geo_dun,
#         locations = df['Parliament'],
#         text = 'Par No',
#         featureidkey="properties.Parliament",
#         mode = 'text',
#         textfont = dict(size=14, color='white'),
#         textposition='middle center',
#         )




st.cache(suppress_st_warning=True)
def card_dun(header, ph_value, non_value, color_lst):
    return f"""
    <div class="mx-auto" style="padding-bottom: 10%">
            <div class="card" style="margin: 3%">
              <div class="card-header" style="background-color: {color_lst};color: #FFFFFF">
                      {header}
                      </div>
                      <div class='container'>
                          <div class="row" style="padding: auto;margin: auto">
                              <div class="col-7" style="padding: 4%;margin: auto;border-bottom: 1px solid #CCD">
                                      <div style="color: #000000"><strong>PH</strong>
                                          <div class="progress" style="border-radius: 8px;height: 15px">
                                              <div class="progress-bar" role="progressbar" style="width: {ph_value}%;background-color: #D0312D" aria-valuenow={ph_value} aria-valuemin="0" aria-valuemax="100"></div>
                                          </div>
                                      </div>
                              </div>
                              <div class="col-5" style="padding: 0%;margin:auto; text-align: center;margin-bottom: -1%;">
                                      <p class='progress-label'>
                                      {ph_value}%
                                      </p>
                              </div>
                          </div>
                          <div class="row" style="padding: auto;margin: auto">
                              <div class="col-7" style="padding: 4%;margin: auto;border-bottom: 1px">
                                      <div style="color: #000000"><strong>Non-PH</strong>
                                          <div class="progress" style="border-radius: 8px;height: 15px">
                                              <div class="progress-bar" role="progressbar" style="width: {non_value}%;background-color: #0000CD" aria-valuenow={non_value} aria-valuemin="0" aria-valuemax="100"></div>
                                          </div>
                                      </div>
                              </div>
                              <div class="col-5" style="padding: 5%;margin:auto; text-align: center;margin-bottom: 1%;">
                                      <div class='progress-label'>
                                      {non_value}%
                                      </div>
                              </div>
                          </div>
                      </div>
                      <div class="card-footer mt-10" style="text-align:left; background-color: #FFF5EE;">
                          <strong>Demographics <br> </strong>
                          Malay:  <br>
                          Chinese: <br>
                          Indian: <br>
                          Others: <br>
                      </div>
                  </div>
              </div>

      """



st.markdown("""
<link href="https://maxcdn.bootstrapcdn.com/font-awesome/6.0.0/css/font-awesome.min.css" rel="stylesheet"/>
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# <l



def return_color(predict):
    if predict == 'PH':
        return '#D0312D' #red
    else:
        return '#0000CD' #blue


# st.subheader("Prediction for State Seats")
# st.markdown("<h3 style='height: 2em;padding: 0%;overflow:auto;font-size:25px;font-family: Lato, sans-serif;font-weight:200;padding-top: 0%'>Prediction for State Seats</h3>", unsafe_allow_html=True)


def split_str(x):
    return x['predicted_win'].split("_")[0]
df['predicted_win'] = df.apply(split_str, axis=1)

#will place a multiselect widget
#will change here to show PH vs non PH
options = st.multiselect("State Seats Prediction Win:", ['PH','Non-PH'], ['PH','Non-PH'])

#get the df of ph vs non ph
df = df[df['predicted_win'].isin(options)]



    #sort by value of DUN no
df.sort_values('DUN No', inplace=True)
lst_dun = df['DUN'].tolist()

#to know the remainder left for column order
func_no = df.shape[0] % 3




for i in range(0, len(lst_dun)-1-func_no, 3):

    idc = df[df['DUN']==lst_dun[i]].index.to_list()
    final_str_1 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_1 = df.loc[idc[0], 'PH_1']
    non_val_1 = df.loc[idc[0], 'Non-PH_1']
    color_1 = return_color(df.loc[idc[0], 'predicted_win'])


    idc = df[df['DUN']==lst_dun[i+1]].index.to_list()
    final_str_2 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_2 = df.loc[idc[0], 'PH_1']
    non_val_2 = df.loc[idc[0], 'Non-PH_1']
    color_2 = return_color(df.loc[idc[0], 'predicted_win'])

    idc = df[df['DUN']==lst_dun[i+2]].index.to_list()
    final_str_3 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_3 = df.loc[idc[0], 'PH_1']
    non_val_3 = df.loc[idc[0], 'Non-PH_1']
    color_3 = return_color(df.loc[idc[0], 'predicted_win'])
    #
    # idc = df[df['DUN']==lst_dun[i+3]].index.to_list()
    # final_str_4 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    # ph_val_4 = df.loc[idc[0], 'PH_1']
    # non_val_4 = df.loc[idc[0], 'Non-PH_1']
    # others_val_4 = df.loc[idc[0], 'Not Sure/Others_1']
    # color_4 = return_color(df.loc[idc[0], 'predicted_win'])


    col1, col2, col3= st.columns(3)



    with col1:
        st.markdown(card_dun(
        final_str_1, round(ph_val_1), round(non_val_1), color_1
        ), unsafe_allow_html=True)


    with col2:
        st.markdown(card_dun(
        final_str_2, round(ph_val_2), round(non_val_2), color_2
        ), unsafe_allow_html=True)


    with col3:
        st.markdown(card_dun(
        final_str_3, round(ph_val_3), round(non_val_3), color_3
        ), unsafe_allow_html=True)


    # with col4:
    #     st.markdown(card_dun(
    #     final_str_4, round(ph_val_4), round(non_val_4), round(others_val_4), color_4
    #     ), unsafe_allow_html=True)



if func_no == 2:

    idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-4]].index.to_list()
    final_str_1 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_1 = df.loc[idc[0], 'PH_1']
    non_val_1 = df.loc[idc[0], 'Non-PH_1']
    color_1 = return_color(df.loc[idc[0], 'predicted_win'])


    idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-3]].index.to_list()
    final_str_2 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_2 = df.loc[idc[0], 'PH_1']
    non_val_2 = df.loc[idc[0], 'Non-PH_1']
    color_2 = return_color(df.loc[idc[0], 'predicted_win'])

    col1, col2, col3= st.columns(3)

    with col1:
        st.markdown(card_dun(
        final_str_1, round(ph_val_1), round(non_val_1), color_1
        ), unsafe_allow_html=True)


    with col2:
        st.markdown(card_dun(
        final_str_2, round(ph_val_2), round(non_val_2), color_2
        ), unsafe_allow_html=True)

    with col3:
        st.markdown("""

        """, unsafe_allow_html=True)

elif func_no == 1:
    idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-3]].index.to_list()
    final_str_1 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
    ph_val_1 = df.loc[idc[0], 'PH_1']
    non_val_1 = df.loc[idc[0], 'Non-PH_1']
    color_1 = return_color(df.loc[idc[0], 'predicted_win'])

    col1, col2, col3= st.columns(3)

    with col1:
        st.markdown(card_dun(
        final_str_1, round(ph_val_1), round(non_val_1), color_1
        ), unsafe_allow_html=True)


    with col2:
        st.markdown("""

        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""

        """, unsafe_allow_html=True)

else:
    pass
