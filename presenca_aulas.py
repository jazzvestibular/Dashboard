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

    dataframe_aluno = dataframe_aluno[dataframe_aluno['Presente'] > 0]

    valores_com_presenca = dataframe_aluno[dataframe_aluno['Presente'] != 0][eixo_x].unique()

    media_presenca = dataframe[dataframe[eixo_x].isin(valores_com_presenca)].groupby(eixo_x)['Presente'].mean().reset_index()

    # Criando o gráfico de barras
    fig = go.Figure()

    if nome_selecionado == 'Maria Eduarda Mariano':
        
        nome_selecionado = 'Aluno exemplo'

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
        marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2)),
        hoverinfo='none'
    ))

    # Mapeando categorias para índices numéricos
    eixo_x_numerico = {category: idx for idx, category in enumerate(media_presenca[eixo_x])}

    # Adicionando linhas horizontais para cada coluna
    for i in range(len(media_presenca[eixo_x])):
        # Adiciona uma linha cheia
        fig.add_shape(
            type='line',
            x0=eixo_x_numerico[media_presenca[eixo_x][i]] - 0.2,  # Ajusta a posição para a esquerda da barra
            x1=eixo_x_numerico[media_presenca[eixo_x][i]] + 0.2,  # Ajusta a posição para a direita da barra
            y0=media_presenca['Presente'][i] * 100,  # Altura da linha (média para essa coluna)
            y1=media_presenca['Presente'][i] * 100,  # Mantém a altura da linha
            line=dict(color='black', width=2)  # Estilo da linha cheia
        )

        # Adiciona o valor da média acima da linha
        fig.add_annotation(
            x=eixo_x_numerico[media_presenca[eixo_x][i]],  # Posição X
            y=media_presenca['Presente'][i] * 100 - 5,  # Posição Y um pouco acima da linha
            text=f"{media_presenca['Presente'][i] * 100:.1f}%",  # Formata o texto para porcentagem
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    fig.add_trace(
        go.Scatter(
            x=media_presenca[eixo_x], 
            y=media_presenca['Presente'],
            mode='lines',
            name='Média',  # Adiciona 'Média' na legenda
            line=dict(color='black', width=2),  # Linha preta na legenda
            showlegend=True,  # Mostra a legenda
            opacity=0  # Linha invisível no gráfico
        )
    )

    # Atualizando layout com base no eixo X
    fig.update_layout(
        xaxis_title=eixo_x,
        yaxis_title='Presença (%)',
        yaxis_range=[0, 100],
        legend=dict(yanchor="bottom", y=1.1, xanchor="center", x=0.5),  # Posiciona a legenda acima do gráfico
        barmode='group',
        template='plotly_white'
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

def mostrar_presenca_aulas(nome, permissao, email):

    estado = get_estado()

    progress_css = """
    <style>
    .progress-bar {
        background-color: #9e089e;
    }
    </style>
    """

    # Renderizar o CSS personalizado
    st.markdown(progress_css, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    percentage_text = st.empty()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    alunos = ler_planilha("1ZyRboIm7Bf2P-sUroxIxidWsnX7ADFDdIN8Ck1Sdp0s", "Streamlit | Alunos!A1:E")
    alunos['Alunos'] = alunos['Alunos'].fillna('').astype(str)
    alunos = alunos[alunos['Alunos'] != '']
    alunos.rename(columns = {'Alunos':'Nome do aluno(a)'}, inplace = True)

    if (permissao == 'Aluno' or permissao == 'Responsável'):

        nome_selecionado = nome
    
    else:

        nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(alunos['Nome do aluno(a)'].unique())

        nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", nome_selecionado, email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

    presenca_aulas = ler_planilha("10ocwUa69s-3c_FMpNMWq6CRooGooa0-9K19rFwm8oEo", "Streamlit | Presença nas aulas!A1:Y")
    #presenca_aulas = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Presença nas aulas!A1:Y")

    progress_bar.progress(50)
    percentage_text.text("50%")

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

    presenca_aulas_dia = presenca_aulas2.groupby(['Nome do aluno(a)','Turma','Data']).mean('Presente').reset_index()
    presenca_aulas_dia['Data'] = pd.to_datetime(presenca_aulas_dia['Data'], errors='coerce')
    presenca_aulas_dia = presenca_aulas_dia.sort_values(by = 'Data', ascending = True)

    presenca_aulas_media = presenca_aulas2.groupby(['Nome do aluno(a)','Turma']).mean('Presente').reset_index()

    progress_bar.progress(100)
    percentage_text.text("100%")

    if nome_selecionado != "Escolha o(a) aluno(a)":

        with st.container():

            col4, col5, col6, col7 = st.columns([4,0.1,4,0.1])

            with col4:

                presenca_aulas_aluno = presenca_aulas_media[presenca_aulas_media['Nome do aluno(a)'] == nome_selecionado].reset_index(drop = True)

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                        <strong>Presença nas aulas de 1ª fase</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                            <strong>{"{:.0%}".format(presenca_aulas_aluno['Presente'][0])}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {"{:.0%}".format(presenca_aulas_media['Presente'].mean())}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                        """
                                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                                            <strong>Presença por semana</strong>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                grafico_presenca(presenca_aulas_semanal, 'Semana', nome_selecionado)

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                        """
                                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                                            <strong>Presença por horário da aula</strong>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                
                grafico_presenca(presenca_aulas_horario, 'Horário da aula', nome_selecionado)

            with col6:

                maior_semana = presenca_aulas_semanal['Semana'].max()

                # Filtrar o DataFrame com base no maior valor
                presenca_aulas_semanal_ult = presenca_aulas_semanal[presenca_aulas_semanal['Semana'] == maior_semana]

                presenca_aulas_aluno_ult = presenca_aulas_semanal_ult[presenca_aulas_semanal_ult['Nome do aluno(a)'] == nome_selecionado].reset_index(drop = True)

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                        <strong>Presença nas aulas na última semana</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                            <strong>{"{:.0%}".format(presenca_aulas_aluno_ult['Presente'][0])}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {"{:.0%}".format(presenca_aulas_semanal_ult['Presente'].mean())}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                        """
                                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                                            <strong>Presença por área</strong>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                grafico_presenca(presenca_aulas_area, 'Área', nome_selecionado)

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                        """
                                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                                            <strong>Presença por frente</strong>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                
                grafico_presenca(presenca_aulas_frente, 'Frente', nome_selecionado)