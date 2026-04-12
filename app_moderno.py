import streamlit as st

st.set_page_config(
    page_title="Rouanet Analytics",
    page_icon="📊",
    layout="wide"
)

# carregar CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =========================
# HEADER
# =========================
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
    
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="
            width:42px; height:42px; border-radius:999px;
            background:#7C3AED; color:white;
            display:flex; align-items:center; justify-content:center;
            font-weight:700;">
            ⬢
        </div>
        <div>
            <div style="font-size:26px; font-weight:700;">Rouanet Analytics</div>
            <div style="font-size:14px; color:#6B7280;">Painel de Investimento Cultural</div>
        </div>
    </div>

    <div style="font-size:13px; color:#6B7280;">
        Dados: SALIC <span style="color:#10B981;">●</span>
    </div>

</div>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.markdown("""
<div class="section-title">Painel do Investidor</div>
<div class="section-subtitle">
Visualize oportunidades, acompanhe captação e identifique onde investir.
</div>
""", unsafe_allow_html=True)
