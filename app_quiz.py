import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Campus Réussite - Apprenant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé professionnel
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(13, 110, 253, 0.15);
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        flex-wrap: wrap;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        flex: 1;
    }
    
    .logo-area {
        width: 80px;
        height: 80px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .header-text h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        opacity: 0.95;
        font-size: 0.95rem;
        margin: 0;
    }
    
    .user-info {
        background: rgba(255, 255, 255, 0.15);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .user-info p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem 2rem 1rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.3s ease;
        border-left: 4px solid #0d6efd;
    }
    
    .stat-card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #0d6efd;
        margin: 0;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .quiz-container {
        background: white;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        padding: 2rem;
    }
    
    .quiz-header {
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .quiz-header h2 {
        color: #0f172a;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .quiz-progress {
        background: #f0f3f7;
        height: 8px;
        border-radius: 4px;
        margin-top: 1rem;
        overflow: hidden;
    }
    
    .quiz-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #0d6efd 0%, #0251d9 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .question-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #0d6efd;
    }
    
    .question-number {
        display: inline-block;
        background: #0d6efd;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .question-text {
        font-size: 1.2rem;
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    .options-container {
        display: grid;
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }
    
    .option-item {
        display: flex;
        gap: 1rem;
        padding: 1rem;
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
    
    .option-label {
        width: 36px;
        height: 36px;
        background: #0d6efd;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }
    
    .option-text {
        flex: 1;
        display: flex;
        align-items: center;
        color: #0f172a;
        font-weight: 500;
    }
    
    .button-group {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    }
    
    .btn-primary:hover {
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.4);
        transform: translateY(-2px);
    }
    
    .btn-secondary {
        background: #f0f3f7;
        color: #0f172a;
        border: 2px solid #e5e7eb;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        border-color: #0d6efd;
        background: #f6f8fb;
    }
    
    .result-container {
        background: #f0f3f7;
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 1rem;
        border-left: 4px solid #0d6efd;
    }
    
    .result-success {
        background: #ecfdf5;
        border-left-color: #10b981;
    }
    
    .result-success .result-title {
        color: #10b981;
    }
    
    .result-error {
        background: #fef2f2;
        border-left-color: #ef4444;
    }
    
    .result-error .result-title {
        color: #ef4444;
    }
    
    .result-title {
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .result-text {
        color: #4b5563;
        font-size: 0.95rem;
    }
    
    /* Auth Styles */
    .login-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        padding: 1rem;
    }
    
    .auth-card {
        background: white;
        padding: 2.5rem;
        border-radius: 14px;
        box-shadow: 0 12px 40px rgba(13, 110, 253, 0.2);
        max-width: 450px;
        width: 100%;
    }
    
    .auth-card h2 {
        text-align: center;
        color: #0f172a;
        margin-bottom: 0.5rem;
        font-size: 1.8rem;
    }
    
    .auth-card p {
        text-align: center;
        color: #6b7280;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
    }
    
    .form-group {
        margin-bottom: 1rem;
    }
    
    .form-group label {
        display: block;
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .form-group input {
        width: 100%;
        padding: 0.8rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 0.95rem;
        transition: border-color 0.3s ease;
    }
    
    .form-group input:focus {
        outline: none;
        border-color: #0d6efd;
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }
    
    .auth-tabs {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .auth-tab {
        padding: 0.8rem 1rem;
        background: transparent;
        border: none;
        cursor: pointer;
        font-weight: 600;
        color: #6b7280;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    
    .auth-tab.active {
        color: #0d6efd;
        border-bottom-color: #0d6efd;
    }
    
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
        }
        
        .logo-section {
            justify-content: center;
            width: 100%;
        }
        
        .header-text h1 {
            font-size: 1.5rem;
        }
        
        .quiz-container {
            padding: 1.5rem;
        }
        
        .button-group {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- FICHIER POUR STOCKER LES APPRENANTS ---
USERS_FILE = "utilisateurs_apprenants.json"

def load_users():
    """Charger les utilisateurs apprenants"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_users(users):
    """Sauvegarder les utilisateurs apprenants"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def is_valid_email(email):
    """Valider le format email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --- INITIALISATION SESSION STATE ---
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # login ou signup
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "df_quiz" not in st.session_state:
    st.session_state.df_quiz = None

# --- AUTHENTIFICATION ---
def render_auth():
    """Afficher les pages de connexion/inscription"""
    st.markdown("""
    <div class="login-container">
        <div class="auth-card">
            <h2>🎓 Campus Réussite</h2>
            <p>Plateforme d'apprentissage interactive</p>
    """, unsafe_allow_html=True)
    
    # Tabs pour login/signup
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 Connexion", use_container_width=True, key="btn_login"):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col2:
        if st.button("📝 S'inscrire", use_container_width=True, key="btn_signup"):
            st.session_state.auth_mode = "signup"
            st.rerun()
    
    st.markdown("---")
    
    users = load_users()
    
    if st.session_state.auth_mode == "login":
        st.markdown("<h3>Connexion</h3>", unsafe_allow_html=True)
        
        email_login = st.text_input("📧 Email", placeholder="votre-email@example.com", key="email_login")
        pwd_login = st.text_input("🔑 Mot de passe", type="password", placeholder="Entrez votre mot de passe", key="pwd_login")
        
        if st.button("Se connecter", use_container_width=True, type="primary"):
            # Chercher l'utilisateur
            user_found = None
            for user in users:
                if user['email'] == email_login and user['password'] == pwd_login:
                    user_found = user
                    break
            
            if user_found:
                if user_found.get('status', 'actif') == 'bloqué':
                    st.error("❌ Votre compte a été bloqué par un administrateur")
                else:
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = user_found
                    st.rerun()
            else:
                st.error("❌ Email ou mot de passe incorrect")
    
    else:  # signup
        st.markdown("<h3>Créer un Compte</h3>", unsafe_allow_html=True)
        
        nom = st.text_input("👤 Nom", placeholder="Votre nom", key="signup_nom")
        prenom = st.text_input("👤 Prénom", placeholder="Votre prénom", key="signup_prenom")
        email = st.text_input("📧 Email", placeholder="votre-email@example.com", key="signup_email")
        username = st.text_input("👤 Username", placeholder="Nom d'utilisateur (pour la connexion)", key="signup_username")
        password = st.text_input("🔑 Mot de passe", type="password", placeholder="Minimum 6 caractères", key="signup_password")
        password_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password", placeholder="Répétez votre mot de passe", key="signup_password_confirm")
        
        if st.button("S'inscrire", use_container_width=True, type="primary"):
            # Validations
            if not nom or not prenom or not email or not username or not password:
                st.error("❌ Tous les champs sont obligatoires")
            elif not is_valid_email(email):
                st.error("❌ Email invalide")
            elif len(password) < 6:
                st.error("❌ Le mot de passe doit faire minimum 6 caractères")
            elif password != password_confirm:
                st.error("❌ Les mots de passe ne correspondent pas")
            elif any(u['email'] == email for u in users):
                st.error("❌ Cet email est déjà utilisé")
            elif any(u['username'] == username for u in users):
                st.error("❌ Ce username est déjà pris")
            else:
                # Créer le nouvel utilisateur
                new_user = {
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'username': username,
                    'password': password,
                    'status': 'actif',
                    'date_creation': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                users.append(new_user)
                save_users(users)
                
                st.session_state.user_logged_in = True
                st.session_state.current_user = new_user
                st.success("✅ Compte créé avec succès!")
                st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- CHARGE LES QUIZ ---
@st.cache_data
def load_quiz_data():
    try:
        if os.path.exists("data_quizzes.csv"):
            try:
                df = pd.read_csv("data_quizzes.csv", encoding="utf-8", sep=";")
            except:
                df = pd.read_csv("data_quizzes.csv", encoding="latin1", sep=";")
            return df
    except:
        return None
    return None

# --- VÉRIFIER AUTHENTIFICATION ---
if not st.session_state.user_logged_in:
    render_auth()
else:
    # --- UTILISATEUR CONNECTÉ ---
    user = st.session_state.current_user
    
    # Header
    st.markdown(f"""
    <div class="header-container">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-area">
                    <span style="font-size: 2.5rem;">🎓</span>
                </div>
                <div class="header-text">
                    <h1>Campus Réussite</h1>
                    <p>Plateforme d'apprentissage interactive</p>
                </div>
            </div>
            <div class="user-info">
                <p><strong>👤 {user.get('nom', '')} {user.get('prenom', '')}</strong></p>
                <p><strong>📧</strong> {user.get('email', '')}</p>
                <p style="margin-top: 0.5rem; opacity: 0.9; font-size: 0.85rem;">Bonne chance ! 💪</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    df_quiz = load_quiz_data()
    
    if df_quiz is None or len(df_quiz) == 0:
        st.markdown("""
        <div class="quiz-container" style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h2 style="color: #0f172a; margin: 0.5rem 0;">Les quiz arrivent bientôt !</h2>
            <p style="color: #6b7280; margin: 0;">L'équipe pédagogique prépare du contenu intéressant pour vous.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            completed = len([v for v in st.session_state.responses.values() if v])
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{completed}</div>
                <div class="stat-label">Complétées</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            remaining = len(df_quiz) - completed
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{remaining}</div>
                <div class="stat-label">Restantes</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            if len(df_quiz) > 0:
                progress = (completed / len(df_quiz)) * 100
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{progress:.0f}%</div>
                    <div class="stat-label">Progression</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # QUIZ
        if not st.session_state.show_results:
            st.markdown("""
            <div class="quiz-container">
                <div class="quiz-header">
                    <h2>🎯 Entraînement Interactif</h2>
                    <div class="quiz-progress">
                        <div class="quiz-progress-bar" style="width: """ + 
                        str((st.session_state.current_question / len(df_quiz)) * 100) + 
                        """%"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Question actuelle
            row = df_quiz.iloc[st.session_state.current_question]
            
            st.markdown(f"""
            <div class="question-card">
                <div class="question-number">Question {st.session_state.current_question + 1} sur {len(df_quiz)}</div>
                <div class="question-text">{row['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Options
            options = [row['a'], row['b'], row['c'], row['d']]
            
            st.markdown('<div class="options-container">', unsafe_allow_html=True)
            selected_option = st.radio(
                "Choisir votre réponse :",
                options,
                key=f"q_{st.session_state.current_question}",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Boutons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.current_question > 0:
                    if st.button("⬅️ Précédente", use_container_width=True):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col2:
                if st.button("✅ Valider", use_container_width=True, type="primary"):
                    st.session_state.responses[st.session_state.current_question] = selected_option
                    
                    if selected_option == row['reponse']:
                        st.success(f"🎯 Bravo {user.get('prenom')} ! C'est correct !")
                        st.balloons()
                    else:
                        st.error(f"❌ La réponse correcte est : **{row['reponse']}**")
                        st.info(f"💡 **Explication** : {row['explication']}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.session_state.current_question < len(df_quiz) - 1:
                        if st.button("Continuer →", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("Voir les résultats finaux 🏆", use_container_width=True):
                            st.session_state.show_results = True
                            st.rerun()
            
            with col3:
                if st.session_state.current_question < len(df_quiz) - 1:
                    if st.button("Suivante ➡️", use_container_width=True):
                        st.session_state.responses[st.session_state.current_question] = selected_option
                        st.session_state.current_question += 1
                        st.rerun()
        
        else:
            # RÉSULTATS
            st.markdown("""
            <div class="quiz-container">
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3.5rem; margin-bottom: 1rem;">🏆</div>
                    <h2 style="color: #0f172a; margin: 0;">Bravo, vous avez terminé !</h2>
                    <p style="color: #6b7280; margin-top: 0.5rem;">Voici votre analyse complète</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Calcul scores
            correct_answers = 0
            for i, row in df_quiz.iterrows():
                if i in st.session_state.responses and st.session_state.responses[i] == row['reponse']:
                    correct_answers += 1
            
            score_percentage = (correct_answers / len(df_quiz)) * 100
            
            # Affichage scores
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Bonnes réponses", f"{correct_answers}/{len(df_quiz)}")
            with col2:
                st.metric("Pourcentage", f"{score_percentage:.0f}%")
            with col3:
                if score_percentage >= 80:
                    st.metric("Note", "🌟 Excellent")
                elif score_percentage >= 60:
                    st.metric("Note", "👍 Bon")
                else:
                    st.metric("Note", "💪 À améliorer")
            with col4:
                st.metric("Catégorie", "Générale")
            
            st.markdown("---")
            
            # Détails
            st.markdown("### 📋 Détail des réponses")
            
            details_data = []
            for i, row in df_quiz.iterrows():
                user_answer = st.session_state.responses.get(i, "Non répondu")
                is_correct = user_answer == row['reponse']
                details_data.append({
                    "Question": row['question'][:50] + "...",
                    "Votre réponse": user_answer,
                    "Correcte": "✅" if is_correct else "❌",
                    "Bonne réponse": row['reponse'],
                })
            
            details_df = pd.DataFrame(details_data)
            st.dataframe(details_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Boutons finaux
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Recommencer", use_container_width=True):
                    st.session_state.current_question = 0
                    st.session_state.responses = {}
                    st.session_state.show_results = False
                    st.rerun()
            
            with col2:
                if st.button("📥 Télécharger résultat", use_container_width=True):
                    csv = details_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Télécharger CSV",
                        data=csv,
                        file_name=f"resultats_quiz_{user.get('nom', '')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🚪 Déconnexion", use_container_width=True):
                    st.session_state.user_logged_in = False
                    st.session_state.current_user = None
                    st.session_state.current_question = 0
                    st.session_state.responses = {}
                    st.session_state.show_results = False
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.85rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #e5e7eb;">
        <p>© 2024 Campus Réussite — Plateforme d'apprentissage | Version 2.1</p>
    </div>
    """, unsafe_allow_html=True)
