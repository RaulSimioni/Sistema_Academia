import streamlit as st
import pandas as pd
import backend as bk  


st.set_page_config(page_title="Sistema de Academia Senai", layout="wide")

def pagina_dashboard():
    st.title("💪 Sistema de Academia Senai")
    st.subheader(f"Bem-vindo {st.session_state.username} ao sistema de gestão de academia!")
    st.divider()

    total_clientes        = bk.get_total_clientes()
    total_planos          = bk.get_total_planos()
    total_pagamentos      = bk.get_total_pagamentos_mes()
    media_idade_clientes  = bk.get_media_idade_clientes()
    clientes_ativos_reais = bk.get_clientes_ativos()
    receita_mes_atual     = bk.get_receita_mes_atual()
    novos_30dias          = bk.get_novos_clientes_30dias()
    top1_plano_list       = bk.get_top1_plano()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes Ativos",       f"{total_clientes}")
    col2.metric("Planos Ativos",         f"{total_planos}")
    col3.metric("Novos (Últimos 30 dias)", f"{novos_30dias}")
    col4.metric("Clientes c/ Treino Ativo", f"{clientes_ativos_reais}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Média de Idade",        f"{media_idade_clientes:.1f}")
    col6.metric("Receita em Jun/2025",   f"R$ {receita_mes_atual:,.2f}")
    col7.metric("Pagamentos Neste Mês",  f"{total_pagamentos}")
    if top1_plano_list:
        nome_plano_mais, _ = top1_plano_list[0]
        col8.metric("Plano mais utilizado", nome_plano_mais)
    else:
        col8.metric("Plano mais utilizado", "—")

    st.divider()

    df_receita_mes = bk.get_receita_por_mes()
    if not df_receita_mes.empty:
        df_receita_mes["mes"] = pd.to_datetime(df_receita_mes["mes"], format="%Y-%m")
        df_receita_mes = df_receita_mes.set_index("mes")
        st.subheader("📈 Evolução da Receita Mensal")
        st.line_chart(df_receita_mes["total"])
    else:
        st.write("Ainda não há dados de pagamentos para gerar o gráfico de receita.")

    st.divider()

def pagina_clientes_por_plano():
    st.title("🏋️‍♂️ CLIENTES POR PLANO")
    st.subheader("A página Clientes por Plano exibe a lista de clientes filtrada por plano contratado")
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("VISUALIZAÇÃO TABULAR")
        plano = st.selectbox('Nome plano:', bk.df_planos['nome'])
        df_filtro_planos = bk.clientes_planos(plano)
        st.dataframe(df_filtro_planos)

    with col2:
        st.subheader("VISUALIZAÇÃO GRÁFICA")
        fig = bk.grafico_clientes_por_plano()
        if isinstance(fig, str):
            st.warning(fig)
        else:
            st.pyplot(fig)


def pagina_treinos():
    st.title("🏃‍♀️ TREINOS E SEUS EXERCÍCIOS")
    st.subheader('A página Treinos exibe a lista de treinos e seus exercícios, permitindo filtrar por cliente e visualizar gráficos de desempenho.')
    
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("VISUALIZAÇÃO TABULAR")
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
    
    with col2:
        st.subheader("VISUALIZAÇÃO GRÁFICA")
        st.pyplot(bk.grafico_treinos_por_cliente())

def pagina_pagamentos():
    st.subheader("PAGAMENTOS")
    
    st.divider()

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

    st.subheader("📋 Pagamentos por Cliente")
    st.dataframe(df_para_exibir.sort_values("cliente_id"), use_container_width=True)

    st.title("Total de Pagamentos por Mês")
    st.pyplot(bk.grafico_pagamentos())

def pagina_instrutores():
    st.subheader("INSTRUTORES E SEUS CLIENTES")
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("VISUALIZAÇÃO TABULAR")
        df_instrutores = bk.carregar_instrutores()
        nome_instrutor = st.selectbox('Nome instrutor:', df_instrutores['nome'])
        df_filtro_instrutor = bk.clientes_instrutor(nome_instrutor)
        st.dataframe(df_filtro_instrutor)

    with col2:
        st.subheader("VISUALIZAÇÃO GRÁFICA")
        st.pyplot(bk.grafico_instrutores())

def pagina_formularios():
    st.subheader("📊 Formulários")
    
    st.divider()

    tabs = st.tabs([
        "👤 Cliente",
        "💰 Pagamentos",
        "🏋️ Treinos",
        "💪 Exercícios",
        "📝 Atribuir Exercício"

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
            resposta = bk.novo_cliente(
                nome, idade, genero, email, telefone, plano_option, instrutor_option
            )

            if resposta["status"] == "sucesso":
                st.success(resposta["mensagem"])
            else:
                st.warning(resposta["mensagem"])
                
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
            if submit_pagamento:
                resposta = bk.novo_pagamento(cliente_pagamento, plano_pagamento, data_pagamento)

                if resposta["status"] == "sucesso":
                    st.success(resposta["mensagem"])
                else:
                    st.warning(resposta["mensagem"])
                   
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
            if novo_treino['status'] == 'success':
                st.success("Treino registrado com sucesso!")
            else:
                st.error(novo_treino['message'])

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

    with tabs[4]:
        st.subheader("Treinos")
        st.write("Aqui você pode atribuir exercícios aos treinos já cadastrados de um cliente.")

        with st.form("form_atribuir_exercicio"):
            df_clientes = bk.get_clientes() 
            lista_clientes = df_clientes["nome"].tolist()

            if not lista_clientes:
                st.warning("Não há clientes cadastrados.")
                st.stop() 
            cliente_selecionado = st.selectbox("Selecione o Cliente", lista_clientes)

            df_treinos = bk.get_treinos_por_cliente(cliente_selecionado)
            if df_treinos.empty:
                st.warning(f"O cliente '{cliente_selecionado}' não possui treinos cadastrados.")
                st.stop()
            
            opcoes_treinos = df_treinos["data_inicio"].dt.strftime("%Y-%m-%d").tolist()
            treino_escolhido = st.selectbox("Selecione a data do Treino", opcoes_treinos)

            idx = opcoes_treinos.index(treino_escolhido)
            treino_id = int(df_treinos.iloc[idx]["id"])

            df_exs = bk.get_exercicios()
            lista_exs = df_exs["nome"].tolist()
            if not lista_exs:
                st.warning("Não há exercícios cadastrados.")
                st.stop()
            exercicio_escolhido = st.selectbox("Selecione o Exercício", lista_exs)

            series = st.number_input("Séries", min_value=1, step=1, value=3)
            repeticoes = st.number_input("Repetições", min_value=1, step=1, value=10)

            submit_exercicio = st.form_submit_button("Atribuir Exercício ao Treino")

    if submit_exercicio:
        resposta = bk.adicionar_exercicio_treino(treino_id, exercicio_escolhido, series, repeticoes)
        if resposta["status"] == "sucesso":
            st.success(resposta["mensagem"])
        else:
            st.error(resposta["mensagem"])

def front_end():
    col1, col2, col3, col4, col5 = st.sidebar.columns([1, 1, 2, 1, 1])
    with col3:
        st.image("Academia_Senai.png", width=80)
    
    col1, col2, col3, col4, col5 = st.sidebar.columns([1, 1, 2, 1, 1])
    with col3:
        st.sidebar.write(f"### **Olá {st.session_state.username}!**")

    st.sidebar.divider()

    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "Dashboard"

    if st.sidebar.button("Dashboard" ,type='tertiary'):
        st.session_state.menu_ativo = "Dashboard"
    if st.sidebar.button("Clientes por Plano", type='tertiary'):
        st.session_state.menu_ativo = "Clientes por Plano"
    if st.sidebar.button("Treinos", type='tertiary'):
        st.session_state.menu_ativo = "Treinos"
    if st.sidebar.button("Pagamentos", type='tertiary'):
        st.session_state.menu_ativo = "Pagamentos"
    if st.sidebar.button("Clientes por Instrutor", type='tertiary'):
        st.session_state.menu_ativo = "Clientes por Instrutor"
    if st.sidebar.button("Formulários", type='tertiary'):
        st.session_state.menu_ativo = "Formulários"


    col1, col2, col3, col4, col5 = st.sidebar.columns([1, 1, 2, 1, 1])
    if col3.button("❌ Sair"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    menu = st.session_state.menu_ativo

    if menu == "Dashboard":
        pagina_dashboard()
    elif menu == "Clientes por Plano":
        pagina_clientes_por_plano()
    elif menu == "Treinos":
        pagina_treinos()
    elif menu == "Pagamentos":
        pagina_pagamentos()
    elif menu == "Clientes por Instrutor":
        pagina_instrutores()
    elif menu == "Formulários":
        pagina_formularios()


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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    front_end()
else:
    tela_login()


