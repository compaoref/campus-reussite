import streamlit as st
import re
from datetime import datetime
from database import db

st.set_page_config(
    page_title="Campus Réussite - Apprenant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    body { font-family: 'Segoe UI', sans-serif; }
    .main-header { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; }
    .card { background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; }
    .btn { padding: 0.7rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
    .btn-primary { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; }
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

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --- PAGE AUTHENTIFICATION ---
if not st.session_state.user_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎓 Campus Réussite")
        
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("📧 Connexion", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
        with col_signup:
            if st.button("📝 S'Inscrire", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
        
        st.divider()
        
        if st.session_state.auth_mode == "login":
            st.markdown("#### Connexion")
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email in admins and admins[email] == pwd:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email, 'is_admin': True}
                        st.rerun()
                except:
                    pass
                
                user = db.get_user_by_email(email)
                if user and user['password'] == pwd:
                    if user['status'] == 'bloqué':
                        st.error("❌ Votre compte a été bloqué")
                    else:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = user
                        st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        else:  # signup
            st.markdown("#### S'Inscrire")
            nom = st.text_input("Nom", key="signup_nom")
            prenom = st.text_input("Prénom", key="signup_prenom")
            email = st.text_input("Email", key="signup_email")
            username = st.text_input("Username", key="signup_username")
            password = st.text_input("Mot de passe", type="password", key="signup_pwd")
            pwd_confirm = st.text_input("Confirmer mot de passe", type="password", key="signup_pwd_confirm")
            
            if st.button("S'Inscrire", use_container_width=True, type="primary"):
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email):
                    st.error("❌ Email invalide")
                elif len(password) < 6:
                    st.error("❌ Minimum 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif db.get_user_by_email(email):
                    st.error("❌ Email déjà utilisé")
                elif db.add_user(nom, prenom, email, username, password):
                    st.success("✅ Compte créé ! Connectez-vous.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création")

else:  # APP LOGGUÉE
    user = st.session_state.current_user
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🎓 Campus Réussite</h1>
        <p>Bienvenue {user.get('prenom', '')} {user.get('nom', '')} | {user.get('email', '')}</p>
    </div>
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
    
    st.divider()
    
    # PAGES
    if st.session_state.current_page == "accueil":
        st.markdown(f"""
        <div class="card">
            <h2>Bienvenue {user.get('prenom', '')} ! 👋</h2>
            <p>Commencez votre apprentissage dès maintenant</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{db.get_quiz_count()}</h3>
                <p>Quiz Disponibles</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="stat-card">
                <h3>0</h3>
                <p>Complétés</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="stat-card">
                <h3>0%</h3>
                <p>Progression</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🎯 Commencer les Quiz", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.rerun()
    
    elif st.session_state.current_page == "quiz":
        st.markdown("### 🎯 Quiz Disponibles")
        
        quiz_list = db.get_all_quiz()
        if not quiz_list:
            st.info("📋 Aucun quiz disponible pour le moment")
        else:
            categories = sorted(set([q['categorie'] for q in quiz_list]))
            selected_cat = st.selectbox("Catégorie", categories)
            
            cat_quizzes = [q for q in quiz_list if q['categorie'] == selected_cat]
            
            for idx, quiz in enumerate(cat_quizzes):
                with st.container(border=True):
                    st.markdown(f"**Question {idx + 1}/{len(cat_quizzes)}**")
                    st.markdown(f"### {quiz['question']}")
                    
                    options = [quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d']]
                    correct = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                    
                    selected = st.multiselect("Réponses :", options, key=f"q_{quiz['id']}")
                    
                    if st.button(f"Valider", key=f"btn_{quiz['id']}"):
                        if set(selected) == set(correct):
                            st.success(f"✅ Correct ! {quiz['explication']}")
                            st.balloons()
                        else:
                            st.error(f"❌ Bonnes réponses : {', '.join(correct)}\n\n💡 {quiz['explication']}")
    
    elif st.session_state.current_page == "profil":
        st.markdown("### 👤 Mon Profil")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nom", user.get('nom', 'N/A'))
            st.metric("Email", user.get('email', 'N/A'))
        with col2:
            st.metric("Prénom", user.get('prenom', 'N/A'))
            st.metric("Username", user.get('username', 'N/A'))
    
    elif st.session_state.current_page == "feedback":
        st.markdown("### 💬 Envoyer un Feedback")
        
        with st.form("feedback_form"):
            titre = st.text_input("Titre")
            msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
            message = st.text_area("Message", height=150)
            
            if st.form_submit_button("Envoyer"):
                if titre and message:
                    if db.add_feedback(user['email'], titre, message, msg_type):
                        st.success("✅ Feedback enregistré !")
                    else:
                        st.error("❌ Erreur")
                else:
                    st.error("❌ Remplissez tous les champs")
