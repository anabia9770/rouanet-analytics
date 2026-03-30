import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")

# -------------------------
# CSS MODERNO
# -------------------------
st.markdown("""
<style>

body {
    background-color: #f7f8fc;
}

.block-container {
    padding-top: 2rem;
}

/* Header */
.header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:20px;
}

.badge {
    background:#e5e7eb;
    padding:6px 12px;
    border-radius:999px;
    font-size:12px;
}

/* Cards */
.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0 2px 10px rgba(0,0,0,0.04);
}

/* KPI */
.kpi-title {
    font-size:13px;
    color:#6b7280;
}

.kpi-value {
    font-size:26px;
    font-weight:600;
    color:#111827;
}

/* Filtros */
.filter-box {
    background:white;
    padding:20px;
    border-radius:16px;
    margin-bottom:20px;
}

/* Tabela */
[data-testid="stDataFrame"] {
    border-radius:12px;
    overflow:hidden;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div class="header">
    <div>
        <h2>📊 Rouanet Analytics</h2>
        <span style="color:#6b7280;">Vale do Itajaí — Projetos Culturais</span>
    </div>
    <div class="badge">Dados: SALIC 🟢</div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# DADOS
# -------------------------
df = pd.read_excel("TCC.xlsx")

df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

df["valor_aprovado"] = pd.to_numeric(df.get("valor_solicitado", 0), errors="coerce").fillna(0)
df["valor_captado"] = pd.to_numeric(df.get("valor_captado", 0), errors="coerce").fillna(0)
df["gap"] = df["valor_aprovado"] - df["valor_captado"]

# -------------------------
# FILTROS NO TOPO
# -------------------------
st.markdown("### 🔎 Filtros Interativos")

with st.container():
    f1, f2 = st.columns(2)

    mun = f1.multiselect("Município", df["cidade"].dropna().unique())
    seg = f2.multiselect("Segmento Cultural", df["segmento"].dropna().unique())

df_f = df.copy()

if mun:
    df_f = df_f[df_f["cidade"].isin(mun)]
if seg:
    df_f = df_f[df_f["segmento"].isin(seg)]

# -------------------------
# KPIs
# -------------------------
c1, c2, c3, c4 = st.columns(4)

def card(title, value, icon):
    return f"""
    <div class="card">
        <div style="display:flex; justify-content:space-between;">
            <div class="kpi-title">{title}</div>
            <div>{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
    </div>
    """

c1.markdown(card("Projetos", len(df_f), "📁"), unsafe_allow_html=True)
c2.markdown(card("Valor Aprovado", f"R$ {df_f['valor_aprovado'].sum():,.0f}", "💰"), unsafe_allow_html=True)
c3.markdown(card("Valor Captado", f"R$ {df_f['valor_captado'].sum():,.0f}", "📊"), unsafe_allow_html=True)
c4.markdown(card("Gap de Investimento", f"R$ {df_f['gap'].sum():,.0f}", "🎯"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# GRÁFICOS
# -------------------------
col1, col2 = st.columns(2)

# Evolução
with col1:
    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year

        evolucao = df_f.groupby("ano")[["valor_aprovado", "valor_captado"]].sum().reset_index()

        fig = px.line(
            evolucao,
            x="ano",
            y=["valor_aprovado", "valor_captado"],
            markers=True
        )

        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title="Evolução por Ano"
        )

        st.plotly_chart(fig, use_container_width=True)

# Segmentos
with col2:
    top = (
        df_f.groupby("segmento")["valor_aprovado"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .reset_index()
    )

    fig2 = px.bar(
        top,
        x="valor_aprovado",
        y="segmento",
        orientation="h",
        text="valor_aprovado"
    )

    fig2.update_traces(marker_color="#6D28D9")
    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Valor por Segmento Cultural"
    )

    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# TABELA FINAL
# -------------------------
st.markdown("## 📋 Projetos")

st.dataframe(
    df_f.sort_values("gap", ascending=False),
    use_container_width=True
)
