"""
Fonctions utilitaires de prétraitement
"""
import pandas as pd
import numpy as np


def clean_data(df):
    """Nettoie les données"""
    df_clean = df.copy()

    # Supprimer les doublons
    df_clean = df_clean.drop_duplicates()

    # Gérer les valeurs manquantes pour les critères numériques
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    return df_clean


def calculate_completion_rate(df, criteria_cols):
    """Calcule le taux de complétion pour des critères donnés"""
    if not criteria_cols:
        return 0

    # Vérifier quelles colonnes existent
    existing_cols = [col for col in criteria_cols if col in df.columns]

    if not existing_cols:
        return 0

    # Calculer le taux de complétion
    completed = df[existing_cols].notna().all(axis=1).sum()
    total = len(df)

    return (completed / total) * 100 if total > 0 else 0


def detect_outliers(df, column, threshold=3):
    """Détecte les valeurs aberrantes"""
    if column not in df.columns:
        return []

    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    outliers = df[z_scores > threshold].index.tolist()

    return outliers


def prepare_time_series(df, date_col, value_col, freq='D'):
    """Prépare une série temporelle"""
    if date_col not in df.columns or value_col not in df.columns:
        return pd.Series()

    df_temp = df.copy()
    df_temp[date_col] = pd.to_datetime(df_temp[date_col])
    df_temp = df_temp.set_index(date_col)

    # Resample selon la fréquence
    time_series = df_temp[value_col].resample(freq).mean()

    return time_series