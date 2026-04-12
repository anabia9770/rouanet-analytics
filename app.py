import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------
# CSS GLOBAL
# -------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    margin: auto;
}

.rank-card {
    background:white;
    padding:10px 14px;
    border-radius:12px;
    margin-bottom:8px;
    border:1px solid #f1f5f9;
}

.rank-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
}

.rank-left {
    display:flex;
    align-items:center;
    gap:10px;
}

.rank-badge {
    background:#EDE9FE;
    color:#6D28D9;
    font-weight:600;
    border-radius:999px;
    padding:4px 8px;
    font-size:11px;
}

.rank-city {
    font-weight:600;
    font-size:14px;
}

.rank-sub {
    font-size:12px;
    color:#6b7280;
}

.rank-gap {
    color:#F59E0B;
    font-weight:600;
    font-size:13px;
}

.rank-total {
    font-weight:600;
    font-size:13px;
}

.rank-bar {
    height:5px;
    background:#E5E7EB;
    border-radius:999px;
    margin-top:5px;
    overflow:hidden;
}

.rank-fill {
    height:100%;
    background:#7C3AED;
}
</style>
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
c2.metric("Aprovado", f"R$ {df_f['valor_aprovado'].sum():,.0f}")
c3.metric("Captado", f"R$ {df_f['valor_captado'].sum():,.0f}")
c4.metric("Gap", f"R$ {df_f['gap'].sum():,.0f}")

# -------------------------
# GRÁFICOS
# -------------------------
col1, col2 = st.columns(2)

with col1:

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

    fig_top.update_traces(marker_color="#7C3AED", textposition="outside")

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="🏆 Top Segmentos"
    )

    st.plotly_chart(fig_top, use_container_width=True)

with col2:

    taxa = (
        df_f.groupby("segmento")[["valor_aprovado", "valor_captado"]]
        .sum()
        .reset_index()
    )

    taxa["taxa_captacao"] = taxa["valor_captado"] / taxa["valor_aprovado"]
    taxa = taxa.sort_values("taxa_captacao", ascending=False).head(6)

    fig_taxa = px.bar(
        taxa,
        x="taxa_captacao",
        y="segmento",
        orientation="h",
        text=taxa["taxa_captacao"].apply(lambda x: f"{x:.0%}")
    )

    fig_taxa.update_traces(marker_color="#7C3AED", textposition="outside")

    fig_taxa.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="📊 Eficiência de Captação"
    )

    st.plotly_chart(fig_taxa, use_container_width=True)

    # -------------------------
    # RANKING BONITO (COMPACTO)
    # -------------------------
    ranking = (
        df_f.groupby("cidade")[["valor_aprovado", "valor_captado"]]
        .sum()
        .assign(gap=lambda x: x["valor_aprovado"] - x["valor_captado"])
        .sort_values("gap", ascending=False)
        .head(6)
        .reset_index()
    )

    st.markdown("### 📍 Onde Investir")

    for i, row in ranking.iterrows():

        progresso = row["valor_captado"] / row["valor_aprovado"] if row["valor_aprovado"] > 0 else 0

        st.markdown(f"""
        <div class="rank-card">
            <div class="rank-row">

                <div class="rank-left">
                    <div class="rank-badge">{i+1}</div>

                    <div>
                        <div class="rank-city">{row['cidade']}</div>
                        <div class="rank-sub">
                            {int(row['valor_aprovado']/1e6)}M total
                        </div>
                    </div>
                </div>

                <div style="text-align:right;">
                    <div class="rank-gap">
                        R$ {row['gap']/1e6:.1f}M
                    </div>
                </div>

            </div>

            <div class="rank-bar">
                <div class="rank-fill" style="width:{progresso*100}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# TABELA
# -------------------------
st.markdown("## 📋 Projetos")
st.dataframe(df_f.sort_values("gap", ascending=False), use_container_width=True)
