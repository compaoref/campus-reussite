import streamlit as st
import pandas as pd
import os
import re
import base64
from datetime import datetime
from database import load_users, save_user, load_quiz, save_feedback, init_database, get_db_info

st.set_page_config(
    page_title="Campus Réussite",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INITIALISATION DATABASE ---
init_database()

def get_image_base64(image_path):
    """Convertir image en base64 pour utiliser comme fond"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# --- FOND AVEC LOGO ---
logo_base64 = get_image_base64("logo.png")
if logo_base64:
    fond_css = f"""
    body {{
        background-image: linear-gradient(135deg, rgba(13, 110, 253, 0.1) 0%, rgba(2, 81, 217, 0.1) 100%), url('data:image/png;base64,{logo_base64}');
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    """
else:
    fond_css = """
    body {{
        background: linear-gradient(135deg, #f0f4ff 0%, #f8faff 100%);
    }}
    """

st.markdown(f"""
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    {fond_css}
    
    .login-page {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(13, 110, 253, 0.95) 0%, rgba(2, 81, 217, 0.95) 100%);
    }}
    
    .login-container {{
        background: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(13, 110, 253, 0.3);
        max-width: 450px;
        width: 100%;
    }}
    
    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .login-logo {{
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.3);
    }}
    
    .login-header h1 {{
        font-size: 2rem;
        color: #0f172a;
        margin-bottom: 0.3rem;
    }}
    
    .login-header p {{
        color: #6b7280;
        font-size: 0.95rem;
    }}
    
    .header {{
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 1.5rem;
        box-shadow: 0 8px 24px rgba(13, 110, 253, 0.2);
    }}
    
    .header-content {{
        max-width: 1300px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
    }}
    
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }}
    
    .logo-container {{
        width: 70px;
        height: 70px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }}
    
    .title-section h1 {{
        font-size: 1.8rem;
        margin-bottom: 0.2rem;
    }}
    
    .title-section p {{
        opacity: 0.95;
    }}
    
    .user-badge {{
        background: rgba(255, 255, 255, 0.2);
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    .main-container {{
        max-width: 1300px;
        margin: 2rem auto;
        padding: 0 1rem 2rem;
    }}
    
    .welcome-card {{
        background: white;
        padding: 2.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border-top: 4px solid #0d6efd;
    }}
    
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }}
    
    .stat-box {{
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #0d6efd;
        text-align: center;
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d6efd;
    }}
    
    .stat-label {{
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }}
    
    .quiz-container {{
        background: white;
        padding: 2rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }}
    
    .question-card {{
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #0d6efd;
    }}
    
    .question-badge {{
        display: inline-block;
        background: #0d6efd;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    
    .question-text {{
        font-size: 1.3rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1.5rem;
    }}
    
    .feedback-form {{
        background: white;
        padding: 2rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }}
    
    .profile-header {{
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }}
    
    @media (max-width: 768px) {{
        .header-content {{
            flex-direction: column;
        }}
        
        .login-container {{
            padding: 2rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# SESSION STATE
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"

def render_auth():
    """Page d'authentification"""
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-header">
        <div class="login-logo">🎓</div>
        <h1>Campus Réussite</h1>
        <p>Plateforme d'apprentissage interactive</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown("<h3 style='text-align: center; color: #0f172a; margin-bottom: 1.5rem;'>Connexion</h3>", unsafe_allow_html=True)
        
        try:
            admins = st.secrets.get("admins", {})
        except:
            admins = {}
        
        email = st.text_input("📧 Email", placeholder="votre-email@example.com", key="login_email")
        pwd = st.text_input("🔑 Mot de passe", type="password", placeholder="Votre mot de passe", key="login_pwd")
        
        if st.button("Se connecter →", use_container_width=True, type="primary"):
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
                            st.markdown('</div></div>', unsafe_allow_html=True)
                            return
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = user
                        st.rerun()
                st.error("❌ Identifiants incorrects")
    
    else:
        st.markdown("<h3 style='text-align: center; color: #0f172a; margin-bottom: 1.5rem;'>Créer un Compte</h3>", unsafe_allow_html=True)
        
        nom = st.text_input("👤 Nom", placeholder="Votre nom", key="signup_nom")
        prenom = st.text_input("👤 Prénom", placeholder="Votre prénom", key="signup_prenom")
        email = st.text_input("📧 Email", placeholder="votre-email@example.com", key="signup_email")
        username = st.text_input("👤 Username", placeholder="Nom d'utilisateur", key="signup_username")
        password = st.text_input("🔑 Mot de passe", type="password", placeholder="Minimum 6 caractères", key="signup_pwd")
        pwd_confirm = st.text_input("🔑 Confirmer", type="password", placeholder="Répétez votre mot de passe", key="signup_pwd_confirm")
        
        if st.button("S'inscrire →", use_container_width=True, type="primary"):
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

if not st.session_state.user_logged_in:
    render_auth()
else:
    user = st.session_state.current_user
    
    st.markdown(f"""
    <div class="header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-container">{'<img src=\"data:image/png;base64,' + get_image_base64('logo.png') + '\">' if os.path.exists('logo.png') else '🎓'}
                </div>
                <div class="title-section">
                    <h1>Campus Réussite</h1>
                    <p>Plateforme d'apprentissage</p>
                </div>
            </div>
            <div class="user-badge">
                👤 {user.get('prenom', '')} {user.get('nom', '')}<br>
                📧 {user.get('email', '')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
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
    
    if st.session_state.current_page == "accueil":
        st.markdown("""
        <div class="welcome-card">
            <h1>Bienvenue ! 👋</h1>
            <p>Bonjour """ + user.get('prenom', '') + """, explorez notre plateforme et améliorez vos connaissances !</p>
        </div>
        """, unsafe_allow_html=True)
        
        df_quiz = load_quiz()
        quiz_count = len(df_quiz) if isinstance(df_quiz, pd.DataFrame) and len(df_quiz) > 0 else 0
        
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
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        
        # Afficher les infos de debug
        db_info = get_db_info()
        st.write(f"📊 Infos DB - Utilisateurs: {db_info['users']} | Quiz: {db_info['quiz']} | Feedback: {db_info['feedback']}")
        
        df_quiz = load_quiz()
        st.write(f"DEBUG: Type de df_quiz: {type(df_quiz)}")
        st.write(f"DEBUG: df_quiz est vide? {df_quiz.empty if isinstance(df_quiz, pd.DataFrame) else 'N/A'}")
        st.write(f"DEBUG: len(df_quiz): {len(df_quiz) if isinstance(df_quiz, pd.DataFrame) else 'N/A'}")
        
        # Vérifier les conditions correctement
        if df_quiz is None or (isinstance(df_quiz, pd.DataFrame) and len(df_quiz) == 0):
            st.info("📋 Aucun quiz disponible pour le moment")
        else:
            try:
                categories = df_quiz['categorie'].unique().tolist()
                st.write(f"✅ Catégories trouvées: {categories}")
                
                selected_cat = st.selectbox("Sélectionner une catégorie :", categories)
                
                cat_quizzes = df_quiz[df_quiz['categorie'] == selected_cat]
                st.write(f"✅ {len(cat_quizzes)} quiz dans la catégorie '{selected_cat}'")
                
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
                        key=f"q_{i}_{idx}"
                    )
                    
                    if st.button(f"Valider Q{idx + 1}", key=f"btn_{i}_{idx}"):
                        is_correct = set(selected) == set(correct)
                        if is_correct:
                            st.success("🎯 Correct !")
                            st.balloons()
                        else:
                            st.error(f"❌ Bonnes réponses : {', '.join(correct)}")
                        st.info(f"💡 {row.get('explication', '')}")
                    
                    st.markdown("---")
            except Exception as e:
                st.error(f"Erreur: {e}")
                import traceback
                st.write(traceback.format_exc())
        
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
            <h2>💬 Nous Aider</h2>
            <p style="color: #6b7280; margin-bottom: 1.5rem;">Partagez vos suggestions</p>
        """, unsafe_allow_html=True)
        
        with st.form("feedback_form", clear_on_submit=True):
            titre = st.text_input("Titre", placeholder="Résumez votre avis")
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
                    success = save_feedback(feedback)
                    if success:
                        st.success("✅ Feedback envoyé !")
                    else:
                        st.error("❌ Erreur lors de l'envoi")
                else:
                    st.error("❌ Remplissez tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
