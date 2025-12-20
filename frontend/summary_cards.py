"""
Cartes de résumé et indicateurs clés
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def display_summary_cards(df):
    """Affiche les cartes de résumé principales"""

    st.markdown("### 📊 Indicateurs Clés de Performance")

    # Calcul des métriques
    total_evaluations = len(df)

    # Taux de complétion
    if 'Évaluation_Complète' in df.columns:
        completed = df['Évaluation_Complète'].sum()
        completion_rate = (completed / total_evaluations) * 100
    else:
        completion_rate = 100  # Par défaut si toutes les données sont complètes

    # Scores moyens
    criteria = ['Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
    available_criteria = [c for c in criteria if c in df.columns]

    if available_criteria:
        avg_scores = {c: df[c].mean(skipna=True) for c in available_criteria}
        overall_avg = np.mean(list(avg_scores.values()))
    else:
        overall_avg = 0

    # Évolution temporelle
    if 'Date' in df.columns and 'Note_Moyenne' in df.columns:
        current_month_avg = df[df['Date'] >= pd.Timestamp.now() - pd.DateOffset(months=1)]['Note_Moyenne'].mean()
        previous_month_avg = df[(df['Date'] >= pd.Timestamp.now() - pd.DateOffset(months=2)) &
                                (df['Date'] < pd.Timestamp.now() - pd.DateOffset(months=1))]['Note_Moyenne'].mean()

        if pd.notna(current_month_avg) and pd.notna(previous_month_avg):
            monthly_change = ((current_month_avg - previous_month_avg) / previous_month_avg) * 100
        else:
            monthly_change = 0
    else:
        monthly_change = 0

    # Afficher les cartes
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Évaluations Total",
            f"{total_evaluations:,}",
            help="Nombre total d'évaluations collectées"
        )

    with col2:
        st.metric(
            "Taux de Complétion",
            f"{completion_rate:.1f}%",
            delta=f"{completed}/{total_evaluations}" if 'Évaluation_Complète' in df.columns else "",
            delta_color="off",
            help="Pourcentage d'évaluations complètement remplies"
        )

    with col3:
        st.metric(
            "Score Moyen Global",
            f"{overall_avg:.2f}/5",
            help="Moyenne de tous les critères d'évaluation"
        )

    with col4:
        delta_text = f"{monthly_change:+.1f}%" if monthly_change != 0 else "N/A"
        delta_color = "normal" if monthly_change >= 0 else "inverse"
        st.metric(
            "Évolution Mensuelle",
            f"{current_month_avg:.2f}/5" if 'Date' in df.columns else "N/A",
            delta=delta_text,
            delta_color=delta_color,
            help="Évolution du score moyen sur le dernier mois"
        )

    # Score par critère en radar chart
    if available_criteria and len(available_criteria) >= 3:
        st.markdown("---")
        st.markdown("#### 📈 Scores par Critère")

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=list(avg_scores.values()),
            theta=list(avg_scores.keys()),
            fill='toself',
            name='Score Moyen',
            line_color='blue',
            opacity=0.6
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(size=10)
                )
            ),
            showlegend=False,
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)


def display_trend_indicator(df, metric='Note_Moyenne', period='monthly'):
    """Affiche un indicateur de tendance"""

    if 'Date' not in df.columns or metric not in df.columns:
        return

    # Préparer les données temporelles
    df_temp = df.copy()
    df_temp = df_temp.dropna(subset=[metric, 'Date'])

    if period == 'monthly':
        df_temp['Période'] = df_temp['Date'].dt.to_period('M').astype(str)
    elif period == 'weekly':
        df_temp['Période'] = df_temp['Date'].dt.to_period('W').astype(str)
    else:  # daily
        df_temp['Période'] = df_temp['Date'].dt.date.astype(str)

    trend_data = df_temp.groupby('Période')[metric].mean().reset_index()

    if len(trend_data) < 2:
        return

    # Calculer la tendance
    recent = trend_data[metric].iloc[-6:].mean() if len(trend_data) >= 6 else trend_data[metric].iloc[-1]
    previous = trend_data[metric].iloc[-12:-6].mean() if len(trend_data) >= 12 else trend_data[metric].iloc[0]

    if previous > 0:
        trend_pct = ((recent - previous) / previous) * 100
    else:
        trend_pct = 0

    # Afficher l'indicateur
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        fig = go.Figure(go.Indicator(
            mode="delta",
            value=trend_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 0, 'position': "bottom"},
            title={"text": "Tendance Récente"}
        ))

        fig.update_layout(
            height=100,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)