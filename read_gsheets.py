import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import numpy as np
import streamlit as st


def open_access_gsheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES)


    # The ID of "meniaga | Analytics Dashboard" spreadsheet
    SPREADSHEET_ID = st.secrets["spreadsheet"]["SPREADSHEET_ID"]
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet

#arg:
#1) sheetid to read from
#2) sheet_idc to read from
#returns a df
def read_from_sheet(sheet, sheetid, sheet_idc):
    result = sheet.values().get(spreadsheetId=sheetid,range=sheet_idc).execute()
    values = result.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    return df
