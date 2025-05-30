import streamlit as st
import pandas as pd
import backend as bk    

st.set_page_config(page_title="Sistema de Academia Senai", layout="wide")

st.title("💪 Sistema de Academia Senai")

st.divider()

#pergunta 1
st.header("Mostrando Clientes por plano")
plano = st.selectbox('Nome plano:', bk.df_planos['nome'])
df_filtro_planos = bk.clientes_planos(plano)
st.dataframe(df_filtro_planos)

st.divider()

#pergunta 4
st.header("Mostrando Clientes por Instrutor")
nome_instrutor = st.selectbox('Nome instrutor:', bk.df_instrutores['nome'])
df_filtro_intrutor = bk.clientes_instrutor(nome_instrutor)
st.dataframe(df_filtro_intrutor)
st.divider()

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
    #Fomulario cadastro de clientes
    # novo_cliente = bk.novo_cliente('Lucas', 19, 'M', 'fadfadfdsfs@gmail.com', '439999999', 'VIP', 'Carlos Rocha')
    # st.write(novo_cliente)
    with st.form("form_novo_cliente"):
        # Buscar planos e nome do instrutor
        nome = st.text_input("Nome do Cliente")
        # with st.form("form_novo_livro"):
        #     titulo = st.text_input("Título do Livro")
        #
        #     # Busca autores disponíveis
        #     autores_df = pd.read_sql_query("SELECT id, nome FROM autores", conn)
        #     autor_option = st.selectbox("Autor", [""] + autores_df["nome"].tolist())
        #     if autor_option:
        #         autor_id = int(autores_df[autores_df["nome"] == autor_option]["id"].values[0])
        #     else:
        #         autor_id = None
        #
        #     # Busca categorias disponíveis
        #     categorias_df = pd.read_sql_query("SELECT id, nome FROM categorias", conn)
        #     categoria_option = st.selectbox("Categoria", [""] + categorias_df["nome"].tolist())
        #     if categoria_option:
        #         categoria_id = int(categorias_df[categorias_df["nome"] == categoria_option]["id"].values[0])
        #     else:
        #         categoria_id = None
        #
        #     ano = st.number_input("Ano de publicação", min_value=1, step=1)
        #     quantidade = st.number_input("Quantidade disponível", min_value=0, step=1)
        #
        #     submit_livro = st.form_submit_button("Registrar Livro")
        #
        #     if submit_livro:
        #         if titulo and autor_id and categoria_id and ano > 0 and quantidade >= 0:
        #             cursor.execute("""
        #                 INSERT INTO livros (titulo, autor_id, categoria_id, ano, quantidade_disponivel)
        #                 VALUES (?, ?, ?, ?, ?)
        #             """, (titulo, autor_id, categoria_id, int(ano), int(quantidade)))
        #             conn.commit()
        #             st.success(f"Livro '{titulo}' inserido com sucesso!")
        #             st.rerun()
        #         else:
        #             st.error("Preencha todos os campos corretamente para o livro.")

with tabs[1]:
    st.subheader("Pagamentos")
    st.write("Aqui você pode registrar um novo pagamento.")

with tabs[2]:
    st.subheader("Treinos")
    st.write("Aqui você pode registrar um novo treino.")

with tabs[3]:
    st.subheader("Exercícios")
    st.write("Aqui você pode registrar um novo exercício.")

