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

    fig_top.update_traces(marker_color="#16A34A", textposition="outside")

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Top 6 Segmentos que Mais Arrecadam"
    )

    st.plotly_chart(fig_top, use_container_width=True)

# -------------------------
# DONUT: TAMANHO DOS PROJETOS
# -------------------------

# Criar faixas
def faixa_valor(v):
    if v <= 100000:
        return "Pequenos"
    elif v <= 500000:
        return "Médios"
    else:
        return "Grandes"

df_f["faixa_projeto"] = df_f["valor_aprovado"].apply(faixa_valor)

dist = df_f["faixa_projeto"].value_counts().reset_index()
dist.columns = ["categoria", "quantidade"]

fig_donut = px.pie(
    dist,
    names="categoria",
    values="quantidade",
    hole=0.6
)

fig_donut.update_traces(
    textinfo="percent+label",
    marker=dict(colors=["#10B981", "#3B82F6", "#F59E0B"])
)

fig_donut.update_layout(
    title="Distribuição por Tamanho de Projetos",
    showlegend=False
)

st.plotly_chart(fig_donut, use_container_width=True)

# DIREITA
with col2:

    # Eficiência
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

    # 🔥 ONDE INVESTIR (NOVO)
    st.markdown("### 📍 Onde Investir")
    st.caption("Municípios com maior gap de captação")

    ranking = (
        df_f.groupby("cidade")[["valor_aprovado", "valor_captado"]]
        .sum()
        .assign(gap=lambda x: x["valor_aprovado"] - x["valor_captado"])
        .sort_values("gap", ascending=False)
        .head(6)
        .reset_index()
    )

    max_val = ranking["valor_aprovado"].max()

    for i, row in ranking.iterrows():
        progresso = row["valor_captado"] / row["valor_aprovado"] if row["valor_aprovado"] > 0 else 0

        st.markdown(f"""
        <div class="card">
            <div class="rank">
                <div class="badge-rank">{i+1}</div>
                <div>
                    <b>{row['cidade']}</b><br>
                    <span style="color:#6b7280;">{int(row['valor_aprovado']/1e6)}M total</span>
                </div>
            </div>
            <div style="margin-top:8px;">
                <span style="color:#f59e0b;">Gap: R$ {row['gap']/1e6:.1f}M</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:{progresso*100}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TABELA
st.markdown("## 📋 Projetos")
st.dataframe(df_f.sort_values("gap", ascending=False), use_container_width=True)
