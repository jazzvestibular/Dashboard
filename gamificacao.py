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
        'pagina_atual': 'Gamificação'
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

def card_principal(pontuacao_aluno, pontuacao_media, nivel_aluno2):

    with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,3,1,3,1])
            with col1:
                st.write("")
            with col2:

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
                        <strong>Pontos</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                            <strong>{pontuacao_aluno}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {pontuacao_media}</strong>
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

            with col3:
                st.write("")
            with col4:

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
                            <strong>Fase</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{nivel_aluno2}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                            <strong>-</strong>
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

            with col5:
                st.write("")

def definir_nivel(pontuacao, pont_nivel12, pont_nivel23, pont_nivel34, pont_nivel45, pont_nivel56, pont_nivel67):
    if pontuacao == 0:
        #return "Nível 1"
        return "1ª | Exploration"
    elif pontuacao < pont_nivel12:
        #return "Nível 1"
        return "1ª | Exploration"
    elif pontuacao < pont_nivel23:
        #return "Nível 2"
        return "2ª | Discovery"
    elif pontuacao < pont_nivel34:
        #return "Nível 3"
        return "3ª | Action"
    elif pontuacao < pont_nivel45:
        #return "Nível 4"
        return "4ª | Confrontation"
    elif pontuacao < pont_nivel56:
        #return "Nível 5"
        return "5ª | Resilience"
    elif pontuacao < pont_nivel67:
        #return "Nível 6"
        return "6ª | Experience"
    else:
        #return "Nível 7"
        return "7ª | Final Battle"

def progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, id_bar, pont_niveis_menor, pont_niveis_maior):

    #prox_nivel = int(nivel_aluno[-1]) + 1

    if id_bar == 1:
        atual =  "Exploration"
        proximo = "Discovery"
    elif id_bar == 2:
        atual = "Discovery"
        proximo = "Action"
    elif id_bar == 3:
        atual = "Action"
        proximo = "Confrontation"
    elif id_bar == 4:
        atual = "Confrontation"
        proximo = "Resilience"
    elif id_bar == 5:
        atual = "Resilience"
        proximo = "Experience"
    elif id_bar == 6:
        atual = "Experience"
        proximo = "Final Battle"
    elif id_bar == 7:
        atual = "Final Battle"
        proximo = ""

    with st.container():

        col1, col2, col3 = st.columns([1,3,1])

        with col1:
            mensagem_html_principal = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: left">
                <p style="font-size: 24px; color: #333; margin: 0;">Fase <strong style="color: #9E089E;">{atual}</strong></p>
            </div>
            """

            mensagem_html_principal2 = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: left">
                <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">{pont_niveis_menor}</strong></p>
            </div>
            """

            st.markdown(mensagem_html_principal, unsafe_allow_html=True)

            if progress > 0:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

            if progress == 0 and pont_niveis_maior == 400:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

        with col3:
            mensagem_html_principal = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: right">
                <p style="font-size: 24px; color: #333; margin: 0;">Fase <strong style="color: #9E089E;">{proximo}</strong></p>
            </div>
            """

            mensagem_html_principal2 = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: right">
                <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">{pont_niveis_maior}</strong></p>
            </div>
            """

            st.markdown(mensagem_html_principal, unsafe_allow_html=True)

            if progress > 0:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

            if progress == 0 and pont_niveis_maior == 400:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

    if progress != 0 and progress != 1:

        progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: #9E089E; height: 45px; border-radius: 8px;"></div>
            </div>
            """
        mensagem_html = f"""
        <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
            <p style="font-size: 16px; color: #333; margin: 0;">Faltam <strong style="color: #9E089E;">{pontos_para_proximo_nivel}</strong> pontos para você alcançar a Fase <strong style="color: #9E089E;">{proximo}</strong>!</p>
        </div>
        """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)
        
    elif progress == 0:
        
        if nivel_aluno == 'Nível 1' and pont_niveis_maior == 400:

            progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: #9E089E; height: 45px; border-radius: 8px;"></div>
            </div>
            """

            mensagem_html = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Faltam <strong style="color: #9E089E;">{pontos_para_proximo_nivel}</strong> pontos para você alcançar a Fase <strong style="color: #9E089E;">{proximo}</strong>!</p>
            </div>
            """

    
        else:

            progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #cccccc; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: rgba(158, 8, 158, 0.8); height: 35px; border-radius: 8px;"></div>
            </div>
            """

            mensagem_html = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Alcance a Fase <strong style="color: #9E089E;">{atual}</strong> para avançar rumo a Fase <strong style="color: #9E089E;">{proximo}!</p>
            </div>
            """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)
        
    else: 

        progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: rgba(158, 8, 158, 0.8); height: 35px; border-radius: 8px;"></div>
            </div>
            """
        
        mensagem_html = f"""
        <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
            <p style="font-size: 16px; color: #333; margin: 0;">Você já alcançou a Fase <strong style="color: #9E089E;">{proximo}</strong>! Parabéns!!</p>
        </div>
        """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)

        if proximo == 'Discovery':

            html_br="""
            <br>
            """

            #st.markdown(html_br, unsafe_allow_html=True)

            mensagem_html_contato_breve = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Entraremos em contato com você em breve!!</p>
            </div>
            """

            st.markdown(mensagem_html_contato_breve, unsafe_allow_html=True)



def esferas_bar(esfera, pont_normalizado_aluno, pont_normalizado_media):

    if pont_normalizado_aluno < pont_normalizado_media - 0.25:
        cor_barra = "rgba(255, 165, 0, 0.6)"  # Laranja com opacidade
    elif pont_normalizado_aluno < pont_normalizado_media:
        cor_barra = "rgba(255, 255, 0, 0.6)"  # Amarela com opacidade
    elif pont_normalizado_aluno > pont_normalizado_media + 0.25:
        cor_barra = "rgba(0, 0, 255, 0.6)"  # Azul com opacidade
    else:
        cor_barra = "rgba(0, 128, 0, 0.6)"  # Verde com opacidade

    # HTML da barra de progresso com linha vertical preta para a média
    progress_bar_html_nivel = f"""
    <div style="position: relative; width: 100%; background-color: #cccccc; border-radius: 8px;">
        <div style="width: {100*pont_normalizado_aluno}%; background-color: {cor_barra}; height: 35px; border-radius: 8px;"></div>
        <div style="position: absolute; left: {100*pont_normalizado_media}%; top: 0; bottom: 0; width: 2px; background-color: #000000;">
            <div style="position: absolute; top: -20px; left: -10px; transform: translateX(-50%); color: #000000; font-size: 12px; font-weight: bold;">Média</div>
        </div>
    </div>
    """

    st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

def create_radar_chart(original_categories, values, medias, nome_selecionado):
    original_to_new_categories = {
        'Pontuação_Presença_Aulas_Normalizada': 'Presença nas aulas',
        'Pontuação_Presença_Mentoria_Normalizada': 'Presença nas mentorias',
        'Pontuação_Presença_Simulado_Normalizada': 'Presença nos simulados',
        'Pontuação_Engajamento_Plataforma_Normalizada': 'Engajamento na plataforma',
        'Pontuação_Duvida_Monitoria_Normalizada': 'Dúvidas na monitoria',
        'Pontuação_Nota_Simulado_Normalizada': 'Nota nos simulados'
    }

    # Convertendo as categorias originais para os novos nomes
    categories = [original_to_new_categories[cat] for cat in original_categories]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + values[:1],
        theta=categories + categories[:1],
        fill='toself',
        fillcolor='rgba(158, 8, 158, 0.4)',  # Cor de preenchimento com opacidade
        line=dict(color='rgba(158, 8, 158, 0.8)', width=2),
        name=nome_selecionado
    ))

    fig.add_trace(go.Scatterpolar(
        r=medias + medias[:1],
        theta=categories + categories[:1],
        fill='toself',
        fillcolor='rgba(255,167,62, 0.4)',  # Cor de preenchimento com opacidade
        line=dict(color='rgba(255,167,62, 0.8)', width=2),
        name='Média'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
    )

    st.plotly_chart(fig)

def tabela_pontuacoes(gamificacao, nome_selecionado):

    st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Tabela de resultados</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
    
    html_br="""
            <br>
            """

    st.markdown(html_br, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1.15,4,1]) 

        with col2:

            st.markdown("""
                <style>
                    th, td {
                        border-top: none;
                        padding: 0px;  /* Adjust padding for better visual appearance */
                        text-align: center;  /* Center align text */
                        height: 60px; 
                        vertical-align: middle;
                    }
                </style>
                <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                    <thead>
                        <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                            <th style="width: 300px; min-width: 300px; max-width: 300px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Aluno(a)</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Turma</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Fase</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Pontuação</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    
            st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

            for _, row in gamificacao.iterrows():
                if row['Nome do aluno(a)'] == nome_selecionado:
                    background_color = 'rgba(158, 8, 158, 0.5)'
                    font_color = '#FFFFFF'
                else: 
                    background_color = 'rgba(255, 255, 255, 1)'
                    font_color = '#000000'

                st.markdown(f"""
                <tr style="text-align: center; background-color: {background_color}; color: {font_color};">
                    <td style="width: 300px; min-width: 300px; max-width: 300px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nome do aluno(a)']}</td>
                    <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Turma']}</td>
                    <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nível']}</td>
                    <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Pontuação']}</td>
                </tr>
                """, unsafe_allow_html=True)

def mostrar_gamificacao(nome, permissao, email):

    estado = get_estado()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    engajamento_plataforma = ler_planilha("12T-TRAZsGYGqnYjbn-K_PZrme-ygyUWJSfuR-LQ0JT8", "Streamlit | Engajamento na plataforma!A1:J")
    presenca_aulasMT1 = ler_planilha("13ZLdLNHMtkJbo9j39GgK4EovuKyaUb1atXbCjoW40oY", "Streamlit | Presença nas aulas | Manhã + Tarde 1!A1:R")
    presenca_aulasT2 = ler_planilha("13ZLdLNHMtkJbo9j39GgK4EovuKyaUb1atXbCjoW40oY", "Streamlit | Presença nas aulas | Tarde 2!A1:R")
    presenca_aulasNT1 = ler_planilha("13ZLdLNHMtkJbo9j39GgK4EovuKyaUb1atXbCjoW40oY", "Streamlit | Presença nas aulas | Tarde 1 (Nat)!A1:R")
    presenca_aulas_aux = pd.concat([presenca_aulasT2, presenca_aulasMT1], axis=0)
    presenca_aulas = pd.concat([presenca_aulas_aux, presenca_aulasNT1], axis=0)
    presenca_mentoria = ler_planilha("1EEzqMd2uBnL5-7-19FhYS3w_s_wVa21s0TN_2wPHUdk", "Streamlit | Presença na mentoria!A1:F")
    presenca_nota_simulado = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Streamlit | Presença + Notas simulado!A1:L")
    duvidas_monitoria = ler_planilha("1SCYS-8FccRCvK18CMqMGFWpTKRlDgzBGAaG26dBsWCg", "Streamlit | Monitoria!A1:O")
    presenca_aulas_2fase = ler_planilha("13AsGUjRUBaachB_9Zjq_-4G7xcxyWFvJtI_0XmF5zfg", "Streamlit | Presença nas aulas | 2ª fase!A1:G10000")

    engajamento_plataforma['Pontuação_Engajamento_Plataforma'] = engajamento_plataforma['Pontuação'].fillna(0).astype(int)
    presenca_aulas['Pontuação_Presença_Aulas'] = presenca_aulas['Pontuação'].fillna(0).astype(int)
    presenca_aulas = presenca_aulas[presenca_aulas['Pontuação_Presença_Aulas'] > 0]
    presenca_mentoria['Pontuação_Presença_Mentoria'] = presenca_mentoria['Pontuação'].fillna(0).astype(int)
    presenca_nota_simulado['Pontuação_Presença_Simulado'] = presenca_nota_simulado['Pontuação Presença'].fillna(0).astype(int)
    presenca_nota_simulado['Pontuação_Nota_Simulado'] = presenca_nota_simulado['Pontuação Nota'].fillna(0).astype(int)
    duvidas_monitoria['Pontuação_Duvidas_Monitoria'] = duvidas_monitoria['Pontuação'].fillna(0).astype(int)
    presenca_aulas_2fase['Pontuação_Presença_2Fase'] = presenca_aulas_2fase['Pontuação'].fillna(0).astype(int)

    #engajamento_plataforma2 = engajamento_plataforma.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    engajamento_plataforma2 = engajamento_plataforma.groupby(['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Engajamento_Plataforma': 'sum'}).reset_index()
    #presenca_aulas2 = presenca_aulas.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_aulas2 = presenca_aulas.groupby(['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Presença_Aulas': 'sum'}).reset_index()
    #presenca_mentoria2 = presenca_mentoria.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_mentoria2 = presenca_mentoria.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Presença_Mentoria': 'sum'}).reset_index()
    #presenca_nota_simulado2 = presenca_nota_simulado.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_nota_simulado2 = presenca_nota_simulado.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Nota_Simulado': 'sum','Pontuação_Presença_Simulado':'sum'}).reset_index()
    #duvidas_monitoria2 = duvidas_monitoria.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    duvidas_monitoria2 = duvidas_monitoria.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Duvidas_Monitoria': 'sum'}).reset_index()

    presenca_aulas_2fase2 = presenca_aulas_2fase.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Presença_2Fase': 'sum'}).reset_index()

    if permissao == 'Aluno':

        nome_selecionado = nome
    
    else:

        nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(presenca_aulas['Nome do aluno(a)'].unique())

        nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", nome_selecionado, email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

    if nome_selecionado != "Escolha o(a) aluno(a)":

        engajamento_plataforma_aluno = engajamento_plataforma[engajamento_plataforma['Nome do aluno(a)'] == nome_selecionado]
        presenca_aulas_aluno = presenca_aulas[presenca_aulas['Nome do aluno(a)'] == nome_selecionado]
        presenca_mentoria_aluno = presenca_mentoria[presenca_mentoria['Nome do aluno(a)'] == nome_selecionado]
        presenca_nota_simulado_aluno = presenca_nota_simulado[presenca_nota_simulado['Nome do aluno(a)'] == nome_selecionado]
        duvidas_monitoria_aluno = duvidas_monitoria[duvidas_monitoria['Nome do aluno(a)'] == nome_selecionado]
        presenca_aulas_2fase_aluno = presenca_aulas_2fase[presenca_aulas_2fase['Nome do aluno(a)'] == nome_selecionado]

        engajamento_plataforma_aluno2 = engajamento_plataforma_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        presenca_aulas_aluno2 = presenca_aulas_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        presenca_mentoria_aluno2 = presenca_mentoria_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        presenca_nota_simulado_aluno2 = presenca_nota_simulado_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        duvidas_monitoria_aluno2 = duvidas_monitoria_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        presenca_aulas_2fase_aluno2 = presenca_aulas_2fase_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()

        gamificacao1 = pd.merge(presenca_aulas2, engajamento_plataforma2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao2 = pd.merge(gamificacao1, presenca_mentoria2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao4 = pd.merge(gamificacao2, presenca_nota_simulado2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao4 = pd.merge(gamificacao4, presenca_aulas_2fase2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao_final = pd.merge(gamificacao4, duvidas_monitoria2, on = ['Nome do aluno(a)','Turma'], how = 'left')

        gamificacao_final.fillna(0, inplace=True)

        gamificacao_final['Pontuação_Engajamento_Plataforma'] = gamificacao_final['Pontuação_Engajamento_Plataforma'].astype(int)
        gamificacao_final['Pontuação_Presença_Aulas'] = gamificacao_final['Pontuação_Presença_Aulas'].astype(int)
        gamificacao_final['Pontuação_Presença_Mentoria'] = gamificacao_final['Pontuação_Presença_Mentoria'].astype(int)
        gamificacao_final['Pontuação_Presença_Simulado'] = gamificacao_final['Pontuação_Presença_Simulado'].astype(int)
        gamificacao_final['Pontuação_Nota_Simulado'] = gamificacao_final['Pontuação_Nota_Simulado'].astype(int)
        gamificacao_final['Pontuação_Duvidas_Monitoria'] = gamificacao_final['Pontuação_Duvidas_Monitoria'].astype(int)
        gamificacao_final['Pontuação_Presença_2Fase'] = gamificacao_final['Pontuação_Presença_2Fase'].astype(int)

        gamificacao_final['Pontuação'] = (
                gamificacao_final['Pontuação_Engajamento_Plataforma'] +
                gamificacao_final['Pontuação_Presença_Aulas'] +
                gamificacao_final['Pontuação_Presença_Mentoria'] + 
                gamificacao_final['Pontuação_Presença_Simulado'] + 
                gamificacao_final['Pontuação_Nota_Simulado'] +
                gamificacao_final['Pontuação_Duvidas_Monitoria'] +
                gamificacao_final['Pontuação_Presença_2Fase']
            )
        
        gamificacao_final['Pontuação_Engajamento_Plataforma_Normalizada'] = gamificacao_final['Pontuação_Engajamento_Plataforma'] / gamificacao_final['Pontuação_Engajamento_Plataforma'].max()
        gamificacao_final['Pontuação_Presença_Aulas_Normalizada'] = (gamificacao_final['Pontuação_Presença_Aulas'] + gamificacao_final['Pontuação_Presença_2Fase'])  / (gamificacao_final['Pontuação_Presença_Aulas'].max() + gamificacao_final['Pontuação_Presença_2Fase'].max())
        #gamificacao2['Pontuação_Presença_Mentoria_Normalizada'] = gamificacao2['Pontuação_Presença_Mentoria'] / gamificacao2['Pontuação_Presença_Mentoria'].max()    

        gamificacao_final['Pontuação_Presença_Mentoria_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Presença_Mentoria'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Presença_Mentoria'] / gamificacao_final['Pontuação_Presença_Mentoria'].max()
        )

        gamificacao_final['Pontuação_Presença_Simulado_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Presença_Simulado'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Presença_Simulado'] / gamificacao_final['Pontuação_Presença_Simulado'].max()
        )

        gamificacao_final['Pontuação_Nota_Simulado_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Nota_Simulado'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Nota_Simulado'] / gamificacao_final['Pontuação_Nota_Simulado'].max()
        )

        gamificacao_final['Pontuação_Duvidas_Monitoria_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Duvidas_Monitoria'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Duvidas_Monitoria'] / gamificacao_final['Pontuação_Duvidas_Monitoria'].max()
        )

        gamificacao3 = gamificacao_final.sort_values(by = 'Pontuação', ascending = False)

        pont_niveis = [400, 1000, 1900, 2800, 3700, 5200]

        gamificacao3['Nível'] = gamificacao3['Pontuação'].apply(definir_nivel, args=(pont_niveis[0], pont_niveis[1], pont_niveis[2], pont_niveis[3], pont_niveis[4], pont_niveis[5]))

        gamificacao3_aluno = gamificacao3[gamificacao3['Nome do aluno(a)'] == nome_selecionado].reset_index(drop = True)

        #gamificacao3_medias = gamificacao3.drop(columns=['Nome do aluno(a)', 'Turma']).mean().reset_index()
        gamificacao3_medias = gamificacao3.drop(columns=['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Engajamento_Plataforma': 'mean','Pontuação_Presença_Aulas': 'mean','Pontuação_Presença_Simulado': 'mean','Pontuação_Nota_Simulado': 'mean','Pontuação_Duvidas_Monitoria': 'mean','Pontuação_Presença_2Fase': 'mean'}).reset_index()
        
        gamificacao3_medias.columns = ['Métrica', 'Média']

        pontuacao_aluno = gamificacao3_aluno['Pontuação'][0]

        pontuacao_media = gamificacao3['Pontuação'].mean().round(0).astype(int)

        nivel_aluno = gamificacao3_aluno['Nível'][0]
        nivel_aluno2 = int(nivel_aluno[0])
        #st.write(nivel_aluno)

        st.markdown('<div style="height: 0px;"></div>', unsafe_allow_html=True)

        #nome_maiusculo = 

        with st.container():

            col1, col2, col3 = st.columns([2,4,2])

            with col2:

                st.markdown(
                                    f"""
                                    <div style="background-color: #9E089E; color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center; font-size: 45px;">
                                        <strong>{nome_selecionado.upper()}</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

        html_br="""
            <br>
            """

        st.markdown(html_br, unsafe_allow_html=True)
        st.markdown(html_br, unsafe_allow_html=True)

        card_principal(pontuacao_aluno, pontuacao_media, nivel_aluno)
        
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Progressão de Fase</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
        #st.markdown(html_br, unsafe_allow_html=True)
        st.markdown(html_br, unsafe_allow_html=True)

        if int(nivel_aluno2) < (len(pont_niveis) + 1):
            pontos_para_proximo_nivel = pont_niveis[int(nivel_aluno2)-1] - pontuacao_aluno
        else:
            pontos_para_proximo_nivel = 0

        if nivel_aluno == '1ª | Exploration':

            progress = pontuacao_aluno / pont_niveis[0]
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '2ª | Discovery':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[0])  / (pont_niveis[1] - pont_niveis[0])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])  
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '3ª | Action':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[1])  / (pont_niveis[2] - pont_niveis[1])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '4ª | Confrontation':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[2])  / (pont_niveis[3] - pont_niveis[2])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '5ª | Resilience':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[3])  / (pont_niveis[4] - pont_niveis[3])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '6ª | Experience':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[4])  / (pont_niveis[5] - pont_niveis[4])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '7ª | Final Battle':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, 1)
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Resultados por esfera</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        st.markdown(html_br, unsafe_allow_html=True)
        st.markdown(html_br, unsafe_allow_html=True)

        with st.container():

            col1, col2, col3, col4, col5, col6, col7 = st.columns([1,10,1,10,1,10,1])

            with col2:

                mensagem_html_pres_aulas = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nas aulas</strong></p>
                </div>
                """
                st.markdown(mensagem_html_pres_aulas, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença nas aulas', gamificacao3_aluno['Pontuação_Presença_Aulas_Normalizada'][0], (100*gamificacao3['Pontuação_Presença_Aulas_Normalizada'].mean()).round(0).astype(int)/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_eng_plataforma = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Engajamento na plataforma</strong></p>
                </div>
                """
                st.markdown(mensagem_html_eng_plataforma, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Engajamento na plataforma', gamificacao3_aluno['Pontuação_Engajamento_Plataforma_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Engajamento_Plataforma_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

            with col4:

                mensagem_html_pres_mentorias = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nas mentorias</strong></p>
                </div>
                """
                st.markdown(mensagem_html_pres_mentorias, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença na mentoria', gamificacao3_aluno['Pontuação_Presença_Mentoria_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Presença_Mentoria_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_duvida_monitoria = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Dúvidas na monitoria</strong></p>
                </div>
                """
                st.markdown(mensagem_html_duvida_monitoria, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Dúvidas na monitoria', gamificacao3_aluno['Pontuação_Duvidas_Monitoria_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Duvidas_Monitoria_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

            with col6:

                mensagem_html_presenca_simulado = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nos simulados</strong></p>
                </div>
                """
                st.markdown(mensagem_html_presenca_simulado, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença no simulado', gamificacao3_aluno['Pontuação_Presença_Simulado_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Presença_Simulado_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_nota_simulado = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Nota nos simulados</strong></p>
                </div>
                """
                st.markdown(mensagem_html_nota_simulado, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Nota no simulado', gamificacao3_aluno['Pontuação_Nota_Simulado_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Nota_Simulado_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

        #gamificacao2['Pontuação_Engajamento_Plataforma_Normalizada'] = gamificacao2['Pontuação_Engajamento_Plataforma'] / gamificacao2['Pontuação_Engajamento_Plataforma'].max()
        #gamificacao2['Pontuação_Presença_Aulas_Normalizada'] = gamificacao2['Pontuação_Presença_Aulas'] / gamificacao2['Pontuação_Presença_Aulas'].max() 
        #gamificacao2['Pontuação_Presença_Mentoria_Normalizada'] = gamificacao2['Pontuação_Presença_Mentoria'] / gamificacao2['Pontuação_Presença_Mentoria'].max()    
        

        with st.container():

            col1, col2, col3 = st.columns([2,7,1])

            with col2: 

                categories = ['Pontuação_Engajamento_Plataforma_Normalizada', 'Pontuação_Presença_Aulas_Normalizada', 'Pontuação_Presença_Mentoria_Normalizada', 'Pontuação_Presença_Simulado_Normalizada', 'Pontuação_Nota_Simulado_Normalizada', 'Pontuação_Duvidas_Monitoria_Normalizada']
                #values = gamificacao3_aluno[categories].values.flatten().tolist()
                #medias = gamificacao3_medias.set_index('Métrica').loc[categories]['Média'].tolist()
                #create_radar_chart(categories, values, medias, nome_selecionado)

                gamificacao3_medias = gamificacao3_medias.set_index('Métrica')

                # Verifique se todas as categorias estão no índice
                if all(cat in gamificacao3_medias.index for cat in categories):
                    medias = gamificacao3_medias.loc[categories, 'Média'].tolist()

        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        tabela_pontuacoes(gamificacao3, nome_selecionado)

