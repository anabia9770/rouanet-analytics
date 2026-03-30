import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

body {
    background-color: #f7f8fc;
}

.main {
    background-color: #f7f8fc;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.kpi-title {
    font-size: 13px;
    color: #6b7280;
}

.kpi-value {
    font-size: 26px;
    font-weight: 600;
    color: #111827;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

.stMultiSelect div {
    border-radius: 999px !important;
}

h1 {
    font-weight: 600;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# TÍTULO
# -------------------------
st.title("📊 Rouanet Analytics")
st.caption("Dashboard de análise de projetos culturais")

# -------------------------
# DADOS
# -------------------------
df = pd.read_excel("TCC.xlsx")
df.columns = df.columns.str.lower().str.replace(" ", "_")

df["valor_aprovado"] = pd.to_numeric(df.get("valor_aprovado", 0), errors="coerce").fillna(0)
df["valor_captado"] = pd.to_numeric(df.get("valor_captado", 0), errors="coerce").fillna(0)
df["gap"] = df["valor_aprovado"] - df["valor_captado"]

# -------------------------
# FILTROS
# -------------------------
st.sidebar.title("Filtros")

mun = st.sidebar.multiselect("Município", df["municipio"].dropna().unique())
seg = st.sidebar.multiselect("Segmento", df["segmento"].dropna().unique())

df_f = df.copy()

if mun:
    df_f = df_f[df_f["municipio"].isin(mun)]
if seg:
    df_f = df_f[df_f["segmento"].isin(seg)]

# -------------------------
# KPIs
# -------------------------
c1, c2, c3, c4 = st.columns(4)

def card(title, value):
    return f"""
    <div class="card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

c1.markdown(card("Projetos", len(df_f)), unsafe_allow_html=True)
c2.markdown(card("Aprovado", f"R$ {df_f['valor_aprovado'].sum():,.0f}"), unsafe_allow_html=True)
c3.markdown(card("Captado", f"R$ {df_f['valor_captado'].sum():,.0f}"), unsafe_allow_html=True)
c4.markdown(card("Gap", f"R$ {df_f['gap'].sum():,.0f}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# 📈 ANÁLISES (GRÁFICOS)
# -------------------------
st.markdown("## 📈 Análises")

col1, col2 = st.columns(2)

# Evolução por ano
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

        fig_linha.update_traces(line=dict(width=3), marker=dict(size=6))

        fig_linha.update_layout(
            title="Evolução por Ano",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis_title="",
            yaxis_title=""
        )

        fig_linha.update_traces(selector=dict(name="valor_aprovado"), line=dict(color="#6D28D9"))
        fig_linha.update_traces(selector=dict(name="valor_captado"), line=dict(color="#10B981"))

        st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.info("Adicione uma coluna de data para ver evolução temporal")

# Top segmentos
with col2:
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
        orientation="h",
        text="valor_aprovado"
    )

    fig_bar.update_traces(
        marker_color="#6D28D9",
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    fig_bar.update_layout(
        title="Valor por Segmento Cultural",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="",
        yaxis_title=""
    )

    fig_bar.update_yaxes(categoryorder="total ascending")

    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------
# 🌎 ANÁLISE TERRITORIAL
# -------------------------
st.markdown("## 🌎 Análise Territorial")

top_municipios = (
    df_f.groupby("municipio")["gap"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_territorio = px.bar(
    top_municipios,
    x="gap",
    y="municipio",
    orientation="h",
    color_discrete_sequence=["#F59E0B"]
)

fig_territorio.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title="",
    yaxis_title=""
)

st.plotly_chart(fig_territorio, use_container_width=True)

# -------------------------
# 💡 ONDE INVESTIR
# -------------------------
st.markdown("## 💡 Onde Investir")

top_oportunidades = df_f.sort_values("gap", ascending=False).head(5)

st.markdown("""
<div class="card">
<b>Top oportunidades com maior potencial de captação:</b>
<ul>
""" + "".join([f"<li>{row['nome']} - R$ {row['gap']:,.0f}</li>" for _, row in top_oportunidades.iterrows()]) + """
</ul>
</div>
""", unsafe_allow_html=True)

# -------------------------
# 📋 TABELA (FINAL DA PÁGINA)
# -------------------------
st.markdown("## 📋 Projetos")

st.dataframe(
    df_f.sort_values("gap", ascending=False),
    use_container_width=True
)
