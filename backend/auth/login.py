# backend/auth/login.py - Version simple avec champs moyens
import hashlib
from datetime import datetime
import streamlit as st
import sys
import os


from config.settings import USERS


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username: str, password: str):
    if username not in USERS:
        return None

    password_hash = _hash_password(password)

    if USERS[username]["password_hash"] == password_hash:
        user_info = USERS[username].copy()
        user_info['username'] = username
        user_info['login_time'] = datetime.now()
        return user_info

    return None


def login_page(navigate_to=None):
    """Page de connexion simple avec champs de taille moyenne"""

    # Style minimal mais efficace
    st.markdown("""
    <style>
    /* Masquer le header et footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* Conteneur principal centré */
    .main-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    /* Champs de taille moyenne - 400px */
    .stTextInput > div > div > input {
        width: 100% !important;
        max-width: 300px !important;
        margin: 0 auto 15px auto !important;
        display: block !important;
    }

    /* Labels centrés */
    .stTextInput label {
        text-align: left !important;
        max-width: 300px !important;
        margin: 0 auto 5px auto !important;
        display: block !important;
    }

    /* Bouton de même largeur */
    .stButton > button {
        width: 100% !important;
        max-width: 300px !important;
        margin: 20px auto 0 auto !important;
        display: block !important;
    }

    /* Centrer le titre */
    h1, h2, h3 {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Conteneur principal
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Titre
    st.markdown("## Analyse statistique des évaluations")
    st.markdown("### Connexion au système")
    st.write("---")

    # Espacement
    st.write("")
    st.write("")

    # Formulaire
    with st.form(key='login_form'):
        # Champ username avec largeur moyenne
        username = st.text_input(
            "Nom d'utilisateur",
            placeholder="Entrez votre nom d'utilisateur",
            key="username_input"
        )

        # Champ password avec largeur moyenne
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="Entrez votre mot de passe",
            key="password_input"
        )

        # Espacement
        st.write("")

        # Bouton unique
        submitted = st.form_submit_button("Se connecter", type="primary")

    # Traitement
    if submitted:
        if username and password:
            user = authenticate(username, password)
            if user:
                st.success("✅ Connexion réussie !")
                st.session_state.authenticated = True
                st.session_state.user_info = user

                import time
                time.sleep(1.5)

                if user.get("profil") == "RH":
                    navigate_to('dashboard') if navigate_to else st.session_state.update(page='main')
                else:
                    navigate_to('dashboard') if navigate_to else st.session_state.update(page='main')
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs")

    st.markdown('</div>', unsafe_allow_html=True)  # Fermeture du conteneur




def check_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
        if st.button("Aller à la page de connexion"):
            st.session_state.page = 'login'
            st.rerun()
        st.stop()
    return True


def logout(navigate_to=None):
    """Déconnecte l'utilisateur"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    if navigate_to:
        navigate_to('login')
    else:
        st.session_state.page = 'login'
        st.rerun()