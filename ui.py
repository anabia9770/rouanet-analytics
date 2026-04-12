import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# carregar dados (reaproveita do seu app atual)
@st.cache_data
def load_data():
    return pd.read_excel("sua_planilha.xlsx")

df = load_data()

# layout moderno
st.title("📊 Rouanet Analytics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Projetos", 388)
col2.metric("Aprovado", "R$ 220M")
col3.metric("Captado", "R$ 52M")
col4.metric("Gap", "R$ 167M")
