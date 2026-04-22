import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="Campus Réussite",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Campus Réussite - Plateforme d'apprentissage v3.0"}
)

# CSS Professionnel
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #f0f4ff 0%, #f8faff 100%);
    }
    
    .header {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 1.5rem;
        border-bottom: none;
        box-shadow: 0 8px 24px rgba(13, 110, 253, 0.2);
    }
    
    .header-content {
        max-width: 1300px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
    }
    
    .logo-and-title {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .logo-container {
        width: 70px;
        height: 70px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        flex-shrink: 0;
    }
    
    .logo-container img {
        width: 90%;
        height: 90%;
        object-fit: contain;
    }
    
    .title-section h1 {
        font-size: 1.8rem;
        margin-bottom: 0.2rem;
    }
    
    .title-section p {
        font-size: 0.9rem;
        opacity: 0.95;
    }
    
    .user-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        font-size: 0.9rem;
    }
    
    .main-container {
        max-width: 1300px;
        margin: 2rem auto;
        padding: 0 1rem;
    }
    
    .welcome-card {
        background: white;
        padding: 2.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border-top: 4px solid #0d6efd;
    }
    
    .welcome-card h1 {
        color: #0f172a;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .welcome-card p {
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #0d6efd;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d6efd;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .btn {
        padding: 0.9rem 1.8rem;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    }
    
    .btn-primary:hover {
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.4);
        transform: translateY(-2px);
    }
    
    .quiz-container {
        background: white;
        padding: 2rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    .question-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #0d6efd;
    }
    
    .question-badge {
        display: inline-block;
        background: #0d6efd;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1.5rem;
    }
    
    .option-item {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        background: white;
    }
    
    .option-item:hover {
        border-color: #0d6efd;
        background: #f6f8fb;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.1);
    }
    
    .option-icon {
        width: 28px;
        height: 28px;
        border: 2px solid #e5e7eb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: all 0.2s ease;
    }
    
    .option-text {
        flex: 1;
        display: flex;
        align-items: center;
        color: #0f172a;
        font-weight: 500;
    }
    
    .feedback-form {
        background: white;
        padding: 2rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-group label {
        display: block;
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .form-group input,
    .form-group textarea,
    .form-group select {
        width: 100%;
        padding: 0.8rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 0.95rem;
        transition: border-color 0.3s ease;
    }
    
    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
        outline: none;
        border-color: #0d6efd;
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }
    
    .form-group textarea {
        min-height: 150px;
        resize: vertical;
    }
    
    .login-page {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        padding: 1rem;
    }
    
    .login-card {
        background: white;
        padding: 2.5rem;
        border-radius: 14px;
        box-shadow: 0 12px 40px rgba(13, 110, 253, 0.2);
        max-width: 420px;
        width: 100%;
    }
    
    .login-card h2 {
        text-align: center;
        color: #0f172a;
        margin-bottom: 0.5rem;
        font-size: 1.8rem;
    }
    
    .login-card p {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    .profile-header {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    .result-success {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    .result-error {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
        }
        
        .logo-container {
            width: 60px;
            height: 60px;
        }
        
        .title-section h1 {
            font-size: 1.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- FICHIERS CSV ---
USERS_CSV = "utilisateurs.csv"
QUIZ_CSV = "data_quizzes.csv"
FEEDBACK_CSV = "feedback.csv"

def init_csv_files():
    """Initialiser les fichiers CSV s'ils n'existent pas"""
    if not os.path.exists(USERS_CSV):
        df = pd.DataFrame(columns=['nom', 'prenom', 'email', 'username', 'password', 'status', 'date_creation'])
        df.to_csv(USERS_CSV, index=False, encoding='utf-8')
    
    if not os.path.exists(QUIZ_CSV):
        df = pd.DataFrame(columns=['question', 'a', 'b', 'c', 'd', 'reponses_correctes', 'explication', 'categorie'])
        df.to_csv(QUIZ_CSV, index=False, sep=";", encoding='utf-8')
    
    if not os.path.exists(FEEDBACK_CSV):
        df = pd.DataFrame(columns=['email', 'titre', 'message', 'type', 'date'])
        df.to_csv(FEEDBACK_CSV, index=False, encoding='utf-8')

def load_users():
    """Charger les utilisateurs"""
    init_csv_files()
    try:
        df = pd.read_csv(USERS_CSV, encoding='utf-8')
        return df.to_dict('records')
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
    """Ajouter un utilisateur"""
    init_csv_files()
    df = pd.read_csv(USERS_CSV, encoding='utf-8')
    new_row = pd.DataFrame([user_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USERS_CSV, index=False, encoding='utf-8')

def save_feedback(feedback_data):
    """Enregistrer un feedback"""
    init_csv_files()
    df = pd.read_csv(FEEDBACK_CSV, encoding='utf-8')
    new_row = pd.DataFrame([feedback_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FEEDBACK_CSV, index=False, encoding='utf-8')

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --- HEADER ---
def render_header(user=None):
    """Afficher le header"""
    logo_html = ""
    if os.path.exists("logo.png"):
        logo_html = '<img src="data:image/png;base64,' + get_image_base64("logo.png") + '" style="width: 90%; height: 90%; object-fit: contain;">'
    else:
        logo_html = '<span style="font-size: 2.5rem;">🎓</span>'
    
    st.markdown(f"""
    <div class="header">
        <div class="header-content">
            <div class="logo-and-title">
                <div class="logo-container">
                    {logo_html}
                </div>
                <div class="title-section">
                    <h1>Campus Réussite</h1>
                    <p>Plateforme d'apprentissage interactive</p>
                </div>
            </div>
            <div class="user-badge">
                👤 {user.get('prenom', '')} {user.get('nom', '')}<br>
                📧 {user.get('email', '')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_image_base64(image_path):
    """Convertir image en base64"""
    import base64
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- INITIALISATION ---
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"
if "quiz_responses" not in st.session_state:
    st.session_state.quiz_responses = {}

# --- AUTHENTIFICATION ---
def render_auth():
    """Page d'authentification"""
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 Connexion", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col2:
        if st.button("📝 S'inscrire", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()
    
    st.markdown("---")
    
    users = load_users()
    
    if st.session_state.auth_mode == "login":
        st.markdown("<h3>Connexion</h3>", unsafe_allow_html=True)
        
        # Admin check
        try:
            admins = st.secrets.get("admins", {})
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            if st.button("Se connecter", use_container_width=True, type="primary"):
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
                                st.error("❌ Compte bloqué")
                                return
                            st.session_state.user_logged_in = True
                            st.session_state.current_user = user
                            st.rerun()
                    st.error("❌ Email ou mot de passe incorrect")
        except:
            pass
    
    else:  # signup
        st.markdown("<h3>Créer un Compte</h3>", unsafe_allow_html=True)
        
        nom = st.text_input("Nom", key="signup_nom")
        prenom = st.text_input("Prénom", key="signup_prenom")
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Mot de passe", type="password", key="signup_pwd")
        pwd_confirm = st.text_input("Confirmer", type="password", key="signup_pwd_confirm")
        
        if st.button("S'inscrire", use_container_width=True, type="primary"):
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
                save_user(new_user)
                st.session_state.user_logged_in = True
                st.session_state.current_user = new_user
                st.success("✅ Compte créé !")
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- APP PRINCIPALE ---
if not st.session_state.user_logged_in:
    render_auth()
else:
    user = st.session_state.current_user
    render_header(user)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
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
    
    st.markdown("---")
    
    # PAGES
    if st.session_state.current_page == "accueil":
        st.markdown("""
        <div class="welcome-card">
            <h1>Bienvenue ! 👋</h1>
            <p>Bonjour """ + user.get('prenom', '') + """, bienvenue sur Campus Réussite. Exercez-vous avec nos quiz et améliorez vos connaissances !</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        df_quiz = load_quiz()
        quiz_count = len(df_quiz) if df_quiz is not None else 0
        
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">""" + str(quiz_count) + """</div>
                <div class="stat-label">Quiz Disponibles</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">0</div>
                <div class="stat-label">Complétés</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">0%</div>
                <div class="stat-label">Progression</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("Commencer les Quiz 🎯", use_container_width=True, type="primary"):
                st.session_state.current_page = "quiz"
                st.rerun()
    
    elif st.session_state.current_page == "quiz":
        df_quiz = load_quiz()
        
        if df_quiz is None or len(df_quiz) == 0:
            st.markdown("""
            <div class="quiz-container" style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <h2>Aucun quiz disponible</h2>
                <p style="color: #6b7280;">L'équipe prépare du contenu intéressant...</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
            
            # Sélectionner le quiz
            quiz_titles = df_quiz['categorie'].unique().tolist()
            selected_cat = st.selectbox("Choisir une catégorie :", quiz_titles)
            
            cat_quizzes = df_quiz[df_quiz['categorie'] == selected_cat]
            
            for idx, (i, row) in enumerate(cat_quizzes.iterrows()):
                st.markdown(f"""
                <div class="question-card">
                    <div class="question-badge">Question {idx + 1}/{len(cat_quizzes)}</div>
                    <div class="question-text">{row['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Options
                options = [row['a'], row['b'], row['c'], row['d']]
                
                # Réponses correctes (peut être une chaîne ou liste)
                correct = str(row['reponses_correctes']).split(',')
                correct = [c.strip() for c in correct]
                
                selected = st.multiselect(
                    "Sélectionner la/les bonne(s) réponse(s) :",
                    options,
                    key=f"q_{i}"
                )
                
                if st.button(f"✅ Valider Q{idx + 1}", key=f"btn_{i}"):
                    is_correct = set(selected) == set(correct)
                    
                    if is_correct:
                        st.success("🎯 Correct ! Bien joué !")
                        st.balloons()
                    else:
                        st.error(f"❌ Bonne(s) réponse(s) : {', '.join(correct)}")
                    
                    st.info(f"💡 {row['explication']}")
                
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
            st.metric("Nom", user.get('nom', ''))
            st.metric("Email", user.get('email', ''))
        with col2:
            st.metric("Prénom", user.get('prenom', ''))
            st.metric("Inscrit depuis", user.get('date_creation', ''))
    
    elif st.session_state.current_page == "feedback":
        st.markdown("""
        <div class="feedback-form">
            <h2>💬 Nous Aider à S'Améliorer</h2>
            <p style="color: #6b7280; margin-bottom: 2rem;">Partagez vos suggestions ou problèmes</p>
        """, unsafe_allow_html=True)
        
        with st.form("feedback_form"):
            titre = st.text_input("Titre", placeholder="Résumez votre feedback")
            msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
            message = st.text_area("Message", placeholder="Détails...")
            
            if st.form_submit_button("Envoyer 📤", use_container_width=True):
                if titre and message:
                    feedback = {
                        'email': user.get('email', ''),
                        'titre': titre,
                        'message': message,
                        'type': msg_type,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_feedback(feedback)
                    st.success("✅ Feedback envoyé ! Merci pour votre aide.")
                else:
                    st.error("❌ Remplissez tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
