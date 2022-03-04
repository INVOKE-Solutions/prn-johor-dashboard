import streamlit as st
st.set_page_config(page_title='JOHOR PRN', page_icon="🗳️")
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import matplotlib.pyplot as plt
from read_gsheets import *


#adding a login page
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["login"]["LOGIN_PASSWORD"]: #error point to this line!
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False


    if "password_correct" not in st.session_state:

        st.header("PRN Johor Dashboard")
        st.text_input(
        "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False

    else:
        # Password correct.
        return True


if check_password():
        # st.info("succesful")



        # to be commented
        # to hide the menu bar on the streamlit page
        st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

        st.markdown("""
        <link href='http://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
        """, unsafe_allow_html=True)

        #the header with the line
        st.markdown("<h2 style='height: 2em;overflow:auto;color: #000000;font-size:25px;border-bottom: 1px solid #ccc;font-family: Lato, sans-serif;font-weight:900;padding-top: 0%'>PRN Johor Dashboard</h2>", unsafe_allow_html=True)



        #import the dun johor geojson file to plot the coordinates for dun border
        #if put geojson file inside local will it be faster?
        repo_url = 'https://raw.githubusercontent.com/TindakMalaysia/Johor-Maps/master/2017/PROPOSAL/DUN/Johor_Syor_2_DUN_2017.geojson'
        my_regions_geo_dun = requests.get(repo_url).json()


        dun_dict = {}
        dun_par_dict = {}


        for i in range(len(my_regions_geo_dun['features'])):
            if (my_regions_geo_dun['features'][i]['properties']['DUN'] == 'ISKANDAR PUTERI'):
                my_regions_geo_dun['features'][i]['properties']['DUN'] = 'KOTA ISKANDAR'
            elif (my_regions_geo_dun['features'][i]['properties']['DUN'] == 'LAYANG - LAYANG'):
                my_regions_geo_dun['features'][i]['properties']['DUN'] = 'LAYANG-LAYANG'
            else:
                pass

        final_str = str(my_regions_geo_dun['features'][i]['properties']['KodDUN'])

        if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_dict:
            dun_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = final_str

        if my_regions_geo_dun['features'][i]['properties']['DUN'] not in dun_par_dict:
            dun_par_dict[my_regions_geo_dun['features'][i]['properties']['DUN']] = my_regions_geo_dun['features'][i]['properties']['Parliament']


        #import the results from the model
        #will place the model reustls in a private google sheet for restricted access
        # df = pd.read_excel("johor-prn-model-results2.xlsx",sheet_name="data (1)")
        sheet = open_access_gsheets()
        df = read_from_sheet(sheet, st.secrets['spreadsheet']['SPREADSHEET_ID'], "data")


        df['Predicted NON-PH'] = df['Predicted NON-PH'].astype(float)
        df['Predicted PH'] = df['Predicted PH'].astype(float)
        df['Non-PH_1'] = round(df['Predicted NON-PH'].apply(lambda x: x*100))
        df['PH_1'] = round(df['Predicted PH'].apply(lambda x: x*100))


        #get the party that will win between PH and Non PH
        df['predicted_win'] = df['Predicted Winner']

        #upper case the DUN column
        df['DUN'] = df['DUN'].apply(lambda x: x.upper())



        #combine for header when hover over each dun
        def combine_dun(x):
            return str(x['ID']) + " " + str(x['DUN'])

            #no need to combine with the %?
        def combine_percent(x):
            return str(round(x)) + "%"

        def round_val(x):
            return str(round(x))

        #to be included when hovering over the map
        df['DUN_str'] = df.apply(combine_dun, axis=1)

        df['PH'] = df['PH_1'].apply(combine_percent)
        df['Non-PH'] = df['Non-PH_1'].apply(combine_percent)

        df['PH_1'] = df['PH_1'].apply(round_val)
        df['Non-PH_1'] = df['Non-PH_1'].apply(round_val)

        #ethnicity value to be % and rounded off
        df['Malay'] = df['Malay'].astype(float)
        df['Chinese'] = df['Chinese'].astype(float)
        df['India'] = df['India'].astype(float)
        df['Others'] = df['Others'].astype(float)

        df['Malay'] = round(df['Malay'].apply(lambda x: x*100), 2)
        df['Chinese'] = round(df['Chinese'].apply(lambda x: x*100), 2)
        df['India'] = round(df['India'].apply(lambda x: x*100), 2)
        df['Others'] = round(df['Others'].apply(lambda x: x*100), 2)

        #the final df
        df = df[['ID', 'DUN','DUN_str','Malay','Chinese','India','Others','PH','PH_1','Non-PH','Non-PH_1','predicted_win']]


        #an expander if want to see map of overall?
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
            'PH Clear Win' : '#FF0000', #in descreasing shades of red
            'PH Tight Win' : '#DC143C',
            'PH Possible to Win':  '#FF5C5C',
            'Non-PH' : '#808080', #grey color
            },
            hover_name='DUN_str',
            hover_data={'PH': True, 'Non-PH': True, 'predicted_win': True, 'DUN': False},
            )

            fig.update_geos(fitbounds="locations",visible=False)

            fig.add_scattergeo(
            geojson=my_regions_geo_dun,
            locations = df['DUN'],
            text = df['DUN_str'],
            featureidkey="properties.DUN",
            mode = 'text')

            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)



        create_map()

        st.cache(suppress_st_warning=True)
        def card_dun(header, ph_value, non_value, color_lst, bumi, chi, ind, oth, win_label):
            return f"""
            <div class="mx-auto" style="padding-bottom: 10%">
            <div class="card" style="margin: 3%">
            <div class="card-header" style="background-color: {color_lst};color: #FFFFFF; text-align: center;">
            {header} <br>
            {win_label}
            </div>
            <div class='container'>
            <div class="row" style="padding: auto;margin: auto">
            <div class="col-7" style="padding: 4%;margin: auto;border-bottom: 1px solid #CCD">
            <div style="color: #000000"><strong>PH</strong>
            <div class="progress" style="border-radius: 8px;height: 15px">
            <div class="progress-bar" role="progressbar" style="width: {ph_value}%;background-color: #D9381E" aria-valuenow={ph_value} aria-valuemin="0" aria-valuemax="100"></div>
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
            <div class="progress-bar" role="progressbar" style="width: {non_value}%;background-color: #808080" aria-valuenow={non_value} aria-valuemin="0" aria-valuemax="100"></div>
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
            Malay:  {bumi}%<br>
            Chinese: {chi}%<br>
            Indian: {ind}%<br>
            Others: {oth}%<br>
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

        def return_color(predict):
            if predict == 'PH Clear Win':
                return '#FF0000' #descreasing shades of red
            elif predict == 'PH Tight Win':
                return  '#DC143C'
            elif predict == 'PH Possible to Win':
                return '#FF5C5C'
            else:
                return '#808080' #grey for non ph


        def return_win_label(label):
            return '(' + str(label) + ')'

        #will place a multiselect widget
        #will change here to show PH (Clear Win, Tight Win, and Possible to Win) vs Non PH
        options = st.multiselect("State Seats Prediction Win:", ['PH Clear Win','PH Tight Win','PH Possible to Win','Non-PH'], ['PH Clear Win','PH Tight Win','PH Possible to Win', 'Non-PH'])

        #get the df of ph vs non ph
        df = df[df['predicted_win'].isin(options)]

        #sort by value of DUN no
        df.sort_values('ID', inplace=True)
        lst_dun = df['DUN'].tolist()

        #to know the remainder left for column order
        func_no = df.shape[0] % 3


        for i in range(0, len(lst_dun)-1-func_no, 3):

            idc = df[df['DUN']==lst_dun[i]].index.to_list()
            final_str_1 = df.loc[idc[0], 'DUN_str']
            ph_val_1 = df.loc[idc[0], 'PH_1']
            non_val_1 = df.loc[idc[0], 'Non-PH_1']
            color_1 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab1 = return_win_label(df.loc[idc[0], 'predicted_win'])


            idc = df[df['DUN']==lst_dun[i+1]].index.to_list()
            final_str_2 = df.loc[idc[0], 'DUN_str']
            ph_val_2 = df.loc[idc[0], 'PH_1']
            non_val_2 = df.loc[idc[0], 'Non-PH_1']
            color_2 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab2 = return_win_label(df.loc[idc[0], 'predicted_win'])

            idc = df[df['DUN']==lst_dun[i+2]].index.to_list()
            final_str_3 = df.loc[idc[0], 'DUN_str']
            ph_val_3 = df.loc[idc[0], 'PH_1']
            non_val_3 = df.loc[idc[0], 'Non-PH_1']
            color_3 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi3 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch3 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind3 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth3 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab3 = return_win_label(df.loc[idc[0], 'predicted_win'])

            col1, col2, col3= st.columns(3)


            with col1:
                st.markdown(card_dun(
                final_str_1, ph_val_1, non_val_1, color_1, demo_bumi1, demo_ch1, demo_ind1, demo_oth1, win_lab1
                ), unsafe_allow_html=True)


            with col2:
                st.markdown(card_dun(
                final_str_2, ph_val_2, non_val_2, color_2,  demo_bumi2, demo_ch2, demo_ind2, demo_oth2, win_lab2
                ), unsafe_allow_html=True)


            with col3:
                st.markdown(card_dun(
                final_str_3, ph_val_3, non_val_3, color_3,  demo_bumi3, demo_ch3, demo_ind3, demo_oth3, win_lab3
                ), unsafe_allow_html=True)




        if func_no == 2:

            idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-4]].index.to_list()
            final_str_1 = df.loc[idc[0], 'DUN_str']
            ph_val_1 = df.loc[idc[0], 'PH_1']
            non_val_1 = df.loc[idc[0], 'Non-PH_1']
            color_1 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab1 = return_win_label(df.loc[idc[0], 'predicted_win'])

            idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-3]].index.to_list()
            final_str_2 = df.loc[idc[0], 'DUN_str']
            ph_val_2 = df.loc[idc[0], 'PH_1']
            non_val_2 = df.loc[idc[0], 'Non-PH_1']
            color_2 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth2 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab2 = return_win_label(df.loc[idc[0], 'predicted_win'])

            col1, col2, col3= st.columns(3)

            with col1:
                st.markdown(card_dun(
                final_str_1, ph_val_1, non_val_1, color_1, demo_bumi1, demo_ch1, demo_ind1, demo_oth1, win_lab1
                ), unsafe_allow_html=True)


            with col2:
                st.markdown(card_dun(
                final_str_2, ph_val_2, non_val_2, color_2,demo_bumi2, demo_ch2, demo_ind2, demo_oth2, win_lab2
                ), unsafe_allow_html=True)

            with col3:
                st.markdown("""

                """, unsafe_allow_html=True)


        elif func_no == 1:
            idc = df[df['DUN']==lst_dun[len(lst_dun[-2:])-3]].index.to_list()
            final_str_1 = df.loc[idc[0], 'DUN_str']
            ph_val_1 = df.loc[idc[0], 'PH_1']
            non_val_1 = df.loc[idc[0], 'Non-PH_1']
            color_1 = return_color(df.loc[idc[0], 'predicted_win'])
            demo_bumi1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Malay'].values[0]
            demo_ch1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Chinese'].values[0]
            demo_ind1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['India'].values[0]
            demo_oth1 = df[df['DUN']==df.loc[idc[0], 'DUN']]['Others'].values[0]
            win_lab1 = return_win_label(df.loc[idc[0], 'predicted_win'])

            col1, col2, col3= st.columns(3)

            with col1:
                st.markdown(card_dun(
                final_str_1, ph_val_1, non_val_1, color_1, demo_bumi1, demo_ch1,demo_ind1,demo_oth1, win_lab1
                ), unsafe_allow_html=True)

            with col2:
                st.markdown("""

                """, unsafe_allow_html=True)

            with col3:
                st.markdown("""

                """, unsafe_allow_html=True)

        else:
                pass
