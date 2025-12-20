"""
Analyse NLP : Wordcloud, n-grams, sentiment
Version corrigée avec gestion des erreurs
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer


def generate_wordcloud_streamlit(df, text_column='commentaire_clean', st_component=None):
    """
    Génère un wordcloud avec gestion des erreurs NLTK
    """
    if st_component is None:
        import streamlit as st
        st_component = st

    try:
        from wordcloud import WordCloud

        # Récupérer les textes
        texts = df[text_column].dropna().tolist()

        if not texts:
            st_component.warning("Aucun texte à analyser")
            return

        # Concaténer tous les textes
        all_text = ' '.join(texts)

        # Utiliser une liste de stopwords français manuelle
        french_stopwords = {
            'au', 'aux', 'avec', 'ce', 'ces', 'dans', 'de', 'des', 'du', 'elle',
            'en', 'et', 'eux', 'il', 'je', 'la', 'le', 'leur', 'lui', 'ma',
            'mais', 'me', 'même', 'mes', 'moi', 'mon', 'ne', 'nos', 'notre',
            'nous', 'on', 'ou', 'par', 'pas', 'pour', 'qu', 'que', 'qui', 'sa',
            'se', 'ses', 'son', 'sur', 'ta', 'te', 'tes', 'toi', 'ton', 'tu',
            'un', 'une', 'vos', 'votre', 'vous', 'c', 'd', 'j', 'l', 'à', 'm',
            'n', 's', 't', 'y', 'été', 'étée', 'étées', 'étés', 'étant', 'suis',
            'es', 'est', 'sommes', 'êtes', 'sont', 'serai', 'seras', 'sera',
            'serons', 'serez', 'seront', 'serais', 'serait', 'serions', 'seriez',
            'seraient', 'étais', 'était', 'étions', 'étiez', 'étaient', 'fus',
            'fut', 'fûmes', 'fûtes', 'furent', 'sois', 'soit', 'soyons', 'soyez',
            'soient', 'fusse', 'fusses', 'fût', 'fussions', 'fussiez', 'fussent',
            'ayant', 'eu', 'eue', 'eues', 'eus', 'ai', 'as', 'avons', 'avez',
            'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez', 'auront',
            'aurais', 'aurait', 'aurions', 'auriez', 'auraient', 'avais',
            'avait', 'avions', 'aviez', 'avaient', 'eut', 'eûmes', 'eûtes',
            'eurent', 'aie', 'aies', 'ait', 'ayons', 'ayez', 'aient', 'eusse',
            'eusses', 'eût', 'eussions', 'eussiez', 'eussent', 'ceci', 'cela',
            'celà', 'cet', 'cette', 'ici', 'ils', 'les', 'leurs', 'quel',
            'quels', 'quelle', 'quelles', 'sans', 'soi', 'tout', 'tous', 'toute',
            'toutes', 'très', 'trois', 'trop'
        }

        # Créer le wordcloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=french_stopwords,
            max_words=100,
            colormap='viridis'
        ).generate(all_text)

        # Afficher
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Nuage de Mots des Commentaires', fontsize=16)

        st_component.pyplot(fig)
        plt.close()

    except ImportError:
        st_component.error("WordCloud non installé. Installez avec: `pip install wordcloud`")
    except Exception as e:
        st_component.error(f"Erreur lors de la génération du wordcloud: {e}")


def analyze_ngrams(df, text_column='commentaire_clean', n=2, top_n=10):
    """
    Analyse les n-grams les plus fréquents
    """
    try:
        # Liste des stopwords français personnalisée
        french_stopwords = [
            'au', 'aux', 'avec', 'ce', 'ces', 'dans', 'de', 'des', 'du', 'elle',
            'en', 'et', 'eux', 'il', 'je', 'la', 'le', 'leur', 'lui', 'ma',
            'mais', 'me', 'même', 'mes', 'moi', 'mon', 'ne', 'nos', 'notre',
            'nous', 'on', 'ou', 'par', 'pas', 'pour', 'qu', 'que', 'qui', 'sa',
            'se', 'ses', 'son', 'sur', 'ta', 'te', 'tes', 'toi', 'ton', 'tu',
            'un', 'une', 'vos', 'votre', 'vous', 'c', 'd', 'j', 'l', 'à', 'm',
            'n', 's', 't', 'y', 'été', 'étée', 'étées', 'étés', 'étant', 'suis',
            'es', 'est', 'sommes', 'êtes', 'sont', 'serai', 'seras', 'sera',
            'serons', 'serez', 'seront', 'serais', 'serait', 'serions', 'seriez',
            'seraient', 'étais', 'était', 'étions', 'étiez', 'étaient', 'fus',
            'fut', 'fûmes', 'fûtes', 'furent', 'sois', 'soit', 'soyons', 'soyez',
            'soient', 'fusse', 'fusses', 'fût', 'fussions', 'fussiez', 'fussent',
            'ayant', 'eu', 'eue', 'eues', 'eus', 'ai', 'as', 'avons', 'avez',
            'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez', 'auront',
            'aurais', 'aurait', 'aurions', 'auriez', 'auraient', 'avais',
            'avait', 'avions', 'aviez', 'avaient', 'eut', 'eûmes', 'eûtes',
            'eurent', 'aie', 'aies', 'ait', 'ayons', 'ayez', 'aient', 'eusse',
            'eusses', 'eût', 'eussions', 'eussiez', 'eussent', 'ceci', 'cela',
            'celà', 'cet', 'cette', 'ici', 'ils', 'les', 'leurs', 'quel',
            'quels', 'quelle', 'quelles', 'sans', 'soi', 'tout', 'tous', 'toute',
            'toutes', 'très', 'trois', 'trop'
        ]

        # Récupérer les textes
        texts = df[text_column].dropna().tolist()

        if len(texts) < 2:
            return pd.DataFrame({'n_gram': [], 'freq': []})

        # Créer le vectorizer avec stopwords personnalisés
        vectorizer = CountVectorizer(
            ngram_range=(n, n),
            stop_words=french_stopwords,  # Passer en liste
            max_features=top_n * 2
        )

        # Calculer les n-grams
        X = vectorizer.fit_transform(texts)

        # Compter les fréquences
        counts = X.sum(axis=0)

        # Créer un DataFrame avec les résultats
        ngrams_df = pd.DataFrame({
            'n_gram': vectorizer.get_feature_names_out(),
            'freq': counts.A1
        }).sort_values('freq', ascending=False).head(top_n)

        return ngrams_df

    except Exception as e:
        print(f"Erreur dans analyze_ngrams: {e}")
        return pd.DataFrame({'n_gram': ['Erreur lors de l\'analyse'], 'freq': [0]})


def plot_ngrams_streamlit(ngrams_df, title="", st_component=None):
    """
    Affiche les n-grams dans Streamlit
    """
    if ngrams_df is None or ngrams_df.empty or len(ngrams_df) == 0:
        if st_component:
            st_component.info("Aucun n-gram à afficher")
        return None

    # Vérifier les colonnes du DataFrame
    if 'n_gram' not in ngrams_df.columns or 'freq' not in ngrams_df.columns:
        st_component.error("Format incorrect des n-grams")
        return None

    # Créer le graphique
    fig = px.bar(
        ngrams_df,
        x='freq',
        y='n_gram',
        orientation='h',
        title=title,
        color='freq',
        color_continuous_scale='viridis',
        labels={'freq': 'Fréquence', 'n_gram': 'N-Gram'}
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400
    )

    if st_component:
        st_component.plotly_chart(fig, use_container_width=True)

    return fig


def analyze_sentiment_simple(df, text_column='commentaire_clean'):
    """
    Analyse sentimentale simple basée sur les mots-clés
    """
    # Mots positifs et négatifs (liste basique)
    positive_words = ['excellent', 'super', 'bien', 'bon', 'agréable', 'utile',
                      'intéressant', 'formidable', 'parfait', 'génial', 'efficace',
                      'claire', 'pratique', 'enrichissant', 'motivant', 'satisfait',
                      'content', 'ravi', 'recommandé', 'apprécié', 'fantastique']

    negative_words = ['mauvais', 'nul', 'décevant', 'difficile', 'compliqué',
                      'inutile', 'ennuyeux', 'pénible', 'médiocre', 'faible',
                      'confus', 'incompréhensible', 'lent', 'problème', 'déçu',
                      'insatisfait', 'peu', 'trop', 'cher', 'manque']

    sentiments = []

    for text in df[text_column].dropna():
        if pd.isna(text):
            sentiments.append('Neutre')
            continue

        text_lower = str(text).lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiments.append('Positif')
        elif neg_count > pos_count:
            sentiments.append('Négatif')
        else:
            sentiments.append('Neutre')

    return sentiments


def analyze_comment_stats(df, text_column='commentaire'):
    """
    Analyse statistique des commentaires
    """
    try:
        # Compter les commentaires remplis
        total = len(df)
        remplis = df[text_column].notna().sum() if text_column in df.columns else 0

        # Calculer les métriques
        stats = {
            'total': total,
            'remplis': remplis,
            'taux_remplissage': (remplis / total * 100) if total > 0 else 0
        }

        # Longueur moyenne des commentaires
        if remplis > 0:
            comment_lengths = df[text_column].dropna().apply(lambda x: len(str(x)))
            stats['longueur_moyenne'] = comment_lengths.mean()
            stats['longueur_max'] = comment_lengths.max()
            stats['longueur_min'] = comment_lengths.min()

            # Nombre moyen de mots
            word_counts = df[text_column].dropna().apply(lambda x: len(str(x).split()))
            stats['mots_moyens'] = word_counts.mean()
        else:
            stats['longueur_moyenne'] = 0
            stats['longueur_max'] = 0
            stats['longueur_min'] = 0
            stats['mots_moyens'] = 0

        return stats

    except Exception as e:
        print(f"Erreur dans analyze_comment_stats: {e}")
        return None


def display_comment_analysis_streamlit(df, text_column='commentaire_clean'):
    """
    Affiche l'analyse complète des commentaires dans Streamlit
    """
    # Vérifier si la colonne existe
    if text_column not in df.columns:
        st.error(f"❌ Colonne '{text_column}' non trouvée dans les données")
        st.write("Colonnes disponibles:", list(df.columns))
        return

    # Vérifier s'il y a des données
    if df[text_column].dropna().empty:
        st.warning("⚠️ Aucun commentaire à analyser")
        return

    st.markdown("---")
    st.markdown("### 💬 Analyse des Commentaires")

    # Statistiques de base
    stats = analyze_comment_stats(df, 'commentaire')

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Commentaires remplis",
                      f"{stats['remplis']}/{stats['total']}")

        with col2:
            st.metric("Taux de remplissage",
                      f"{stats['taux_remplissage']:.1f}%")

        with col3:
            st.metric("Longueur moyenne",
                      f"{stats['longueur_moyenne']:.0f} caractères")

        with col4:
            st.metric("Mots moyens",
                      f"{stats['mots_moyens']:.1f}")

    # Onglets pour différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "☁️ WordCloud",
        "📊 N-Grams",
        "📈 Fréquences",
        "🔍 Analyse Détail"
    ])

    with tab1:
        st.markdown("#### Nuage de Mots des Commentaires")

        # Options
        col_a, col_b = st.columns(2)
        with col_a:
            max_words = st.slider("Nombre max de mots", 50, 200, 100, key='wc_max_words')
        with col_b:
            color_map = st.selectbox("Couleurs",
                                     ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
                                     key='wc_colors')

        generate_wordcloud_streamlit(df, text_column=text_column, st_component=st)

    with tab2:
        st.markdown("#### Analyse des N-Grams")

        col1, col2 = st.columns(2)

        with col1:
            n_options = [("Mots uniques", 1), ("Bigrammes", 2), ("Trigrammes", 3)]
            selected_option = st.selectbox(
                "Type de n-gram",
                options=range(len(n_options)),
                format_func=lambda i: n_options[i][0],
                key='ngram_type'
            )
            n_gram_type, n_val = n_options[selected_option]

        with col2:
            top_n = st.slider("Nombre à afficher", 5, 30, 15, key='ngram_top')

        # Générer et afficher les n-grams
        ngrams_df = analyze_ngrams(df, text_column=text_column, n=n_val, top_n=top_n)

        if not ngrams_df.empty:
            plot_ngrams_streamlit(ngrams_df,
                                  title=f"Top {top_n} {n_gram_type} les plus fréquents",
                                  st_component=st)

            # Tableau détaillé
            with st.expander("📋 Voir les données détaillées"):
                st.dataframe(ngrams_df, use_container_width=True)
        else:
            st.info("⚠️ Pas assez de données pour analyser les n-grams")

    with tab3:
        st.markdown("#### Distribution des Longueurs")

        # Préparer les données si nécessaire
        if 'longueur_commentaire' not in df.columns:
            df['longueur_commentaire'] = df['commentaire'].fillna('').apply(len)

        # Histogramme
        fig = px.histogram(
            df,
            x='longueur_commentaire',
            nbins=30,
            title='Distribution de la Longueur des Commentaires',
            labels={'longueur_commentaire': 'Nombre de caractères'},
            color_discrete_sequence=['#1f77b4']
        )

        # Ajouter la moyenne
        if 'longueur_commentaire' in df.columns:
            mean_length = df['longueur_commentaire'].mean()
            fig.add_vline(x=mean_length, line_dash="dash", line_color="red",
                          annotation_text=f"Moyenne: {mean_length:.0f} caractères")

        st.plotly_chart(fig, use_container_width=True)

        # Boxplot par satisfaction
        if 'satisfaction' in df.columns and 'longueur_commentaire' in df.columns:
            fig2 = px.box(
                df,
                x='satisfaction',
                y='longueur_commentaire',
                title='Longueur des Commentaires par Niveau de Satisfaction',
                labels={'satisfaction': 'Satisfaction', 'longueur_commentaire': 'Longueur (caractères)'}
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Analyse des sentiments
        st.markdown("#### 😊 Analyse des Sentiments")
        sentiments = analyze_sentiment_simple(df, text_column=text_column)

        if sentiments:
            sentiment_counts = pd.Series(sentiments).value_counts()

            fig3 = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title='Distribution des Sentiments',
                color=sentiment_counts.index,
                color_discrete_map={
                    'Positif': 'green',
                    'Neutre': 'gray',
                    'Négatif': 'red'
                }
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.markdown("#### 🔍 Exploration des Commentaires")

        # Filtres
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            min_length = st.slider("Longueur minimum (caractères)", 0, 500, 50, key='filter_length')

        with col_filter2:
            keyword = st.text_input("Rechercher un mot-clé", "", key='filter_keyword')

        # Appliquer les filtres
        filtered_df = df.copy()

        # Filtrer par longueur
        if 'longueur_commentaire' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['longueur_commentaire'] >= min_length]

        # Filtrer par mot-clé
        if keyword:
            mask = filtered_df['commentaire'].str.contains(keyword, case=False, na=False)
            filtered_df = filtered_df[mask]

        # Afficher les commentaires filtrés
        st.write(f"**{len(filtered_df)} commentaires trouvés**")

        if len(filtered_df) > 0:
            for idx, row in filtered_df.head(10).iterrows():
                with st.expander(f"📝 Commentaire {idx + 1} - Satisfaction: {row.get('satisfaction', 'N/A')}"):
                    col_disp1, col_disp2 = st.columns([3, 1])
                    with col_disp1:
                        st.write(row['commentaire'])
                    with col_disp2:
                        if 'longueur_commentaire' in row:
                            st.metric("Longueur", f"{row['longueur_commentaire']} caractères")
                        if 'nombre_mots' in row:
                            st.metric("Mots", f"{row['nombre_mots']}")
        else:
            st.info("Aucun commentaire ne correspond aux filtres")

# Exporter les fonctions
__all__ = [
    'generate_wordcloud_streamlit',
    'analyze_ngrams',
    'plot_ngrams_streamlit',
    'analyze_sentiment_simple',
    'analyze_comment_stats',
    'display_comment_analysis_streamlit'
]