import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------
# CSS GLOBAL
# -------------------------
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

/* NOVA TABELA */
.table-container {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.table-header {
    display: grid;
    grid-template-columns: 2.5fr 1.2fr 1.2fr 1fr 1fr 1fr 1fr;
    font-size: 13px;
    color: #6B7280;
    padding-bottom: 10px;
    border-bottom: 1px solid #E5E7EB;
}

.table-row {
    display: grid;
    grid-template-columns: 2.5fr 1.2fr 1.2fr 1fr 1fr 1fr 1fr;
    padding: 14px 0;
    border-bottom: 1px solid #F1F5F9;
    align-items: center;
}

.title {
    font-weight: 600;
    color: #111827;
}

.subtitle {
    font-size: 13px;
    color: #6B7280;
}

.status {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

.status-aberto {
    background: #EDE9FE;
    color: #7C3AED;
}

.status-residual {
    background: #DDD6FE;
    color: #6D28D9;
}

.status-arquivado {
    background: #FEE2E2;
    color: #DC2626;
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
st.markdown("### 🔎 Filtros Interativos")

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

# -------------------------
# FUNÇÃO TABELA NOVA
# -------------------------
def render_table(df):
    html = '<div class="table-container">'

    html += """
    <div class="table-header">
        <div>Projeto</div>
        <div>Segmento</div>
        <div>Município</div>
        <div>Aprovado</div>
        <div>Captado</div>
        <div>Gap</div>
        <div>Status</div>
    </div>
    """

    for _, row in df.iterrows():

        status_text = str(row["situacao_do_projeto"])

        status_class = "status-aberto"
        if "residual" in status_text.lower():
            status_class = "status-residual"
        if "arquiv" in status_text.lower():
            status_class = "status-arquivado"

        progresso = 0
        if row["valor_aprovado"] > 0:
            progresso = row["valor_captado"] / row["valor_aprovado"]

        html += f"""
        <div class="table-row">
            <div>
                <div class="title">{row['evento']}</div>
                <div class="subtitle">{row['tipo_do_projeto']}</div>
            </div>
            <div>{row['segmento']}</div>
            <div>{row['cidade']}</div>
            <div>R$ {row['valor_aprovado']:,.0f}</div>
            <div>
                R$ {row['valor_captado']:,.0f}
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{progresso*100}%"></div>
                </div>
            </div>
            <div style="color:#F59E0B; font-weight:600;">
                R$ {row['gap']:,.0f}
            </div>
            <div>
                <span class="status {status_class}">
                    {status_text}
                </span>
            </div>
        </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# -------------------------
# MOSTRAR TABELA
# -------------------------
st.markdown("## 📋 Projetos")
render_table(df_f.head(30))
