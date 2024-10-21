import streamlit as st
import streamlit.components.v1 as components
from presenca_alunos import ler_planilha, ler_planilha2

def define_estado():
    return {
        'pagina_atual': 'Página Inicial'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
        htmlstr = f"""
            <script>
                var elements = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < elements.length; ++i) {{ 
                    if (elements[i].innerText == '{widget_label}') {{ 
                        elements[i].style.color ='{font_color}';
                        elements[i].style.background = '{background_color}';
                        elements[i].style.width = '120px';  // Adiciona a largura desejada
                        elements[i].style.height = '50px';  // Adiciona a altura desejada
                    }}
                }}
            </script>
            """
        components.html(f"{htmlstr}", height=0, width=0)




def mostrar_formulario_login():

    html_br="""
        <br>
        """

    with st.container():
            col1, col2, col3 = st.columns([3,4,3])
            with col1:
                st.markdown(html_br, unsafe_allow_html=True)
            with col2:
                st.image("./logo_jazz.png")
            with col3:
                st.markdown(html_br, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    email = col2.text_input("Email", key="emaill", value="")

    senha = col2.text_input("Senha", type="password", key="senha", value="")

    html_br="""
        <br>
        """

    st.markdown(html_br, unsafe_allow_html=True)

    col4, col5, col6 = st.columns([9, 1, 10])
    st.write('Entrei01')
    entrar_button = col5.button('Entrar', key='b20')
    ChangeButtonColour('Entrar', 'white', '#9E089E')

    tabela_usuarios = ler_planilha2("1YxmzHU3AWA_SVoRDX7n8AQmLMravj093Wtzsuvkuo3M", "Lista de usuários | Streamlit | Tabela permissões!A1:E1000")
    st.dataframe(tabela_usuarios)
    lista_emails = tabela_usuarios["Email"].tolist()
    st.write(lista_emails)

    if entrar_button:
        st.write('Entrei')
        email = email.lower()  

        if email in lista_emails:
            st.write('Entrei02')

            indice_email = lista_emails.index(email)  
            senha_correspondente = tabela_usuarios.loc[indice_email, "Senha"]


            if senha == senha_correspondente:
                st.write('Entrei 03')
                st.session_state.logged_in = True
                st.success("Login bem-sucedido! Você pode acessar seu conteúdo aqui.")
                st.write('Entrei2')

                if tabela_usuarios.loc[indice_email, "Permissão"] != 'Responsável':
                    st.write('Entrei3')
                    return True, tabela_usuarios.loc[indice_email, "Permissão"], tabela_usuarios.loc[indice_email, "Nome"], tabela_usuarios.loc[indice_email, "Email"]
                else:
                    return True, tabela_usuarios.loc[indice_email, "Permissão"], tabela_usuarios.loc[indice_email, "Aluno (responsável)"], tabela_usuarios.loc[indice_email, "Email"]
            else:
                st.error("Senha incorreta. Tente novamente.")
                return False, "Sem Permissão", "Sem Nome", "Sem Email"
        else:
            st.error("Email não encontrado. Verifique o email fornecido.")
            return False, "Sem Permissão", "Sem Nome",  "Sem Email"

    return False, "Sem Permissão", "Sem Nome",  "Sem Email"
        
def mostrar_tela_login():

    estado = get_estado()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "tipo_usuario" not in st.session_state:
        st.session_state.tipo_usuario = "Sem Permissão"

    if "nome_usuario" not in st.session_state:
        st.session_state.nome_usuario = "Sem Nome"

    if "Email" not in st.session_state:
        st.session_state.email = "Sem Email"

    if st.session_state.logged_in:
        tipo_usuario = st.session_state.get("tipo_usuario", None)
        nome_usuario = st.session_state.get("nome_usuario", None)
        Email = st.session_state.get("Email", None)
        return True, tipo_usuario, nome_usuario, Email

    if not st.session_state.logged_in:
        st.write('Entrei0')
        login_ok, tipo_usuario, nome_usuario, Email = mostrar_formulario_login()
        st.write('Entrei04')
        if login_ok:
            st.session_state.tipo_usuario = tipo_usuario
            st.session_state.nome_usuario = nome_usuario
            st.session_state.Email = Email
            i = 0
            #if i == 0:
            #    st.experimental_rerun()
            #    i = i + 1
            return True, st.session_state.tipo_usuario, st.session_state.nome_usuario, st.session_state.Email
        
        return False, "Sem Permissão", "Sem Nome", "Sem Email"

    else:
        return True, st.session_state.tipo_usuario, st.session_state.nome_usuario, st.session_state.Email



        
