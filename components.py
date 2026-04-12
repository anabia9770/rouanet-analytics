def card(title, value, icon):
    st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                <div style="
                    width:40px;
                    height:40px;
                    border-radius:50%;
                    background:#ede9fe;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:18px;
                ">
                    {icon}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
