# -------------------------
# GRÁFICOS
# -------------------------
col1, col2 = st.columns(2)

# COLUNA ESQUERDA
with col1:
    # Evolução
    if "data_inicio" in df_f.columns:
        df_f["ano"] = pd.to_datetime(df_f["data_inicio"], errors="coerce").dt.year

        evolucao = df_f.groupby("ano")[["valor_aprovado", "valor_captado"]].sum().reset_index()

        fig = px.line(
            evolucao,
            x="ano",
            y=["valor_aprovado", "valor_captado"],
            markers=True
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title="Evolução por Ano"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # TOP 6 (MANTIDO)
    # -------------------------
    top_captado = (
        df_f.groupby("segmento")["valor_captado"]
        .sum()
        .sort_values(ascending=False)
        .head(6)
        .reset_index()
    )

    fig_top = px.bar(
        top_captado,
        x="segmento",
        y="valor_captado",
        text="valor_captado"
    )

    fig_top.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Top 6 Segmentos que Mais Arrecadam"
    )

    st.plotly_chart(fig_top, use_container_width=True)


# COLUNA DIREITA
with col2:

    # -------------------------
    # EFICIÊNCIA
    # -------------------------
    taxa = (
        df_f.groupby("segmento")[["valor_aprovado", "valor_captado"]]
        .sum()
        .reset_index()
    )

    taxa["taxa_captacao"] = taxa["valor_captado"] / taxa["valor_aprovado"]

    taxa = taxa.sort_values("taxa_captacao", ascending=False).head(8)

    fig_taxa = px.bar(
        taxa,
        x="taxa_captacao",
        y="segmento",
        orientation="h",
        text=taxa["taxa_captacao"].apply(lambda x: f"{x:.0%}")
    )

    fig_taxa.update_traces(marker_color="#10B981")

    fig_taxa.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="📈 Eficiência de Captação por Segmento (%)"
    )

    st.plotly_chart(fig_taxa, use_container_width=True)

    # -------------------------
    # MAPA (AGORA SEM REMOVER NADA)
    # -------------------------

    coords = {
        "Blumenau": (-26.9194, -49.0661),
        "Itajaí": (-26.9071, -48.6617),
        "Balneário Camboriú": (-26.9926, -48.6350),
        "Brusque": (-27.0977, -48.9175),
        "Gaspar": (-26.9336, -48.9587),
        "Indaial": (-26.8976, -49.2310),
        "Timbó": (-26.8237, -49.2697),
        "Pomerode": (-26.7406, -49.1787),
        "Navegantes": (-26.8943, -48.6537)
    }

    mapa_df = (
        df_f.groupby("cidade")["valor_captado"]
        .sum()
        .reset_index()
    )

    mapa_df["lat"] = mapa_df["cidade"].map(lambda x: coords.get(x, (None, None))[0])
    mapa_df["lon"] = mapa_df["cidade"].map(lambda x: coords.get(x, (None, None))[1])

    mapa_df = mapa_df.dropna()

    fig_map = px.scatter_mapbox(
        mapa_df,
        lat="lat",
        lon="lon",
        size="valor_captado",
        color="valor_captado",
        hover_name="cidade",
        zoom=8,
        height=350,
        color_continuous_scale="Viridis"
    )

    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=40, b=0),
        title="📍 Distribuição de Investimentos - Vale do Itajaí"
    )

    st.plotly_chart(fig_map, use_container_width=True)
