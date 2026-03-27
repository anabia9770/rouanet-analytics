import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 Rouanet Analytics")
st.caption("Dashboard interativo de projetos culturais")

# carregar dados
df = pd.read_excel("TCC_Projeto.xlsx")

# padronizar
df.columns = df.columns.str.lower().str.replace(" ", "_")

# garantir números
for col in ["valor_aprovado", "valor_captado"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# criar gap
if "valor_aprovado" in df.columns and "valor_captado" in df.columns:
    df["gap"] = df["valor_aprovado"] - df["valor_captado"]

# SIDEBAR (filtros)
st.sidebar.header("Filtros")

municipios = df["municipio"].dropna().unique() if "municipio" in df.columns else []
segmentos = df["segmento"].dropna().unique() if "segmento" in df.columns else []

municipio_sel = st.sidebar.multiselect("Município", municipios)
segmento_sel = st.sidebar.multiselect("Segmento", segmentos)

df_filtrado = df.copy()

if municipio_sel:
    df_filtrado = df_filtrado[df_filtrado["municipio"].isin(municipio_sel)]

if segmento_sel:
    df_filtrado = df_filtrado[df_filtrado["segmento"].isin(segmento_sel)]

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Projetos", len(df_filtrado))
col2.metric("Aprovado", f"R$ {df_filtrado['valor_aprovado'].sum():,.0f}")
col3.metric("Captado", f"R$ {df_filtrado['valor_captado'].sum():,.0f}")
col4.metric("Gap", f"R$ {df_filtrado['gap'].sum():,.0f}")

# GRÁFICO POR SEGMENTO
if "segmento" in df_filtrado.columns:
    fig = px.bar(
        df_filtrado.groupby("segmento")["valor_aprovado"].sum().reset_index(),
        x="valor_aprovado",
        y="segmento",
        orientation="h",
        title="Valor por Segmento"
    )
    st.plotly_chart(fig, use_container_width=True)

# GRÁFICO POR MUNICÍPIO
if "municipio" in df_filtrado.columns:
    fig2 = px.bar(
        df_filtrado.groupby("municipio")["gap"].sum().reset_index().sort_values("gap"),
        x="gap",
        y="municipio",
        orientation="h",
        title="Gap por Município"
    )
    st.plotly_chart(fig2, use_container_width=True)

# TABELA
st.subheader("Projetos")

st.dataframe(
    df_filtrado.sort_values("gap", ascending=False),
    use_container_width=True
)
