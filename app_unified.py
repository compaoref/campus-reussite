"""
🎓 CAMPUS RÉUSSITE v6.0
Application Fusionnée - Admin + Apprenant dans un seul fichier
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime
import os

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="Campus Réussite v6",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CONSTANTES ==========
DB_PATH = os.path.join(os.path.dirname(__file__), "campus.db")

# ========== DATABASE - INTÉGRÉE DANS LE FICHIER ==========
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'apprenant',
            status TEXT DEFAULT 'actif',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            reponses_correctes TEXT NOT NULL,
            explication TEXT NOT NULL,
            categorie TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_pending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            reponses_correctes TEXT NOT NULL,
            explication TEXT NOT NULL,
            categorie TEXT NOT NULL,
            source_file TEXT,
            date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            titre TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def query(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def fetch_one(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def fetch_all(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

db = Database()

# ========== CSS PERSONNALISÉ ==========
st.markdown("""
<style>
    * { font-family: 'Segoe UI', sans-serif; }
    
    .header-admin {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .header-admin h1 { margin: 0; font-size: 2.5rem; }
    .header-admin p { margin: 0.5rem 0 0; opacity: 0.95; }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .tab-button {
        padding: 0.8rem 1.5rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        background: #f0f3f7;
        color: #6b7280;
        transition: all 0.3s ease;
    }
    
    .tab-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .quiz-container {
        border: 2px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== INITIALISATION SESSION ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dashboard"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None  # None = choix rôle, "apprenant" = inscription, "admin" = connexion

# ========== FONCTIONS UTILITAIRES ==========
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def add_user(nom, prenom, email, username, password, role='apprenant'):
    try:
        db.query(
            'INSERT INTO utilisateurs (nom, prenom, email, username, password, role, status, date_creation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (nom, prenom, email, username, password, role, 'actif', datetime.now().isoformat())
        )
        return True
    except:
        return False

def get_user_by_email(email):
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email,))

def add_quiz(question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
    db.query(
        'INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie)
    )

def add_pending_quiz(question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file):
    db.query(
        'INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file)
    )

def get_all_quiz():
    return db.fetch_all('SELECT * FROM quiz ORDER BY categorie, date_creation')

def get_pending_quiz():
    return db.fetch_all('SELECT * FROM quiz_pending ORDER BY date_import DESC')

def approve_pending_quiz(pending_id):
    quiz = db.fetch_one('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
    if quiz:
        add_quiz(quiz['question'], quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d'], 
                quiz['reponses_correctes'], quiz['explication'], quiz['categorie'])
        db.query('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))

def reject_pending_quiz(pending_id):
    db.query('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))

def delete_quiz(quiz_id):
    db.query('DELETE FROM quiz WHERE id = ?', (quiz_id,))

def add_feedback(email, titre, message, type_feedback):
    db.query(
        'INSERT INTO feedback (email, titre, message, type, date_creation) VALUES (?, ?, ?, ?, ?)',
        (email, titre, message, type_feedback, datetime.now().isoformat())
    )

def get_all_feedback():
    return db.fetch_all('SELECT * FROM feedback ORDER BY date_creation DESC')

def get_all_users():
    return db.fetch_all('SELECT * FROM utilisateurs ORDER BY date_creation DESC')

# ========== PAGE AUTHENTIFICATION ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🎓 Campus Réussite</h1>
            <p style="font-size: 1.2rem; color: #6b7280; margin-top: 1rem;">Plateforme d'Apprentissage Interactive</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # === SÉLECTEUR DE RÔLE ===
        if st.session_state.auth_mode is None:
            st.markdown("### Qui êtes-vous?")
            
            col_apprenant, col_admin = st.columns(2)
            
            with col_apprenant:
                if st.button("👨‍🎓 Je suis Apprenant", use_container_width=True, type="primary"):
                    st.session_state.auth_mode = "apprenant"
                    st.rerun()
                st.markdown("_Créer un compte et suivre les cours_")
            
            with col_admin:
                if st.button("👮 Je suis Admin", use_container_width=True, type="primary"):
                    st.session_state.auth_mode = "admin"
                    st.rerun()
                st.markdown("_Se connecter au tableau de bord_")
        
        # === INSCRIPTION APPRENANT ===
        elif st.session_state.auth_mode == "apprenant":
            st.markdown("### 📝 S'Inscrire comme Apprenant")
            
            if st.button("← Retour", use_container_width=True):
                st.session_state.auth_mode = None
                st.rerun()
            
            st.divider()
            
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
                    st.error("❌ Min 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif get_user_by_email(email):
                    st.error("❌ Email déjà utilisé")
                elif add_user(nom, prenom, email, username, password):
                    st.success("✅ Compte créé!")
                    st.session_state.logged_in = True
                    st.session_state.user = {'nom': nom, 'prenom': prenom, 'email': email, 'username': username, 'role': 'apprenant'}
                    st.rerun()
                else:
                    st.error("❌ Erreur")
        
        # === CONNEXION ADMIN ===
        elif st.session_state.auth_mode == "admin":
            st.markdown("### 🔐 Connexion Admin")
            
            if st.button("← Retour", use_container_width=True):
                st.session_state.auth_mode = None
                st.rerun()
            
            st.divider()
            
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            # Identifiants de test (fallback)
            TEST_ADMINS = {
                "admin@campus.fr": "12345678",
                "test@admin.com": "password123"
            }
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                connected = False
                
                # Essayer avec secrets.toml d'abord
                try:
                    admins = st.secrets.get("admins", {})
                    if email in admins and admins[email] == pwd:
                        connected = True
                except:
                    pass
                
                # Fallback: utiliser identifiants de test
                if not connected:
                    if email in TEST_ADMINS and TEST_ADMINS[email] == pwd:
                        connected = True
                
                if connected:
                    st.session_state.logged_in = True
                    st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email, 'role': 'admin'}
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
                    st.info("💡 Identifiants de test: admin@campus.fr / 12345678")

# ========== APPLICATION PRINCIPALE ==========
else:
    user = st.session_state.user
    is_admin = user.get('role') == 'admin'
    
    # HEADER
    st.markdown(f"""
    <div class="header-admin">
        <h1>🎓 Campus Réussite v6.0</h1>
        <p>{'👮 Admin: ' if is_admin else '👨‍🎓 Apprenant: '} {user['prenom']} {user['nom']} | {user['email']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # DÉCONNEXION
    col1, col2, col3 = st.columns([10, 1, 1])
    with col3:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    st.divider()
    
    # ========== DASHBOARD ADMIN ==========
    if is_admin:
        st.markdown("### 🎛️ Administration")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dashboard"
                st.rerun()
        with col2:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
                st.rerun()
        with col3:
            if st.button("🎯 Quiz", use_container_width=True):
                st.session_state.admin_tab = "quiz"
                st.rerun()
        with col4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.rerun()
        with col5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
                st.rerun()
        with col6:
            if st.button("🔍 DEBUG", use_container_width=True):
                st.session_state.admin_tab = "debug"
                st.rerun()
        
        st.divider()
        
        # DASHBOARD
        if st.session_state.admin_tab == "dashboard":
            st.markdown("### 📊 Statistiques")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_users())}</div><div class="stat-label">Apprenants</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_quiz())}</div><div class="stat-label">Quiz Publiés</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_pending_quiz())}</div><div class="stat-label">En Révision</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_feedback())}</div><div class="stat-label">Feedbacks</div></div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 📋 Quiz Publiés")
            quiz_list = get_all_quiz()
            if quiz_list:
                df = pd.DataFrame(quiz_list)[['question', 'reponses_correctes', 'categorie']]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun quiz")
        
        # IMPORTER
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz")
            
            uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                    st.success(f"✅ {len(df)} lignes chargées")
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    if st.button("📥 Ajouter à la Révision", use_container_width=True, type="primary"):
                        count = 0
                        for _, row in df.iterrows():
                            add_pending_quiz(row['question'], row['a'], row['b'], row['c'], row['d'], 
                                           row['reponses_correctes'], row['explication'], row['categorie'], uploaded_file.name)
                            count += 1
                        st.success(f"✅ {count} quiz ajoutés à la révision")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
            
            st.divider()
            st.markdown("### ⏳ Quiz en Révision")
            
            pending = get_pending_quiz()
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
                    
                    with col2:
                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button("✅", key=f"accept_{idx}_{q['id']}", help="Accepter"):
                                approve_pending_quiz(q['id'])
                                st.success("✅ Accepté")
                                st.rerun()
                        with col_r:
                            if st.button("❌", key=f"reject_{idx}_{q['id']}", help="Rejeter"):
                                reject_pending_quiz(q['id'])
                                st.info("❌ Rejeté")
                                st.rerun()
                    st.divider()
        
        # QUIZ
        elif st.session_state.admin_tab == "quiz":
            st.markdown("### 🎯 Gestion des Quiz")
            
            quiz_list = get_all_quiz()
            st.write(f"**{len(quiz_list)} quiz publiés**")
            
            if quiz_list:
                for q in quiz_list:
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
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{q['id']}", help="Supprimer"):
                            delete_quiz(q['id'])
                            st.success("✅ Supprimé")
                            st.rerun()
                    st.divider()
            else:
                st.info("Aucun quiz")
        
        # APPRENANTS
        elif st.session_state.admin_tab == "users":
            st.markdown("### 👥 Gestion des Apprenants")
            
            users = get_all_users()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(users))
            with col2:
                st.metric("Actifs", len([u for u in users if u['status'] == 'actif']))
            with col3:
                st.metric("Bloqués", len([u for u in users if u['status'] == 'bloqué']))
            
            st.divider()
            
            if users:
                df = pd.DataFrame([u for u in users if u['role'] == 'apprenant'])
                if not df.empty:
                    st.dataframe(df[['nom', 'prenom', 'email', 'status']], use_container_width=True, hide_index=True)
            else:
                st.info("Aucun apprenant")
        
        # FEEDBACK
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback des Apprenants")
            
            feedback_list = get_all_feedback()
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
        
        # DEBUG
        elif st.session_state.admin_tab == "debug":
            st.markdown("### 🔍 DEBUG")
            st.warning("État de la base de données")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Quiz: {len(get_all_quiz())}**")
            with col2:
                st.markdown(f"**En attente: {len(get_pending_quiz())}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Apprenants: {len([u for u in get_all_users() if u['role'] == 'apprenant'])}**")
            with col2:
                st.markdown(f"**Feedbacks: {len(get_all_feedback())}**")
    
    # ========== PLATEFORME APPRENANT ==========
    else:
        st.markdown("### 📚 Plateforme d'Apprentissage")
        
        col1, col2, col3, col4 = st.columns(4)
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
        
        st.divider()
        
        # ACCUEIL
        if st.session_state.current_page == "accueil":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_quiz())}</div><div class="stat-label">Quiz Disponibles</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">0</div><div class="stat-label">Complétés</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-box"><div class="stat-number">0%</div><div class="stat-label">Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            
            if st.button("🎯 Commencer les Quiz", use_container_width=True, type="primary"):
                st.session_state.current_page = "quiz"
                st.rerun()
        
        # QUIZ
        elif st.session_state.current_page == "quiz":
            st.markdown("### 🎯 Quiz Disponibles")
            
            quiz_list = get_all_quiz()
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
                        
                        st.divider()
        
        # PROFIL
        elif st.session_state.current_page == "profil":
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
        
        # FEEDBACK
        elif st.session_state.current_page == "feedback":
            st.markdown("### 💬 Envoyer un Feedback")
            
            with st.form("feedback_form"):
                titre = st.text_input("Titre")
                msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
                message = st.text_area("Message", height=150)
                
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and message:
                        add_feedback(user['email'], titre, message, msg_type)
                        st.success("✅ Feedback enregistré!")
                    else:
                        st.error("❌ Remplissez tous les champs")
