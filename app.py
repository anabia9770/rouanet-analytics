import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
<style>
body { background-color: #f7f8fc; }
.block-container { padding-top: 2rem; }

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
}

.kpi-title { font-size:13px; color:#6b7280; }
.kpi-value { font-size:26px; font-weight:600; color:#111827; }

[data-testid="stDataFrame"] {
    border-radius:12px;
    overflow:hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <div>
        <h2>📊 Rouanet Analytics</h2>
        <span style="color:#6b7280;">Vale do Itajaí — Projetos Culturais</span>
    </div>
    <div class="badge">Dados: SALIC 🟢</div>
</div>
""", unsafe_allow_html=True)

df = pd.read_excel("TCC.xlsx")
df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

df["valor_aprovado"] = pd.to_numeric(df.get("valor_solicitado", 0), errors="coerce").fillna(0)
df["valor_captado"] = pd.to_numeric(df.get("valor_captado", 0), errors="coerce").fillna(0)
df["gap"] = df["valor_aprovado"] - df["valor_captado"]

st.markdown("### 🔎 Filtros Interativos")

f1, f2 = st.columns(2)
mun = f1.multiselect("Município", df["cidade"].dropna().unique())
seg = f2.multiselect("Segmento Cultural", df["segmento"].dropna().unique())

df_f = df.copy()
if mun: df_f = df_f[df_f["cidade"].isin(mun)]
if seg: df_f = df_f[df_f["segmento"].isin(seg)]

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

col1, col2 = st.columns(2)

# ESQUERDA
with col1:

    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year

        evolucao = df_f.groupby("ano")[["valor_aprovado", "valor_captado"]].sum().reset_index()

        fig = px.line(evolucao, x="ano", y=["valor_aprovado", "valor_captado"], markers=True)

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title="Evolução por Ano"
        )

        st.plotly_chart(fig, use_container_width=True)

    # TOP 6
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
        marker_color="#16A34A",
        textposition="outside"
    )

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Top 6 Segmentos que Mais Arrecadam"
    )

    st.plotly_chart(fig_top, use_container_width=True)

# DIREITA
with col2:

    taxa = (
        df_f.groupby("segmento")[["valor_aprovado", "valor_captado"]]
        .sum()
        .reset_index()
    )

    taxa["taxa_captacao"] = taxa["valor_captado"] / taxa["valor_aprovado"]
    taxa = taxa.sort_values("taxa_captacao", ascending=False).head(8)

    fig_taxa = px.bar(
        taxa,
        x="taxa_captacao",
        y="segmento",
        orientation="h",
        text=taxa["taxa_captacao"].apply(lambda x: f"{x:.0%}")
    )

    fig_taxa.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="📈 Eficiência de Captação por Segmento (%)"
    )

    st.plotly_chart(fig_taxa, use_container_width=True)

    # MAPA (AGORA MENOR)
    coords = {
        "Blumenau": (-26.9194, -49.0661),
        "Itajaí": (-26.9071, -48.6617),
        "Balneário Camboriú": (-26.9926, -48.6350),
        "Brusque": (-27.0977, -48.9175),
        "Gaspar": (-26.9336, -48.9587),
        "Indaial": (-26.8976, -49.2310),
        "Timbó": (-26.8237, -49.2697),
        "Pomerode": (-26.7406, -49.1787),
        "Navegantes": (-26.8943, -48.6537)
    }

    mapa_df = (
        df_f.groupby("cidade")["valor_captado"]
        .sum()
        .reset_index()
    )

    mapa_df["lat"] = mapa_df["cidade"].map(lambda x: coords.get(x, (None, None))[0])
    mapa_df["lon"] = mapa_df["cidade"].map(lambda x: coords.get(x, (None, None))[1])
    mapa_df = mapa_df.dropna()

    fig_map = px.scatter_mapbox(
        mapa_df,
        lat="lat",
        lon="lon",
        size="valor_captado",
        color="valor_captado",
        hover_name="cidade",
        zoom=8,
        height=300
    )

    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=40, b=0),
        title="📍 Distribuição de Investimentos - Vale do Itajaí"
    )

    st.plotly_chart(fig_map, use_container_width=True)

# TABELA
st.markdown("## 📋 Projetos")
st.dataframe(df_f.sort_values("gap", ascending=False), use_container_width=True)
