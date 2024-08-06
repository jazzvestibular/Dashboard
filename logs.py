import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def encontrar_ultima_linha_preenchida(service, spreadsheet_id, sheet_name):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A:A").execute()
    values = result.get("values", [])
    return len(values) + 1  

def escrever_planilha(SAMPLE_SPREADSHEET_ID, data_to_write, sheet_name):

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        ultima_linha_preeenchida = encontrar_ultima_linha_preenchida(service, SAMPLE_SPREADSHEET_ID, sheet_name)
        SAMPLE_RANGE_NAME = "A"+str(ultima_linha_preeenchida)
        range_with_sheet = f"{sheet_name}!{SAMPLE_RANGE_NAME}"
        body = {"values": data_to_write}
        result = (
            sheet.values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range_with_sheet,
                valueInputOption="RAW",
                body=body
            )
            .execute()
        )

        print("Dados escritos na planilha com sucesso.")

    except HttpError as err:
        print("Ocorreu um erro ao escrever na planilha:", err)

