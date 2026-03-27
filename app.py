import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")

# -------------------------
# FUNÇÃO NORMALIZAR COLUNAS
# -------------------------
def normalize_col(col):
    col = col.strip().lower().replace(" ", "_")
    col = unicodedata.normalize("NFKD", col).encode("ascii", "ignore").decode("utf-8")
    return col

# -------------------------
# TÍTULO
# -------------------------
st.title("📊 Rouanet Analytics")
st.caption("Dashboard de análise de projetos culturais")

# -------------------------
# DADOS
# -------------------------
df = pd.read_excel("TCC.xlsx")

# normaliza nomes
df.columns = [normalize_col(c) for c in df.columns]

# ajuste correto baseado no seu Excel
df["valor_aprovado"] = pd.to_numeric(df.get("valor_solicitado", 0), errors="coerce").fillna(0)
df["valor_captado"] = pd.to_numeric(df.get("valor_captado", 0), errors="coerce").fillna(0)

df["gap"] = df["valor_aprovado"] - df["valor_captado"]

# -------------------------
# FILTROS
# -------------------------
st.sidebar.title("Filtros")

mun = st.sidebar.multiselect("Cidade", df["cidade"].dropna().unique())
seg = st.sidebar.multiselect("Segmento", df["segmento"].dropna().unique())

df_f = df.copy()

if mun:
    df_f = df_f[df_f["cidade"].isin(mun)]

if seg:
    df_f = df_f[df_f["segmento"].isin(seg)]

# -------------------------
# KPIs
# -------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Projetos", len(df_f))
c2.metric("Solicitado", f"R$ {df_f['valor_aprovado'].sum():,.0f}")
c3.metric("Captado", f"R$ {df_f['valor_captado'].sum():,.0f}")
c4.metric("Gap", f"R$ {df_f['gap'].sum():,.0f}")

# -------------------------
# GRÁFICOS
# -------------------------
st.markdown("### 📈 Análises")

col1, col2 = st.columns(2)

# Evolução por Ano
with col1:

    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year

        evolucao = (
            df_f.groupby("ano")[["valor_aprovado", "valor_captado"]]
            .sum()
            .reset_index()
            .sort_values("ano")
        )

        fig_linha = px.line(
            evolucao,
            x="ano",
            y=["valor_aprovado", "valor_captado"],
            markers=True
        )

        st.plotly_chart(fig_linha, use_container_width=True)

    else:
        st.warning("Coluna 'data_inicio' não encontrada")

# Top Segmentos
with col2:

    if "segmento" in df_f.columns:

        top_segmentos = (
            df_f.groupby("segmento")["valor_aprovado"]
            .sum()
            .sort_values(ascending=False)
            .head(8)
            .reset_index()
        )

        fig_bar = px.bar(
            top_segmentos,
            x="valor_aprovado",
            y="segmento",
            orientation="h"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("Coluna 'segmento' não encontrada")

# -------------------------
# TABELA
# -------------------------
st.markdown("### Projetos")

st.dataframe(
    df_f.sort_values("gap", ascending=False),
    use_container_width=True
)
