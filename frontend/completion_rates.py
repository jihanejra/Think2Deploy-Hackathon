"""
Visualisations des taux de complétion
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def display_completion_analysis(df):
    """Affiche l'analyse des taux de complétion"""

    st.markdown("### 📝 Taux de Complétion des Évaluations")

    # Créer un onglet pour différents types d'analyse
    tab1, tab2, tab3 = st.tabs([
        "📊 Vue d'Ensemble",
        "🔍 Par Type de Formation",
        "📅 Évolution Temporelle"
    ])

    with tab1:
        display_completion_overview(df)

    with tab2:
        display_completion_by_type(df)

    with tab3:
        display_completion_trends(df)


def display_completion_overview(df):
    """Vue d'ensemble des taux de complétion"""

    if 'Évaluation_Complète' not in df.columns:
        st.info("Les données de complétion ne sont pas disponibles")
        return

    total = len(df)
    completed = df['Évaluation_Complète'].sum()
    completion_rate = (completed / total) * 100

    col1, col2 = st.columns([2, 1])

    with col1:
        # Diagramme en anneau
        labels = ['Complètes', 'Incomplètes']
        values = [completed, total - completed]
        colors = ['#2ca02c', '#d62728']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.5,
            marker_colors=colors,
            textinfo='percent+label',
            hoverinfo='value+percent'
        )])

        fig.update_layout(
            title=f"Taux de Complétion: {completion_rate:.1f}%",
            showlegend=True,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Statistiques détaillées
        st.metric("Évaluations Complètes", f"{completed:,}")
        st.metric("Évaluations Incomplètes", f"{total - completed:,}")
        st.metric("Taux Global", f"{completion_rate:.1f}%")

        # Analyse par critère manquant
        criteria = ['Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
        missing_data = {}

        for criterion in criteria:
            if criterion in df.columns:
                missing_count = df[criterion].isna().sum()
                missing_data[criterion] = missing_count

        if missing_data:
            st.markdown("**Critères manquants:**")
            for criterion, count in missing_data.items():
                percentage = (count / total) * 100
                st.write(f"- {criterion}: {count} ({percentage:.1f}%)")

    # Heatmap de complétion
    if len(df) > 0:
        st.markdown("#### 🗺️ Carte Thermique de Complétion")

        # Préparer les données pour la heatmap
        if 'Type de Formation' in df.columns and 'ID Formateur' in df.columns:
            # Échantillonner si trop de données
            sample_size = min(20, df['ID Formateur'].nunique())
            top_formateurs = df['ID Formateur'].value_counts().head(sample_size).index.tolist()
            df_filtered = df[df['ID Formateur'].isin(top_formateurs)]

            pivot_data = df_filtered.groupby(['Type de Formation', 'ID Formateur'])[
                'Évaluation_Complète'].mean().unstack()

            fig = px.imshow(
                pivot_data,
                color_continuous_scale='RdYlGn',
                title="Taux de Complétion par Type de Formation et Formateur",
                labels=dict(color="Taux de Complétion")
            )

            st.plotly_chart(fig, use_container_width=True)


def display_completion_by_type(df):
    """Analyse par type de formation"""

    if 'Type de Formation' not in df.columns or 'Évaluation_Complète' not in df.columns:
        st.info("Données insuffisantes pour l'analyse par type")
        return

    # Calculer les taux par type
    completion_by_type = df.groupby('Type de Formation').agg({
        'Évaluation_Complète': ['count', 'sum', 'mean']
    }).round(3)

    completion_by_type.columns = ['Total', 'Complètes', 'Taux']
    completion_by_type['Taux'] = completion_by_type['Taux'] * 100
    completion_by_type = completion_by_type.sort_values('Taux', ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Bar chart horizontal
        fig = px.bar(
            completion_by_type.reset_index(),
            x='Taux',
            y='Type de Formation',
            orientation='h',
            color='Taux',
            color_continuous_scale='RdYlGn',
            text='Taux',
            title="Taux de Complétion par Type de Formation"
        )

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Tableau détaillé
        st.dataframe(
            completion_by_type.style.format({
                'Total': '{:,.0f}',
                'Complètes': '{:,.0f}',
                'Taux': '{:.1f}%'
            }).background_gradient(
                subset=['Taux'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ),
            use_container_width=True
        )

    # Analyse des corrélations
    if 'Note_Moyenne' in df.columns:
        st.markdown("#### 🔗 Relation entre Complétion et Satisfaction")

        fig = px.scatter(
            df,
            x='Évaluation_Complète',
            y='Note_Moyenne',
            color='Type de Formation',

            title="Corrélation entre Complétion et Note Moyenne",
            labels={
                'Évaluation_Complète': 'Évaluation Complète',
                'Note_Moyenne': 'Note Moyenne'
            }
        )

        st.plotly_chart(fig, use_container_width=True)


def display_completion_trends(df):
    """Évolution temporelle des taux de complétion"""

    if 'Date' not in df.columns or 'Évaluation_Complète' not in df.columns:
        st.info("Données temporelles insuffisantes")
        return

    # Préparer les données temporelles
    df_temp = df.copy()
    df_temp = df_temp.dropna(subset=['Date'])

    # Choix de la granularité
    granularity = st.radio(
        "Granularité temporelle:",
        ["Mensuelle", "Hebdomadaire", "Quotidienne"],
        horizontal=True
    )

    if granularity == "Mensuelle":
        df_temp['Période'] = df_temp['Date'].dt.to_period('M').astype(str)
    elif granularity == "Hebdomadaire":
        df_temp['Période'] = df_temp['Date'].dt.to_period('W').astype(str)
    else:
        df_temp['Période'] = df_temp['Date'].dt.date.astype(str)

    # Calculer les taux par période
    trend_data = df_temp.groupby('Période').agg({
        'Évaluation_Complète': ['count', 'sum']
    }).round(2)

    trend_data.columns = ['Total', 'Complètes']
    trend_data['Taux'] = (trend_data['Complètes'] / trend_data['Total']) * 100
    trend_data = trend_data.reset_index()

    # Graphique de tendance
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_data['Période'],
        y=trend_data['Taux'],
        mode='lines+markers',
        name='Taux de Complétion',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))

    # Ajouter une moyenne mobile
    if len(trend_data) > 7:
        trend_data['Moyenne_Mobile'] = trend_data['Taux'].rolling(window=3, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=trend_data['Période'],
            y=trend_data['Moyenne_Mobile'],
            mode='lines',
            name='Moyenne Mobile (3 périodes)',
            line=dict(color='orange', width=2, dash='dash')
        ))

    fig.update_layout(
        title=f"Évolution du Taux de Complétion ({granularity})",
        xaxis_title="Période",
        yaxis_title="Taux de Complétion (%)",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistiques temporelles
    col1, col2, col3 = st.columns(3)

    with col1:
        current_rate = trend_data['Taux'].iloc[-1] if len(trend_data) > 0 else 0
        st.metric("Taux Actuel", f"{current_rate:.1f}%")

    with col2:
        if len(trend_data) > 1:
            best_rate = trend_data['Taux'].max()
            best_period = trend_data.loc[trend_data['Taux'].idxmax(), 'Période']
            st.metric("Meilleur Taux", f"{best_rate:.1f}%", delta=f"Période: {best_period}")

    with col3:
        avg_rate = trend_data['Taux'].mean()
        st.metric("Moyenne Historique", f"{avg_rate:.1f}%")