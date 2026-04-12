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
