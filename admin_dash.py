import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Campus Réussite - Admin",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    .admin-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    .admin-header h1 {
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }
    
    .main-content {
        max-width: 1300px;
        margin: 0 auto;
        padding: 0 1rem 2rem 1rem;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .card h2 {
        color: #1e293b;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 0.8rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #0d6efd;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
    }
    
    .form-group {
        margin-bottom: 1rem;
    }
    
    .form-group label {
        display: block;
        color: #1e293b;
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
    }
    
    .login-container {
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
        max-width: 400px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- FICHIERS ---
USERS_CSV = "utilisateurs.csv"
QUIZ_CSV = "data_quizzes.csv"
FEEDBACK_CSV = "feedback.csv"

def init_files():
    """Initialiser les fichiers"""
    for csv_file in [USERS_CSV, QUIZ_CSV, FEEDBACK_CSV]:
        if csv_file == QUIZ_CSV and not os.path.exists(csv_file):
            df = pd.DataFrame(columns=['question', 'a', 'b', 'c', 'd', 'reponses_correctes', 'explication', 'categorie'])
            df.to_csv(csv_file, index=False, sep=";", encoding='utf-8')
        elif csv_file == USERS_CSV and not os.path.exists(csv_file):
            df = pd.DataFrame(columns=['nom', 'prenom', 'email', 'username', 'password', 'status', 'date_creation'])
            df.to_csv(csv_file, index=False, encoding='utf-8')
        elif csv_file == FEEDBACK_CSV and not os.path.exists(csv_file):
            df = pd.DataFrame(columns=['email', 'titre', 'message', 'type', 'date'])
            df.to_csv(csv_file, index=False, encoding='utf-8')

def load_quiz():
    """Charger les quiz"""
    init_files()
    try:
        df = pd.read_csv(QUIZ_CSV, sep=";", encoding='utf-8')
        return df if len(df) > 0 else None
    except:
        return None

def load_users():
    """Charger les apprenants"""
    init_files()
    try:
        df = pd.read_csv(USERS_CSV, encoding='utf-8')
        return df.to_dict('records') if len(df) > 0 else []
    except:
        return []

def add_quiz(question, a, b, c, d, correct, explication, categorie):
    """Ajouter un quiz"""
    init_files()
    df = pd.read_csv(QUIZ_CSV, sep=";", encoding='utf-8')
    new_row = pd.DataFrame([{
        'question': question,
        'a': a,
        'b': b,
        'c': c,
        'd': d,
        'reponses_correctes': correct,
        'explication': explication,
        'categorie': categorie
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(QUIZ_CSV, index=False, sep=";", encoding='utf-8')

def load_feedback():
    """Charger les feedbacks"""
    init_files()
    try:
        df = pd.read_csv(FEEDBACK_CSV, encoding='utf-8')
        return df if len(df) > 0 else None
    except:
        return None

# --- AUTHENTIFICATION ---
def check_auth():
    """Vérifier authentification"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center;'>🔐 Administration</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280;'>Campus Réussite</p>", unsafe_allow_html=True)
        
        email = st.text_input("Email")
        pwd = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True, type="primary"):
            try:
                admins = st.secrets.get("admins", {})
                if email in admins and admins[email] == pwd:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_email = email
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            except:
                st.error("❌ Erreur")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        return False
    return True

if not check_auth():
    st.stop()

# --- HEADER ---
st.markdown(f"""
<div class="admin-header">
    <h1>🎓 Campus Réussite - Admin</h1>
    <p>Tableau de bord administrateur</p>
    <div style="margin-top: 1rem; opacity: 0.9;">👤 {st.session_state.admin_email}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.tabs(["📊 Dashboard", "🎯 Gestion Quiz", "👥 Apprenants", "💬 Feedback", "⚙️ Paramètres"])

# --- TAB 1: DASHBOARD ---
with menu[0]:
    init_files()
    df_quiz = load_quiz()
    users = load_users()
    
    st.markdown("## 📈 Statistiques")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(users)}</div>
            <div class="stat-label">Apprenants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        quiz_count = len(df_quiz) if df_quiz is not None else 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{quiz_count}</div>
            <div class="stat-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cats = len(df_quiz['categorie'].unique()) if df_quiz is not None else 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{cats}</div>
            <div class="stat-label">Catégories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">✅</div>
            <div class="stat-label">Actif</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class="card">
        <h2>📋 Détail des Questions</h2>
    """, unsafe_allow_html=True)
    
    if df_quiz is not None and len(df_quiz) > 0:
        display_df = df_quiz[['question', 'reponses_correctes', 'explication', 'categorie']].copy()
        display_df.columns = ['Question', 'Réponses Correctes', 'Explication', 'Catégorie']
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("Aucun quiz")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: GESTION QUIZ ---
with menu[1]:
    st.markdown("## 🎯 Gestion des Quiz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Créer un Quiz Manuellement")
        
        with st.form("new_quiz_form"):
            question = st.text_input("Question")
            col_a, col_b = st.columns(2)
            with col_a:
                opt_a = st.text_input("Option A")
                opt_c = st.text_input("Option C")
            with col_b:
                opt_b = st.text_input("Option B")
                opt_d = st.text_input("Option D")
            
            st.markdown("**Sélectionner les bonnes réponses (peut en avoir plusieurs) :**")
            col_cb1, col_cb2 = st.columns(2)
            with col_cb1:
                cb_a = st.checkbox("A")
                cb_c = st.checkbox("C")
            with col_cb2:
                cb_b = st.checkbox("B")
                cb_d = st.checkbox("D")
            
            correct_answers = []
            if cb_a: correct_answers.append("A")
            if cb_b: correct_answers.append("B")
            if cb_c: correct_answers.append("C")
            if cb_d: correct_answers.append("D")
            
            explication = st.text_area("Explication")
            categorie = st.text_input("Catégorie")
            
            if st.form_submit_button("➕ Ajouter", use_container_width=True):
                if all([question, opt_a, opt_b, opt_c, opt_d, explication, categorie, correct_answers]):
                    correct_str = ", ".join(correct_answers)
                    add_quiz(question, opt_a, opt_b, opt_c, opt_d, correct_str, explication, categorie)
                    st.success("✅ Quiz ajouté !")
                else:
                    st.error("❌ Remplissez tous les champs")
    
    with col2:
        st.markdown("### 📤 Importer des Quiz (CSV)")
        
        uploaded = st.file_uploader("Choisir un CSV", type=["csv"], key="quiz_upload")
        
        if uploaded:
            try:
                df = pd.read_csv(uploaded, sep=";", encoding='utf-8')
                
                st.success("✅ Fichier chargé")
                st.dataframe(df, use_container_width=True, height=300)
                
                if st.button("🚀 Importer", use_container_width=True):
                    existing = pd.read_csv(QUIZ_CSV, sep=";", encoding='utf-8')
                    merged = pd.concat([existing, df], ignore_index=True)
                    merged.to_csv(QUIZ_CSV, index=False, sep=";", encoding='utf-8')
                    st.success("✅ Quiz importés !")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

# --- TAB 3: APPRENANTS ---
with menu[2]:
    st.markdown("## 👥 Gestion des Apprenants")
    
    users = load_users()
    
    if not users:
        st.info("Aucun apprenant")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", len(users))
        with col2:
            active = len([u for u in users if u.get('status') == 'actif'])
            st.metric("Actifs", active)
        with col3:
            blocked = len([u for u in users if u.get('status') == 'bloqué'])
            st.metric("Bloqués", blocked)
        
        st.markdown("---")
        st.markdown("### 📊 Liste")
        
        df_users = pd.DataFrame([{
            'Nom': u.get('nom'),
            'Prénom': u.get('prenom'),
            'Email': u.get('email'),
            'Status': u.get('status'),
            'Date': u.get('date_creation')
        } for u in users])
        
        st.dataframe(df_users, use_container_width=True, height=400)
        
        st.markdown("---")
        st.markdown("### ⚙️ Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_names = [f"{u['nom']} {u['prenom']}" for u in users]
            to_block = st.selectbox("Bloquer/Débloquer", user_names)
            
            if st.button("🚫 Appliquer"):
                df = pd.read_csv(USERS_CSV, encoding='utf-8')
                for idx, row in df.iterrows():
                    if f"{row['nom']} {row['prenom']}" == to_block:
                        df.at[idx, 'status'] = 'actif' if row['status'] == 'bloqué' else 'bloqué'
                        break
                df.to_csv(USERS_CSV, index=False, encoding='utf-8')
                st.success("✅ Statut changé")
                st.rerun()
        
        with col2:
            to_delete = st.selectbox("Supprimer", user_names, key="del")
            
            if st.button("🗑️ Supprimer"):
                df = pd.read_csv(USERS_CSV, encoding='utf-8')
                df = df[~((df['nom'] + ' ' + df['prenom']) == to_delete)]
                df.to_csv(USERS_CSV, index=False, encoding='utf-8')
                st.success("✅ Supprimé")
                st.rerun()
        
        st.markdown("---")
        
        csv_data = df_users.to_csv(index=False)
        st.download_button(
            "📥 Exporter (CSV)",
            csv_data,
            f"apprenants_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )

# --- TAB 4: FEEDBACK ---
with menu[3]:
    st.markdown("## 💬 Feedback des Apprenants")
    
    df_feedback = load_feedback()
    
    if df_feedback is None or len(df_feedback) == 0:
        st.info("Aucun feedback")
    else:
        for idx, row in df_feedback.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{row['titre']}**")
                    st.markdown(f"De : {row['email']}")
                    st.markdown(f"Message : {row['message']}")
                with col2:
                    st.markdown(f"**{row['type']}**")
                    st.markdown(f"__{row['date']}__")

# --- TAB 5: PARAMÈTRES ---
with menu[4]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Sécurité")
        st.info("✅ Auth via secrets.toml")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Données")
        
        if st.button("💾 Exporter Tout", use_container_width=True):
            df_users = pd.read_csv(USERS_CSV, encoding='utf-8')
            csv = df_users.to_csv(index=False)
            st.download_button(
                "Users CSV",
                csv,
                f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #e2e8f0;">
    <p>Campus Réussite Admin v3.0</p>
</div>
""", unsafe_allow_html=True)
