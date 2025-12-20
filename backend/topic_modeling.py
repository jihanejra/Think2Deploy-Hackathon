"""
Topic Modeling dynamique - Entraînement à la volée
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import joblib
import os
import hashlib
from datetime import datetime


def train_bertopic_dynamic(df, text_column='commentaire_clean', use_cache=True):
    """
    Entraîne BERTopic dynamiquement avec cache intelligent
    """
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer

        # Vérifier si on a assez de données
        texts = df[text_column].dropna().tolist()
        if len(texts) < 10:
            st.warning("⚠️ Pas assez de commentaires pour l'analyse thématique (minimum 10)")
            return None, None, None

        # Créer un hash des données pour le cache
        data_hash = hashlib.md5(''.join(texts).encode()).hexdigest()[:10]
        cache_key = f"bertopic_cache_{data_hash}.pkl"
        cache_path = os.path.join("backend", "cache", cache_key)

        # Créer le dossier cache si nécessaire
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        # Vérifier le cache
        if use_cache and os.path.exists(cache_path):
            try:
                st.info("📂 Chargement du modèle depuis le cache...")
                model_data = joblib.load(cache_path)

                # Vérifier si les données correspondent
                if model_data['data_hash'] == data_hash:
                    st.success("✅ Modèle chargé depuis le cache")
                    return model_data['model'], model_data['topics'], model_data['probabilities']
            except:
                pass

        # Si pas de cache, entraîner
        st.info("🚀 Entraînement de BERTopic en cours...")

        with st.spinner(f"Analyse de {len(texts)} commentaires..."):
            # Afficher la progression
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Étape 1/3 : Préparation des données...")
            progress_bar.progress(20)

            # Modèle léger pour rapidité
            embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

            status_text.text("Étape 2/3 : Création des embeddings...")
            progress_bar.progress(50)

            # Configurer BERTopic avec paramètres optimisés
            topic_model = BERTopic(
                embedding_model=embedding_model,
                language="multilingual",
                min_topic_size=max(3, len(texts) // 20),  # Adaptatif
                nr_topics="auto",
                top_n_words=8,
                calculate_probabilities=True,
                verbose=False
            )

            status_text.text("Étape 3/3 : Entraînement du modèle...")
            progress_bar.progress(80)

            # Entraînement
            topics, probabilities = topic_model.fit_transform(texts)

            progress_bar.progress(100)
            status_text.text("✅ Entraînement terminé!")

            # Sauvegarder dans le cache
            model_data = {
                'model': topic_model,
                'topics': topics,
                'probabilities': probabilities,
                'data_hash': data_hash,
                'timestamp': datetime.now().isoformat(),
                'n_documents': len(texts)
            }

            try:
                joblib.dump(model_data, cache_path)
                st.success(f"✅ Modèle sauvegardé dans le cache ({len(texts)} documents)")
            except:
                st.info("ℹ️ Modèle non sauvegardé en cache")

            # Nettoyer l'affichage
            progress_bar.empty()
            status_text.empty()

            return topic_model, topics, probabilities

    except ImportError as e:
        st.error(f"❌ Bibliothèque manquante : {e}")
        st.info("Installez avec: `pip install bertopic sentence-transformers`")
        return None, None, None

    except Exception as e:
        st.error(f"❌ Erreur lors de l'entraînement : {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None, None, None


def clear_bertopic_cache():
    """Nettoie le cache des modèles BERTopic"""
    cache_dir = os.path.join("backend", "cache")
    if os.path.exists(cache_dir):
        import shutil
        shutil.rmtree(cache_dir)
        st.success("✅ Cache nettoyé")
    else:
        st.info("ℹ️ Aucun cache à nettoyer")


def display_dynamic_topic_analysis(df, text_column='commentaire_clean'):
    """
    Analyse thématique dynamique avec entraînement automatique
    """
    st.markdown("### 🎯 Analyse Thématique Dynamique")

    # Options de configuration
    with st.expander("⚙️ Paramètres d'analyse", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            min_topic_size = st.slider(
                "Taille minimale des thèmes",
                min_value=2,
                max_value=20,
                value=5,
                help="Nombre minimum de documents par thème"
            )

        with col2:
            n_top_words = st.slider(
                "Mots par thème",
                min_value=5,
                max_value=15,
                value=8
            )

        with col3:
            use_cache = st.checkbox("Utiliser le cache", value=True)
            force_retrain = st.checkbox("Forcer ré-entraînement", value=False)

    # Statistiques des données
    texts = df[text_column].dropna().tolist()

    if len(texts) == 0:
        st.warning("⚠️ Aucun commentaire à analyser")
        return

    st.info(f"📊 **{len(texts)} commentaires** à analyser")

    # Bouton d'analyse
    if st.button("🚀 Lancer l'analyse thématique", type="primary") or force_retrain:

        # Entraînement dynamique
        topic_model, topics, probabilities = train_bertopic_dynamic(
            df,
            text_column=text_column,
            use_cache=use_cache and not force_retrain
        )

        if topic_model is None:
            st.error("Impossible d'entraîner le modèle")
            return

        # Ajouter les thèmes au dataframe
        df_analysis = df.copy()
        df_analysis['topic'] = topics
        df_analysis['topic_probability'] = probabilities.max(axis=1) if probabilities is not None else None

        # Afficher les résultats
        display_topic_results(topic_model, df_analysis)

        # Options d'export
        with st.expander("💾 Export des résultats"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Exporter les thèmes détectés"):
                    export_topics_csv(topic_model, df_analysis)

            with col2:
                if st.button("🧹 Nettoyer le cache"):
                    clear_bertopic_cache()


def display_topic_results(topic_model, df):
    """
    Affiche les résultats de l'analyse thématique
    """
    # Obtenir les informations des thèmes
    topic_info = topic_model.get_topic_info()

    # Statistiques
    st.markdown("#### 📈 Statistiques de l'analyse")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_topics = len(topic_info) - 1
        st.metric("Thèmes détectés", total_topics)

    with col2:
        docs_classifies = topic_info[topic_info['Topic'] != -1]['Count'].sum()
        st.metric("Documents classés", docs_classifies)

    with col3:
        total_docs = len(df)
        taux_classif = (docs_classifies / total_docs) * 100
        st.metric("Taux classification", f"{taux_classif:.1f}%")

    with col4:
        avg_prob = df['topic_probability'].mean() if 'topic_probability' in df.columns else 0
        st.metric("Confiance moyenne", f"{avg_prob:.2%}")

    # Visualisation 1 : Distribution des thèmes
    st.markdown("#### 📊 Distribution des Thèmes")

    # Exclure le thème -1 (non classés)
    topics_filtered = topic_info[topic_info['Topic'] != -1].sort_values('Count', ascending=False)

    if len(topics_filtered) > 0:
        # Graphique à barres
        fig1 = px.bar(
            topics_filtered.head(10),
            x='Count',
            y='Name',
            orientation='h',
            title='Top 10 Thèmes les plus fréquents',
            color='Count',
            color_continuous_scale='viridis',
            labels={'Count': 'Nombre de documents', 'Name': 'Thème'}
        )

        fig1.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )

        st.plotly_chart(fig1, use_container_width=True)

        # Visualisation 2 : Détails par thème
        st.markdown("#### 🔍 Exploration des Thèmes")

        # Sélectionner un thème
        selected_topic = st.selectbox(
            "Explorer un thème en détail:",
            options=topics_filtered['Topic'].tolist(),
            format_func=lambda x: f"Thème {x}: {topic_info[topic_info['Topic'] == x]['Name'].values[0]}"
        )

        if selected_topic is not None:
            display_topic_details(topic_model, df, selected_topic)

        # Visualisation 3 : Mots-clés globaux
        st.markdown("#### 🔑 Mots-clés Principaux")

        all_topics_words = []
        for topic_id in topics_filtered['Topic'].head(5):
            words = topic_model.get_topic(topic_id)
            for word, score in words[:3]:  # Top 3 mots par thème
                all_topics_words.append({
                    'Mot': word,
                    'Score': score,
                    'Thème': f"Thème {topic_id}"
                })

        if all_topics_words:
            words_df = pd.DataFrame(all_topics_words)

            # Wordcloud des mots-clés
            try:
                from wordcloud import WordCloud

                text = ' '.join(words_df['Mot'].tolist())
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white'
                ).generate(text)

                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wordcloud, interpolation='bilinear')
                ax_wc.axis('off')
                ax_wc.set_title('Wordcloud des Mots-clés des Thèmes', fontsize=14)

                st.pyplot(fig_wc)
                plt.close()
            except:
                pass

        # Tableau complet
        with st.expander("📋 Tableau Complet des Thèmes"):
            st.dataframe(
                topic_info[['Topic', 'Count', 'Name']].sort_values('Count', ascending=False),
                use_container_width=True,
                height=300
            )
    else:
        st.info("ℹ️ Aucun thème significatif détecté. Essayez de réduire la taille minimale des thèmes.")


def display_topic_details(topic_model, df, topic_id):
    """
    Affiche les détails d'un thème spécifique
    """
    # Mots-clés du thème
    topic_words = topic_model.get_topic(topic_id)

    if topic_words:
        words_df = pd.DataFrame(topic_words, columns=['Mot', 'Importance'])

        col1, col2 = st.columns([2, 1])

        with col1:
            # Graphique des mots-clés
            fig = px.bar(
                words_df,
                x='Importance',
                y='Mot',
                orientation='h',
                title=f'Mots-clés du Thème {topic_id}',
                color='Importance',
                color_continuous_scale='plasma'
            )

            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Statistiques du thème
            topic_docs = df[df['topic'] == topic_id]

            st.metric("Documents", len(topic_docs))

            if 'satisfaction' in topic_docs.columns:
                avg_satisfaction = topic_docs['satisfaction'].mean()
                st.metric("Satisfaction moyenne", f"{avg_satisfaction:.2f}/5")

            if 'topic_probability' in topic_docs.columns:
                avg_prob = topic_docs['topic_probability'].mean()
                st.metric("Confiance moyenne", f"{avg_prob:.2%}")

        # Exemples de commentaires
        st.markdown("**💬 Exemples de commentaires de ce thème:**")

        if 'commentaire' in df.columns:
            topic_comments = df[df['topic'] == topic_id]['commentaire'].dropna().head(5)

            for i, comment in enumerate(topic_comments, 1):
                with st.expander(f"Commentaire {i}"):
                    st.write(comment)

                    # Métriques du commentaire
                    comment_row = df[df['commentaire'] == comment].iloc[0]
                    col_metrics = st.columns(3)

                    with col_metrics[0]:
                        if 'satisfaction' in comment_row:
                            st.metric("Satisfaction", comment_row['satisfaction'])

                    with col_metrics[1]:
                        if 'topic_probability' in comment_row:
                            st.metric("Confiance", f"{comment_row['topic_probability']:.1%}")

                    with col_metrics[2]:
                        st.metric("Longueur", f"{len(str(comment))} caractères")


def export_topics_csv(topic_model, df):
    """
    Exporte les résultats en CSV
    """
    try:
        # Préparer les données
        export_df = df.copy()

        # Garder les colonnes importantes
        export_cols = ['commentaire', 'topic', 'topic_probability']
        if 'satisfaction' in export_df.columns:
            export_cols.append('satisfaction')
        if 'type_formation' in export_df.columns:
            export_cols.append('type_formation')
        if 'Date' in export_df.columns:
            export_cols.append('Date')

        export_df = export_df[export_cols]

        # Ajouter les noms des thèmes
        topic_info = topic_model.get_topic_info()
        topic_names = {row['Topic']: row['Name'] for _, row in topic_info.iterrows()}
        export_df['topic_name'] = export_df['topic'].map(topic_names)

        # Convertir en CSV
        csv = export_df.to_csv(index=False, encoding='utf-8-sig')

        # Téléchargement
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name=f"topics_analysis_{timestamp}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Erreur lors de l'export : {e}")


# Mettre à jour l'import dans backend/__init__.py
__all__ = [
    # ... autres imports
    'train_bertopic_dynamic',
    'display_dynamic_topic_analysis',
    'clear_bertopic_cache',
    'display_topic_results',
    'export_topics_csv'
]