import streamlit as st
import pandas as pd
import backend as bk    

st.set_page_config(page_title="Sistema de Academia Senai", layout="wide")

def front_end():  

    st.title("💪 Sistema de Academia Senai")
    st.subheader(f"Bem-vindo {st.session_state.username} ao sistema de gestão de academia!")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.divider()
#----------------------------------------pergunta 1---------------------------------------------------#
    col1, col2 = st.columns(2)
    with col1:
        st.header("Mostrando Clientes por plano")
        plano = st.selectbox('Nome plano:', bk.df_planos['nome'])
        df_filtro_planos = bk.clientes_planos(plano)
        st.dataframe(df_filtro_planos)

    with col2:
        st.subheader("📊 Clientes por Plano")
        fig = bk.grafico_clientes_por_plano()
        if isinstance(fig, str):
            st.warning(fig)
        else:
            st.pyplot(fig)

    st.divider()

#----------------------------------------pergunta 2---------------------------------------------------#
    st.subheader("Treinos")
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

    st.divider()
#----------------------------------------pergunta 3---------------------------------------------------#
    df_pagamentos = bk.carregar_pagamentos()
    conn = bk.get_connection()
    df_clientes = bk.get_clientes()
    conn.close()

    df_resumo = bk.calcular_resumo_pagamentos(df_pagamentos, df_clientes)

    df_para_exibir = df_resumo.copy()
    df_para_exibir["ultimo_pagamento"] = (
        df_para_exibir["ultimo_pagamento"]
        .dt.strftime("%d/%m/%Y")
        .fillna("")
    )

    st.subheader("🔍 Filtrar por Cliente")

    cliente_id = st.selectbox(
        "Selecione o Cliente",
        df_resumo["cliente_id"],
        format_func=lambda x: df_resumo[df_resumo["cliente_id"] == x]["cliente_nome"].values[0]
    )

    cliente = df_resumo[df_resumo["cliente_id"] == cliente_id].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Nome", value=cliente["cliente_nome"])
    col2.metric(label="Cliente ID", value=str(cliente_id))
    col3.metric(label="Total Pago", value=f"R$ {cliente['total_pago']:,.2f}")
    if pd.isna(cliente["ultimo_pagamento"]):
        col4.metric(label="Último Pagamento", value="—")
    else:
        data_str = cliente["ultimo_pagamento"].date().strftime("%d/%m/%Y")
        col4.metric(label="Último Pagamento", value=data_str)

    st.subheader("📋 3 Pagamentos por Cliente")
    st.dataframe(df_para_exibir.sort_values("cliente_id"), use_container_width=True)

    st.divider()
#----------------------------------------pergunta 4---------------------------------------------------#
    col1, col2 = st.columns(2)
    with col1:
        st.header("Mostrando Clientes por Instrutor")
        df_instrutores = bk.carregar_instrutores()
        nome_instrutor = st.selectbox('Nome instrutor:', df_instrutores['nome'])
        df_filtro_intrutor = bk.clientes_instrutor(nome_instrutor)
        st.dataframe(df_filtro_intrutor)

    with col2:
        st.header("Distribuição de Clientes por Instrutor")

        st.pyplot(bk.grafico_instrutores())

    st.divider()
#----------------------------------------pergunta 5---------------------------------------------------#
    st.subheader("📊 Formulários")
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
            instrutor_option = st.selectbox("Instrutor", bk.carregar_instrutores()['nome'].tolist())
            submit_cliente = st.form_submit_button("Registrar Cliente")    
        if submit_cliente:
            novo_cliente = bk.novo_cliente(nome, idade, genero, email, telefone, plano_option, instrutor_option)
            st.write(novo_cliente)
            st.success("Cliente registrado com sucesso!")

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

def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2: 
        with st.container():
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

if st.session_state.logged_in:
    front_end()
else:
    tela_login()