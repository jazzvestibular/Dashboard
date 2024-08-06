import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from presenca_alunos import mostrar_presenca_alunos
from gamificacao import mostrar_gamificacao
from resultados_simulados import mostrar_resultados_simulados
import datetime
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
        'pagina_atual': 'Alunos'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def mostrar_alunos(nome, permissao, email):
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

    if permissao != 'Aluno':

        with st.container():
                col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
                with col1:
                    botao_clicado12 = col1.button('Gamificação', key='b12')
                    ChangeButtonColour('Gamificação', 'white', '#ff80e6')
                with col2:
                    botao_clicado10 = col2.button('Presença nas aulas', key='b10')
                    ChangeButtonColour('Presença nas aulas', 'white', '#ff80e6')
                with col3:
                    botao_clicado11 = col3.button('Engajamento na plataforma', key='b11')
                    ChangeButtonColour('Engajamento na plataforma', 'white', '#ff80e6')
                with col4:
                    botao_clicado13 = col4.button('Resultado nos simulados', key='b13')
                    ChangeButtonColour('Resultado nos simulados', 'white', '#ff80e6')
                with col5:
                    st.write("")

        st.markdown(
        """
        <hr style="border: 1px solid #ff80e6; margin-top: -30px;">
        """,
        unsafe_allow_html=True
        )

        botoes_menu = [botao_clicado10, botao_clicado11, botao_clicado12, botao_clicado13]

        if all(not botao for botao in botoes_menu) and estado['pagina_atual'] != 'Alunos - Resultados nos simulados':
            estado['pagina_atual'] = 'Alunos - Gamificação'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_gamificacao(nome, permissao, email)

        elif botao_clicado12:
            estado['pagina_atual'] = 'Alunos - Gamificação'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_gamificacao(nome, permissao, email)

        if botao_clicado10:
            estado['pagina_atual'] = 'Alunos - Presença nas aulas'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_presenca_alunos()

        if botao_clicado11:
            estado['pagina_atual'] = 'Alunos - Engajamento na plataforma'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

        if botao_clicado13 or estado['pagina_atual'] == 'Alunos - Resultados nos simulados':
            estado['pagina_atual'] = 'Alunos - Resultados nos simulados'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_resultados_simulados()

    elif permissao == 'Aluno':

        with st.container():
                col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
                with col1:
                    botao_clicado12 = col1.button('Gamificação', key='b12')
                    ChangeButtonColour('Gamificação', 'white', '#ff80e6')
                with col2:
                    botao_clicado13 = col2.button('Resultado nos simulados', key='b13')
                    ChangeButtonColour('Resultado nos simulados', 'white', '#ff80e6')
                with col3:
                    st.write("")
                    #botao_clicado11 = col3.button('Engajamento na plataforma', key='b11')
                    #ChangeButtonColour('Engajamento na plataforma', 'white', '#ff80e6')
                with col4:
                    st.write("")
                    #botao_clicado10 = col4.button('Presença nas aulas', key='b10')
                    #ChangeButtonColour('Presença nas aulas', 'white', '#ff80e6')
                with col5:
                    st.write("")

        st.markdown(
        """
        <hr style="border: 1px solid #ff80e6; margin-top: -30px;">
        """,
        unsafe_allow_html=True
        )

        botoes_menu = [botao_clicado12, botao_clicado13]#, botao_clicado11, botao_clicado10, botao_clicado13]

        if all(not botao for botao in botoes_menu) and estado['pagina_atual'] != 'Alunos - Resultados nos simulados':
            estado['pagina_atual'] = 'Alunos - Gamificação'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_gamificacao(nome, permissao, email)

        elif botao_clicado12:
            estado['pagina_atual'] = 'Alunos - Gamificação'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_gamificacao(nome, permissao, email)

        elif botao_clicado13:
            estado['pagina_atual'] = 'Alunos - Resultados nos simulados'
            data_hoje_brasilia, hora_atual_brasilia = dia_hora()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
            escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
            mostrar_resultados_simulados(nome, permissao, email)

        #if botao_clicado10:
        #    estado['pagina_atual'] = 'Alunos - Presença nas aulas'
        #    data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        #    data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
        #    escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
        #    mostrar_presenca_alunos()

        #if botao_clicado11:
        #    estado['pagina_atual'] = 'Alunos - Engajamento na plataforma'
        #    data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        #    data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
        #    escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")

        #if botao_clicado13 or estado['pagina_atual'] == 'Alunos - Resultados nos simulados':
        #    estado['pagina_atual'] = 'Alunos - Resultados nos simulados'
        #    data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        #    data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", "", email]]
        #    escrever_planilha("1Folwdg9mIwSxyzQuQlmwCoEPFq_sqC39MohQxx_J2_I", data_to_write, "Logs")
        #    mostrar_resultados_simulados()


    

    



    