import streamlit as st
import pandas as pd
import os
import re
import base64
from datetime import datetime
import json

st.set_page_config(
    page_title="Campus Réussite - Apprenant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS COMPLET v3.2 ---
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* LOGIN PAGE SPECTACULAIRE */
    .login-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
        overflow: hidden;
    }
    
    .login-bg-animation {
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: 0;
    }
    
    .bubble {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        animation: float 6s infinite ease-in-out;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .login-container {
        position: relative;
        z-index: 10;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3.5rem;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.3);
        max-width: 480px;
        width: 95%;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .login-logo-section {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .login-logo-circle {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        margin: 0 auto 1.5rem;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .login-title {
        font-size: 2.2rem;
        color: #1a1a1a;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .login-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 2rem;
        background: #f0f0f0;
        border-radius: 12px;
        padding: 4px;
    }
    
    .login-tab {
        flex: 1;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        color: #666;
        border: none;
        background: transparent;
    }
    
    .login-tab.active {
        background: white;
        color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .login-form {
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
    }
    
    .form-label {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
    }
    
    .form-input {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
        font-family: inherit;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: #f8f9ff;
    }
    
    .login-button {
        padding: 1.1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
    }
    
    .login-button:active {
        transform: translateY(0);
    }
    
    .login-divider {
        text-align: center;
        margin: 1.5rem 0;
        color: #999;
        font-size: 0.9rem;
    }
    
    /* HEADER APRES CONNEXION */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .header-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .header-logo-section {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .header-logo {
        width: 80px;
        height: 80px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        backdrop-filter: blur(10px);
    }
    
    .header-text h1 {
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }
    
    .header-text p {
        opacity: 0.95;
        font-size: 0.95rem;
    }
    
    .header-user {
        background: rgba(255, 255, 255, 0.15);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-buttons {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    
    .nav-btn {
        padding: 0.8rem 1.5rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .nav-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: white;
        transform: translateY(-2px);
    }
    
    .nav-btn.active {
        background: white;
        color: #667eea;
        border-color: white;
    }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .welcome-card {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border-top: 5px solid #667eea;
    }
    
    .welcome-card h1 {
        font-size: 2.5rem;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .welcome-card p {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #666;
        font-size: 1rem;
    }
    
    .quiz-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .question-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 5px solid #667eea;
    }
    
    .question-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .question-text {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1.5rem;
    }
    
    .feedback-form {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 5px solid #28a745;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"

# --- CHEMINS DE FICHIERS ---
USERS_CSV = os.path.join(os.getcwd(), "utilisateurs.csv")
QUIZ_CSV = os.path.join(os.getcwd(), "data_quizzes.csv")
FEEDBACK_CSV = os.path.join(os.getcwd(), "feedback.csv")

def init_csv_files():
    """Créer les fichiers CSV s'ils n'existent pas"""
    try:
        if not os.path.exists(USERS_CSV):
            df = pd.DataFrame(columns=['nom', 'prenom', 'email', 'username', 'password', 'status', 'date_creation'])
            df.to_csv(USERS_CSV, index=False, encoding='utf-8')
        
        if not os.path.exists(QUIZ_CSV):
            df = pd.DataFrame(columns=['question', 'a', 'b', 'c', 'd', 'reponses_correctes', 'explication', 'categorie'])
            df.to_csv(QUIZ_CSV, index=False, sep=";", encoding='utf-8')
        
        if not os.path.exists(FEEDBACK_CSV):
            df = pd.DataFrame(columns=['email', 'titre', 'message', 'type', 'date'])
            df.to_csv(FEEDBACK_CSV, index=False, encoding='utf-8')
    except Exception as e:
        st.error(f"Erreur création fichiers : {e}")

def load_users():
    """Charger les utilisateurs"""
    init_csv_files()
    try:
        df = pd.read_csv(USERS_CSV, encoding='utf-8')
        return df.to_dict('records') if len(df) > 0 else []
    except:
        return []

def load_quiz():
    """Charger les quiz"""
    init_csv_files()
    try:
        df = pd.read_csv(QUIZ_CSV, sep=";", encoding='utf-8')
        return df if len(df) > 0 else None
    except:
        return None

def save_user(user_data):
    """SAUVEGARDER UN UTILISATEUR - VÉRIFIÉ"""
    try:
        init_csv_files()
        df = pd.read_csv(USERS_CSV, encoding='utf-8')
        new_row = pd.DataFrame([user_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(USERS_CSV, index=False, encoding='utf-8')
        
        # VÉRIFIER QUE C'EST BIEN SAUVEGARDÉ
        df_check = pd.read_csv(USERS_CSV, encoding='utf-8')
        if len(df_check) > len(df) - 1:
            return True
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde user : {e}")
        return False

def save_feedback(feedback_data):
    """SAUVEGARDER UN FEEDBACK - VÉRIFIÉ"""
    try:
        init_csv_files()
        try:
            df = pd.read_csv(FEEDBACK_CSV, encoding='utf-8')
        except:
            df = pd.DataFrame(columns=['email', 'titre', 'message', 'type', 'date'])
        
        new_row = pd.DataFrame([feedback_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FEEDBACK_CSV, index=False, encoding='utf-8')
        
        # VÉRIFIER QUE C'EST BIEN SAUVEGARDÉ
        df_check = pd.read_csv(FEEDBACK_CSV, encoding='utf-8')
        if len(df_check) > 0:
            return True
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde feedback : {e}")
        return False

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --- PAGE CONNEXION SPECTACULAIRE ---
def render_auth():
    """Page d'authentification v3.2 - Spectaculaire"""
    st.markdown("""
    <div class="login-wrapper">
        <div class="login-bg-animation">
            <div class="bubble" style="width: 300px; height: 300px; left: 10%; top: 10%;"></div>
            <div class="bubble" style="width: 200px; height: 200px; right: 10%; top: 30%; animation-delay: 2s;"></div>
            <div class="bubble" style="width: 250px; height: 250px; left: 50%; bottom: 10%; animation-delay: 4s;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo-section">
                <div class="login-logo-circle">🎓</div>
                <h1 class="login-title">Campus Réussite</h1>
                <p class="login-subtitle">Plateforme d'apprentissage interactive</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("📧 Se Connecter", use_container_width=True, key="btn_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
        with col_signup:
            if st.button("📝 S'Inscrire", use_container_width=True, key="btn_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()
        
        st.markdown("---")
        
        users = load_users()
        
        if st.session_state.auth_mode == "login":
            st.markdown("<h3 style='text-align: center; color: #667eea; margin-bottom: 1.5rem;'>Connexion</h3>", unsafe_allow_html=True)
            
            try:
                admins = st.secrets.get("admins", {})
            except:
                admins = {}
            
            email = st.text_input("📧 Email", placeholder="votre-email@example.com", key="login_email")
            pwd = st.text_input("🔑 Mot de passe", type="password", placeholder="Votre mot de passe", key="login_pwd")
            
            if st.button("→ Se Connecter", use_container_width=True, type="primary"):
                if email in admins and admins[email] == pwd:
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = {
                        'nom': 'Admin',
                        'prenom': 'Campus',
                        'email': email,
                        'is_admin': True
                    }
                    st.rerun()
                else:
                    for user in users:
                        if user['email'] == email and user['password'] == pwd:
                            if user.get('status') == 'bloqué':
                                st.error("❌ Votre compte a été bloqué")
                                return
                            st.session_state.user_logged_in = True
                            st.session_state.current_user = user
                            st.rerun()
                    st.error("❌ Email ou mot de passe incorrect")
        
        else:  # signup
            st.markdown("<h3 style='text-align: center; color: #667eea; margin-bottom: 1.5rem;'>Créer un Compte</h3>", unsafe_allow_html=True)
            
            nom = st.text_input("👤 Nom", placeholder="Votre nom", key="signup_nom")
            prenom = st.text_input("👤 Prénom", placeholder="Votre prénom", key="signup_prenom")
            email = st.text_input("📧 Email", placeholder="votre-email@example.com", key="signup_email")
            username = st.text_input("👤 Username", placeholder="Nom d'utilisateur", key="signup_username")
            password = st.text_input("🔑 Mot de passe", type="password", placeholder="Minimum 6 caractères", key="signup_pwd")
            pwd_confirm = st.text_input("🔑 Confirmer", type="password", placeholder="Répétez votre mot de passe", key="signup_pwd_confirm")
            
            if st.button("→ S'Inscrire", use_container_width=True, type="primary"):
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email):
                    st.error("❌ Email invalide")
                elif len(password) < 6:
                    st.error("❌ Minimum 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif any(u['email'] == email for u in users):
                    st.error("❌ Email déjà utilisé")
                else:
                    new_user = {
                        'nom': nom,
                        'prenom': prenom,
                        'email': email,
                        'username': username,
                        'password': password,
                        'status': 'actif',
                        'date_creation': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # SAUVEGARDER ET VÉRIFIER
                    if save_user(new_user):
                        st.success("✅ Compte créé avec succès !")
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = new_user
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la création du compte")
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# --- APP PRINCIPALE ---
if not st.session_state.user_logged_in:
    render_auth()
else:
    user = st.session_state.current_user
    
    # Header
    st.markdown(f"""
    <div class="app-header">
        <div class="header-top">
            <div class="header-logo-section">
                <div class="header-logo">🎓</div>
                <div class="header-text">
                    <h1>Campus Réussite</h1>
                    <p>Bienvenue {user.get('prenom', '')} ! 👋</p>
                </div>
            </div>
            <div class="header-user">
                <div>👤 {user.get('prenom', '')} {user.get('nom', '')}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">📧 {user.get('email', '')}</div>
            </div>
        </div>
        <div class="nav-buttons">
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.current_page = "accueil"
            st.rerun()
    with col2:
        if st.button("🎯 Quiz", use_container_width=True):
            st.session_state.current_page = "quiz"
            st.rerun()
    with col3:
        if st.button("👤 Profil", use_container_width=True):
            st.session_state.current_page = "profil"
            st.rerun()
    with col4:
        if st.button("💬 Feedback", use_container_width=True):
            st.session_state.current_page = "feedback"
            st.rerun()
    with col5:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # PAGES
    if st.session_state.current_page == "accueil":
        st.markdown(f"""
        <div class="welcome-card">
            <h1>Bienvenue {user.get('prenom', '')} ! 🎉</h1>
            <p>Découvrez nos quiz et progressez dans votre apprentissage</p>
        </div>
        """, unsafe_allow_html=True)
        
        df_quiz = load_quiz()
        quiz_count = len(df_quiz) if df_quiz is not None else 0
        
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">{quiz_count}</div>
                <div class="stat-label">Quiz Disponibles</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">0</div>
                <div class="stat-label">Quiz Complétés</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">0%</div>
                <div class="stat-label">Progression</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🎯 Commencer les Quiz →", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.rerun()
    
    elif st.session_state.current_page == "quiz":
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        df_quiz = load_quiz()
        
        if df_quiz is None or len(df_quiz) == 0:
            st.info("📋 Aucun quiz disponible pour le moment. Revenez bientôt !")
        else:
            categories = df_quiz['categorie'].unique().tolist() if 'categorie' in df_quiz.columns else []
            selected_cat = st.selectbox("📂 Sélectionner une catégorie :", categories)
            
            cat_quizzes = df_quiz[df_quiz['categorie'] == selected_cat]
            
            for idx, (i, row) in enumerate(cat_quizzes.iterrows()):
                st.markdown(f"""
                <div class="question-card">
                    <div class="question-badge">Question {idx + 1}/{len(cat_quizzes)}</div>
                    <div class="question-text">{row.get('question', 'Question')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                options = [row.get('a', ''), row.get('b', ''), row.get('c', ''), row.get('d', '')]
                correct = str(row.get('reponses_correctes', '')).split(',')
                correct = [c.strip() for c in correct]
                
                selected = st.multiselect(
                    "Choisir la/les réponse(s) :",
                    options,
                    key=f"q_{i}"
                )
                
                if st.button(f"✅ Valider Q{idx + 1}", key=f"btn_{i}"):
                    is_correct = set(selected) == set(correct)
                    if is_correct:
                        st.success("🎯 Correct ! Bien joué !")
                        st.balloons()
                    else:
                        st.error(f"❌ Bonnes réponses : {', '.join(correct)}")
                    st.info(f"💡 {row.get('explication', '')}")
                
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_page == "profil":
        st.markdown("""
        <div class="profile-header">
            <h1>👤 Mon Profil</h1>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👤 Nom", user.get('nom', 'N/A'))
            st.metric("📧 Email", user.get('email', 'N/A'))
        with col2:
            st.metric("👤 Prénom", user.get('prenom', 'N/A'))
            st.metric("📅 Inscrit depuis", user.get('date_creation', 'N/A'))
    
    elif st.session_state.current_page == "feedback":
        st.markdown("""
        <div class="feedback-form">
            <h2>💬 Nous Aider à S'Améliorer</h2>
            <p style="color: #666; margin-bottom: 1.5rem;">Partagez vos suggestions ou problèmes</p>
        """, unsafe_allow_html=True)
        
        with st.form("feedback_form"):
            titre = st.text_input("📌 Titre", placeholder="Résumez votre avis en quelques mots")
            msg_type = st.selectbox("🏷️ Type", ["💡 Suggestion", "🐛 Problème", "💬 Autre"])
            message = st.text_area("📝 Message", placeholder="Détails... (soyez constructif)", height=120)
            
            if st.form_submit_button("📤 Envoyer Feedback", use_container_width=True):
                if titre and message:
                    feedback = {
                        'email': user.get('email', ''),
                        'titre': titre,
                        'message': message,
                        'type': msg_type,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # SAUVEGARDER ET VÉRIFIER
                    if save_feedback(feedback):
                        st.success("✅ Merci ! Votre feedback a été enregistré.")
                    else:
                        st.error("❌ Erreur lors de l'enregistrement")
                else:
                    st.error("❌ Remplissez tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
