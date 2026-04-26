# app_unified.py
"""
🎓 PLATEFORME CAMPUS RÉUSSITE - Version finale sécurisée
- Auth admin via st.secrets["admins"] (haché ou clair)
- Hashage utilisateurs PBKDF2-HMAC-SHA256
- Re-hash automatique des mots de passe en clair
- Sidebar Interface : Apprenant / Administration / DEBUG
- Séries de quiz + validation groupée
- Blocage/déblocage utilisateurs + ajout manuel quiz + import + debug
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime
import os
import traceback
import hashlib
import hmac
import secrets as _secrets

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="Campus Réussite v6 (sécurisé)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CONSTANTES ==========
DB_PATH = os.path.join(os.path.dirname(__file__), "campus.db")
PBKDF2_ITER = 200_000  # itérations PBKDF2 pour le hachage des mots de passe
HASH_PREFIX = "pbkdf2_sha256$"

# ========== UTILITAIRES DE HASH ==========
def hash_password(password: str) -> str:
    """Retourne : pbkdf2_sha256$iterations$salt_hex$derived_hex"""
    salt = _secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITER)
    return f"{HASH_PREFIX}{PBKDF2_ITER}${salt.hex()}${dk.hex()}"

def verify_password_hash(stored_hash: str, provided_password: str) -> bool:
    """Vérifie un mot de passe contre une valeur stockée (format pbkdf2_sha256$...)."""
    try:
        if not stored_hash or not isinstance(stored_hash, str):
            return False
        if not stored_hash.startswith(HASH_PREFIX):
            return False
        rest = stored_hash[len(HASH_PREFIX):]
        parts = rest.split("$")
        if len(parts) != 3:
            return False
        iterations_s, salt_hex, dk_hex = parts
        iterations = int(iterations_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
        test_dk = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(expected, test_dk)
    except Exception:
        return False

def is_hashed_password(value: str) -> bool:
    return isinstance(value, str) and value.startswith(HASH_PREFIX)

# ========== DATABASE ==========
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
            serie TEXT,
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
            serie TEXT,
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

# ========== FONCTIONS MÉTIER ==========
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def add_user(nom, prenom, email, username, password, role='apprenant'):
    try:
        hashed = hash_password(password)
        db.query(
            'INSERT INTO utilisateurs (nom, prenom, email, username, password, role, status, date_creation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (nom, prenom, email, username, hashed, role, 'actif', datetime.now().isoformat())
        )
        return True
    except Exception:
        traceback.print_exc()
        return False

def update_user_password(user_id, new_hashed_password):
    db.query('UPDATE utilisateurs SET password = ? WHERE id = ?', (new_hashed_password, user_id))

def get_user_by_email(email):
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email,))

def add_quiz(question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, serie=None):
    db.query(
        'INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, serie, date_creation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, serie, datetime.now().isoformat())
    )

def add_pending_quiz(question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file, serie=None):
    db.query(
        'INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file, serie, date_import) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file, serie, datetime.now().isoformat())
    )

def get_all_quiz():
    return db.fetch_all('SELECT * FROM quiz ORDER BY categorie, date_creation')

def get_pending_quiz():
    return db.fetch_all('SELECT * FROM quiz_pending ORDER BY date_import DESC')

def approve_pending_quiz(pending_id):
    quiz = db.fetch_one('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
    if quiz:
        add_quiz(quiz['question'], quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d'],
                quiz['reponses_correctes'], quiz['explication'], quiz['categorie'], serie=quiz.get('serie'))
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

def update_user_status(user_id, new_status):
    db.query('UPDATE utilisateurs SET status = ? WHERE id = ?', (new_status, user_id))

# ========== CSS ==========
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
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; }
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR - CHOIX INTERFACE ==========
st.sidebar.title("Interface")
interface_mode = st.sidebar.radio("Choisir", ["Apprenant", "Administration", "DEBUG"])

if interface_mode == "DEBUG":
    st.sidebar.write("DB path:")
    st.sidebar.code(DB_PATH)

# ========== AUTHENTIFICATION / ROUTING ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dashboard"

# Page de connexion / inscription
if not st.session_state.logged_in:
    if interface_mode == "Administration":
        st.markdown("<h2>Administration — Connexion</h2>", unsafe_allow_html=True)
        st.divider()
        admin_email = st.text_input("Email admin", key="admin_email")
        admin_pwd = st.text_input("Mot de passe", type="password", key="admin_pwd")
        if st.button("Se Connecter (Admin)", use_container_width=True):
            connected = False
            try:
                admins = st.secrets.get("admins", {})
            except Exception:
                admins = {}
            # lookup
            if admin_email in admins:
                stored = admins[admin_email]
                # support hashed or plaintext
                if is_hashed_password(stored):
                    if verify_password_hash(stored, admin_pwd):
                        connected = True
                else:
                    # compare secure if plaintext in secrets
                    if hmac.compare_digest(stored, admin_pwd):
                        connected = True
            if connected:
                st.session_state.logged_in = True
                st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': admin_email, 'role': 'admin'}
                st.experimental_rerun()
            else:
                st.error("❌ Identifiants admin incorrects")
    else:
        # Apprenant: login à gauche, signup à droite
        st.markdown("<h2>Apprenant — Connexion / Inscription</h2>", unsafe_allow_html=True)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Se connecter")
            email = st.text_input("Email", key="user_login_email")
            pwd = st.text_input("Mot de passe", type="password", key="user_login_pwd")
            if st.button("Se Connecter", use_container_width=True, key="login_btn"):
                user = get_user_by_email(email)
                if user:
                    stored_pwd = user.get('password', '')
                    # if hashed
                    if is_hashed_password(stored_pwd):
                        if verify_password_hash(stored_pwd, pwd):
                            if user.get('status') == 'bloqué':
                                st.error("❌ Votre compte est bloqué.")
                            else:
                                st.session_state.logged_in = True
                                st.session_state.user = user
                                st.experimental_rerun()
                        else:
                            st.error("❌ Email ou mot de passe incorrect")
                    else:
                        # legacy: plaintext stored in DB; compare and re-hash on success
                        if hmac.compare_digest(stored_pwd, pwd):
                            # re-hash and update
                            new_hash = hash_password(pwd)
                            update_user_password(user['id'], new_hash)
                            if user.get('status') == 'bloqué':
                                st.error("❌ Votre compte est bloqué.")
                            else:
                                # update the user dict to include hashed password
                                user['password'] = new_hash
                                st.session_state.logged_in = True
                                st.session_state.user = user
                                st.experimental_rerun()
                        else:
                            st.error("❌ Email ou mot de passe incorrect")
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        with col2:
            st.markdown("### S'inscrire")
            nom = st.text_input("Nom", key="signup_nom")
            prenom = st.text_input("Prénom", key="signup_prenom")
            email_s = st.text_input("Email", key="signup_email")
            username = st.text_input("Username", key="signup_username")
            password = st.text_input("Mot de passe", type="password", key="signup_pwd")
            pwd_confirm = st.text_input("Confirmer", type="password", key="signup_pwd_confirm")
            if st.button("S'Inscrire", use_container_width=True, key="signup_btn"):
                if not all([nom, prenom, email_s, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email_s):
                    st.error("❌ Email invalide")
                elif len(password) < 6:
                    st.error("❌ Min 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif get_user_by_email(email_s):
                    st.error("❌ Email déjà utilisé")
                else:
                    ok = add_user(nom, prenom, email_s, username, password)
                    if ok:
                        st.success("✅ Compte créé!")
                        st.session_state.logged_in = True
                        st.session_state.user = {'nom': nom, 'prenom': prenom, 'email': email_s, 'username': username, 'role': 'apprenant'}
                        st.experimental_rerun()
                    else:
                        st.error("❌ Erreur lors de la création du compte")

# ========== APPLICATION PRINCIPALE ==========
else:
    user = st.session_state.user
    is_admin = user.get('role') == 'admin'
    # header
    st.markdown(f"""
    <div class="header-admin">
        <h1>🎓 Campus Réussite</h1>
        <p>{'👮 Admin: ' if is_admin else '👨‍🎓 Apprenant: '} {user.get('prenom','')} {user.get('nom','')} | {user.get('email','')}</p>
    </div>
    """, unsafe_allow_html=True)

    # logout
    col1, col2, col3 = st.columns([10,1,1])
    with col3:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.experimental_rerun()

    st.divider()

    # Security: if user selected Admin in sidebar but is not admin, show message
    if interface_mode == "Administration" and not is_admin:
        st.error("Accès admin requis. Sélectionnez 'Apprenant' dans la sidebar pour accéder à la plateforme apprenant.")
        # still allow viewing limited content
    # ADMIN INTERFACE
    if is_admin and interface_mode == "Administration":
        st.markdown("### 🎛️ Administration")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dashboard"
                st.experimental_rerun()
        with col2:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
                st.experimental_rerun()
        with col3:
            if st.button("🎯 Quiz", use_container_width=True):
                st.session_state.admin_tab = "quiz"
                st.experimental_rerun()
        with col4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.experimental_rerun()
        with col5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
                st.experimental_rerun()
        with col6:
            if st.button("🔍 DEBUG", use_container_width=True):
                st.session_state.admin_tab = "debug"
                st.experimental_rerun()

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
                df = pd.DataFrame(quiz_list)[['question', 'reponses_correctes', 'categorie', 'serie']]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun quiz")

        # IMPORT
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz (CSV ; séparateur ; )")
            uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                    st.success(f"✅ {len(df)} lignes chargées")
                    st.dataframe(df, use_container_width=True, height=300)
                    if st.button("📥 Ajouter à la Révision", use_container_width=True, type="primary"):
                        count = 0
                        for _, row in df.iterrows():
                            serie = row.get('serie') if 'serie' in row.index else None
                            add_pending_quiz(row['question'], row['a'], row['b'], row['c'], row['d'],
                                           row['reponses_correctes'], row['explication'], row['categorie'], uploaded_file.name, serie=serie)
                            count += 1
                        st.success(f"✅ {count} quiz ajoutés à la révision")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

            st.divider()
            st.markdown("### ⏳ Quiz en Révision")
            pending = get_pending_quiz()
            st.write(f"**{len(pending)} quiz en attente**")
            if pending:
                for idx, q in enumerate(pending):
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"**Q{q['id']}: {q['question']}**")
                        st.markdown(f"Catégorie: {q['categorie']} | Série: {q.get('serie','-')}")
                        with st.expander("Détails"):
                            st.text(f"A) {q['option_a']}")
                            st.text(f"B) {q['option_b']}")
                            st.text(f"C) {q['option_c']}")
                            st.text(f"D) {q['option_d']}")
                            st.text(f"Réponses: {q['reponses_correctes']}")
                    with col2:
                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button("✅", key=f"accept_{idx}_{q['id']}"):
                                approve_pending_quiz(q['id'])
                                st.success("✅ Accepté")
                                st.experimental_rerun()
                        with col_r:
                            if st.button("❌", key=f"reject_{idx}_{q['id']}"):
                                reject_pending_quiz(q['id'])
                                st.info("❌ Rejeté")
                                st.experimental_rerun()
                    st.divider()

        # QUIZ - gestion + ajout manuel
        elif st.session_state.admin_tab == "quiz":
            st.markdown("### 🎯 Gestion des Quiz")
            with st.expander("➕ Ajouter un quiz manuellement"):
                q_question = st.text_area("Question", key="new_q_question")
                q_a = st.text_input("Option A", key="new_q_a")
                q_b = st.text_input("Option B", key="new_q_b")
                q_c = st.text_input("Option C", key="new_q_c")
                q_d = st.text_input("Option D", key="new_q_d")
                q_correct = st.text_input("Réponses correctes (séparées par virgule)", key="new_q_correct")
                q_exp = st.text_area("Explication", key="new_q_exp")
                q_cat = st.text_input("Catégorie", key="new_q_cat")
                q_serie = st.text_input("Série (ex: Serie A or 45-50)", key="new_q_serie")
                if st.button("Ajouter le quiz", key="add_quiz_manual"):
                    try:
                        add_quiz(q_question, q_a, q_b, q_c, q_d, q_correct, q_exp, q_cat, serie=q_serie if q_serie else None)
                        st.success("✅ Quiz ajouté")
                        st.experimental_rerun()
                    except Exception:
                        st.error("❌ Erreur lors de l'ajout")
                        traceback.print_exc()

            st.divider()
            quiz_list = get_all_quiz()
            st.write(f"**{len(quiz_list)} quiz publiés**")
            if quiz_list:
                series = sorted({q.get('serie') or "Sans série" for q in quiz_list})
                selected_series = st.selectbox("Afficher la série", ["Toutes"] + series, key="admin_series_select")
                if selected_series == "Toutes":
                    shown = quiz_list
                else:
                    targ = None if selected_series == "Sans série" else selected_series
                    shown = [q for q in quiz_list if (q.get('serie') or "Sans série") == selected_series]
                for q in shown:
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"**Q{q['id']}: {q['question']}**")
                        st.markdown(f"Catégorie: {q['categorie']} | Série: {q.get('serie','-')}")
                        with st.expander("Détails"):
                            st.text(f"A) {q['option_a']}")
                            st.text(f"B) {q['option_b']}")
                            st.text(f"C) {q['option_c']}")
                            st.text(f"D) {q['option_d']}")
                            st.text(f"Réponses: {q['reponses_correctes']}")
                    with col2:
                        if st.button("🗑️", key=f"del_{q['id']}"):
                            delete_quiz(q['id'])
                            st.success("✅ Supprimé")
                            st.experimental_rerun()
                    st.divider()
            else:
                st.info("Aucun quiz")

        # USERS - block / unblock
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
                df = pd.DataFrame(users)
                if not df.empty:
                    st.dataframe(df[['id','nom','prenom','email','role','status']], use_container_width=True, hide_index=True)
                st.divider()
                st.markdown("### Actions rapides")
                for u in users:
                    if u.get('role') != 'admin':
                        colA, colB = st.columns([5,1])
                        with colA:
                            st.write(f"{u['prenom']} {u['nom']} — {u['email']} — statut: {u['status']}")
                        with colB:
                            btn_key = f"toggle_status_{u['id']}"
                            label = "Débloquer" if u['status']=='bloqué' else "Bloquer"
                            if st.button(label, key=btn_key):
                                new_status = 'actif' if u['status']=='bloqué' else 'bloqué'
                                update_user_status(u['id'], new_status)
                                st.success(f"✅ Utilisateur {new_status}")
                                st.experimental_rerun()
            else:
                st.info("Aucun utilisateur")

        # FEEDBACK
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback des Apprenants")
            feedback_list = get_all_feedback()
            st.write(f"**{len(feedback_list)} feedbacks**")
            if feedback_list:
                for fb in feedback_list:
                    col1, col2 = st.columns([4,1])
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
                st.markdown(f"**Apprenants: {len([u for u in get_all_users() if u['role']=='apprenant'])}**")
            with col2:
                st.markdown(f"**Feedbacks: {len(get_all_feedback())}**")
            st.divider()
            st.markdown("DB path:")
            st.code(DB_PATH)

    # LEARNER INTERFACE
    else:
        st.markdown("### 📚 Plateforme d'Apprentissage")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.current_page = "accueil"
                st.experimental_rerun()
        with col2:
            if st.button("🎯 Quiz", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.experimental_rerun()
        with col3:
            if st.button("👤 Profil", use_container_width=True):
                st.session_state.current_page = "profil"
                st.experimental_rerun()
        with col4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.current_page = "feedback"
                st.experimental_rerun()
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
                st.experimental_rerun()

        # QUIZ - par série, validation groupée
        elif st.session_state.current_page == "quiz":
            st.markdown("### 🎯 Quiz Disponibles — par Série")
            quiz_list = get_all_quiz()
            st.write(f"**Total: {len(quiz_list)} quiz**")
            if not quiz_list:
                st.info("📋 Aucun quiz pour le moment")
            else:
                series_set = sorted({q.get('serie') for q in quiz_list if q.get('serie')})  # only non-empty
                series_opts = ["Toutes"] + series_set if series_set else ["Toutes"]
                selected_serie = st.selectbox("Série", series_opts, key="learner_series_select")
                if selected_serie == "Toutes":
                    selected_quizzes = quiz_list
                else:
                    selected_quizzes = [q for q in quiz_list if (q.get('serie') or "") == selected_serie]
                st.write(f"**{len(selected_quizzes)} quiz dans cette sélection**")
                if len(selected_quizzes) == 0:
                    st.info("Aucune question dans cette série.")
                else:
                    st.markdown("Répondez à toutes les questions puis validez la série en une seule fois.")
                    for q in selected_quizzes:
                        key = f"answer_{q['id']}"
                        if key not in st.session_state:
                            st.session_state[key] = []
                        with st.container():
                            st.markdown(f"**Q{q['id']}: {q['question']}**")
                            options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
                            st.multiselect("Sélectionnez vos réponses", options, key=key)
                            st.divider()
                    # Validate button
                    if st.button("Valider la série", key=f"validate_series_{selected_serie}"):
                        unanswered = []
                        for q in selected_quizzes:
                            sel = st.session_state.get(f"answer_{q['id']}", [])
                            if not sel:
                                unanswered.append(q['id'])
                        if unanswered:
                            st.error(f"❌ Répondez à toutes les questions avant de valider. Non répondues: {len(unanswered)}")
                        else:
                            correct_count = 0
                            results = []
                            for q in selected_quizzes:
                                selected = st.session_state.get(f"answer_{q['id']}", [])
                                correct = [c.strip() for c in q['reponses_correctes'].split(',')]
                                is_correct = set([s.strip() for s in selected]) == set(correct)
                                results.append({
                                    'id': q['id'],
                                    'question': q['question'],
                                    'selected': selected,
                                    'correct': correct,
                                    'explication': q['explication'],
                                    'is_correct': is_correct
                                })
                                if is_correct:
                                    correct_count += 1
                            score_pct = int(round(100.0 * correct_count / len(selected_quizzes))) if len(selected_quizzes) > 0 else 0
                            st.session_state[f"serie_result_{selected_serie}"] = {
                                'results': results,
                                'score': score_pct,
                                'correct_count': correct_count,
                                'total': len(selected_quizzes)
                            }
                            st.success(f"✅ Série validée — Score: {score_pct}% ({correct_count}/{len(selected_quizzes)})")
                            st.experimental_rerun()
                    # show corrections if validated
                    res_key = f"serie_result_{selected_serie}"
                    if res_key in st.session_state:
                        res = st.session_state[res_key]
                        st.markdown("### Résultats et corrections")
                        st.markdown(f"Score: **{res['score']}%** — {res['correct_count']}/{res['total']} correct(s)")
                        for r in res['results']:
                            st.markdown(f"**Q{r['id']}: {r['question']}**")
                            st.markdown(f"Vos réponses: {', '.join(r['selected']) if r['selected'] else '—'}")
                            st.markdown(f"Réponse(s) correcte(s): {', '.join(r['correct'])}")
                            st.markdown(f"Explication: {r['explication']}")
                            st.divider()

        # PROFIL
        elif st.session_state.current_page == "profil":
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
