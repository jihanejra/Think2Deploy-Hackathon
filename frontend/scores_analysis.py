"""
Analyse des scores par critère
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats


def display_scores_analysis(df):
    """Affiche l'analyse des scores par critère"""

    st.markdown("###  Scores Moyens par Critère")

    # Critères disponibles
    criteria = ['Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
    available_criteria = [c for c in criteria if c in df.columns]

    if not available_criteria:
        st.info("Aucun critère d'évaluation disponible")
        return

    # Onglets d'analyse
    tab1, tab2, tab3, tab4 = st.tabs([
        " Comparaison des Critères",
        " Distribution des Notes",
        " Classements",
        " Corrélations"
    ])

    with tab1:
        display_criteria_comparison(df, available_criteria)

    with tab2:
        display_score_distributions(df, available_criteria)

    with tab3:
        display_rankings(df, available_criteria)

    with tab4:
        display_correlations(df, available_criteria)


def display_criteria_comparison(df, criteria):
    """Comparaison visuelle des critères"""

    # Calculer les statistiques
    stats_df = pd.DataFrame({
        'Critère': criteria,
        'Moyenne': [df[c].mean(skipna=True) for c in criteria],
        'Médiane': [df[c].median(skipna=True) for c in criteria],
        'Écart-Type': [df[c].std(skipna=True) for c in criteria],
        'Minimum': [df[c].min(skipna=True) for c in criteria],
        'Maximum': [df[c].max(skipna=True) for c in criteria],
        'Complétion': [(df[c].notna().sum() / len(df)) * 100 for c in criteria]
    })

    col1, col2 = st.columns([2, 1])

    with col1:
        # Radar chart des moyennes
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=stats_df['Moyenne'].tolist() + [stats_df['Moyenne'].iloc[0]],
            theta=stats_df['Critère'].tolist() + [stats_df['Critère'].iloc[0]],
            fill='toself',
            name='Score Moyen',
            line_color='blue'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['1', '2', '3', '4', '5']
                )
            ),
            showlegend=False,
            title="Performance par Critère",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar chart horizontal
        fig = px.bar(
            stats_df.sort_values('Moyenne', ascending=True),
            x='Moyenne',
            y='Critère',
            orientation='h',
            color='Moyenne',
            color_continuous_scale='RdYlGn',
            range_color=[1, 5],
            text='Moyenne'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_range=[0, 5],
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé
    st.dataframe(
        stats_df.style.format({
            'Moyenne': '{:.2f}',
            'Médiane': '{:.2f}',
            'Écart-Type': '{:.2f}',
            'Minimum': '{:.0f}',
            'Maximum': '{:.0f}',
            'Complétion': '{:.1f}%'
        }).background_gradient(
            subset=['Moyenne', 'Complétion'],
            cmap='RdYlGn',
            vmin=1, vmax=5
        ),
        use_container_width=True
    )

    # Score global calculé
    if 'Note_Moyenne' in df.columns:
        st.metric(
            "Score Global Moyen",
            f"{df['Note_Moyenne'].mean():.2f}/5",
            help="Moyenne de tous les critères combinés"
        )


def display_score_distributions(df, criteria):
    """Distribution des notes pour chaque critère"""

    # Sélection du critère
    selected_criterion = st.selectbox(
        "Sélectionnez un critère à analyser:",
        criteria
    )

    if not selected_criterion:
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        # Histogramme
        fig = px.histogram(
            df,
            x=selected_criterion,
            nbins=10,
            title=f"Distribution des Notes - {selected_criterion}",
            labels={selected_criterion: 'Note'},
            color_discrete_sequence=['blue']
        )

        # Ajouter une ligne pour la moyenne
        mean_val = df[selected_criterion].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Moyenne: {mean_val:.2f}",
            annotation_position="top right"
        )

        st.plotly_chart(fig, use_container_width=True)






def display_rankings(df, criteria):
    """Classements et performances"""

    # Classement par formateur
    if 'ID Formateur' in df.columns:
        st.markdown("#### 🏆 Classement des Formateurs")

        # Calculer le score moyen par formateur (minimum 5 évaluations)
        formateur_stats = df.groupby('ID Formateur').agg({
            'Note_Moyenne': ['mean', 'count'],
            'Satisfaction': 'mean',
            'Contenu': 'mean',
            'Logistique': 'mean',
            'Applicabilité': 'mean'
        }).round(2)

        formateur_stats.columns = ['Note_Moyenne', 'Nombre', 'Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
        formateur_stats = formateur_stats[formateur_stats['Nombre'] >= 3]  # Minimum 3 évaluations

        if len(formateur_stats) > 0:
            # Top 10 formateurs
            top_formateurs = formateur_stats.sort_values('Note_Moyenne', ascending=False).head(10)

            fig = px.bar(
                top_formateurs.reset_index(),
                x='ID Formateur',
                y='Note_Moyenne',
                color='Nombre',
                color_continuous_scale='Viridis',
                title="Top 10 Formateurs par Note Moyenne",
                labels={'Note_Moyenne': 'Score Moyen', 'Nombre': 'Nb. Évaluations'}
            )

            st.plotly_chart(fig, use_container_width=True)

            # Tableau détaillé
            st.dataframe(
                top_formateurs.style.format({
                    'Note_Moyenne': '{:.2f}',
                    'Satisfaction': '{:.2f}',
                    'Contenu': '{:.2f}',
                    'Logistique': '{:.2f}',
                    'Applicabilité': '{:.2f}'
                }).background_gradient(
                    subset=['Note_Moyenne'],
                    cmap='RdYlGn',
                    vmin=1,
                    vmax=5
                ),
                use_container_width=True
            )

    # Classement par type de formation
    if 'Type de Formation' in df.columns:
        st.markdown("#### 📈 Performance par Type de Formation")

        type_performance = df.groupby('Type de Formation').agg({
            'Note_Moyenne': 'mean',
            'Évaluation_Complète': 'mean',
            'Satisfaction': 'mean',
            'ID Formation': 'nunique'
        }).round(2)

        type_performance.columns = ['Score_Moyen', 'Taux_Complétion', 'Satisfaction_Moyenne', 'Nb_Formations']
        type_performance['Taux_Complétion'] = type_performance['Taux_Complétion'] * 100

        # Scatter plot avec taille selon le nombre de formations
        fig = px.scatter(
            type_performance.reset_index(),
            x='Score_Moyen',
            y='Taux_Complétion',
            size='Nb_Formations',
            color='Satisfaction_Moyenne',
            hover_name='Type de Formation',
            color_continuous_scale='RdYlGn',
            size_max=60,
            title="Performance vs Complétion par Type de Formation",
            labels={
                'Score_Moyen': 'Score Moyen',
                'Taux_Complétion': 'Taux de Complétion (%)',
                'Satisfaction_Moyenne': 'Satisfaction Moyenne'
            }
        )

        st.plotly_chart(fig, use_container_width=True)


def display_correlations(df, criteria):
    """Analyse des corrélations entre critères"""

    if len(criteria) < 2:
        st.info("Au moins 2 critères nécessaires pour l'analyse des corrélations")
        return

    # Matrice de corrélation
    corr_matrix = df[criteria].corr().round(2)

    # Heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu',
        aspect="auto",
        title="Matrice de Corrélation entre Critères"
    )

    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Analyse des paires les plus corrélées
    st.markdown("#### 🔗 Paires de Critères les Plus Liées")

    # Trouver les paires les plus corrélées
    correlations = []
    for i in range(len(criteria)):
        for j in range(i + 1, len(criteria)):
            corr = corr_matrix.iloc[i, j]
            correlations.append({
                'Critère 1': criteria[i],
                'Critère 2': criteria[j],
                'Corrélation': corr,
                'Force': 'Forte' if abs(corr) > 0.7 else 'Modérée' if abs(corr) > 0.4 else 'Faible'
            })

    corr_df = pd.DataFrame(correlations).sort_values('Corrélation', key=abs, ascending=False)

    # Afficher les paires
    for _, row in corr_df.head(5).iterrows():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**{row['Critère 1']}**")
        with col2:
            st.write(f"**{row['Critère 2']}**")
        with col3:
            color = "green" if row['Corrélation'] > 0 else "red"
            st.markdown(f"<span style='color:{color};font-weight:bold'>{row['Corrélation']:.2f}</span>",
                        unsafe_allow_html=True)

        # Scatter plot pour la paire
        if st.checkbox(f"Voir relation {row['Critère 1']} vs {row['Critère 2']}",
                       key=f"scatter_{row['Critère 1']}_{row['Critère 2']}"):
            fig = px.scatter(
                df,
                x=row['Critère 1'],
                y=row['Critère 2'],

                title=f"Relation entre {row['Critère 1']} et {row['Critère 2']}",
                labels={
                    row['Critère 1']: row['Critère 1'],
                    row['Critère 2']: row['Critère 2']
                }
            )

            st.plotly_chart(fig, use_container_width=True)