"""
Analyse temporelle des évaluations
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from plotly.subplots import make_subplots

def display_temporal_analysis(df):
    """Affiche l'analyse temporelle"""

    st.markdown("### 📈 Évolution des Scores dans le Temps")

    if 'Date' not in df.columns:
        st.info("Les données temporelles ne sont pas disponibles")
        return

    # Onglets d'analyse temporelle
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Tendances Temporelles",
        "📊 Analyse Saisonnière",
        "⚡ Performance Récente",
        "📋 Tableaux de Bord"
    ])

    with tab1:
        display_time_trends(df)

    with tab2:
        display_seasonal_analysis(df)

    with tab3:
        display_recent_performance(df)

    with tab4:
        display_temporal_dashboards(df)


def display_time_trends(df):
    """Tendances temporelles des scores"""

    # Choix de la métrique
    metric_options = ['Note_Moyenne', 'Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
    available_metrics = [m for m in metric_options if m in df.columns]

    if not available_metrics:
        st.info("Aucune métrique disponible pour l'analyse temporelle")
        return

    selected_metric = st.selectbox(
        "Sélectionnez la métrique à analyser:",
        available_metrics
    )

    # Choix de la granularité
    granularity = st.radio(
        "Granularité temporelle:",
        ["Quotidienne", "Hebdomadaire", "Mensuelle", "Trimestrielle"],
        horizontal=True
    )

    # Préparer les données
    df_temp = df.copy()
    df_temp = df_temp.dropna(subset=['Date', selected_metric])

    if granularity == "Quotidienne":
        df_temp['Période'] = df_temp['Date'].dt.date
        period_format = '%Y-%m-%d'
    elif granularity == "Hebdomadaire":
        df_temp['Période'] = df_temp['Date'].dt.to_period('W').astype(str)
        period_format = 'Semaine'
    elif granularity == "Mensuelle":
        df_temp['Période'] = df_temp['Date'].dt.to_period('M').astype(str)
        period_format = 'Mois'
    else:  # Trimestrielle
        df_temp['Période'] = df_temp['Date'].dt.to_period('Q').astype(str)
        period_format = 'Trimestre'

    # Agréger par période
    trend_data = df_temp.groupby('Période').agg({
        selected_metric: ['mean', 'count', 'std']
    }).round(3)

    trend_data.columns = ['Moyenne', 'Nombre', 'Écart_Type']
    trend_data = trend_data.reset_index()

    # Graphique principal
    fig = go.Figure()

    # Ligne de tendance
    fig.add_trace(go.Scatter(
        x=trend_data['Période'],
        y=trend_data['Moyenne'],
        mode='lines+markers',
        name='Score Moyen',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        error_y=dict(
            type='data',
            array=trend_data['Écart_Type'],
            visible=True
        )
    ))

    # Moyenne mobile
    if len(trend_data) > 3:
        trend_data['Moyenne_Mobile'] = trend_data['Moyenne'].rolling(window=3, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=trend_data['Période'],
            y=trend_data['Moyenne_Mobile'],
            mode='lines',
            name='Moyenne Mobile (3 périodes)',
            line=dict(color='orange', width=2, dash='dash')
        ))

    fig.update_layout(
        title=f"Évolution de {selected_metric} ({granularity})",
        xaxis_title="Période",
        yaxis_title=f"Score {selected_metric}",
        hovermode='x unified',
        height=500,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistiques temporelles
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        current_val = trend_data['Moyenne'].iloc[-1] if len(trend_data) > 0 else 0
        st.metric("Valeur Actuelle", f"{current_val:.2f}")

    with col2:
        peak_val = trend_data['Moyenne'].max()
        peak_period = trend_data.loc[trend_data['Moyenne'].idxmax(), 'Période']
        st.metric("Pic Historique", f"{peak_val:.2f}", delta=f"{period_format}: {peak_period}")

    with col3:
        avg_val = trend_data['Moyenne'].mean()
        st.metric("Moyenne Historique", f"{avg_val:.2f}")

    with col4:
        if len(trend_data) > 1:
            current_trend = trend_data['Moyenne'].iloc[-1] - trend_data['Moyenne'].iloc[-2]
            trend_icon = "↗️" if current_trend > 0 else "↘️" if current_trend < 0 else "➡️"
            st.metric("Tendance Récente", f"{trend_icon} {abs(current_trend):.2f}")

    # Volume d'évaluations
    st.markdown("#### 📊 Volume d'Évaluations")

    fig_volume = px.bar(
        trend_data,
        x='Période',
        y='Nombre',
        title=f"Nombre d'Évaluations par Période ({granularity})",
        labels={'Nombre': "Nb. d'Évaluations"}
    )

    st.plotly_chart(fig_volume, use_container_width=True)


def display_seasonal_analysis(df):
    """Analyse saisonnière des scores"""

    # Vérifier les colonnes nécessaires
    if 'Date' not in df.columns or 'Note_Moyenne' not in df.columns:
        st.info("Données insuffisantes pour l'analyse saisonnière")
        return

    # Préparer les données
    df_temp = df.copy()
    df_temp = df_temp.dropna(subset=['Date', 'Note_Moyenne'])

    # Extraire les composantes temporelles
    df_temp['Année'] = df_temp['Date'].dt.year
    df_temp['Mois'] = df_temp['Date'].dt.month
    df_temp['Semaine'] = df_temp['Date'].dt.isocalendar().week
    df_temp['Jour_Semaine'] = df_temp['Date'].dt.day_name()

    # Options d'analyse
    analysis_type = st.radio(
        "Type d'analyse saisonnière:",
        ["Par Mois", "Par Jour de la Semaine", "Par Semaine de l'Année"],
        horizontal=True
    )

    if analysis_type == "Par Mois":
        seasonal_data = df_temp.groupby(['Année', 'Mois']).agg({
            'Note_Moyenne': 'mean',
            'Satisfaction': 'mean',
            'ID Formation': 'count'
        }).round(2).reset_index()

        seasonal_data.columns = ['Année', 'Mois', 'Score_Moyen', 'Satisfaction', 'Nb_Évaluations']

        # Heatmap par année/mois
        pivot_data = seasonal_data.pivot(index='Mois', columns='Année', values='Score_Moyen')

        fig = px.imshow(
            pivot_data,
            color_continuous_scale='RdYlGn',
            title="Score Moyen par Mois et Année",
            labels=dict(color="Score Moyen")
        )

        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Par Jour de la Semaine":
        # Ordre des jours
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        df_temp['Jour_Semaine'] = pd.Categorical(
            df_temp['Jour_Semaine'],
            categories=day_order,
            ordered=True
        )

        daily_data = df_temp.groupby('Jour_Semaine').agg({
            'Note_Moyenne': ['mean', 'count', 'std']
        }).round(2)

        daily_data.columns = ['Moyenne', 'Nombre', 'Écart_Type']
        daily_data = daily_data.reset_index()
        daily_data['Jour'] = day_fr

        fig = px.bar(
            daily_data,
            x='Jour',
            y='Moyenne',
            error_y='Écart_Type',
            color='Moyenne',
            color_continuous_scale='RdYlGn',
            title="Performance par Jour de la Semaine",
            labels={'Moyenne': 'Score Moyen', 'Nombre': 'Nb. Évaluations'}
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # Par semaine de l'année
        weekly_data = df_temp.groupby(['Année', 'Semaine']).agg({
            'Note_Moyenne': 'mean',
            'ID Formation': 'count'
        }).round(2).reset_index()

        weekly_data.columns = ['Année', 'Semaine', 'Score_Moyen', 'Nb_Évaluations']

        fig = px.line(
            weekly_data,
            x='Semaine',
            y='Score_Moyen',
            color='Année',
            title="Évolution Hebdomadaire par Année",
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # Analyse des corrélations temporelles
    st.markdown("#### 🔍 Corrélations Temporelles")

    if 'Jours_Depuis_Evaluation' in df_temp.columns:
        fig = px.scatter(
            df_temp,
            x='Jours_Depuis_Evaluation',
            y='Note_Moyenne',

            title="Relation entre Délai d'Évaluation et Score",
            labels={
                'Jours_Depuis_Evaluation': "Jours depuis l'évaluation",
                'Note_Moyenne': 'Score Moyen'
            }
        )

        st.plotly_chart(fig, use_container_width=True)


def display_recent_performance(df):
    """Analyse des performances récentes"""

    # Période de référence
    period_options = {
        "7 derniers jours": 7,
        "30 derniers jours": 30,
        "90 derniers jours": 90,
        "6 derniers mois": 180,
        "12 derniers mois": 365
    }

    selected_period = st.selectbox(
        "Période d'analyse:",
        list(period_options.keys())
    )

    days_back = period_options[selected_period]
    cutoff_date = datetime.now() - timedelta(days=days_back)

    # Filtrer les données récentes
    recent_data = df[df['Date'] >= cutoff_date].copy()

    if len(recent_data) == 0:
        st.info(f"Aucune donnée pour les {selected_period}")
        return

    st.metric(
        f"Évaluations ({selected_period})",
        len(recent_data),
        delta=f"{(len(recent_data) / len(df) * 100):.1f}% du total"
    )

    # Comparaison avec période précédente
    previous_cutoff = cutoff_date - timedelta(days=days_back)
    previous_data = df[(df['Date'] >= previous_cutoff) & (df['Date'] < cutoff_date)].copy()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        recent_avg = recent_data['Note_Moyenne'].mean() if 'Note_Moyenne' in recent_data.columns else 0
        previous_avg = previous_data['Note_Moyenne'].mean() if 'Note_Moyenne' in previous_data.columns and len(
            previous_data) > 0 else recent_avg

        delta = recent_avg - previous_avg if previous_avg > 0 else 0
        st.metric(
            "Score Moyen Récent",
            f"{recent_avg:.2f}",
            delta=f"{delta:+.2f}"
        )

    with col2:
        recent_completion = recent_data[
                                'Évaluation_Complète'].mean() * 100 if 'Évaluation_Complète' in recent_data.columns else 100
        previous_completion = previous_data[
                                  'Évaluation_Complète'].mean() * 100 if 'Évaluation_Complète' in previous_data.columns and len(
            previous_data) > 0 else recent_completion

        delta_completion = recent_completion - previous_completion
        st.metric(
            "Taux Complétion Récent",
            f"{recent_completion:.1f}%",
            delta=f"{delta_completion:+.1f}%"
        )

    with col3:
        recent_satisfaction = recent_data['Satisfaction'].mean() if 'Satisfaction' in recent_data.columns else 0
        previous_satisfaction = previous_data['Satisfaction'].mean() if 'Satisfaction' in previous_data.columns and len(
            previous_data) > 0 else recent_satisfaction

        delta_satisfaction = recent_satisfaction - previous_satisfaction
        st.metric(
            "Satisfaction Récente",
            f"{recent_satisfaction:.2f}",
            delta=f"{delta_satisfaction:+.2f}"
        )

    with col4:
        # Taux de réponse (NPS simplifié)
        if 'Satisfaction' in recent_data.columns:
            recent_promoters = (recent_data['Satisfaction'] >= 4).sum()
            recent_detractors = (recent_data['Satisfaction'] <= 2).sum()
            recent_total = len(recent_data['Satisfaction'].dropna())

            if recent_total > 0:
                recent_nps = ((recent_promoters - recent_detractors) / recent_total) * 100

                if len(previous_data) > 0 and 'Satisfaction' in previous_data.columns:
                    previous_promoters = (previous_data['Satisfaction'] >= 4).sum()
                    previous_detractors = (previous_data['Satisfaction'] <= 2).sum()
                    previous_total = len(previous_data['Satisfaction'].dropna())

                    if previous_total > 0:
                        previous_nps = ((previous_promoters - previous_detractors) / previous_total) * 100
                        delta_nps = recent_nps - previous_nps
                    else:
                        delta_nps = 0
                else:
                    delta_nps = 0

                st.metric(
                    "NPS Récent",
                    f"{recent_nps:.0f}",
                    delta=f"{delta_nps:+.0f}"
                )

    # Heatmap des performances récentes
    st.markdown("#### 📅 Performance Journalière Récente")

    if len(recent_data) > 0:
        # Préparer les données pour la heatmap
        recent_data['Date_Str'] = recent_data['Date'].dt.date.astype(str)
        recent_data['Jour_Semaine'] = recent_data['Date'].dt.day_name()
        recent_data['Semaine'] = recent_data['Date'].dt.isocalendar().week

        # Pivot pour heatmap
        heatmap_data = recent_data.pivot_table(
            values='Note_Moyenne',
            index='Jour_Semaine',
            columns='Date_Str',
            aggfunc='mean'
        ).fillna(0)

        # Réorganiser les jours
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

        # Renommer les index
        heatmap_data.index = [day_fr[day_order.index(d)] for d in heatmap_data.index if d in day_order]

        fig = px.imshow(
            heatmap_data,
            color_continuous_scale='RdYlGn',
            title="Score Moyen par Jour (Heatmap)",
            labels=dict(color="Score Moyen")
        )

        st.plotly_chart(fig, use_container_width=True)


def display_temporal_dashboards(df):
    """Tableaux de bord temporels interactifs"""

    # Filtres temporels
    st.markdown("#### ⚙️ Filtres Temporels")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Date de début:",
            value=df['Date'].min().date() if 'Date' in df.columns else datetime.now().date() - timedelta(days=30)
        )

    with col2:
        end_date = st.date_input(
            "Date de fin:",
            value=df['Date'].max().date() if 'Date' in df.columns else datetime.now().date()
        )

    # Appliquer les filtres
    filtered_df = df.copy()
    if 'Date' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= start_date) &
            (filtered_df['Date'].dt.date <= end_date)
            ]

    # Dashboard 1: Vue d'ensemble temporelle
    st.markdown(f"##### 📈 Performance du {start_date} au {end_date}")

    if len(filtered_df) == 0:
        st.info("Aucune donnée pour la période sélectionnée")
        return

    # Indicateurs clés pour la période
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        period_avg = filtered_df['Note_Moyenne'].mean() if 'Note_Moyenne' in filtered_df.columns else 0
        st.metric("Score Moyen Période", f"{period_avg:.2f}")

    with col2:
        period_count = len(filtered_df)
        st.metric("Évaluations Période", f"{period_count:,}")

    with col3:
        if 'Évaluation_Complète' in filtered_df.columns:
            period_completion = filtered_df['Évaluation_Complète'].mean() * 100
            st.metric("Taux Complétion", f"{period_completion:.1f}%")

    with col4:
        if 'Type de Formation' in filtered_df.columns:
            unique_formations = filtered_df['Type de Formation'].nunique()
            st.metric("Types de Formation", unique_formations)

    # Graphiques comparatifs
    st.markdown("##### 📊 Comparaison des Critères sur la Période")

    criteria = ['Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
    available_criteria = [c for c in criteria if c in filtered_df.columns]

    if available_criteria:
        # Box plot comparatif
        fig = px.box(
            filtered_df.melt(value_vars=available_criteria, var_name='Critère', value_name='Score'),
            x='Critère',
            y='Score',
            color='Critère',
            title="Distribution des Scores par Critère"
        )

        st.plotly_chart(fig, use_container_width=True)

    # Évolution dans le temps pour la période
    if 'Date' in filtered_df.columns and 'Note_Moyenne' in filtered_df.columns:
        st.markdown("##### 📅 Évolution Journalière")

        daily_trend = filtered_df.groupby(filtered_df['Date'].dt.date).agg({
            'Note_Moyenne': 'mean',
            'Satisfaction': 'mean',
            'ID Formation': 'count'
        }).reset_index()

        daily_trend.columns = ['Date', 'Score_Moyen', 'Satisfaction', 'Nb_Évaluations']

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Score Moyen Journalier', "Volume d'Évaluations"),
            vertical_spacing=0.15
        )

        fig.add_trace(
            go.Scatter(
                x=daily_trend['Date'],
                y=daily_trend['Score_Moyen'],
                mode='lines+markers',
                name='Score Moyen',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=daily_trend['Date'],
                y=daily_trend['Nb_Évaluations'],
                name="Nb. d'Évaluations",
                marker_color='lightblue'
            ),
            row=2, col=1
        )

        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)