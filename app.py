import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")

# -------------------------
# CSS (VISUAL MODERNO)
# -------------------------
st.markdown("""
<style>

body {
    background-color: #f7f8fc;
}

.main {
    background-color: #f7f8fc;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

/* KPI */
.kpi-title {
    font-size: 13px;
    color: #6b7280;
}

.kpi-value {
    font-size: 26px;
    font-weight: 600;
    color: #111827;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

/* Botões estilo pill */
.stMultiSelect div {
    border-radius: 999px !important;
}

/* Título */
h1 {
    font-weight: 600;
}

/* Tabela */
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
df = pd.read_excel("TCC_Projeto.xlsx")
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
# KPIs (CARDS)
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
# NOVOS GRÁFICOS
# -------------------------
st.markdown("### 📈 Análises")

col1, col2 = st.columns(2)

# -------- Evolução por Ano --------
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

        fig_linha.update_traces(
            selector=dict(name="valor_aprovado"),
            line=dict(color="#6D28D9")
        )

        fig_linha.update_traces(
            selector=dict(name="valor_captado"),
            line=dict(color="#10B981")
        )

        st.plotly_chart(fig_linha, use_container_width=True)

    else:
        st.warning("Coluna 'data_inicio' não encontrada para gráfico de evolução.")

# -------- Top Segmentos --------
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
# TABELA
# -------------------------
st.markdown("### Projetos")

st.dataframe(
    df_f.sort_values("gap", ascending=False),
    use_container_width=True
)
