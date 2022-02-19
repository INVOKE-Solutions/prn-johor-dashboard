import streamlit as st
st.set_page_config(page_title='JOHOR PRN', page_icon="🗳️", layout='wide')
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




st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown("""
<link href='http://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;font-family: Lato, sans-serif;font-weight:400'>PRN Johor Dashboard</h1>", unsafe_allow_html=True)

# st.title("PRN Johor Dashboard")

#dun johor geojson
repo_url = 'https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/DUN/Johor_Syor_2_DUN_2017.geojson'
my_regions_geo_dun = requests.get(repo_url).json()

dun_dict = {}
dun_par_dict = {}

for i in range(len(my_regions_geo_dun['features'])):
    # lst_dun.append(my_regions_geo_dun['features'][i]['properties']['DUN'])
    final_str = str(my_regions_geo_dun['features'][i]['properties']['KodDUN'])

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_dict:
        dun_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = final_str

    if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_par_dict:
        dun_par_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = my_regions_geo_dun['features'][i]['properties']['Parliament']



#parliament johor geojson
repo_url = "https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/PAR/Johor_Syor_2_PAR_2017.geojson"
my_regions_geo_par = requests.get(repo_url).json()


lst_par = []
par_dict = {}

for i in range(len(my_regions_geo_par['features'])):
    lst_par.append(my_regions_geo_par['features'][i]['properties']['Parliament'])
    final_str = str(my_regions_geo_par['features'][i]['properties']['KodPar'])

    if my_regions_geo_par['features'][i]['properties']['Parliament'] not in par_dict:
        par_dict[my_regions_geo_par['features'][i]['properties']['Parliament']] = final_str



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


#for parliament will need to divide appropriately
# df



#sidebar
st.sidebar.header("Welcome @user")
choice = st.sidebar.selectbox("Choose by Parliamen/DUN",['Parliament', 'DUN'])

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
    # 'Non PH' : '#FFF5EE',
    # 'Not Sure/Others': '#DC143C',
    # },
    basemap_visible = False,
    scope="asia",
    # title = "Map of Johor DUN",
    )

    fig.update_layout(showlegend=False)

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
    scope="asia",
    )

    fig.update_layout(showlegend=False)
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



#an expander widget to display all the dun/par % --> table
#to create a widget automatically
# @st.cache(suppress_st_warning=True)
# def custom_expander_dun(df):
#     idc = df.index.to_list()
#     with st.expander(df.loc[idc[0], 'DUN No'] + " " + str(df.loc[idc[0], 'DUN'])):
#
#             col1, col2 = st.columns(2)
#             with col1:
#
#                 st.subheader('PH ' + str(df.loc[idc[0], 'PH']) + "%")
#                 st.subheader('Non-PH ' + str(df.loc[idc[0], 'Non-PH']) + "%")
#                 st.subheader('Not Sure/Others ' + str(df.loc[idc[0], 'Not Sure/Others']) + "%")
#
#             with col2:
#                 st.info("Demographics")
#
# #need to take into accoun that a parliament has several duns under it --> will need to divide properly
# def custom_expander_par(df):
#     idc = df.index.to_list()
#     with st.expander(df.loc[idc[0], 'Par No'] + " " + str(df.loc[idc[0], 'Parliament'])):
#
#         col1, col2 = st.columns(2)
#         with col1:
#
#             st.subheader('PH ' + str(df.loc[idc[0], 'PH']) + "%")
#             st.subheader('Non-PH ' + str(df.loc[idc[0], 'Non-PH']) + "%")
#             st.subheader('Not Sure/Others ' + str(df.loc[idc[0], 'Not Sure/Others']) + "%")
#
#             with col2:
#                 st.info("Demographics")
#
#
#
# #customizing the show all button
# # m = st.markdown("""
# # <style>
# # div.stButton > button:first-child {
# #     color: #FFFFFF;
# #     border-radius: 20%;
# #     background-color: #B22222;
# #     height: 1.5em;
# #     width: 5em;
# #     position:relative;left:90%;
# #     font-size:20px
# # }
# # </style>""", unsafe_allow_html=True)
# if (choice == 'DUN'):
#     for d in lst_dun:
#         custom_expander_dun(df[df['DUN']==d])
#
# elif (choice == 'Parliament'):
#     for p in lst_par:
#         custom_expander_par(df[df['Parliament']==p])


#will create a card using boostrap incorporated into streamlit
def card_dun(header, ph_value, non_value, notsure_value):
    return f"""
        <div class="d-flex mt-5 justify-content-center" style="padding-left: 50px;">
			<div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[0]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[0]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[0]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[0]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
			<div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[1]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[1]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[1]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[1]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
            <div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[2]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[2]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[2]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[2]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
            <div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[3]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[3]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[3]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[3]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
            </div>
        </div>
    """


#susun in terms of 2
def card_par_2(header, ph_value, non_value, notsure_value):
    return f"""
        <div class="d-flex mt-5 justify-content-center" style="padding-left: 50px;">
			<div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[0]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[0]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[0]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[0]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
			<div class="card text-center" style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
				<div class="card-header" style="background-color: #DC143C;color: #FFFFFF">
                {header[1]}
                </div>
				<div class="list-group list-group-flush">
                    <a href="#" class="list-group-item" style="color: #000000"><strong>PH</strong>: {ph_value[1]}%
                    </a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Non-PH</strong>: {non_value[1]}%</a>
					<a href="#" class="list-group-item" style="color: #000000"><strong>Fence Sitter</strong>: {notsure_value[1]}%</a>
				</div>
                <div class="card-footer" style="text-align:left; background-color: #FFF5EE;">
                        <strong>Demographics <br> </strong>
                        Malay:  <br>
                        Chinese: <br>
                        Indian: <br>
                        Others: <br>
                </div>
			</div>
            <div style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
			</div>
            <div style="width: 20em;margin: auto;margin-right: 20px;margin-bottom: 20px;">
			</div>
        </div>

    """

st.markdown("""
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
""", unsafe_allow_html=True)

st.markdown("""
<html>
<head>
<script src="https://kit.fontawesome.com/365011cb0b.js" crossorigin="anonymous"></script>
</head>
</html>
""", unsafe_allow_html=True)

if (choice == 'DUN'):

    #sort by value of DUN no
    df.sort_values('DUN No', inplace=True)
    lst_dun = df['DUN'].tolist()
    for i in range(0, len(lst_dun)-1,4):


        header_lst = []
        ph_lst = []
        non_lst = []
        others_lst = []


        idc = df[df['DUN']==lst_dun[i]].index.to_list()
        final_str_1 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
        ph_val_1 = df.loc[idc[0], 'PH']
        non_val_1 = df.loc[idc[0], 'Non-PH']
        others_val_1 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['DUN']==lst_dun[i+1]].index.to_list()
        final_str_2 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
        ph_val_2 = df.loc[idc[0], 'PH']
        non_val_2 = df.loc[idc[0], 'Non-PH']
        others_val_2 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['DUN']==lst_dun[i+2]].index.to_list()
        final_str_3 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
        ph_val_3 = df.loc[idc[0], 'PH']
        non_val_3 = df.loc[idc[0], 'Non-PH']
        others_val_3 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['DUN']==lst_dun[i+3]].index.to_list()
        final_str_4 = 'N' + df.loc[idc[0], 'DUN No'] + ' ' + str(df.loc[idc[0], 'DUN'])
        ph_val_4 = df.loc[idc[0], 'PH']
        non_val_4 = df.loc[idc[0], 'Non-PH']
        others_val_4 = df.loc[idc[0], 'Not Sure/Others']


        header_lst.extend([final_str_1, final_str_2, final_str_3, final_str_4])
        ph_lst.extend([ph_val_1, ph_val_2, ph_val_3, ph_val_4])
        ph_lst = [round(num) for num in ph_lst]
        non_lst.extend([non_val_1, non_val_2, non_val_3, non_val_4])
        non_lst = [round(num) for num in non_lst]
        others_lst.extend([others_val_1, others_val_2, others_val_3, others_val_4])
        others_lst = [round(num) for num in others_lst]

        st.markdown(card_dun(
        header_lst, ph_lst, non_lst, others_lst
        ), unsafe_allow_html=True)

elif (choice == 'Parliament'):

    #sort by value of Par no
    df.sort_values('Par No', inplace=True)
    # st.write(df)

    #sort based on the parliament kod no
    par_dict = {k: v for k, v in sorted(par_dict.items(), key=lambda item: item[1])}

    lst_par = list(par_dict.keys())


    # do in mult of 4 then check if last 2 then 2 je
    for i in range(0,len(lst_par)-3, 4):

        header_lst = []
        ph_lst = []
        non_lst = []
        others_lst = []

        idc = df[df['Parliament']==lst_par[i]].index.to_list()
        final_str_1 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_1 = df.loc[idc[0], 'PH']
        non_val_1 = df.loc[idc[0], 'Non-PH']
        others_val_1 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['Parliament']==lst_par[i+1]].index.to_list()
        final_str_2 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_2 = df.loc[idc[0], 'PH']
        non_val_2 = df.loc[idc[0], 'Non-PH']
        others_val_2 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['Parliament']==lst_par[i+2]].index.to_list()
        final_str_3 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_3 = df.loc[idc[0], 'PH']
        non_val_3 = df.loc[idc[0], 'Non-PH']
        others_val_3 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['Parliament']==lst_par[i+3]].index.to_list()
        final_str_4 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_4 = df.loc[idc[0], 'PH']
        non_val_4 = df.loc[idc[0], 'Non-PH']
        others_val_4 = df.loc[idc[0], 'Not Sure/Others']

        header_lst.extend([final_str_1, final_str_2, final_str_3, final_str_4])
        ph_lst.extend([ph_val_1, ph_val_2, ph_val_3, ph_val_4])
        ph_lst = [round(num) for num in ph_lst]
        non_lst.extend([non_val_1, non_val_2, non_val_3, non_val_4])
        non_lst = [round(num) for num in non_lst]
        others_lst.extend([others_val_1, others_val_2, others_val_3, others_val_4])
        others_lst = [round(num) for num in others_lst]

        st.markdown(card_dun(
        header_lst, ph_lst, non_lst, others_lst
        ), unsafe_allow_html=True)


    for i in range(0, len(lst_par[-2:])-1,2):
        header_lst = []
        ph_lst = []
        non_lst = []
        others_lst = []

        idc = df[df['Parliament']==lst_par[i]].index.to_list()
        final_str_1 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_1 = df.loc[idc[0], 'PH']
        non_val_1 = df.loc[idc[0], 'Non-PH']
        others_val_1 = df.loc[idc[0], 'Not Sure/Others']

        idc = df[df['Parliament']==lst_par[i+1]].index.to_list()
        final_str_2 = 'P' + df.loc[idc[0], 'Par No'] + ' ' + str(df.loc[idc[0], 'Parliament'])
        ph_val_2 = df.loc[idc[0], 'PH']
        non_val_2 = df.loc[idc[0], 'Non-PH']
        others_val_2 = df.loc[idc[0], 'Not Sure/Others']

        header_lst.extend([final_str_1, final_str_2])
        ph_lst.extend([ph_val_1, ph_val_2])
        ph_lst = [round(num) for num in ph_lst]
        non_lst.extend([non_val_1, non_val_2])
        non_lst = [round(num) for num in non_lst]
        others_lst.extend([others_val_1, others_val_2])
        others_lst = [round(num) for num in others_lst]

        st.markdown(card_par_2(
        header_lst, ph_lst, non_lst, others_lst
        ), unsafe_allow_html=True)
