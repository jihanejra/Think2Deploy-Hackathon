# backend/__init__.py

# Imports des autres modules
from .nlp_preprocessing import preprocess_comments
from .analysis import display_comment_analysis_streamlit

# Imports de topic_modeling (utilisez les noms EXACTES de vos fonctions)
from .topic_modeling import (
    train_bertopic_dynamic,      # Votre fonction d'entraînement
    display_dynamic_topic_analysis,  # Votre fonction principale
    clear_bertopic_cache,        # Votre fonction de nettoyage cache
    display_topic_results,       # Votre fonction d'affichage résultats
    export_topics_csv            # Votre fonction d'export
)

# Liste des fonctions disponibles
__all__ = [
    'preprocess_comments',
    'display_comment_analysis_streamlit',
    'train_bertopic_dynamic',
    'display_dynamic_topic_analysis',
    'clear_bertopic_cache',
    'display_topic_results',
    'export_topics_csv'
]