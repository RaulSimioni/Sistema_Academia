import streamlit as st
import backend as bk


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