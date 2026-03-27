import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

st.set_page_config(layout="wide")

# -------------------------
# NORMALIZAR COLUNAS
# -------------------------
def normalize_col(col):
    col = col.strip().lower().replace(" ", "_")
    col = unicodedata.normalize("NFKD", col).encode("ascii", "ignore").decode("utf-8")
    return col

# -------------------------
# CSS (CARDS BONITOS)
# -------------------------
st.markdown("""
<style>

.card {
    background: #f9fafb;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

.kpi-title {
    font-size: 14px;
    color: #6b7280;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #111827;
}

.block {
    background: #f9fafb;
    padding: 15px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# TÍTULO
# -------------------------
st.title("📊 Rouanet Analytics")
st.caption("Painel do Investidor")

# -------------------------
# DADOS
# -------------------------
df = pd.read_excel("TCC.xlsx")
df.columns = [normalize_col(c) for c in df.columns]

df["valor_aprovado"] = pd.to_numeric(df.get("valor_solicitado", 0), errors="coerce").fillna(0)
df["valor_captado"] = pd.to_numeric(df.get("valor_captado", 0), errors="coerce").fillna(0)
df["gap"] = df["valor_aprovado"] - df["valor_captado"]

# -------------------------
# FILTROS NO TOPO
# -------------------------
st.markdown("### 🔎 Filtros")

f1, f2 = st.columns(2)

with f1:
    cidade = st.multiselect("Cidade", df["cidade"].dropna().unique())

with f2:
    segmento = st.multiselect("Segmento", df["segmento"].dropna().unique())

df_f = df.copy()

if cidade:
    df_f = df_f[df_f["cidade"].isin(cidade)]

if segmento:
    df_f = df_f[df_f["segmento"].isin(segmento)]

# -------------------------
# KPIs (CARDS)
# -------------------------
st.markdown("### 📊 Visão Geral")

c1, c2, c3, c4 = st.columns(4)

def card(titulo, valor):
    return f"""
    <div class="card">
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor}</div>
    </div>
    """

c1.markdown(card("Projetos", len(df_f)), unsafe_allow_html=True)
c2.markdown(card("Valor Aprovado", f"R$ {df_f['valor_aprovado'].sum()/1e6:.1f}M"), unsafe_allow_html=True)
c3.markdown(card("Valor Captado", f"R$ {df_f['valor_captado'].sum()/1e6:.1f}M"), unsafe_allow_html=True)
c4.markdown(card("Gap de Investimento", f"R$ {df_f['gap'].sum()/1e6:.1f}M"), unsafe_allow_html=True)

# -------------------------
# GRÁFICOS
# -------------------------
st.markdown("### 📈 Análises")

col1, col2 = st.columns(2)

# Evolução
with col1:

    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year

        evolucao = (
            df_f.groupby("ano")[["valor_aprovado", "valor_captado"]]
            .sum()
            .reset_index()
        )

        fig = px.line(evolucao, x="ano", y=["valor_aprovado", "valor_captado"], markers=True)
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

    fig = px.bar(top, x="valor_aprovado", y="segmento", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABELA
# -------------------------
st.markdown("### 📋 Projetos")
st.dataframe(df_f, use_container_width=True)

# -------------------------
# NOVOS BLOCOS (MUNICÍPIOS)
# -------------------------
st.markdown("## 📍 Análise Territorial")

col1, col2 = st.columns([2, 1])

# -------------------------
# GRÁFICO: ANÁLISE POR MUNICÍPIO
# -------------------------
with col1:

    top_mun = (
        df_f.groupby("cidade")[["valor_aprovado", "valor_captado"]]
        .sum()
        .sort_values("valor_aprovado", ascending=False)
        .head(10)
        .reset_index()
    )

    fig_mun = px.bar(
        top_mun,
        x="cidade",
        y=["valor_aprovado", "valor_captado"],
        barmode="group",
        title="Análise por Município"
    )

    fig_mun.update_layout(
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig_mun.update_traces(
        selector=dict(name="valor_aprovado"),
        marker_color="#6D28D9"
    )

    fig_mun.update_traces(
        selector=dict(name="valor_captado"),
        marker_color="#10B981"
    )

    st.plotly_chart(fig_mun, use_container_width=True)

# -------------------------
# RANKING: ONDE INVESTIR
# -------------------------
with col2:

    st.markdown("### 📌 Onde Investir")
    st.caption("Municípios com maior gap de captação")

    ranking = (
        df_f.groupby("cidade")[["valor_aprovado", "valor_captado"]]
        .sum()
        .assign(gap=lambda x: x["valor_aprovado"] - x["valor_captado"])
        .sort_values("gap", ascending=False)
        .head(6)
        .reset_index()
    )

    for i, row in ranking.iterrows():

        progresso = row["valor_captado"] / row["valor_aprovado"] if row["valor_aprovado"] > 0 else 0

        st.markdown(f"""
        <div style="background:#f9fafb;padding:12px;border-radius:12px;margin-bottom:10px;">
            <b>{i+1}. {row['cidade']}</b><br>
            Gap: R$ {row['gap']/1e6:.1f}M<br>
            Total: R$ {row['valor_aprovado']/1e6:.1f}M
        </div>
        """, unsafe_allow_html=True)

        st.progress(progresso)
