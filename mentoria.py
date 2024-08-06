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
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pytz
from logs import escrever_planilha
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def dia_hora():

    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    data_e_hora_brasilia = datetime.datetime.now(fuso_horario_brasilia)
    data_hoje_brasilia = str(data_e_hora_brasilia.date())
    hora_atual_brasilia = str(data_e_hora_brasilia.strftime('%H:%M:%S'))
    return data_hoje_brasilia, hora_atual_brasilia

def define_estado():
    return {
        'pagina_atual': 'Página Inicial'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def ler_planilha(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):

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
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )

    values = result.get("values", [])
    
    values2 = pd.DataFrame(values[1:], columns=values[0])

  except HttpError as err:
    var = 1

  return values2

def mostrar_mentoria(nome, permissao, email):

    estado = get_estado()

    mentoria_presenca = ler_planilha("1Ew9AZCGJJXRRbJP2mxz_1UGymb-PX8yZHNUwrbumK70", "Mentoria | Streamlit | Presença dos alunos!A1:BU100")

    mentoria_presenca_area = ler_planilha("1Ew9AZCGJJXRRbJP2mxz_1UGymb-PX8yZHNUwrbumK70", "Mentoria | Streamlit | Alunos | Área!A1:S100")

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:

            nomes_alunos = ["Escolha o(a) aluno(a)"] + mentoria_presenca['Nome Completo'].tolist()

            nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

        with col3:
           
           opcao_periodo = st.selectbox('Selecione o período:', ['Última semana', 'Últimas 4 semanas', 'Desde o início'])

    if nome_selecionado == "Escolha o(a) aluno(a)":
        st.warning("Por favor, selecione um(a) aluno(a)!")
        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'],"Por favor, selecione um(a) aluno(a)!", "", email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

    if nome_selecionado !=  "Escolha o(a) aluno(a)":
        
        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], nome_selecionado, opcao_periodo, email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

        st.markdown(
            """
            <hr style="border: 10px solid #gray; margin-top: 0px;">
            """,
            unsafe_allow_html=True
        )
        
        mentoria_presenca_aluno = mentoria_presenca[mentoria_presenca['Nome Completo'] == nome_selecionado].reset_index(drop = True)

        if opcao_periodo == 'Última semana':
            presenca_1_fase = mentoria_presenca_aluno['Última Semana 1F'][0]
            presenca_2_fase = mentoria_presenca_aluno['Última Semana 2F'][0]
            mentoria_presenca['Última Semana 1F'] = mentoria_presenca['Última Semana 1F'].str.replace(',', '.').astype(float)
            mentoria_presenca['Última Semana 2F'] = mentoria_presenca['Última Semana 2F'].str.replace(',', '.').astype(float)
            mentoria_presenca_1fase = mentoria_presenca[mentoria_presenca['Última Semana 1F'] > 0]
            mentoria_presenca_1fase_ = mentoria_presenca_1fase['Última Semana 1F'].mean()
            mentoria_presenca_2fase = mentoria_presenca['Última Semana 2F'].reset_index(drop = True).mean()
        elif opcao_periodo == 'Últimas 4 semanas':
            presenca_1_fase = mentoria_presenca_aluno['Últimas 4 Semanas 1F'][0]
            presenca_2_fase = mentoria_presenca_aluno['Últimas 4 Semanas 2F'][0]
            mentoria_presenca['Últimas 4 Semanas 1F'] = mentoria_presenca['Últimas 4 Semanas 1F'].str.replace(',', '.').astype(float)
            mentoria_presenca['Últimas 4 Semanas 2F'] = mentoria_presenca['Últimas 4 Semanas 2F'].str.replace(',', '.').astype(float)
            mentoria_presenca_1fase = mentoria_presenca[mentoria_presenca['Últimas 4 Semanas 1F'] > 0]
            mentoria_presenca_1fase_ = mentoria_presenca_1fase['Últimas 4 Semanas 1F'].mean()
            mentoria_presenca_2fase = mentoria_presenca['Últimas 4 Semanas 2F'].reset_index(drop = True).mean()
        else:
            presenca_1_fase = mentoria_presenca_aluno['Geral 1F'][0]
            presenca_2_fase = mentoria_presenca_aluno['Geral 2F'][0]
            mentoria_presenca['Geral 1F'] = mentoria_presenca['Geral 1F'].str.replace(',', '.').astype(float)
            mentoria_presenca['Geral 2F'] = mentoria_presenca['Geral 2F'].str.replace(',', '.').astype(float)
            mentoria_presenca_1fase = mentoria_presenca[mentoria_presenca['Geral 1F'] > 0]
            mentoria_presenca_1fase_ = mentoria_presenca_1fase['Geral 1F'].mean()
            mentoria_presenca_2fase = mentoria_presenca['Geral 2F'].reset_index(drop = True).mean()
        
        presenca_1_fase_float = float(presenca_1_fase.replace(',', '.'))
        presenca_1_fase_porc = presenca_1_fase_float * 100
        presenca_1_fase_porc_formatada = f"{presenca_1_fase_porc:.0f}%"

        presenca_2_fase_float = float(presenca_2_fase.replace(',', '.'))
        presenca_2_fase_porc = presenca_2_fase_float * 100
        presenca_2_fase_porc_formatada = f"{presenca_2_fase_porc:.0f}%"

        media_presenca_1_fase_porc = mentoria_presenca_1fase_ * 100
        media_presenca_1_fase_porc_formatada = f"{media_presenca_1_fase_porc:.0f}%"

        media_presenca_2_fase_porc = mentoria_presenca_2fase * 100
        media_presenca_2_fase_porc_formatada = f"{media_presenca_2_fase_porc:.0f}%"

        with st.container():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1])
            with col1:

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
                        <strong>Porcentagem de presença nas aulas de 1ª fase</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                        <strong>{presenca_1_fase_porc_formatada}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if presenca_1_fase_float == 0:
                    st.image('sem_progresso.png', use_column_width=True)
                elif presenca_1_fase_float < mentoria_presenca_1fase_:
                    st.image('estudou.png', use_column_width=True)
                elif presenca_1_fase_float > mentoria_presenca_1fase_ and presenca_1_fase_float < 0.9:
                    st.image('engajado.png', use_column_width=True)
                elif presenca_1_fase_float >= 0.9:
                    st.image('destaque.png', use_column_width=True)

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {media_presenca_1_fase_porc_formatada}</strong>
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

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px; ">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                        <strong>Porcentagem de presença nas aulas de 2ª fase</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                        <strong>{presenca_2_fase_porc_formatada}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if presenca_2_fase_float == 0:
                    st.image('sem_progresso.png', use_column_width=True)
                elif presenca_2_fase_float < mentoria_presenca_2fase:
                    st.image('estudou.png', use_column_width=True)
                elif presenca_2_fase_float > mentoria_presenca_2fase and presenca_2_fase_float < 0.9:
                    st.image('engajado.png', use_column_width=True)
                elif presenca_2_fase_float >= 0.9:
                    st.image('destaque.png', use_column_width=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: 6px;">
                        <strong>Média: {media_presenca_2_fase_porc_formatada}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-top: 6px; ">
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            """
            <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-top: -20px; margin-bottom: -40px;">
                <div style="font-size: 50px; font-weight: bold; text-transform: uppercase; color: #9E089E;">Presença nas aulas</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        mentoria_presenca = mentoria_presenca.dropna(subset=['Endereço de email'])
        cor_texto_roxo = '#FFFFFF'
        cor_texto_laranja = '#000000'

        medias = pd.DataFrame(columns=mentoria_presenca.columns)

        for col in mentoria_presenca.columns:

            if mentoria_presenca[col].dtype == 'object' and mentoria_presenca[col].str.contains(',').any():
                mentoria_presenca[col] = mentoria_presenca[col].str.replace(',', '.').astype(float)

                if col.startswith('1S'):
                    aux = mentoria_presenca[mentoria_presenca[col] > 0]
                    aux2 = aux[col].mean()
                    medias.loc[0, col] = aux2
                else:
                    medias.loc[0, col] = mentoria_presenca[col].mean()

        mentoria_presenca = pd.concat([mentoria_presenca, medias], ignore_index=True)

        mentoria_presenca.loc[len(mentoria_presenca) - 1, 'Nome Completo'] = 'Média'

        

        filtro = (mentoria_presenca['Nome Completo'] == nome_selecionado) | (mentoria_presenca['Nome Completo'] == 'Média')
        mentoria_filtrada = mentoria_presenca[filtro]
                
        with st.container():
            col1, col2, col3 = st.columns([0.001, 1, 0.001])
            with col2:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Presença nas aulas de 1ª fase x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo', '1S1', '1S2', '1S3', '1S4', '1S5', '1S6', '1S7', '1S8', '1S9', '1S10', '1S11', '1S12', '1S13', '1S14', '1S15', '1S16', '1S17', '1S18', '1S19', '1S20']
                colunas_ps2 = ['1S1', '1S2', '1S3', '1S4', '1S5', '1S6', '1S7', '1S8', '1S9', '1S10', '1S11', '1S12', '1S13', '1S14', '1S15', '1S16', '1S17', '1S18', '1S19', '1S20']

                df_plot = mentoria_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                for index, row in df_plot.iterrows():

                    x_values = [i for i, col in enumerate(colunas_ps2, 1) if i <= 20]
                    if row['Nome Completo'] == 'Média':
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=x_values, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                                textposition='inside',
                                                textfont=dict(color=cor_texto_laranja), 
                                                texttemplate='<b>%{text:.0%}</b>',
                                                textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))
                    else:
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=x_values, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                                textposition='inside',
                                                textfont=dict(color=cor_texto_roxo), 
                                                texttemplate='<b>%{text:.0%}</b>',
                                                textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Semana',
                    yaxis_title='Presença (%)',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    yaxis_tickformat=".0%",
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                st.plotly_chart(fig2, use_container_width=True)

        with st.container():
            col1, col2, col3 = st.columns([0.001, 1, 0.001])
            with col2:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Presença nas aulas de 2ª fase x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo', '2S1', '2S2', '2S3', '2S4', '2S5', '2S6', '2S7', '2S8', '2S9', '2S10', '2S11', '2S12', '2S13', '2S14', '2S15', '2S16', '2S17', '2S18', '2S19', '2S20']
                colunas_ps2 = ['2S1', '2S2', '2S3', '2S4', '2S5', '2S6', '2S7', '2S8', '2S9', '2S10', '2S11', '2S12', '2S13', '2S14', '2S15', '2S16', '2S17', '2S18', '2S19', '2S20']

                df_plot = mentoria_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                for index, row in df_plot.iterrows():

                    x_values = [i for i, col in enumerate(colunas_ps2, 1) if i <= 20]
                    if row['Nome Completo'] == 'Média':
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=x_values, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                                textposition='inside',
                                                textfont=dict(color=cor_texto_laranja), 
                                                texttemplate='<b>%{text:.0%}</b>',
                                                textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))
                    else:
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=x_values, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                                textposition='inside',
                                                textfont=dict(color=cor_texto_roxo), 
                                                texttemplate='<b>%{text:.0%}</b>',
                                                textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Semana',
                    yaxis_title='Presença (%)',
                    barmode='group', 
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    yaxis_tickformat=".0%",
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                st.plotly_chart(fig2, use_container_width=True)

        filtro2 = (mentoria_presenca_area['Nome'] == nome_selecionado) | (mentoria_presenca_area['Nome'] == 'Média')

        mentoria_area_filtrada = mentoria_presenca_area[filtro2]

        cor_texto_roxo = '#FFFFFF'
        cor_texto_laranja = '#000000'

        convert_columns = ['Matemática', 'Ciências Humanas', 'Ciências da Natureza', 'Redação', 'Linguagens','2ª fase']
        for col in convert_columns:
            mentoria_area_filtrada[col] = [float(value.replace(',', '.')) if value else float('nan') for value in mentoria_area_filtrada[col]]

        disciplinas = [col for col in convert_columns if ((mentoria_area_filtrada[col] > 0).all())]

        fig = go.Figure()

        for index, row in mentoria_area_filtrada.iterrows():
            if row['Nome'] == 'Média':
                continue
            fig.add_trace(go.Bar(name=row['Nome'], x=disciplinas, y=row[disciplinas], 
                                    text= row[disciplinas],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
            offsetgroup=row['Nome'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

        fig.add_trace(go.Bar(name='Média', x=disciplinas, y=mentoria_area_filtrada.loc[mentoria_area_filtrada['Nome'] == 'Média', disciplinas].values[0],
                            text= mentoria_area_filtrada.loc[mentoria_area_filtrada['Nome'] == 'Média', disciplinas].values[0],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                            offsetgroup='Média', marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

        fig.update_layout(
            xaxis_title='Áreas',
            yaxis_title='Presença (%)',
            barmode='group',  
            yaxis=dict(range=[0, 1]), 
            legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="center",
            x=0.5),
            yaxis_tickformat=".0%",
            height=400, 
            width=1200, 
            margin=dict(l=5, r=5, b=50, t=50, pad=0),

        )

        convert_columns2 = ['Matemática A', 'Matemática B', 'Matemática C', 'História', 'Geografia','Biologia', 'Física', 'Química', 'Linguagens', 'Redação']
        for col in convert_columns2:

            if mentoria_area_filtrada[col].dtype != 'float64':

                mentoria_area_filtrada[col] = mentoria_area_filtrada[col].apply(lambda x: float(x.replace(',', '.')) if isinstance(x, str) and x else x)

        disciplinas2 = [col for col in convert_columns2 if (mentoria_area_filtrada[col].apply(lambda x: x > 0 if isinstance(x, float) else False).all())]

        fig2 = go.Figure()

        for index, row in mentoria_area_filtrada.iterrows():
            if row['Nome'] == 'Média':
                continue
            fig2.add_trace(go.Bar(name=row['Nome'], x=disciplinas2, y=row[disciplinas2], 
                                text= row[disciplinas2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                offsetgroup=row['Nome'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

        fig2.add_trace(go.Bar(name='Média', x=disciplinas2, y=mentoria_area_filtrada.loc[mentoria_area_filtrada['Nome'] == 'Média', disciplinas2].values[0],
                            text= mentoria_area_filtrada.loc[mentoria_area_filtrada['Nome'] == 'Média', disciplinas2].values[0],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                            offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

        fig2.update_layout(
            xaxis_title='Disciplinas',
            yaxis_title='Presença (%)',
            barmode='group',  
            yaxis=dict(range=[0, 1]),  
            legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="center",
            x=0.5),
            yaxis_tickformat=".0%",
            height=400, 
            width=1200, 
            margin=dict(l=5, r=5, b=50, t=50, pad=0),
        )

        with st.container():
            col1, col2, col3 = st.columns([1,0.05,1])
            with col1:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Presença nas aulas por área x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.plotly_chart(fig, use_container_width=True)

            with col3:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Presença nas aulas por disciplina x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.plotly_chart(fig2, use_container_width=True)

        st.markdown(
            """
            <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-top: -20px; margin-bottom: -40px;">
                <div style="font-size: 50px; font-weight: bold; text-transform: uppercase; color: #9E089E;">Simulados de 1ª fase</div>
            </div>
            """,
            unsafe_allow_html=True
        ) 

        mentoria_simulado = ler_planilha("1Ew9AZCGJJXRRbJP2mxz_1UGymb-PX8yZHNUwrbumK70", "Mentoria | Streamlit | Simulado!A1:EB100")

        lista_simulados = ['S1', 'S2', 'S3','S4','S5','S6']

        for col in mentoria_simulado.columns:
            if mentoria_simulado[col].dtype == 'object' and mentoria_simulado[col].str.contains(',').any() and not mentoria_simulado[col].str.contains('a').any():
                mentoria_simulado[col] = mentoria_simulado[col].str.replace(',', '.').astype(float)

            elif (mentoria_simulado[col].dtype == 'object' and not mentoria_simulado[col].astype(str).str.contains('a').any()):
                mentoria_simulado[col] = mentoria_simulado[col] + '.0'
                mentoria_simulado[col] = mentoria_simulado[col].astype(float)

        filtro2 = (mentoria_simulado['Nome Completo'] == nome_selecionado) | (mentoria_simulado['Nome Completo'] == 'Média')

        with st.container():
            col1, col2, col3 = st.columns([0.525, 1, 0.525]) 
            with col2:
                
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Número de acertos x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + lista_simulados
                colunas_ps2 = lista_simulados

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps2, y=row[colunas_ps2], 
                                    text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text}</b>',
                                    offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps2, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0], 
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text}</b>',
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 72]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                st.plotly_chart(fig2, use_container_width=True)

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,0.05,1,0.05,1]) 
            with col1:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Acertos em Matemática x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + [f'{simulado} | Matemática' for simulado in lista_simulados]
                colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' | Matemática')]
                colunas_ps3 = [coluna.split(' | ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 24]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),

                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                st.plotly_chart(fig2, use_container_width=True)

            with col3:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Acertos em Linguagens x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + [f'{simulado} | Linguagens' for simulado in lista_simulados]
                colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' | Linguagens')]
                colunas_ps3 = [coluna.split(' | ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                                text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 24]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                st.plotly_chart(fig2, use_container_width=True)

            with col5:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                if mentoria_simulado_filtrada['Turma'][index] == 'Administração, Economia e Direito':

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            Acertos em Ciências Humanas x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} | Ciências Humanas' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' | Ciências Humanas')]
                    colunas_ps3 = [coluna.split(' | ')[0] for coluna in colunas_ps2]

                    mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                    df_plot = mentoria_simulado_filtrada[colunas_ps]

                    df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                    fig2 = go.Figure()

                    color_aluno = '#9E089E'
                    color_media = '#FFA73E'
                    
                    for index, row in mentoria_simulado_filtrada.iterrows():
                        if row['Nome Completo'] == 'Média':
                            continue
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2],
                                            text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                    offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                        text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                        textposition='inside',
                                        textfont=dict(color=cor_texto_laranja), 
                                        texttemplate='<b>%{text}</b>',
                                        textangle=0,
                                        offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.update_layout(
                        xaxis_title='Simulado',
                        yaxis_title='Número de acertos',
                        barmode='group',  
                        yaxis=dict(range=[0, 24]),  
                        legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5),

                        height=400, 
                        width=1200, 
                        margin=dict(l=5, r=5, b=50, t=50, pad=0),
                    )

                    st.plotly_chart(fig2, use_container_width=True)

                else:

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            Acertos em Ciências da Natureza x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} | Ciências da Natureza' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' | Ciências da Natureza')]
                    colunas_ps3 = [coluna.split(' | ')[0] for coluna in colunas_ps2]

                    mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                    df_plot = mentoria_simulado_filtrada[colunas_ps]

                    df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                    fig2 = go.Figure()

                    color_aluno = '#9E089E'
                    color_media = '#FFA73E'
                    
                    for index, row in mentoria_simulado_filtrada.iterrows():
                        if row['Nome Completo'] == 'Média':
                            continue
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text}</b>',
                                    textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                        text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                        textposition='inside',
                                        textfont=dict(color=cor_texto_laranja), 
                                        texttemplate='<b>%{text}</b>',
                                        textangle=0,
                                        offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.update_layout(
                        xaxis_title='Simulado',
                        yaxis_title='Número de acertos',
                        barmode='group',  
                        yaxis=dict(range=[0, 24]),  
                        legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5),
                        height=400, 
                        width=1200, 
                        margin=dict(l=5, r=5, b=50, t=50, pad=0),
                    )

                    st.plotly_chart(fig2, use_container_width=True)


        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,0.05,1,0.05,1]) 
            with col1:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        % de acerto em Matemática A x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + [f'{simulado} - Matemática A' for simulado in lista_simulados]
                colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Matemática A')]
                colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))


                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

            with col3:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        % de acerto em Matemática B x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + [f'{simulado} - Matemática B' for simulado in lista_simulados]
                colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Matemática B')]
                colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

            with col5:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        % de acerto em Matemática C x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps = ['Nome Completo'] + [f'{simulado} - Matemática C' for simulado in lista_simulados]
                colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Matemática C')]
                colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,0.05,1,0.05,1]) 
            with col1:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                if mentoria_simulado_filtrada['Turma'][index] == 'Administração, Economia e Direito':

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em História Geral x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - História Geral' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - História Geral')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                else: 

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Biologia x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Biologia' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Biologia')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

            with col3:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                if mentoria_simulado_filtrada['Turma'][index] == 'Administração, Economia e Direito':

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em História do Brasil x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - História do Brasil' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - História do Brasil')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                else: 
                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Física x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Física' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Física')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

            with col5:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                if mentoria_simulado_filtrada['Turma'][index] == 'Administração, Economia e Direito':

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Atualidades x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Atualidades' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Atualidades')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                else: 

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Química x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Química' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Química')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.update_layout(
                    xaxis_title='Simulado',
                    yaxis_title='Número de acertos',
                    barmode='group',  
                    yaxis=dict(range=[0, 1]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),
                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                st.plotly_chart(fig2, use_container_width=True)

        if mentoria_simulado_filtrada['Turma'][index] == 'Administração, Economia e Direito':

            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1,0.05,1,0.05,1]) 
                with col1:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Geografia Física x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Geografia Física' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Geografia Física')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                    mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                    df_plot = mentoria_simulado_filtrada[colunas_ps]

                    df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                    fig2 = go.Figure()

                    color_aluno = '#9E089E'
                    color_media = '#FFA73E'
                    
                    for index, row in mentoria_simulado_filtrada.iterrows():
                        if row['Nome Completo'] == 'Média':
                            continue
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                        text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    # Atualizando o layout
                    fig2.update_layout(
                        xaxis_title='Simulado',
                        yaxis_title='Número de acertos',
                        barmode='group',  
                        yaxis=dict(range=[0, 1]),  
                        legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5),
                        height=400, 
                        width=1200, 
                        margin=dict(l=5, r=5, b=50, t=50, pad=0),
                    )

                    fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                    st.plotly_chart(fig2, use_container_width=True)

                with col3:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Geografia Humana x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Geografia Humana' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Geografia Humana')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                    mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                    df_plot = mentoria_simulado_filtrada[colunas_ps]

                    df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                    fig2 = go.Figure()

                    color_aluno = '#9E089E'
                    color_media = '#FFA73E'
                    
                    for index, row in mentoria_simulado_filtrada.iterrows():
                        if row['Nome Completo'] == 'Média':
                            continue
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                        text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.update_layout(
                        xaxis_title='Simulado',
                        yaxis_title='Número de acertos',
                        barmode='group',  
                        yaxis=dict(range=[0, 1]),  
                        legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5),
                        height=400, 
                        width=1200, 
                        margin=dict(l=5, r=5, b=50, t=50, pad=0),
                    )

                    fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                    st.plotly_chart(fig2, use_container_width=True)

                with col5:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            % de acerto em Filosofia/Sociologia x Média
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    colunas_ps = ['Nome Completo'] + [f'{simulado} - Filosofia/Sociologia' for simulado in lista_simulados]
                    colunas_ps2 = [coluna for coluna in colunas_ps if coluna.endswith(' - Filosofia/Sociologia')]
                    colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                    mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                    df_plot = mentoria_simulado_filtrada[colunas_ps]

                    df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                    fig2 = go.Figure()

                    color_aluno = '#9E089E'
                    color_media = '#FFA73E'
                    
                    for index, row in mentoria_simulado_filtrada.iterrows():
                        if row['Nome Completo'] == 'Média':
                            continue
                        fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                            text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                            offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                        text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0%}</b>',
                                    textangle=0,
                                        offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))

                    fig2.update_layout(
                        xaxis_title='Simulado',
                        yaxis_title='Número de acertos',
                        barmode='group',  
                        yaxis=dict(range=[0, 1]),  
                        legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5),

                        height=400, 
                        width=1200, 
                        margin=dict(l=5, r=5, b=50, t=50, pad=0),
                    )

                    fig2.update_yaxes(title_text='Acerto (%)', tickformat=',.0%')

                    st.plotly_chart(fig2, use_container_width=True)

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,0.05,1,0.05,1]) 
            with col3:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                        Nota de Redação x Média
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                colunas_ps_aux = ['Nome Completo'] + [f'{simulado} - Redação' for simulado in lista_simulados]

                colunas_ps2 = [coluna for coluna in colunas_ps_aux if coluna.endswith(' - Redação')]
                colunas_ps3 = [coluna.split(' - ')[0] for coluna in colunas_ps2]

                mentoria_simulado_filtrada = mentoria_simulado[filtro2]

                df_plot = mentoria_simulado_filtrada[colunas_ps_aux]

                df_plot[colunas_ps2] = df_plot[colunas_ps2].replace(0, np.nan)

                fig2 = go.Figure()

                color_aluno = '#9E089E'
                color_media = '#FFA73E'
                
                for index, row in mentoria_simulado_filtrada.iterrows():
                    if row['Nome Completo'] == 'Média':
                        continue
                    fig2.add_trace(go.Bar(name=row['Nome Completo'], x=colunas_ps3, y=row[colunas_ps2], 
                                        text= row[colunas_ps2],
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_roxo), 
                                    texttemplate='<b>%{text:.0f}</b>',
                                    textangle=0,
                                        offsetgroup=row['Nome Completo'], marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))))

                fig2.add_trace(go.Bar(name='Média', x=colunas_ps3, y=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],
                                    text=mentoria_simulado_filtrada.loc[mentoria_simulado_filtrada['Nome Completo'] == 'Média', colunas_ps2].values[0],  # Adiciona o texto (valores) dentro das colunas
                                    textposition='inside',
                                    textfont=dict(color=cor_texto_laranja), 
                                    texttemplate='<b>%{text:.0f}</b>',
                                    textangle=0,
                                    offsetgroup='Média',  marker=dict(color='rgba(255, 167, 62, 0.6)', line=dict(color='#FFFFFF', width=2))))


                fig2.update_layout(

                    xaxis_title='Simulado',
                    yaxis_title='Nota',
                    barmode='group',  
                    yaxis=dict(range=[0, 1000]),  
                    legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5),

                    height=400, 
                    width=1200, 
                    margin=dict(l=5, r=5, b=50, t=50, pad=0),
                )

                fig2.update_yaxes(title_text='Nota', tickformat=',.0f')

                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(
                        """
                        <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-top: -20px; margin-bottom: -40px;">
                            <div style="font-size: 50px; font-weight: bold; text-transform: uppercase; color: #9E089E;">Presença nas aulas X Simulado de 1ª fase</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

            with st.container():
                col1, col2, col3 = st.columns([0.2,0.5,0.2]) 
                with col2:

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                            Presença x Simulado
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    disciplinas_simulado  = ['Matemática A','Matemática B','Matemática C','História','Geografia','Linguagens','Redação','Biologia','Física','Química']

                    colunas_combinadas = ['Nome Completo']

                    for simulado in lista_simulados:
                        for disciplina in disciplinas_simulado:
                            coluna = f"{simulado} - {disciplina}"
                            if coluna in mentoria_simulado_filtrada.columns:
                                colunas_combinadas.append(coluna)

                    mentoria_simulado_filtrada2 = mentoria_simulado_filtrada[colunas_combinadas]

                    medias_por_disciplina = {}

                    for disciplina in disciplinas_simulado:
                        colunas_disciplina = [f"{simulado} - {disciplina}" for simulado in lista_simulados]

                        valores_filtrados = mentoria_simulado_filtrada2[colunas_disciplina].apply(lambda x: x[x > 0], axis=1)

                        media_disciplina = valores_filtrados.mean(axis=1)

                        if disciplina == 'Redação':
                            media_disciplina = media_disciplina/1000

                        medias_por_disciplina[f"Simulado - {disciplina}"] = media_disciplina

                    for coluna, valores in medias_por_disciplina.items():
                        mentoria_simulado_filtrada2[coluna] = valores

                    mentoria_presenca_filtrada = mentoria_area_filtrada.copy()

                    for coluna in disciplinas_simulado:
                        mentoria_presenca_filtrada.rename(columns={coluna: f"Presença - {coluna}"}, inplace=True)

                    mentoria_presenca_filtrada.rename(columns = {'Nome':'Nome Completo'}, inplace = True)

                    mentoria_presenca_simulado_filtrada = pd.merge(mentoria_presenca_filtrada, mentoria_simulado_filtrada2, on = 'Nome Completo', how = 'inner')

                    colunas_desejadas = [coluna for coluna in mentoria_presenca_simulado_filtrada.columns if coluna.startswith('Simulado') or coluna.startswith('Presença') or 'Nome Completo' in coluna]

                    mentoria_presenca_simulado_filtrada2 = mentoria_presenca_simulado_filtrada[colunas_desejadas]

                    mentoria_presenca_simulado_filtrada_aluno = mentoria_presenca_simulado_filtrada2.iloc[1][1:]

                    colunas_presenca = sorted([coluna for coluna in mentoria_presenca_simulado_filtrada_aluno.index if 'Presença' in coluna])
                    colunas_simulado = sorted([coluna for coluna in mentoria_presenca_simulado_filtrada_aluno.index if 'Simulado' in coluna])

                    mentoria_presenca_simulado_filtrada_aluno2 = pd.DataFrame({
                        'Presença': mentoria_presenca_simulado_filtrada_aluno[colunas_presenca].values,
                        'Simulado': mentoria_presenca_simulado_filtrada_aluno[colunas_simulado].values
                    }, index=[coluna.split(' - ')[1] for coluna in colunas_presenca])

                    mentoria_presenca_simulado_filtrada_aluno2['Presença'] = pd.to_numeric(mentoria_presenca_simulado_filtrada_aluno2['Presença'], errors='coerce')

                    mentoria_presenca_simulado_filtrada_aluno2['Presença'] = mentoria_presenca_simulado_filtrada_aluno2['Presença'].fillna(0)

                    mentoria_presenca_simulado_filtrada_aluno3 = mentoria_presenca_simulado_filtrada_aluno2[mentoria_presenca_simulado_filtrada_aluno2['Presença'] > 0]

                    presenca = mentoria_presenca_simulado_filtrada_aluno3['Presença'].tolist()
                    simulado = mentoria_presenca_simulado_filtrada_aluno3['Simulado'].tolist()

                    mentoria_presenca_simulado_filtrada_media = mentoria_presenca_simulado_filtrada2.iloc[0][1:]

                    mentoria_presenca_simulado_filtrada_media2 = pd.DataFrame({
                        'Presença': mentoria_presenca_simulado_filtrada_media[colunas_presenca].values,
                        'Simulado': mentoria_presenca_simulado_filtrada_media[colunas_simulado].values
                    }, index=[coluna.split(' - ')[1] for coluna in colunas_presenca])

                    mentoria_presenca_simulado_filtrada_media2['Presença'] = pd.to_numeric(mentoria_presenca_simulado_filtrada_media2['Presença'], errors='coerce')

                    mentoria_presenca_simulado_filtrada_media2['Presença'] = mentoria_presenca_simulado_filtrada_media2['Presença'].fillna(0)

                    mentoria_presenca_simulado_filtrada_media3 = mentoria_presenca_simulado_filtrada_media2[mentoria_presenca_simulado_filtrada_media2['Presença'] > 0]

                    presenca_media = mentoria_presenca_simulado_filtrada_media3['Presença'].tolist()
                    simulado_media = mentoria_presenca_simulado_filtrada_media3['Simulado'].tolist()

                    fig = go.Figure()

                    for disciplina, x, y in zip(disciplinas_simulado, presenca, simulado):

                        fig.add_trace(go.Scatter(
                            x=[x], 
                            y=[y], 
                            mode='markers', 
                            name=disciplina, 
                            marker_color='#9E089E',
                            marker_size=9  
                        ))

                        fig.add_trace(go.Scatter(
                            x=[x],
                            y=[y + 0.01],
                            mode='text',
                            text=[disciplina],
                            textposition='top center',  
                            textfont=dict(size=9)
                        ))

                    fig.update_layout(
                        xaxis=dict(title='Presença', range=[0, 1.02]),
                        yaxis=dict(title='Simulado', range=[0, 1.02]),
                        showlegend=False,
                        height=700, 
                        width=400,
                    )

                    fig.update_yaxes(tickformat=',.0%')
                    fig.update_xaxes(tickformat=',.0%')

                    st.plotly_chart(fig, use_container_width=True)



                        

                        