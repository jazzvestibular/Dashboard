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
import locale
import numpy as np

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def define_estado():
    return {
        'pagina_atual': 'Página Inicial'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)
  
def ler_planilha(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
    
    creds = None

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)
            
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

        values = result.get("values", [])
        values2 = pd.DataFrame(values[1:], columns=values[0])

    except HttpError as err:
        var = 1

    return values2

def graficos_semana(valor_por_semana, aulas_por_professor):

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-top: -20px; margin-bottom: -40px;">
            <div style="font-size: 50px; font-weight: bold; text-transform: uppercase; color: #9E089E;">Controle Semanal</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        col0, col1, col2, col3 = st.columns([0.05,1,0.05,1])
        with col1:

            valor_por_semana['Total'] = valor_por_semana['Total'].astype(int)

            valor_total = valor_por_semana['Total'].sum()

            formatted_html = """
                <div style="background-color: white; color: #9E089E; font-weight: bold; height: 40px; padding: -10px; border-radius: 10px; text-align: center; margin-top: 20px; margin-bottom: -50px; display: flex; align-items: center; justify-content: center; font-size: 30px;">
                    Valor Total: R$ {},00
                </div>
            """.format(valor_total)

            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

            st.markdown(
                """
                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                    Valores por semana
                </div>
                """,
                unsafe_allow_html=True
            )

            valor_por_semana['Pago'] = valor_por_semana['Pago'].astype(int)
            valor_por_semana['Não Pago'] = valor_por_semana['Não Pago'].astype(int)

            fig = make_subplots(rows=1, cols=1)

            fig.add_trace(go.Bar(
                x=valor_por_semana['Semana'],
                y=valor_por_semana['Pago'],
                name='Pago',
                marker=dict(color='rgba(158, 8, 158, 0.6)', line=dict(color='#FFFFFF', width=2))
            ))

            fig.add_trace(go.Bar(
                x=valor_por_semana['Semana'],
                y=valor_por_semana['Não Pago'],
                name='Não Pago',
                marker=dict(color='rgba(1, 225, 225, 0.6)', line=dict(color='#FFFFFF', width=2))
            ))

            total_pago = valor_por_semana['Pago'].sum()
            total_nao_pago = valor_por_semana['Não Pago'].sum()

            fig.update_layout(
                barmode='stack',  
                showlegend=True,  
                height=400, 
                width=1200, 
                yaxis=dict(title='Valor (R$)', tickformat='$.2f'),
                xaxis=dict(title='Semana'),
                margin=dict(l=5, r=5, b=50, t=50, pad=0),
                legend=dict(orientation='h', y=1.02, yanchor='bottom', x=0.5, xanchor='center'),
                annotations=[
                    dict(
                        text=f'<br>Total Pago: R${total_pago:.2f}<br>Em aberto: R${total_nao_pago:.2f}',
                        x=0.98, y=0.98,  
                        xref='paper', yref='paper',
                        xanchor='right', yanchor='top',  
                        showarrow=False,
                        font=dict(size=12, color = 'black')
                    )
                ]
            )

            st.plotly_chart(fig, use_container_width=True)

        with col3:

            valor_por_semana['Pago'] = valor_por_semana['Pago'].astype(int)

            valor_pago = valor_por_semana['Pago'].sum()

            formatted_html = """
                <div style="background-color: white; color: #9E089E; font-weight: bold; height: 40px; padding: -10px; border-radius: 10px; text-align: center; margin-top: 20px; margin-bottom: -50px; display: flex; align-items: center; justify-content: center; font-size: 30px;">
                    Valor Pago: R$ {},00
                </div>
            """.format(valor_pago)  

            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

            st.markdown(
                """
                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center;">
                    Presença dos alunos por área
                </div>
                """,
                unsafe_allow_html=True
            )

            colunas_ps = ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PS6', 'PS7', 'PS8', 'PS9', 'PS10', 'PS11', 'PS12', 'PS13', 'PS14', 'PS15', 'PS16', 'PS17', 'PS18', 'PS19', 'PS20', 'PS21']

            for coluna in colunas_ps:
                aulas_por_professor[coluna] = pd.to_numeric(aulas_por_professor[coluna].str.replace(',', '.'), errors='coerce')

            numeric_cols = aulas_por_professor.select_dtypes(include='number')

            numeric_cols['Área'] = aulas_por_professor['Área']

            aulas_por_professor2 = numeric_cols.groupby('Área').mean().reset_index()


            df_plot = aulas_por_professor2.copy()

            df_plot[colunas_ps] = df_plot[colunas_ps].replace(0, np.nan)

            df_plot = df_plot[df_plot['Área'] != '2ª fase']

            cores = {
                'Humanas': '#9E089E',
                'Natureza': '#01E1E1',
                'Linguagens': '#FFAA73',
                'Matemática': '#0010B3',
                'Redação': 'gray'
            }

            fig = go.Figure()

            for index, row in df_plot.iterrows():

                x_values = [i for i, col in enumerate(colunas_ps, 1) if i <= 20]

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=row[colunas_ps].values,
                    mode='lines+markers',
                    name=row['Área'],
                    line_color=cores.get(row['Área'], 'gray')  
                ))

            fig.update_xaxes(tickvals=list(range(1, 21)))

            fig.update_layout(
                xaxis=dict(title='Semana', showgrid=False),
                yaxis=dict(title='Presença dos alunos (%)', range=[0, 1.05]),
                showlegend=True,
                height=400, 
                width=1200, 
                margin=dict(l=5, r=5, b=50, t=50, pad=0),
                legend=dict(orientation='h', y=1.02, yanchor='bottom', x=0.5, xanchor='center')
            )

            fig.update_yaxes(title_text='Presença (%)', tickformat=',.0%')
            fig.update_xaxes(title_text='Semana')

            st.plotly_chart(fig, use_container_width=True)

def tabela_professores(aulas_por_professor):

    aulas_por_professor[['Presença']] = aulas_por_professor[['Presença']].applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)
    aulas_por_professor[['Presença Manhã']] = aulas_por_professor[['Presença Manhã']].applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)
    aulas_por_professor[['Presença Tarde']] = aulas_por_professor[['Presença Tarde']].applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)

    aulas_por_professor['Presença'] = aulas_por_professor['Presença'].replace('', '0')
    aulas_por_professor['Presença Manhã'] = aulas_por_professor['Presença Manhã'].replace('', '0')
    aulas_por_professor['Presença Tarde'] = aulas_por_professor['Presença Tarde'].replace('', '0')

    aulas_por_professor2 = aulas_por_professor.sort_values(by = 'Presença', ascending = False)

    aulas_por_professor2['Presença'] = 100*aulas_por_professor2['Presença'].astype(float)
    aulas_por_professor2['Presença'] = aulas_por_professor2['Presença'].round(0).astype(int).astype(str) + '%'

    aulas_por_professor2['Presença Manhã'] = 100*aulas_por_professor2['Presença Manhã'].astype(float)
    aulas_por_professor2['Presença Manhã'] = aulas_por_professor2['Presença Manhã'].round(0).astype(int).astype(str) + '%'

    aulas_por_professor2['Presença Tarde'] = 100*aulas_por_professor2['Presença Tarde'].astype(float)
    aulas_por_professor2['Presença Tarde'] = aulas_por_professor2['Presença Tarde'].round(0).astype(int).astype(str) + '%'

    aulas_por_professor2['Valor'] = pd.to_numeric(aulas_por_professor2['Valor'], errors='coerce')
    aulas_por_professor2 = aulas_por_professor2[aulas_por_professor2['Valor'] > 0]

    aulas_por_professor2['Valor'] = aulas_por_professor2['Valor'].map('R$ {:,.2f}'.format)

    aulas_por_professor2['Presença'] = aulas_por_professor2['Presença'].replace('0%', '')
    aulas_por_professor2['Presença Manhã'] = aulas_por_professor2['Presença Manhã'].replace('0%', '')
    aulas_por_professor2['Presença Tarde'] = aulas_por_professor2['Presença Tarde'].replace('0%', '')

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <div style="font-size: 50px; font-weight: bold; text-transform: uppercase; color: #9E089E;">Ranking de Professores - Presença dos Alunos</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        col1, col2, col3 = st.columns([0.01,5,0.01])
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
                            <th style="width: 200px; min-width: 200px; max-width: 200px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Nome</th>
                            <th style="width: 280px; min-width: 280px; max-width: 280px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Email</th>
                            <th style="width: 220px; min-width: 220px; max-width: 220px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Área</th>
                            <th style="width: 100px; min-width: 100px; max-width: 100px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Número de aulas</th>
                            <th style="width: 100px; min-width: 100px; max-width: 100px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Valor</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Presença</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Presença Manhã</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Presença Tarde</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    

    with st.container():
        col1, col2, col3 = st.columns([0.01,5,0.01])
        with col1:
           st.write("")
        with col2:

            for _, row in aulas_por_professor2.iterrows():

                st.markdown("""
                <tr style="text-align: center; ">
                    <td style="width: 200px; min-width: 200px; max-width: 200px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{0}</td>
                    <td style="width: 280px; min-width: 280px; max-width: 280px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{1}</td>
                    <td style="width: 220px; min-width: 220px; max-width: 220px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{2}</td>
                    <td style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{3}</td>
                    <td style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{4}</td>
                    <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{5}</td>
                    <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{6}</td>
                    <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #9E089E; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{7}</td>
                </tr>
            """.format(row['Professor'], row['Email'], row['Área'], row['Número de aulas'], row['Valor'], row['Presença'], row['Presença Manhã'], row['Presença Tarde']), unsafe_allow_html=True)
        with col3:
           st.write("")

def mostrar_controle_aulas():
    
    estado = get_estado()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    aulas_por_professor = ler_planilha("1eAsyur4ioNUC5ckSMDt2sWtfdzroL6MUor23hmV_BE8", "Controle das aulas | Streamlit | Tabela professor!A1:BT50")
    valor_por_semana = ler_planilha("1eAsyur4ioNUC5ckSMDt2sWtfdzroL6MUor23hmV_BE8", "Controle das aulas | Streamlit | Valores semanais!A1:D21")

    graficos_semana(valor_por_semana, aulas_por_professor)
    tabela_professores(aulas_por_professor)
