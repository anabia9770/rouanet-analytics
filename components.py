import streamlit as st

def card(titulo, valor):
    st.markdown(f"""
        <div class="card">
            <h4 style="color:#6B7280; font-size:14px;">{titulo}</h4>
            <h2 style="color:#111827;">{valor}</h2>
        </div>
    """, unsafe_allow_html=True)
