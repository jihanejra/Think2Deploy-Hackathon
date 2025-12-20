"""
Prétraitement des commentaires pour l'analyse NLP
"""
import re
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords

# Télécharger les ressources NLTK (une seule fois)
try:
    nltk.download('stopwords', quiet=True)
except:
    pass

# Liste complète des mots à exclure
MOTS_A_EXCLURE = [
    # Articles
    'le', 'la', 'les', 'l', 'un', 'une', 'des', 'du', 'de', 'au', 'aux',

    # Prépositions
    'à', 'dans', 'par', 'pour', 'sur', 'avec', 'sans', 'sous', 'chez',
    'entre', 'vers', 'depuis', 'jusque', 'pendant', 'malgré', 'durant',

    # Conjonctions
    'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'que', 'qui', 'quoi',
    'dont', 'où', 'comme', 'si', 'quand', 'lorsque', 'puisque', 'quoique',

    # Pronoms
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te',
    'se', 'y', 'en', 'ce', 'cela', 'celui', 'celle', 'ceux', 'celles',

    # Adverbes courants
    'très', 'trop', 'plus', 'moins', 'bien', 'mal', 'vite', 'lentement',
    'beaucoup', 'peu', 'assez', 'toujours', 'jamais', 'souvent', 'rarement',

    # Verbes auxiliaires/courants
    'être', 'avoir', 'faire', 'dire', 'voir', 'savoir', 'pouvoir', 'vouloir',
    'devoir', 'aller', 'venir', 'prendre', 'mettre', 'donner', 'trouver',

    # Mots génériques des évaluations
    'formation', 'formateur', 'participant', 'session', 'cours', 'stage',
    'apprentissage', 'contenu', 'programme', 'méthode', 'pédagogie',
    'aspect', 'point', 'élément', 'chose', 'fait', 'manière', 'sens'
]


def clean_text(text):
    """Nettoie le texte des commentaires"""
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # Convertir en minuscules
    text = text.lower()

    # Supprimer les espaces multiples
    text = ' '.join(text.split())

    # Supprimer les caractères spéciaux mais garder les accents
    text = re.sub(r'[^\w\sàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def preprocess_comments(df, text_column='commentaire'):
    # Dans main.py, avant d'appeler preprocess_comments
    if 'Commentaire' in df.columns:
        # Renommer la colonne
        df = df.rename(columns={'Commentaire': 'commentaire'})

    """
    
    Prétraitement complet des commentaires
    """
    df_clean = df.copy()

    # Nettoyage de base
    df_clean['commentaire_clean'] = df_clean[text_column].apply(clean_text)

    # Filtrer les commentaires trop courts
    df_clean = df_clean[df_clean['commentaire_clean'].str.len() > 10].copy()

    # Calculer la longueur
    df_clean['longueur_commentaire'] = df_clean['commentaire_clean'].apply(len)
    df_clean['nombre_mots'] = df_clean['commentaire_clean'].apply(lambda x: len(str(x).split()))

    return df_clean


def get_stopwords_french():
    """
    Récupère les stopwords français avec contournement du bug NLTK
    """
    try:
        # Essayer d'abord avec NLTK normal
        from nltk.corpus import stopwords

        # Vérifier si les données sont disponibles
        try:
            nltk.data.find('corpora/stopwords')
            stop_words = set(stopwords.words('french'))
            return stop_words
        except LookupError:
            # Télécharger si pas disponible
            import nltk
            nltk.download('stopwords')
            return set(stopwords.words('french'))

    except AttributeError as e:
        # Si bug NLTK, utiliser une liste manuelle
        print("⚠️ Bug NLTK détecté, utilisation des stopwords manuels")

        # Liste des stopwords français manuelle (top 100)
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
            'quels', 'quelle', 'quelles', 'sans', 'soi'
        }

        return french_stopwords
    except Exception as e:
        print(f"❌ Erreur avec les stopwords: {e}")
        return set()  # Retourner un set vide plutôt que de planter


def prepare_for_bertopic(df, text_column='commentaire_clean'):
    """
    Prépare les données pour BERTopic
    """
    texts = df[text_column].dropna().tolist()
    return texts


def analyze_comment_stats(df):
    """
    Analyse statistique des commentaires
    """
    stats = {}

    if 'commentaire' not in df.columns:
        return stats

    # Taux de remplissage
    stats['total'] = len(df)
    stats['remplis'] = df['commentaire'].notna().sum()
    stats['taux_remplissage'] = (stats['remplis'] / stats['total']) * 100

    # Longueur moyenne
    if 'longueur_commentaire' in df.columns:
        stats['longueur_moyenne'] = df['longueur_commentaire'].mean()
        stats['mots_moyens'] = df['nombre_mots'].mean()
    else:
        # Calculer si non présent
        df['longueur_temp'] = df['commentaire'].fillna('').apply(len)
        df['mots_temp'] = df['commentaire'].fillna('').apply(lambda x: len(str(x).split()))
        stats['longueur_moyenne'] = df['longueur_temp'].mean()
        stats['mots_moyens'] = df['mots_temp'].mean()

    return stats