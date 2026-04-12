import streamlit as st

def load_css():
    css = """
    <style>

    .main {
        background-color: #F5F6F8;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def table_styles():
    import streamlit as st

    st.markdown("""
    <style>

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
        width: fit-content;
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

    .progress-bar {
        height: 6px;
        background: #E5E7EB;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 6px;
    }

    .progress-fill {
        height: 100%;
        background: #7C3AED;
    }

    </style>
    """, unsafe_allow_html=True)
