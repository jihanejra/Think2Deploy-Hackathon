"""
Configuration de l'application
"""
# config/settings.py - Configuration des utilisateurs et paramètres

# Utilisateurs autorisés avec leurs informations
USERS = {
    "rh_user": {
        "nom_complet": "Marie Dubois",
        "email": "marie.dubois@entreprise.com",
        "role": "Responsable RH",
        "profil": "RH",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    },
    "user.cdi": {
        "nom_complet": "Jean Martin",
        "email": "jean.martin@entreprise.com",
        "role": "Développeur",
        "profil": "CDI",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    },
    "user.cdd": {
        "nom_complet": "Sophie Bernard",
        "email": "sophie.bernard@entreprise.com",
        "role": "Assistant administratif",
        "profil": "CDD",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    },
    "user.stagiaire": {
        "nom_complet": "Lucas Petit",
        "email": "lucas.petit@entreprise.com",
        "role": "Stagiaire",
        "profil": "Stagiaire",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    },
    "user.iterim": {
        "nom_complet": "Lucas Alves",
        "email": "lucas.alves@entreprise.com",
        "role": "Intérimaire",
        "profil": "Intérimaire",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    },
    "user.cadre": {
        "nom_complet": "Lucas Alves",
        "email": "lucas.alves@entreprise.com",
        "role": "Cadre",
        "profil": "Cadre",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    }
    ,
    "user.noncadre": {
        "nom_complet": "Lucas Alves",
        "email": "lucas.alves@entreprise.com",
        "role": "Non-cadre",
        "profil": "Non-cadre",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    }
    ,
    "user.apprenti": {
        "nom_complet": "Lucas Alves",
        "email": "lucas.alves@entreprise.com",
        "role": "Apprenti",
        "profil": "Apprenti",
        "password_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
    }
}






# Chemins des données
DATA_PATH = "data/evaluation_formation_francais.csv"

# Colonnes du dataset
COLUMNS = {
    'formation_id': 'ID Formation',
    'type_formation': 'Type de Formation',
    'formateur_id': 'ID Formateur',
    'satisfaction': 'Satisfaction',
    'contenu': 'Contenu',
    'logistique': 'Logistique',
    'applicabilite': 'Applicabilité',
    'commentaire': 'Commentaire',
    'langue': 'Langue',
    'date': 'Date'
}

# Critères d'évaluation
EVALUATION_CRITERIA = ['satisfaction', 'contenu', 'logistique', 'applicabilite']

# Paramètres de visualisation
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}
