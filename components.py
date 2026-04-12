import streamlit as st

def card(title, value, icon):
    st.markdown(f"""
    <div style="
        background:white;
        padding:20px;
        border-radius:16px;
        box-shadow:0 4px 20px rgba(0,0,0,0.05);
        display:flex;
        justify-content:space-between;
        align-items:center;
        height:110px;
    ">
        <div>
            <div style="font-size:14px; color:#6b7280;">
                {title}
            </div>
            <div style="font-size:28px; font-weight:700; color:#111827;">
                {value}
            </div>
        </div>

        <div style="
            background:#ede9fe;
            color:#6D28D9;
            padding:10px;
            border-radius:12px;
            font-size:18px;
        ">
            {icon}
        </div>
    </div>
    """, unsafe_allow_html=True)
