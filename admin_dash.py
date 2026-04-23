import streamlit as st
import pandas as pd
import os
from datetime import datetime
from database import (
    load_users, load_quiz, load_feedback, add_quiz, init_database,
    delete_user, toggle_user_status, clear_all_quizzes, check_quiz_exists
)

st.set_page_config(
    page_title="Campus Réussite - Admin",
    layout="wide"
)

st.markdown("""
<style>
    .admin-login {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1rem;
    }}
    
    .admin-login-card {{
        background: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        max-width: 450px;
        width: 100%;
    }}
    
    .admin-login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .admin-logo {{
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }}
    
    .admin-login-header h1 {{
        font-size: 2rem;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }}
    
    .admin-login-header p {{
        color: #6b7280;
        font-size: 0.95rem;
    }}
    
    .admin-header {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }}
    
    .admin-header h1 {{
        font-size: 2rem;
        margin: 0;
    }}
    
    .main-content {{
        max-width: 1300px;
        margin: 0 auto;
        padding: 0 1rem 2rem;
    }}
    
    .card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }}
    
    .card h2 {{
        color: #1e293b;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 0.8rem;
    }}
    
    .stat-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #0d6efd;
        text-align: center;
    }}
    
    .stat-number {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
    }}
    
    .stat-label {{
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
    }}
</style>
""", unsafe_allow_html=True)

init_database()

def check_auth():
    """Vérifier authentification"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown('<div class="admin-login">', unsafe_allow_html=True)
        st.markdown('<div class="admin-login-card">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="admin-login-header">
            <div class="admin-logo">🔐</div>
            <h1>Administration</h1>
            <p>Campus Réussite</p>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email", placeholder="admin@campus.fr")
        pwd = st.text_input("🔑 Mot de passe", type="password", placeholder="Votre mot de passe")
        
        if st.button("Se connecter →", use_container_width=True, type="primary"):
            try:
                admins = st.secrets.get("admins", {})
                if email and pwd and email in admins and admins[email] == pwd:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_email = email
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            except:
                st.error("⚠️ Erreur : Vérifiez secrets.toml")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        return False
    return True

if not check_auth():
    st.stop()

st.markdown(f"""
<div class="admin-header">
    <h1>🎓 Campus Réussite - Administration</h1>
    <p style="margin-top: 0.5rem; opacity: 0.9;">👤 {st.session_state.admin_email}</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

menu = st.tabs(["📊 Dashboard", "🎯 Gestion Quiz", "👥 Apprenants", "💬 Feedback", "⚙️ Paramètres"])

# --- TAB 1: DASHBOARD ---
with menu[0]:
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
        cats = len(df_quiz['categorie'].unique()) if df_quiz is not None and 'categorie' in df_quiz.columns else 0
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
            <div class="stat-label">En Ligne</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="card"><h2>📋 Détail des Questions</h2>', unsafe_allow_html=True)
    
    if df_quiz is not None and len(df_quiz) > 0:
        display_df = df_quiz[['question', 'reponses_correctes', 'explication', 'categorie']].copy()
        display_df.columns = ['Question', 'Réponses', 'Explication', 'Catégorie']
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("Aucun quiz")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: GESTION QUIZ ---
with menu[1]:
    st.markdown("## 🎯 Gestion des Quiz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Créer un Quiz")
        
        with st.form("new_quiz_form", clear_on_submit=True):
            question = st.text_input("Question")
            col_a, col_b = st.columns(2)
            with col_a:
                opt_a = st.text_input("Option A")
                opt_c = st.text_input("Option C")
            with col_b:
                opt_b = st.text_input("Option B")
                opt_d = st.text_input("Option D")
            
            st.markdown("**Bonnes réponses :**")
            col_cb1, col_cb2 = st.columns(2)
            with col_cb1:
                cb_a = st.checkbox("A", key="cb_a")
                cb_c = st.checkbox("C", key="cb_c")
            with col_cb2:
                cb_b = st.checkbox("B", key="cb_b")
                cb_d = st.checkbox("D", key="cb_d")
            
            explication = st.text_area("Explication")
            categorie = st.text_input("Catégorie")
            
            submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
            if submitted:
                correct_answers = []
                if cb_a: correct_answers.append("A")
                if cb_b: correct_answers.append("B")
                if cb_c: correct_answers.append("C")
                if cb_d: correct_answers.append("D")
                
                if all([question, opt_a, opt_b, opt_c, opt_d, explication, categorie, correct_answers]):
                    correct_str = ", ".join(correct_answers)
                    success = add_quiz(question, opt_a, opt_b, opt_c, opt_d, correct_str, explication, categorie)
                    if success:
                        st.success("✅ Quiz ajouté !")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'ajout")
                else:
                    st.error("❌ Remplissez tous les champs")
    
    with col2:
        st.markdown("### 📤 Importer CSV")
        
        uploaded = st.file_uploader("Choisir un CSV", type=["csv"], key="quiz_upload")
        
        if uploaded:
            try:
                df = pd.read_csv(uploaded, sep=";", encoding='utf-8')
                st.success("✅ Fichier chargé")
                st.dataframe(df, use_container_width=True, height=300)
                
                if st.button("🚀 Importer", use_container_width=True):
                    count = 0
                    for idx, row in df.iterrows():
                        success = add_quiz(
                            row.get('question', ''),
                            row.get('a', ''),
                            row.get('b', ''),
                            row.get('c', ''),
                            row.get('d', ''),
                            row.get('reponses_correctes', ''),
                            row.get('explication', ''),
                            row.get('categorie', '')
                        )
                        if success:
                            count += 1
                    st.success(f"✅ {count} quiz importés !")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

# --- TAB 3: APPRENANTS ---
with menu[2]:
    st.markdown("## 👥 Gestion des Apprenants")
    
    users = load_users()
    
    if not users:
        st.info("Aucun apprenant inscrit")
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
            user_emails = [u['email'] for u in users]
            to_toggle = st.selectbox("Bloquer/Débloquer", user_emails, key="toggle")
            
            if st.button("🔄 Appliquer", use_container_width=True):
                toggle_user_status(to_toggle)
                st.success("✅ Statut changé")
                st.rerun()
        
        with col2:
            to_delete = st.selectbox("Supprimer", user_emails, key="del")
            
            if st.button("🗑️ Supprimer", use_container_width=True):
                delete_user(to_delete)
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
            users = load_users()
            df_users = pd.DataFrame(users)
            csv = df_users.to_csv(index=False)
            st.download_button(
                "Users CSV",
                csv,
                f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

st.markdown('</div>', unsafe_allow_html=True)
