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
    # Evolução por Ano
    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year
        evolucao = df_f.groupby("ano")[["valor_aprovado", "valor_captado"]].sum().reset_index()
        fig = px.line(evolucao, x="ano", y=["valor_aprovado", "valor_captado"], markers=True)
        fig.update_traces(line=dict(width=3))
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", title="📈 Evolução por Ano")
        st.plotly_chart(fig, use_container_width=True)

    # ==================== TOP 6 - MAIS ARRECADAM (Arredondado + Cores Vibrantes) ====================
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
    top_captado["segmento_curto"] = top_captado["segmento"].map(mapa_nomes).fillna(top_captado["segmento"])

    colors_top = ["#6366F1", "#8B5CF6", "#EC4899", "#F43F5E", "#14B8A6", "#F59E0B"]

    fig_top = px.bar(
        top_captado,
        x="segmento_curto",
        y="valor_captado",
        text="valor_captado",
        color="segmento_curto",
        color_discrete_sequence=colors_top
    )

    fig_top.update_traces(
        marker_line_color="white",
        marker_line_width=2,
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="🏆 Top 6 Segmentos que Mais Arrecadam",
        xaxis_title="",
        yaxis_title="Valor Captado",
        showlegend=False,
        bargap=0.15,
        bargroupgap=0.1
    )

    # Arredondar as colunas
    fig_top.update_traces(marker_corner_radius=8)

    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    # ==================== EFICIÊNCIA DE CAPTAÇÃO (%) - Arredondado + Roxo Moderno ====================
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
        text=taxa["taxa_captacao"].apply(lambda x: f"{x:.0%}"),
        color_discrete_sequence=["#7C3AED"]  # Roxo principal bonito
    )

    fig_taxa.update_traces(
        marker_line_color="white",
        marker_line_width=1.5,
        textposition="outside"
    )

    fig_taxa.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="📊 Eficiência de Captação (%)",
        xaxis_title="Taxa de Captação",
        yaxis_title="",
        xaxis_tickformat=".0%",
        showlegend=False,
        bargap=0.25
    )

    # Arredondar as barras horizontais
    fig_taxa.update_traces(marker_corner_radius=8)

    st.plotly_chart(fig_taxa, use_container_width=True)

# ========================= NOVA TABELA BONITA =========================
st.markdown("---")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown(f"### Projetos ({len(df_f)})")
with col_b:
    st.markdown('<div style="text-align:right;">', unsafe_allow_html=True)
    sort_option = st.radio(
        "Ordenar por:",
        ["Maior Gap", "Maior Valor", "Mais Captado"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<span style="color:#6b7280;">Oportunidades de investimento no Vale do Itajaí</span>', unsafe_allow_html=True)

if sort_option == "Maior Gap":
    df_sorted = df_f.sort_values("gap", ascending=False)
elif sort_option == "Maior Valor":
    df_sorted = df_f.sort_values("valor_aprovado", ascending=False)
else:
    df_sorted = df_f.sort_values("valor_captado", ascending=False)

df_display = df_sorted.copy()
df_display["Aprovado"] = "R$ " + df_display["valor_aprovado"].apply(lambda x: f"{x:,.2f}")
df_display["Captado"] = "R$ " + df_display["valor_captado"].apply(lambda x: f"{x:,.2f}")
df_display["Gap"] = "R$ " + df_display["gap"].apply(lambda x: f"{x:,.2f}")

df_display = df_display.rename(columns={
    "evento": "Projeto",
    "segmento": "Segmento",
    "cidade": "Município"
})

cols_to_show = ["Projeto", "Segmento", "Município", "Aprovado", "Captado", "Gap"]

st.dataframe(
    df_display[cols_to_show],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Projeto": st.column_config.TextColumn("Projeto", width="medium"),
        "Segmento": st.column_config.TextColumn("Segmento"),
        "Município": st.column_config.TextColumn("Município"),
        "Aprovado": st.column_config.TextColumn("Aprovado"),
        "Captado": st.column_config.TextColumn("Captado"),
        "Gap": st.column_config.TextColumn("Gap")
    }
)
