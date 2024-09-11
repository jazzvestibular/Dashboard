import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from plotly.subplots import make_subplots
from PIL import Image
import numpy as np
from logs import escrever_planilha
import datetime
import pytz

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

def define_estado():
    return {
        'pagina_atual': 'Alunos - Presença nas aulas'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def dia_hora():

    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    data_e_hora_brasilia = datetime.datetime.now(fuso_horario_brasilia)
    data_hoje_brasilia = str(data_e_hora_brasilia.date())
    hora_atual_brasilia = str(data_e_hora_brasilia.strftime('%H:%M:%S'))
    return data_hoje_brasilia, hora_atual_brasilia

def ler_planilha(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
    creds = None
    values2 = pd.DataFrame()  # Inicializando a variável

    if os.path.exists("token_gami.json"):
        creds = Credentials.from_authorized_user_file("token_gami.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials_gami.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        with open("token_gami.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )

        values = result.get("values", [])
    
        values2 = pd.DataFrame(values[1:], columns=values[0])

    except HttpError as err:
        st.error(f"Erro ao ler a planilha: {err}")

    return values2

def grafico_presenca(dataframe, eixo_x, nome_selecionado):

    dataframe_aluno = dataframe[dataframe['Nome do aluno(a)'] == nome_selecionado]

    # Criando o gráfico de barras
    fig = go.Figure()

    # Adicionando as barras
    fig.add_trace(go.Bar(
        name=nome_selecionado,
        x=dataframe_aluno[eixo_x],
        y=dataframe_aluno['Presente']*100,  # Multiplicando por 100 para representar em porcentagem
        text=dataframe_aluno['Presente']*100,
        textposition='inside',
        textfont=dict(color='white'),
        texttemplate='<b>%{text:.0f}%</b>',  # Formatando o texto para porcentagem
        textangle=0,
        offsetgroup=nome_selecionado,
        marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))
    ))

    if eixo_x == 'Semana':

        # Atualizando layout
        fig.update_layout(
            xaxis_title=eixo_x,
            yaxis_title='Presença (%)',
            yaxis_range=[0, 100],  # Definindo o eixo Y de 0 a 100%
            xaxis_range=[-1, dataframe_aluno['Semana'].max()],  # Definindo o eixo X de 1 ao valor máximo
            barmode='group',
            template='plotly_white'
        )

    if eixo_x == 'Área' or eixo_x == 'Frente' or eixo_x == 'Horário da aula':

        # Atualizando layout
        fig.update_layout(
            xaxis_title=eixo_x,
            yaxis_title='Presença (%)',
            yaxis_range=[0, 100],  # Definindo o eixo Y de 0 a 100%
            #xaxis_range=[-1, dataframe['Semana'].max()],  # Definindo o eixo X de 1 ao valor máximo
            barmode='group',
            template='plotly_white'
        )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig)

def mostrar_presenca_aulas(nome, permissao, email):

    estado = get_estado()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    alunos = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Alunos!A1:E")
    alunos['Alunos'] = alunos['Alunos'].fillna('').astype(str)
    alunos = alunos[alunos['Alunos'] != '']
    alunos.rename(columns = {'Alunos':'Nome do aluno(a)'}, inplace = True)

    presenca_aulas = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Presença nas aulas!A1:Y")
    #presenca_aulas['Pontuação_Presença_Aulas'] = presenca_aulas['Pontuação'].fillna(0).astype(int)
    presenca_aulas['Presente'] = presenca_aulas['Presente'].fillna(0).astype(int)
    
    presenca_aulas2 = presenca_aulas[presenca_aulas['Considerar'] == 'Sim'].reset_index(drop = True)

    presenca_aulas_semanal = presenca_aulas2.groupby(['Nome do aluno(a)','Turma','Semana']).mean('Presente').reset_index()

    presenca_aulas_area = presenca_aulas2.groupby(['Nome do aluno(a)','Turma','Área']).mean('Presente').reset_index()
    presenca_aulas_area = presenca_aulas_area.sort_values(by = 'Área', ascending = True)

    presenca_aulas_frente = presenca_aulas2.groupby(['Nome do aluno(a)','Turma','Frente']).mean('Presente').reset_index()
    presenca_aulas_frente = presenca_aulas_frente.sort_values(by = 'Frente', ascending = True)

    presenca_aulas_horario = presenca_aulas2.groupby(['Nome do aluno(a)','Turma','Horário da aula']).mean('Presente').reset_index()
    presenca_aulas_horario = presenca_aulas_horario.sort_values(by = 'Horário da aula', ascending = True)
    
    if permissao == 'Aluno':

        nome_selecionado = nome
    
    else:

        nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(alunos['Nome do aluno(a)'].unique())

        nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", nome_selecionado, email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

    if nome_selecionado != "Escolha o(a) aluno(a)":

        with st.container():

            col1, col2, col3 = st.columns([4,0.5, 4])

            with col1:

                grafico_presenca(presenca_aulas_semanal, 'Semana', nome_selecionado)

                grafico_presenca(presenca_aulas_horario, 'Horário da aula', nome_selecionado)

            with col3:

                grafico_presenca(presenca_aulas_area, 'Área', nome_selecionado)

                grafico_presenca(presenca_aulas_frente, 'Frente', nome_selecionado)

        st.dataframe(presenca_aulas_semanal)



