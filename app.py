import streamlit as st
import pandas as pd
import plotly.express as px
from styles import load_css
from components import card

st.set_page_config(layout="wide")
load_css()

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
body { background-color: #f7f8fc; }
.block-container { padding-top: 2rem; max-width:1400px; margin:auto; }

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

.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0 2px 10px rgba(0,0,0,0.04);
    margin-bottom:12px;
}

.kpi-title { font-size:13px; color:#6b7280; }
.kpi-value { font-size:26px; font-weight:600; color:#111827; }

.rank {
    display:flex;
    align-items:center;
    gap:10px;
}

.badge-rank {
    background:#e9d5ff;
    color:#6D28D9;
    font-weight:600;
    border-radius:999px;
    padding:6px 10px;
    font-size:12px;
}

.progress-bar {
    height:6px;
    background:#e5e7eb;
    border-radius:999px;
    overflow:hidden;
    margin-top:6px;
}

.progress-fill {
    height:100%;
    background:#6D28D9;
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
# FILTROS
# -------------------------
st.markdown("### 🔎 Filtros")

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

c1.metric("Projetos", len(df_f))
c2.metric("Valor Aprovado", f"R$ {df_f['valor_aprovado'].sum():,.0f}")
c3.metric("Valor Captado", f"R$ {df_f['valor_captado'].sum():,.0f}")
c4.metric("Gap", f"R$ {df_f['gap'].sum():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# GRÁFICOS
# -------------------------
col1, col2 = st.columns(2)

with col1:

    # Evolução
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
            title="📈 Evolução por Ano"
        )

        st.plotly_chart(fig, use_container_width=True)

    # Top 6 Segmentos
    top_captado = (
        df_f.groupby("segmento")["valor_captado"]
        .sum()
        .sort_values(ascending=False)
        .head(6)
        .reset_index()
    )

    mapa_nomes = {
        "Formação Educacional": "Educacional",
        "Desfiles festivos de caráter musical e cênico": "Musical",
        "Apresentação Música Instrumental": "Musical Instrumental",
        "Apresentação Teatro": "Teatro",
        "LITERATURA": "Literatura",
        "Apresentação Música Regional": "Música Regional"
    }

    top_captado["segmento_curto"] = top_captado["segmento"].map(mapa_nomes)

    fig_top = px.bar(
        top_captado,
        x="segmento_curto",
        y="valor_captado",
        text="valor_captado"
    )

    fig_top.update_traces(
        marker=dict(color="#7C3AED"),
        textposition="outside"
    )

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="🏆 Top 6 Segmentos que Mais Arrecadam"
    )

    st.plotly_chart(fig_top, use_container_width=True)

with col2:

    # Eficiência de Captação (%)
    taxa = (
        df_f.groupby("segmento")[["valor_aprovado", "valor_captado"]]
        .sum()
        .reset_index()
    )

    taxa["taxa_captacao"] = taxa["valor_captado"] / taxa["valor_aprovado"].replace(0, 1)
    taxa = taxa.sort_values("taxa_captacao", ascending=False).head(8)

    fig_taxa = px.bar(
        taxa,
        x="taxa_captacao",
        y="segmento",
        orientation="h",
        text=taxa["taxa_captacao"].apply(lambda x: f"{x:.0%}")
    )

    fig_taxa.update_traces(marker_color="#7C3AED")

    fig_taxa.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="📊 Eficiência de Captação (%)"
    )

    st.plotly_chart(fig_taxa, use_container_width=True)

    # ====================== NOVO RANKING: ONDE INVESTIR ======================
    st.markdown("### 📍 Onde Investir")
    st.markdown('<span style="color:#6b7280; font-size:14px;">Municípios com maior gap de captação</span>', unsafe_allow_html=True)

    # Cálculo do ranking por município (maior Gap)
    ranking_gap = (
        df_f.groupby("cidade")
        .agg(
            projetos=("cidade", "count"),
            valor_aprovado=("valor_aprovado", "sum"),
            valor_captado=("valor_captado", "sum"),
            gap=("gap", "sum")
        )
        .reset_index()
    )
    ranking_gap = ranking_gap.sort_values("gap", ascending=False).head(6).reset_index(drop=True)

    for i, row in ranking_gap.iterrows():
        percent = row["valor_captado"] / row["valor_aprovado"] if row["valor_aprovado"] > 0 else 0
        gap_m = row["gap"] / 1_000_000
        aprovado_m = row["valor_aprovado"] / 1_000_000

        st.markdown(f"""
        <div class="card" style="padding:16px 20px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="background:#f3e8ff; color:#6D28D9; width:28px; height:28px; border-radius:50%; 
                                display:flex; align-items:center; justify-content:center; font-weight:700; font-size:15px;">
                        {i+1}
                    </div>
                    <div>
                        <span style="font-weight:600; color:#111827;">{row["cidade"]}</span><br>
                        <span style="font-size:13px; color:#6b7280;">{row["projetos"]} projetos</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="color:#ea580c; font-weight:600;">Gap: R$ {gap_m:.1f}M</span><br>
                    <span style="font-size:15px; font-weight:700; color:#111827;">R$ {aprovado_m:.1f}M</span>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:{percent*100}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    # =========================================================================

# -------------------------
# TABELA
# -------------------------
st.markdown("## 📋 Projetos")
st.dataframe(df_f.sort_values("gap", ascending=False), use_container_width=True)
