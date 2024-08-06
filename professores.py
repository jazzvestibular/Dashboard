import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from controle_aulas import mostrar_controle_aulas
import datetime
import pytz
import pytz
from logs import escrever_planilha

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

def mostrar_professores(nome, permissao, email):

    estado = get_estado()

    def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
        htmlstr = f"""
            <script>
                var elements = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < elements.length; ++i) {{ 
                    if (elements[i].innerText == '{widget_label}') {{ 
                        elements[i].style.color ='{font_color}';
                        elements[i].style.background = '{background_color}';
                        elements[i].style.width = '230px';  // Adiciona a largura desejada
                        elements[i].style.height = '50px';  // Adiciona a altura desejada
                    }}
                }}
            </script>
            """
        components.html(f"{htmlstr}", height=0, width=0)

    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        with col1:
            botao_clicado15 = col1.button('Controle das aulas', key='b15')
            ChangeButtonColour('Controle das aulas', 'white', '#ff80e6')
        with col2:
            st.write("")
        with col3:
            st.write("")
        with col4:
            st.write("")
        with col5:
            st.write("")

    st.markdown(
    """
    <hr style="border: 1px solid #ff80e6; margin-top: -30px;">
    """,
    unsafe_allow_html=True
    )

    botoes_menu = [botao_clicado15]

    if all(not botao for botao in botoes_menu):
        estado['pagina_atual'] = 'Professores - Controle das aulas'
        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
        mostrar_controle_aulas()

    if botao_clicado15:
        estado['pagina_atual'] = 'Professores - Controle das aulas'
        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
        escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
        mostrar_controle_aulas()