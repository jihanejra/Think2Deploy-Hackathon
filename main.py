"""
Application d'analyse des évaluations de formation avec authentification
"""
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from data.loader import load_data
from frontend import (
    display_summary_cards,
    display_completion_analysis,
    display_scores_analysis,
    display_temporal_analysis
)
# Ajoutez cette cellule au début de votre application pour initialiser le cache
import os

# Créer les dossiers nécessaires
os.makedirs("backend/cache", exist_ok=True)
os.makedirs("backend/models", exist_ok=True)

# Import du module d'authentification
from backend.auth.login import login_page, check_authentication, logout

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Évaluations de Formation",

    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2ca02c;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #eee;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# GESTION DE LA NAVIGATION ET AUTHENTIFICATION
# -------------------------------------------------------------------

def navigate_to(page_name):
    """Fonction de navigation entre les pages"""
    st.session_state.page = page_name
    st.experimental_rerun()
# Initialiser l'état de session si nécessaire
if 'page' not in st.session_state:
    st.session_state.page = 'login'

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# -------------------------------------------------------------------
# PAGE DE CONNEXION
# -------------------------------------------------------------------
if st.session_state.page == 'login':
    login_page(navigate_to=navigate_to)
    st.stop()

# -------------------------------------------------------------------
# VÉRIFICATION DE L'AUTHENTIFICATION POUR LES AUTRES PAGES
# -------------------------------------------------------------------
if not st.session_state.authenticated:
    st.error(" Accès non autorisé. Veuillez vous connecter.")
    if st.button("Aller à la page de connexion"):
        st.session_state.page = 'login'
        st.experimental_rerun()
    st.stop()

# -------------------------------------------------------------------
# PAGES APRÈS AUTHENTIFICATION
# -------------------------------------------------------------------

# Fonction pour la page chatbot (exemple)


# Fonction pour la page dashboard
def dashboard_page():
    # Barre latérale avec informations utilisateur et bouton de déconnexion
    with st.sidebar:
        # Afficher les informations utilisateur
        if 'user_info' in st.session_state:
            user = st.session_state.user_info
            st.markdown(f"### 👤 {user.get('username', 'Utilisateur')}")
            st.markdown(f"**Profil:** {user.get('profil', 'Non défini')}")
            st.markdown(f"**Connecté depuis:** {user.get('login_time', 'N/A')}")
            st.markdown("---")

        st.markdown("###  Filtres d'Analyse")

        # Charger les données avec cache
        @st.cache_data
        def load_cached_data():
            return load_data()

        df = load_cached_data()

        # Afficher des infos dans la sidebar
        st.markdown(f"**📋 Total évaluations:** {len(df):,}")

        if 'Date' in df.columns:
            date_range = f"{df['Date'].min().date()} au {df['Date'].max().date()}"
            st.markdown(f"**📅 Période:** {date_range}")

        # Filtres interactifs
        st.markdown("---")
        st.markdown("### Filtres")

        # Filtre par type de formation
        if 'Type de Formation' in df.columns:
            formation_types = df['Type de Formation'].unique().tolist()
            selected_types = st.multiselect(
                "Types de formation:",
                formation_types,
                default=formation_types[:min(3, len(formation_types))]
            )

            if selected_types:
                df = df[df['Type de Formation'].isin(selected_types)]

        # Filtre par plage de dates
        if 'Date' in df.columns:
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()

            date_range = st.date_input(
                "Plage de dates:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        # Filtre par score minimum
        if 'Note_Moyenne' in df.columns:
            min_score = st.slider(
                "Score minimum:",
                min_value=1.0,
                max_value=5.0,
                value=1.0,
                step=0.5
            )
            df = df[df['Note_Moyenne'] >= min_score]

        # Informations sur les données filtrées
        st.markdown("---")
        st.markdown("### 📈 Données Filtrées")
        st.markdown(f"**Échantillons:** {len(df):,}")

        if len(df) > 0 and 'Note_Moyenne' in df.columns:
            st.markdown(f"**Score moyen:** {df['Note_Moyenne'].mean():.2f}/5")

        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser les filtres"):
            st.experimental_rerun()

        # Bouton de déconnexion
        st.markdown("---")
        if st.button(" Se déconnecter", type="secondary"):
            logout(navigate_to=navigate_to)

    # Contenu principal du dashboard
    st.markdown("<h1 class='main-header'>Tableau de Bord des Évaluations de Formation</h1>",
                unsafe_allow_html=True)

    # Section 1: Cartes de résumé
    st.markdown("<h2 class='section-header'> Vue d'Ensemble</h2>", unsafe_allow_html=True)
    display_summary_cards(df)

    # Section 2: Taux de complétion
    st.markdown("<h2 class='section-header'> Taux de Complétion des Évaluations</h2>", unsafe_allow_html=True)
    display_completion_analysis(df)

    # Section 3: Scores moyens par critère
    st.markdown("<h2 class='section-header'> Scores Moyens par Critère</h2>", unsafe_allow_html=True)
    display_scores_analysis(df)

    # Section 4: Évolution temporelle
    st.markdown("<h2 class='section-header'> Évolution des Scores dans le Temps</h2>", unsafe_allow_html=True)
    display_temporal_analysis(df)

    # Section 5: Exporter les résultats
    st.markdown("---")
    st.markdown("<h2 class='section-header'>💾 Export des Résultats</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(" Exporter les données analysées"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name="evaluations_analysees.csv",
                mime="text/csv"
            )

    with col2:
        # Générer un rapport PDF
        if st.button("📄 Générer un rapport PDF"):
            # ... (garder votre code de génération de PDF existant)
            st.info("Fonctionnalité de génération de rapport à implémenter")

    with col3:
        # Réinitialiser
        if st.button("🔄 Tout réinitialiser"):
            st.experimental_rerun()

    # Pied de page

    # Afficher un aperçu des données
    with st.expander(" Aperçu des Données Brutes"):
        st.dataframe(df.head(100), use_container_width=True)

        # Statistiques descriptives
        if st.checkbox("Afficher les statistiques descriptives"):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)

    # -------------------------------------------------------------------
    # SECTION 5 : ANALYSE NLP DES COMMENTAIRES
    # -------------------------------------------------------------------

    if 'Commentaire' in df.columns and df['Commentaire'].notna().sum() > 0:
        st.markdown("---")
        st.markdown("<h2 class='section-header'> Analyse NLP des Commentaires</h2>", unsafe_allow_html=True)

        # Prétraitement des commentaires
        from backend.nlp_preprocessing import preprocess_comments

        df_clean = preprocess_comments(df)

        # Onglets pour différentes analyses NLP
        tab1, tab2 = st.tabs([
            " Analyse Textuelle",
            " Topic Modeling",

        ])

        with tab1:
            # Analyse textuelle de base
            from backend.analysis import display_comment_analysis_streamlit

            display_comment_analysis_streamlit(df_clean)

        with tab2:
            st.markdown("### Topic Modeling - Entraînement Dynamique")

            # Informations sur les données
            if 'commentaire_clean' in df_clean.columns:
                n_comments = df_clean['commentaire_clean'].dropna().shape[0]
                st.info(f" **{n_comments} commentaires** disponibles pour l'analyse")

                if n_comments < 10:
                    st.warning(" Au moins 10 commentaires sont nécessaires pour une analyse significative")
                else:
                    from backend.topic_modeling import display_dynamic_topic_analysis

                    with st.expander("⏱️ Estimation du temps", expanded=False):
                        st.write("""
                        **Temps estimé en fonction du nombre de commentaires:**
                        - 10-50 commentaires : 10-30 secondes
                        - 50-200 commentaires : 30-60 secondes  
                        - 200+ commentaires : 1-3 minutes
                        """)

                    display_dynamic_topic_analysis(df_clean)

            else:
                st.warning(" Les commentaires doivent d'abord être nettoyés")

                if st.button(" Nettoyer les commentaires maintenant"):
                    from backend.nlp_preprocessing import preprocess_comments
                    df_clean = preprocess_comments(df)
                    st.experimental_rerun()


# -------------------------------------------------------------------
# ROUTAGE DES PAGES
# -------------------------------------------------------------------
if st.session_state.page == 'dashboard':
    dashboard_page()

else:
    # Page par défaut (dashboard pour RH, chatbot pour autres)
    if st.session_state.user_info.get('profil') == 'RH':
        navigate_to('dashboard')
    else:
        navigate_to('chatbot')