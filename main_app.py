
````python name=main_app.py
import streamlit as st
import pandas as pd
import re
from database import db
import traceback

st.set_page_config(page_title="Campus Réussite - Unified", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .header { background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 1.2rem; border-radius: 10px; margin-bottom: 1rem; }
    .card { background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); margin-bottom: 1rem; }
    .stat { background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 1rem; border-radius: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Sidebar: choose interface
mode = st.sidebar.selectbox("Interface", ["Apprenant", "Administration", "DEBUG"])

# --- COMMON STATE DEFAULTS ---
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "admin_email" not in st.session_state:
    st.session_state.admin_email = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page_user" not in st.session_state:
    st.session_state.page_user = "accueil"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dashboard"

# Utility: simple email validation
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

# Load secrets for admin / preusers
try:
    admins = st.secrets.get("admins", {})
    preusers = st.secrets.get("preusers", {})
    preusers_info = st.secrets.get("preusers_info", {})
except Exception:
    admins = {}
    preusers = {}
    preusers_info = {}

# --------------------------
# Administration interface
# --------------------------
def render_admin():
    st.markdown(f"""
    <div class="header">
        <h2 style="margin:0">🎓 Campus Réussite - Admin</h2>
        <p style="margin:0.5rem 0 0; opacity:0.9">Chemin DB: {db.get_db_path()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Auth
    if not st.session_state.admin_auth:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🔐 Administration")
            email = st.text_input("Email", key="admin_email_input")
            pwd = st.text_input("Mot de passe", type="password", key="admin_pwd_input")
            if st.button("Se Connecter", use_container_width=True):
                try:
                    if email in admins and admins[email] == pwd:
                        st.session_state.admin_auth = True
                        st.session_state.admin_email = email
                        st.experimental_rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
                except Exception:
                    st.error("⚠️ Erreur lors de la vérification des admins")
    else:
        # Header + logout
        st.markdown(f"<div style='margin-bottom:0.5rem'>👤 {st.session_state.admin_email}</div>", unsafe_allow_html=True)
        if st.button("🚪 Déconnexion", key="admin_logout"):
            st.session_state.admin_auth = False
            st.session_state.admin_email = ""
            st.experimental_rerun()

        st.divider()

        # Tabs
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dashboard"
        with col2:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
        with col3:
            if st.button("🎯 Quiz", use_container_width=True):
                st.session_state.admin_tab = "quiz"
        with col4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
        with col5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
        with col6:
            if st.button("🔍 DEBUG", use_container_width=True):
                st.session_state.admin_tab = "debug"

        st.divider()

        # Dashboard
        if st.session_state.admin_tab == "dashboard":
            st.markdown("### 📊 Statistiques")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_all_users())}</div><div>Apprenants</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{db.get_quiz_count()}</div><div>Quiz Publiés</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_pending_quiz())}</div><div>En Révision</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_all_feedback())}</div><div>Feedbacks</div></div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📋 Quiz Publiés (Aperçu)")
            quiz_list = db.get_all_quiz()
            st.write(f"**Total: {len(quiz_list)} quiz**")
            if quiz_list:
                df = pd.DataFrame(quiz_list)[['question', 'reponses_correctes', 'categorie']]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun quiz")

        # Gestion quiz publiés
        elif st.session_state.admin_tab == "quiz":
            st.markdown("### 🎯 Gestion des Quiz Publiés")
            quiz_list = db.get_all_quiz()
            st.write(f"**{len(quiz_list)} quiz publiés**")
            if not quiz_list:
                st.info("Aucun quiz publié")
            else:
                for q in quiz_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Q{q['id']}: {q['question']}**")
                        st.markdown(f"Catégorie: {q['categorie']}")
                        with st.expander("Détails complets"):
                            st.text(f"A) {q['option_a']}")
                            st.text(f"B) {q['option_b']}")
                            st.text(f"C) {q['option_c']}")
                            st.text(f"D) {q['option_d']}")
                            st.text(f"Réponses correctes: {q['reponses_correctes']}")
                            st.text(f"Explication: {q['explication']}")
                    with col2:
                        if st.button("🗑️", key=f"del_q_{q['id']}", help="Supprimer ce quiz"):
                            if db.delete_quiz(q['id']):
                                st.success("✅ Quiz supprimé")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Erreur lors de la suppression")
                    st.divider()

        # Import / pending / approve etc (kept similar to original)
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz")
            uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                    st.success(f"✅ {len(df)} lignes chargées")
                    st.dataframe(df, use_container_width=True, height=300)
                    if st.button("📥 Ajouter à la Révision", use_container_width=True):
                        count = 0
                        for _, row in df.iterrows():
                            try:
                                added = db.add_pending_quiz(
                                    row['question'],
                                    row['a'],
                                    row['b'],
                                    row['c'],
                                    row['d'],
                                    row['reponses_correctes'],
                                    row['explication'],
                                    row['categorie'],
                                    uploaded_file.name
                                )
                                if added:
                                    count += 1
                            except Exception:
                                # continue on row failure
                                traceback.print_exc()
                        st.success(f"✅ {count} quiz ajoutés à la révision")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

            st.divider()
            st.markdown("### ⏳ Quiz en Révision")
            pending = db.get_pending_quiz()
            st.write(f"**{len(pending)} quiz en attente**")
            if pending:
                for idx, q in enumerate(pending):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Q{q['id']}: {q['question']}**")
                        st.markdown(f"Catégorie: {q['categorie']}")
                        with st.expander("Détails"):
                            st.text(f"A) {q['option_a']}")
                            st.text(f"B) {q['option_b']}")
                            st.text(f"C) {q['option_c']}")
                            st.text(f"D) {q['option_d']}")
                            st.text(f"Réponses: {q['reponses_correctes']}")
                            st.text(f"Explication: {q['explication']}")
                        with st.expander("✏️ Modifier"):
                            question = st.text_input("Question", value=q['question'], key=f"q_{idx}_{q['id']}")
                            opt_a = st.text_input("A", value=q['option_a'], key=f"opt_a_{idx}_{q['id']}")
                            opt_b = st.text_input("B", value=q['option_b'], key=f"opt_b_{idx}_{q['id']}")
                            opt_c = st.text_input("C", value=q['option_c'], key=f"opt_c_{idx}_{q['id']}")
                            opt_d = st.text_input("D", value=q['option_d'], key=f"opt_d_{idx}_{q['id']}")
                            correct = st.text_input("Réponses", value=q['reponses_correctes'], key=f"r_{idx}_{q['id']}")
                            expl = st.text_area("Explication", value=q['explication'], key=f"e_{idx}_{q['id']}")
                            cat = st.text_input("Catégorie", value=q['categorie'], key=f"cat_{idx}_{q['id']}")
                            if st.button("Sauvegarder", key=f"save_{idx}_{q['id']}"):
                                db.update_pending_quiz(q['id'], question, opt_a, opt_b, opt_c, opt_d, correct, expl, cat)
                                st.success("✅ Modifié")
                                st.experimental_rerun()
                    with col2:
                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button("✅", key=f"accept_{idx}_{q['id']}", help="Accepter"):
                                db.approve_pending_quiz(q['id'])
                                st.success("✅ Accepté")
                                st.experimental_rerun()
                        with col_r:
                            if st.button("❌", key=f"reject_{idx}_{q['id']}", help="Rejeter"):
                                db.reject_pending_quiz(q['id'])
                                st.info("❌ Rejeté")
                                st.experimental_rerun()
                    st.divider()
            else:
                st.info("Aucun quiz en attente")

        elif st.session_state.admin_tab == "users":
            st.markdown("### 👥 Gestion des Apprenants")
            users = db.get_all_users()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(users))
            with col2:
                st.metric("Actifs", len([u for u in users if u['status'] == 'actif']))
            with col3:
                st.metric("Bloqués", len([u for u in users if u['status'] == 'bloqué']))
            st.divider()
            if users:
                df = pd.DataFrame(users)[['nom', 'prenom', 'email', 'status']]
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.divider()
                st.markdown("### Actions")
                user_names = [f"{u['prenom']} {u['nom']}" for u in users]
                col1, col2 = st.columns(2)
                with col1:
                    selected = st.selectbox("Sélectionner", user_names)
                    if st.button("🚫 Bloquer/Débloquer", use_container_width=True):
                        for u in users:
                            if f"{u['prenom']} {u['nom']}" == selected:
                                new_status = 'actif' if u['status'] == 'bloqué' else 'bloqué'
                                db.update_user_status(u['id'], new_status)
                                st.success(f"✅ {new_status}")
                                st.experimental_rerun()
                with col2:
                    selected2 = st.selectbox("Sélectionner pour supprimer", user_names, key="del")
                    if st.button("🗑️ Supprimer", use_container_width=True):
                        for u in users:
                            if f"{u['prenom']} {u['nom']}" == selected2:
                                db.delete_user(u['id'])
                                st.success("✅ Supprimé")
                                st.experimental_rerun()
            else:
                st.info("Aucun apprenant")

        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback des Apprenants")
            feedback_list = db.get_all_feedback()
            st.write(f"**{len(feedback_list)} feedbacks**")
            if feedback_list:
                for fb in feedback_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{fb['titre']}**")
                        st.markdown(f"De: {fb['email']} | Type: {fb['type']}")
                        st.markdown(f"Message: {fb['message']}")
                    with col2:
                        st.caption(fb['date_creation'])
                    st.divider()
            else:
                st.info("Aucun feedback")

        elif st.session_state.admin_tab == "debug":
            st.markdown("### 🔍 DEBUG - État de la Base de Données")
            st.warning("ℹ️ Cet écran montre l'état exact de la base de données")
            st.divider()
            st.markdown("**Chemin de la DB:**")
            st.code(db.get_db_path())
            st.divider()
            st.markdown("**Table: quiz (Quiz Publiés)**")
            quiz_list = db.get_all_quiz()
            st.write(f"Nombre de quiz: {len(quiz_list)}")
            if quiz_list:
                st.dataframe(pd.DataFrame(quiz_list), use_container_width=True)
            else:
                st.warning("❌ Aucun quiz dans la table quiz")
            st.divider()
            st.markdown("**Table: quiz_pending (Quiz en Révision)**")
            pending = db.get_pending_quiz()
            st.write(f"Nombre en attente: {len(pending)}")
            if pending:
                st.dataframe(pd.DataFrame(pending), use_container_width=True)
            else:
                st.info("Aucun quiz en attente")
            st.divider()
            st.markdown("**Table: utilisateurs (Apprenants)**")
            users = db.get_all_users()
            st.write(f"Nombre d'apprenants: {len(users)}")
            if users:
                st.dataframe(pd.DataFrame(users)[['nom', 'prenom', 'email', 'status']], use_container_width=True)
            else:
                st.warning("❌ Aucun apprenant")
            st.divider()
            st.markdown("**Table: feedback**")
            feedback_list = db.get_all_feedback()
            st.write(f"Nombre de feedbacks: {len(feedback_list)}")
            if feedback_list:
                st.dataframe(pd.DataFrame(feedback_list), use_container_width=True)
            else:
                st.info("Aucun feedback")
            st.divider()

            # === Quick DB tests (INSERT) ===
            st.markdown("### Quick DB tests")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("➕ Insert test user"):
                    ok = db.add_user("TestNom", "TestPrenom", "test+user@example.com", f"testuser{int(pd.Timestamp.now().timestamp())}", "pass1234")
                    st.write("Insert user:", ok)
            with col_b:
                if st.button("➕ Insert test quiz"):
                    ok = db.add_quiz("Q test ?", "A", "B", "C", "D", "A", "Explication", "Général")
                    st.write("Insert quiz:", ok)
            with col_c:
                if st.button("➕ Insert test feedback"):
                    ok = db.add_feedback("test+user@example.com", "Titre test", "Message test", "Suggestion")
                    st.write("Insert feedback:", ok)

            st.divider()
            st.write("Counts now:")
            st.write("Users:", len(db.get_all_users()))
            st.write("Quiz:", len(db.get_all_quiz()))
            st.write("Pending:", len(db.get_pending_quiz()))
            st.write("Feedback:", len(db.get_all_feedback()))

# --------------------------
# Apprenant interface
# --------------------------
def render_apprenant():
    # Authentication / signup
    st.markdown("""
    <div class="header">
        <h2 style="margin:0">🎓 Campus Réussite</h2>
        <p style="margin:0.3rem 0 0; opacity:0.9">Plateforme - Apprenant</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## Connexion / Inscription")
            col_l, col_s = st.columns(2)
            with col_l:
                if st.button("📧 Connexion", use_container_width=True):
                    st.session_state.page_user = "login"
                    st.experimental_rerun()
            with col_s:
                if st.button("📝 S'Inscrire", use_container_width=True):
                    st.session_state.page_user = "signup"
                    st.experimental_rerun()
            st.divider()

            if st.session_state.page_user == "login":
                email = st.text_input("Email", key="user_login_email")
                pwd = st.text_input("Mot de passe", type="password", key="user_login_pwd")
                if st.button("Se Connecter", use_container_width=True, type="primary"):
                    # Check admin from secrets first
                    try:
                        if email in admins and admins[email] == pwd:
                            st.session_state.logged_in = True
                            st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email}
                            st.experimental_rerun()
                    except Exception:
                        pass

                    # preusers from secrets
                    if email in preusers and preusers[email] == pwd:
                        info = preusers_info.get(email, {})
                        st.session_state.logged_in = True
                        st.session_state.user = {
                            'nom': info.get('nom', ''),
                            'prenom': info.get('prenom', ''),
                            'email': email,
                            'username': info.get('username', email.split('@')[0])
                        }
                        st.experimental_rerun()

                    # Normal DB users
                    user = db.get_user_by_email(email)
                    if user and user['password'] == pwd:
                        if user['status'] == 'bloqué':
                            st.error("❌ Votre compte a été bloqué")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.experimental_rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
            else:
                nom = st.text_input("Nom", key="signup_nom")
                prenom = st.text_input("Prénom", key="signup_prenom")
                email = st.text_input("Email", key="signup_email")
                username = st.text_input("Username", key="signup_username")
                password = st.text_input("Mot de passe", type="password", key="signup_pwd")
                pwd_confirm = st.text_input("Confirmer", type="password", key="signup_pwd2")
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
                    else:
                        added = db.add_user(nom, prenom, email, username, password)
                        if added:
                            st.success("✅ Compte créé!")
                            st.session_state.logged_in = True
                            st.session_state.user = {'nom': nom, 'prenom': prenom, 'email': email, 'username': username}
                            st.experimental_rerun()
                        else:
                            st.error("❌ Erreur lors de l'inscription — consultez les logs serveur")
    else:
        user = st.session_state.user
        st.markdown(f"""
        <div style="margin-bottom:0.5rem">
            Bienvenue {user.get('prenom','')} {user.get('nom','')} — {user.get('email','')}
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.page_user = "accueil"
        with col2:
            if st.button("🎯 Quiz", use_container_width=True):
                st.session_state.page_user = "quiz"
        with col3:
            if st.button("👤 Profil", use_container_width=True):
                st.session_state.page_user = "profil"
        with col4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.page_user = "feedback"
        with col5:
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.page_user = "accueil"
                st.experimental_rerun()

        st.divider()

        # Pages
        if st.session_state.page_user == "accueil":
            st.markdown(f"""
            <div class="card">
                <h3>Bienvenue {user.get('prenom','')} ! 👋</h3>
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
                st.session_state.page_user = "quiz"
                st.experimental_rerun()

        elif st.session_state.page_user == "quiz":
            st.markdown("### 🎯 Quiz Disponibles")
            quiz_list = db.get_all_quiz()
            st.write(f"**Total: {len(quiz_list)} quiz**")
            if not quiz_list:
                st.info("📋 Aucun quiz pour le moment")
            else:
                categories = sorted(set([q['categorie'] for q in quiz_list]))
                selected_cat = st.selectbox("Catégorie", categories)
                cat_quizzes = [q for q in quiz_list if q['categorie'] == selected_cat]
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

        elif st.session_state.page_user == "profil":
            st.markdown("### 👤 Mon Profil")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nom", user.get('nom'))
            with col2:
                st.metric("Prénom", user.get('prenom'))
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Email", user.get('email'))
            with col2:
                st.metric("Username", user.get('username', 'N/A'))

        elif st.session_state.page_user == "feedback":
            st.markdown("### 💬 Envoyer un Feedback")
            with st.form("feedback_form"):
                titre = st.text_input("Titre")
                msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
                message = st.text_area("Message", height=150)
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and message:
                        added = db.add_feedback(user['email'], titre, message, msg_type)
                        if added:
                            st.success("✅ Feedback enregistré!")
                        else:
                            st.error("❌ Erreur lors de l'enregistrement du feedback")
                    else:
                        st.error("❌ Remplissez tous les champs")

# --------------------------
# Router
# --------------------------
if mode == "Administration":
    render_admin()
elif mode == "Apprenant":
    render_apprenant()
else:
    st.markdown("### DEBUG Mode")
    st.code(f"DB path: {db.get_db_path()}")
    st.write("Tables overview:")
    try:
        st.write("Quiz:", len(db.get_all_quiz()))
        st.write("Pending:", len(db.get_pending_quiz()))
        st.write("Users:", len(db.get_all_users()))
        st.write("Feedback:", len(db.get_all_feedback()))
    except Exception as e:
        st.error("Erreur debug: voir logs")
        traceback.print_exc()
