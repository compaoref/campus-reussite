import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Campus Réussite - Admin",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
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
    
    .admin-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    .header-flex {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .header-flex h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .admin-badge {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.5);
        color: #22c55e;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .main-content {
        max-width: 1200px;
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
    
    .stat-card.warning { border-left-color: #f59e0b; }
    .stat-card.success { border-left-color: #10b981; }
    .stat-card.danger { border-left-color: #ef4444; }
    
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
    
    .login-card h2 {
        text-align: center;
        color: #1e293b;
        margin-bottom: 0.5rem;
        font-size: 1.8rem;
        border: none;
    }
    
    .login-card p {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- FICHIER APPRENANTS CSV ---
USERS_CSV = "utilisateurs.csv"

def load_users_from_csv():
    """Charger les apprenants depuis le CSV"""
    if os.path.exists(USERS_CSV):
        try:
            df = pd.read_csv(USERS_CSV, encoding='utf-8')
            return df.to_dict('records')
        except:
            return []
    return []

# --- AUTHENTIFICATION ADMIN ---
def check_admin_password():
    """Vérifier les identifiants admin depuis st.secrets"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div class="login-container">
            <div class="login-card">
                <h2>🔐 Administration</h2>
                <p>Campus Réussite — Accès Administrateur</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            email_input = st.text_input("📧 Email", placeholder="votre-email@example.com", key="admin_email_input")
        with col2:
            pwd_input = st.text_input("🔑 Mot de passe", type="password", placeholder="Votre mot de passe", key="admin_pwd_input")
        
        if st.button("Se connecter", use_container_width=True, type="primary"):
            try:
                admins_dict = st.secrets.get("admins", {})
                
                if email_input in admins_dict:
                    if admins_dict[email_input] == pwd_input:
                        st.session_state.admin_authenticated = True
                        st.session_state.authenticated_admin_email = email_input
                        st.rerun()
                    else:
                        st.error("❌ Mot de passe incorrect")
                else:
                    st.error("❌ Email non trouvé")
            except Exception as e:
                st.error("⚠️ Erreur : Vérifiez que secrets.toml est configuré")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        return False
    
    return True

# --- VÉRIFICATION AUTH ---
if not check_admin_password():
    st.stop()

# --- HEADER ---
st.markdown(f"""
<div class="admin-header">
    <div class="header-flex">
        <div>
            <h1>🎓 Campus Réussite</h1>
            <p>Tableau de bord administrateur</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="admin-badge">👤 {st.session_state.authenticated_admin_email}</div>
            <div style="text-align: right; font-size: 0.9rem;">
                <div style="color: white; font-weight: 600;">Administrateur</div>
                <div style="opacity: 0.9; font-size: 0.85rem;">Interface de gestion</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.tabs(["📊 Tableau de Bord", "👥 Utilisateurs", "📤 Importer Quiz", "⚙️ Paramètres"])

# --- TAB 1: DASHBOARD ---
with menu[0]:
    @st.cache_data(ttl=5)  # Cache 5 secondes pour synchro plus rapide
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
    
    df_quiz = load_quiz_data()
    users_data = load_users_from_csv()
    
    st.markdown("""
    <h2 style="color: #1e293b; margin-bottom: 1rem; font-size: 1.5rem;">📈 Statistiques Globales</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(users_data) if users_data else 0}</div>
            <div class="stat-label">Apprenants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        quiz_count = len(df_quiz) if df_quiz is not None else 0
        st.markdown(f"""
        <div class="stat-card warning">
            <div class="stat-number">{quiz_count}</div>
            <div class="stat-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        categories = len(df_quiz['categorie'].unique()) if df_quiz is not None and 'categorie' in df_quiz.columns else 0
        st.markdown(f"""
        <div class="stat-card success">
            <div class="stat-number">{categories}</div>
            <div class="stat-label">Catégories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card danger">
            <div class="stat-number">✅</div>
            <div class="stat-label">En Ligne</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quiz
    st.markdown("""
    <div class="card">
        <h2>📋 Détail des Questions</h2>
    """, unsafe_allow_html=True)
    
    if df_quiz is not None and len(df_quiz) > 0:
        display_df = df_quiz[['question', 'reponse', 'explication', 'categorie']].copy()
        display_df.columns = ['Question', 'Réponse', 'Explication', 'Catégorie']
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("📋 Aucun quiz. Importer un fichier CSV.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if df_quiz is not None and len(df_quiz) > 0:
        csv = df_quiz.to_csv(index=False, sep=";")
        st.download_button(
            label="📥 Télécharger questions (CSV)",
            data=csv,
            file_name=f"quiz_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- TAB 2: UTILISATEURS ---
with menu[1]:
    users_data = load_users_from_csv()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h2 style='color: #1e293b;'>👥 Gestion des Apprenants</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(users_data)}</div>
            <div class="stat-label">Total Inscrits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_users = len([u for u in users_data if u.get('status', 'actif') == 'actif'])
        st.markdown(f"""
        <div class="stat-card success">
            <div class="stat-number">{active_users}</div>
            <div class="stat-label">Actifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        blocked_users = len([u for u in users_data if u.get('status', 'actif') == 'bloqué'])
        st.markdown(f"""
        <div class="stat-card danger">
            <div class="stat-number">{blocked_users}</div>
            <div class="stat-label">Bloqués</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h3>📊 Liste des Apprenants</h3>", unsafe_allow_html=True)
    
    if users_data:
        # Tableau
        display_users = []
        for idx, user in enumerate(users_data):
            display_users.append({
                "ID": idx + 1,
                "Nom": user.get('nom', ''),
                "Prénom": user.get('prenom', ''),
                "Email": user.get('email', ''),
                "Username": user.get('username', ''),
                "Status": user.get('status', 'actif'),
                "Date": user.get('date_creation', '')
            })
        
        df_display = pd.DataFrame(display_users)
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
        
        # Actions
        st.markdown("---")
        st.markdown("<h3>⚙️ Gestion</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_names = [f"{u.get('nom', '')} {u.get('prenom', '')}" for u in users_data]
            user_to_block = st.selectbox("Bloquer/Débloquer :", user_names, key="block_select")
            if st.button("🚫 Appliquer", use_container_width=True):
                df = pd.read_csv(USERS_CSV, encoding='utf-8')
                for idx, user in enumerate(df.itertuples()):
                    if f"{user.nom} {user.prenom}" == user_to_block:
                        current_status = df.at[idx, 'status']
                        df.at[idx, 'status'] = 'actif' if current_status == 'bloqué' else 'bloqué'
                        break
                df.to_csv(USERS_CSV, index=False, encoding='utf-8')
                st.success("✅ Statut mis à jour")
                st.rerun()
        
        with col2:
            user_to_delete = st.selectbox("Supprimer :", user_names, key="delete_select")
            if st.button("🗑️ Supprimer", use_container_width=True):
                df = pd.read_csv(USERS_CSV, encoding='utf-8')
                df = df[~((df['nom'] + ' ' + df['prenom']) == user_to_delete)]
                df.to_csv(USERS_CSV, index=False, encoding='utf-8')
                st.success("✅ Apprenant supprimé")
                st.rerun()
        
        with col3:
            if st.button("📥 Exporter (CSV)", use_container_width=True):
                csv_data = df_display.to_csv(index=False)
                st.download_button(
                    label="Télécharger",
                    data=csv_data,
                    file_name=f"apprenants_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("📭 Aucun apprenant inscrit")

# --- TAB 3: IMPORTER QUIZ ---
with menu[2]:
    st.markdown("<h2 style='color: #1e293b;'>📤 Importer des Quiz</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f0f3f7; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0d6efd;">
        <strong>📝 Format :</strong><br>
        Colonnes : question, a, b, c, d, reponse, explication, categorie<br>
        Séparateur : <code>;</code>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"], key="quiz_uploader")
    
    if uploaded_file is not None:
        try:
            df_new = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
            
            st.success("✅ Fichier chargé !")
            st.markdown("### Aperçu")
            st.dataframe(df_new, use_container_width=True, height=300)
            
            st.markdown("### Statistiques")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions", len(df_new))
            with col2:
                st.metric("Colonnes", len(df_new.columns))
            with col3:
                st.metric("Valides", "✅")
            
            st.markdown("---")
            
            if st.button("🚀 Publier sur la plateforme", use_container_width=True, type="primary"):
                try:
                    df_new.to_csv("data_quizzes.csv", index=False, sep=";", encoding="utf-8")
                    # Nettoyer le cache
                    st.cache_data.clear()
                    st.success("✅ Quiz publiés !")
                    st.info("💡 Les quiz apparaissent immédiatement pour les apprenants")
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur lecture : {e}")

# --- TAB 4: PARAMÈTRES ---
with menu[3]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>🔐 Sécurité</h3>", unsafe_allow_html=True)
        st.info("✅ Authentification via st.secrets")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    with col2:
        st.markdown("<h3>📊 Données</h3>", unsafe_allow_html=True)
        st.info("📂 CSV + Secrets")
    
    st.markdown("---")
    st.markdown("""
    <div style="margin-top: 2rem; padding: 1.5rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #0d6efd;">
        <h4>ℹ️ À propos</h4>
        <p style="color: #64748b;">
            <strong>Campus Réussite</strong>Construite pour aider<br>
            Plateforme d'apprentissage interactive<br>
            © 2026 — Tous droits réservés
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #e2e8f0;">
    <p>Campus Réussite — Dashboard Admin ® Fabrice</p>
</div>
""", unsafe_allow_html=True)
