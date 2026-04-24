import streamlit as st
import re
from database import db

st.set_page_config(page_title="Campus Réussite", layout="wide")

# --- STYLE MINIMALISTE ---
st.markdown("""
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .header { background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
    .card { background: white; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# Optional debug in sidebar when environment variable DEBUG_DB=1 is set
if str(os.environ.get("DEBUG_DB", "")).strip() == "1":
    try:
        st.sidebar.info(f"DEBUG DB: {db.get_db_path()}")
        st.sidebar.info(f"DEBUG quiz_count: {db.get_quiz_count()}  | pending: {len(db.get_pending_quiz())}")
    except Exception:
        pass

# --- INITIALISATION SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "accueil"

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

# --- PAGE AUTHENTICATION ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🎓 Campus Réussite")
        
        col_l, col_s = st.columns(2)
        with col_l:
            if st.button("📧 Connexion", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        with col_s:
            if st.button("📝 S'Inscrire", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()
        
        st.divider()
        
        if st.session_state.page == "login":
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email in admins and admins[email] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email}
                        st.rerun()
                except:
                    pass
                
                user = db.get_user_by_email(email)
                if user and user['password'] == pwd:
                    if user['status'] == 'bloqué':
                        st.error("❌ Votre compte a été bloqué")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        else:  # signup
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Mot de passe", type="password")
            pwd_confirm = st.text_input("Confirmer", type="password")
            
            if st.button("S'Inscrire", use_container_width=True, type="primary"):
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email):
                    st.error("❌ Email invalide")
                elif len(password) < 6:
                    st.error("❌ Min 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif db.get_user_by_email(email):
                    st.error("❌ Email déjà utilisé")
                elif db.add_user(nom, prenom, email, username, password):
                    st.success("✅ Compte créé!")
                    st.session_state.logged_in = True
                    st.session_state.user = {'nom': nom, 'prenom': prenom, 'email': email, 'username': username}
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'inscription")

# --- APP PRINCIPALE ---
else:
    user = st.session_state.user
    
    st.markdown(f"""
    <div class="header">
        <h2 style="margin:0">🎓 Campus Réussite</h2>
        <p style="margin:0.5rem 0 0; opacity:0.9">Bienvenue {user['prenom']} {user['nom']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.page = "accueil"
            st.rerun()
    with col2:
        if st.button("🎯 Quiz", use_container_width=True):
            st.session_state.page = "quiz"
            st.rerun()
    with col3:
        if st.button("👤 Profil", use_container_width=True):
            st.session_state.page = "profil"
            st.rerun()
    with col4:
        if st.button("💬 Feedback", use_container_width=True):
            st.session_state.page = "feedback"
            st.rerun()
    with col5:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    st.divider()
    
    # === ACCUEIL ===
    if st.session_state.page == "accueil":
        st.markdown(f"""
        <div class="card">
            <h3>Bienvenue {user['prenom']} ! 👋</h3>
            <p>Commencez votre apprentissage dès maintenant</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quiz Disponibles", db.get_quiz_count())
        with col2:
            st.metric("Complétés", 0)
        with col3:
            st.metric("Progression", "0%")
        
        if st.button("🎯 Commencer les Quiz", use_container_width=True, type="primary"):
            st.session_state.page = "quiz"
            st.rerun()
    
    # === QUIZ ===
    elif st.session_state.page == "quiz":
        st.markdown("### 🎯 Quiz Disponibles")
        
        quiz_list = db.get_all_quiz()
        st.write(f"**Total: {len(quiz_list)} quiz**")
        
        if not quiz_list:
            st.info("📋 Aucun quiz pour le moment")
        else:
            categories = sorted(set([(q.get('categorie') or 'Sans catégorie') for q in quiz_list]))
            selected_cat = st.selectbox("Catégorie", categories)
            
            cat_quizzes = [q for q in quiz_list if (q.get('categorie') or 'Sans catégorie') == selected_cat]
            st.write(f"**{len(cat_quizzes)} quiz dans cette catégorie**")
            
            for idx, q in enumerate(cat_quizzes):
                with st.container():
                    st.markdown(f"**Q{idx+1}/{len(cat_quizzes)}: {q['question']}**")
                    
                    options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
                    correct = [c.strip() for c in q['reponses_correctes'].split(',')]
                    
                    selected = st.multiselect("Réponses:", options, key=f"q_{q['id']}")
                    
                    if st.button(f"Valider", key=f"btn_{q['id']}"):
                        if set(selected) == set(correct):
                            st.success(f"✅ Correct! {q['explication']}")
                            st.balloons()
                        else:
                            st.error(f"❌ Réponses: {', '.join(correct)}\n\n💡 {q['explication']}")
    
    # === PROFIL ===
    elif st.session_state.page == "profil":
        st.markdown("### 👤 Mon Profil")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nom", user['nom'])
        with col2:
            st.metric("Prénom", user['prenom'])
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Email", user['email'])
        with col2:
            st.metric("Username", user.get('username', 'N/A'))
    
    # === FEEDBACK ===
    elif st.session_state.page == "feedback":
        st.markdown("### 💬 Envoyer un Feedback")
        
        with st.form("feedback_form"):
            titre = st.text_input("Titre")
            msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
            message = st.text_area("Message", height=150)
            
            if st.form_submit_button("Envoyer", use_container_width=True):
                if titre and message:
                    if db.add_feedback(user['email'], titre, message, msg_type):
                        st.success("✅ Feedback enregistré!")
                    else:
                        st.error("❌ Erreur")
                else:
                    st.error("❌ Remplissez tous les champs")
