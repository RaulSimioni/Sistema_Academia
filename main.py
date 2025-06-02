import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import backend as bk    

st.set_page_config(page_title="Sistema de Academia Senai", layout="wide")


def front_end():  

    st.title("💪 Sistema de Academia Senai")
    st.subheader(f"Bem-vindo {st.session_state.username} ao sistema de gestão de academia!")
    # - **Cliente ID:** `{cliente_id}`

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.divider()
#----------------------------------------pergunta 1---------------------------------------------------#

    st.header("Mostrando Clientes por plano")
    plano = st.selectbox('Nome plano:', bk.df_planos['nome'])
    df_filtro_planos = bk.clientes_planos(plano)
    st.dataframe(df_filtro_planos)

    st.divider()


#----------------------------------------pergunta 2---------------------------------------------------#
    st.subheader("2 Treinos")
    df_treinos_ex = bk.listar_treinos_com_exercicios()

    if df_treinos_ex.empty:
        st.warning("Nenhum treino com exercício encontrado.")
    else:
        clientes = df_treinos_ex['Cliente'].unique().tolist()
        cliente_selecionado = st.selectbox("Filtrar por cliente:", ["Todos"] + clientes)

        if cliente_selecionado != "Todos":
            df_filtrado = df_treinos_ex[df_treinos_ex["Cliente"] == cliente_selecionado]
        else:
            df_filtrado = df_treinos_ex

        st.dataframe(df_filtrado, use_container_width=True)


#----------------------------------------pergunta 3---------------------------------------------------#
    # --- Execução ---
    df_pagamentos = bk.carregar_pagamentos()
    df_resumo = bk.calcular_resumo_pagamentos(df_pagamentos)

    # --- Exibição ---
    st.subheader("📋 3 Pagamentos por Cliente")
    st.dataframe(df_resumo.sort_values("cliente_id"), use_container_width=True)

    # --- Filtro individual ---
    st.subheader("🔍 Filtrar por Cliente")
    cliente_id = st.selectbox("Selecione o Cliente ID", df_resumo["cliente_id"].unique())

    cliente = df_resumo[df_resumo["cliente_id"] == cliente_id].iloc[0]
    st.markdown(f"""
    - **Cliente ID:** `{cliente_id}`  
    - **Total Pago:** `R$ {cliente['total_pago']:,.2f}`  
    - **Último Pagamento:** `{cliente['ultimo_pagamento'].date().strftime('%d/%m/%Y')}`
    """)

    st.divider()
#----------------------------------------pergunta 4---------------------------------------------------#
    st.header("4 Mostrando Clientes por Instrutor")
    nome_instrutor = st.selectbox('Nome instrutor:', bk.df_instrutores['nome'])
    df_filtro_intrutor = bk.clientes_instrutor(nome_instrutor)
    st.dataframe(df_filtro_intrutor)
    st.divider()

    st.header("Distribuição de Clientes por Instrutor")

    df_instrutores = bk.clientes_por_instrutor_com_vazios() 

    # Gráfico de pizza
    # fig, ax = plt.subplots()
    # ax.pie(df_instrutores['quantidade'], 
    #    labels=df_instrutores['instrutor'], 
    #    autopct='%1.1f%%', 
    #    startangle=90, 
    #    counterclock=False)
    # ax.axis('equal')  # Mantém formato circular
    # st.pyplot(fig)


    # --- Carregar dados diretamente sem importar do services ---


#----------------------------------------pergunta 5---------------------------------------------------#
    st.subheader("📊 5 Formulários")
    tabs = st.tabs([
        "👤 Cliente",
        "💰 Pagamentos",
        "🏋️ Treinos",
        "💪 Exercícios"
    ])

    with tabs[0]:
        st.subheader("Cliente")
        st.write("Aqui você pode cadastrar um novo cliente.")
        with st.form("form_novo_cliente"):
            nome = st.text_input("Nome do Cliente")
            idade = st.number_input("Idade", min_value=1, step=1)
            genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
            email = st.text_input("Email")
            telefone = st.text_input("Telefone")
            plano_option = st.selectbox("Plano", bk.df_planos['nome'].tolist())
            instrutor_option = st.selectbox("Instrutor", bk.df_instrutores['nome'].tolist())
            submit_cliente = st.form_submit_button("Registrar Cliente")
            if submit_cliente:
                novo_cliente = bk.novo_cliente(nome, idade, genero, email, telefone, plano_option, instrutor_option)
                st.write(novo_cliente)
                st.success("Cliente registrado com sucesso!")
                st.balloons()

    with tabs[1]:
        st.subheader("Pagamentos")
        st.write("Aqui você pode registrar um novo pagamento.")
        with st.form("form_novo_pagamento"):
            clientes_atualizados = bk.get_clientes()['nome'].tolist()
            cliente_pagamento = st.selectbox("Cliente", clientes_atualizados)
            plano_pagamento = st.selectbox("Plano", bk.df_planos['nome'].tolist())
            data_pagamento = st.date_input("Data do Pagamento")
            submit_pagamento = st.form_submit_button("Registrar Pagamento")
    
        if submit_pagamento:
            novo_pagamento = bk.novo_pagamento(cliente_pagamento, plano_pagamento, data_pagamento)
            st.write(novo_pagamento)
            st.success("Pagamento registrado com sucesso!")
                   
    with tabs[2]:
        st.subheader("Treinos")
        st.write("Aqui você pode registrar um novo treino.")
        with st.form("form_novo_treino"):
            clientes_atualizados = bk.get_clientes()['nome'].tolist()
            cliente_treino = st.selectbox("Cliente", clientes_atualizados)
            data_treino = st.date_input("Data do Treino")
            submit_treino = st.form_submit_button("Registrar Treino")
            if submit_treino:
                novo_treino = bk.novo_treino(cliente_treino, data_treino)
                st.write(novo_treino)
                st.success("Treino registrado com sucesso!")

    with tabs[3]:
        st.subheader("Exercícios")
        st.write("Aqui você pode cadastrar um novo exercício.")

        with st.form("form_novo_exercicio"):
            nome_exercicio = st.text_input("Nome do Exercício")
            grupo_muscular = st.selectbox("Grupo Muscular", [
                "Peito", "Costas", "Pernas", "Bíceps", "Tríceps", "Ombro", "Abdômen"
            ])
            submit_exercicio = st.form_submit_button("Registrar Exercício")
        
        if submit_exercicio:
            resultado = bk.novo_exercicio(nome_exercicio, grupo_muscular)
            st.write(resultado)
            if "sucesso" in resultado:
                st.success("Exercício registrado com sucesso!")
            else:
                st.error(resultado)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Telas
def tela_login():
    st.title("Login / Registro")

    tab1, tab2 = st.tabs(["Login", "Registrar"])

    with tab1:
        user = st.text_input("Usuário", key="login_user")
        pwd = st.text_input("Senha", type="password", key="login_pwd")
        if st.button("Entrar"):
            if bk.verificar_usuario(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success("Login bem-sucedido!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with tab2:
        new_user = st.text_input("Novo usuário", key="reg_user")
        new_pwd = st.text_input("Nova senha", type="password", key="reg_pwd")
        if st.button("Registrar"):
            if bk.registrar_usuario(new_user, new_pwd):
                st.success("Usuário registrado com sucesso!")
            else:
                st.error("Usuário já existe.")

# Controle de navegação
if st.session_state.logged_in:
    front_end()
else:
    tela_login()