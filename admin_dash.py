import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Campus Réussite - Admin",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
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
    .admin-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2rem;
        border-radius: 0;
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
    
    .header-flex p {
        opacity: 0.9;
        margin: 0;
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
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .card h2 {
        color: #1e293b;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 0.8rem;
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
        border-left: 4px solid #0d6efd;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }
    
    .stat-card.warning { border-left-color: #f59e0b; }
    .stat-card.success { border-left-color: #10b981; }
    .stat-card.danger { border-left-color: #ef4444; }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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
    
    @media (max-width: 768px) {
        .header-flex {
            flex-direction: column;
            text-align: center;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- FICHIER POUR STOCKER LES APPRENANTS ---
USERS_FILE = "utilisateurs_apprenants.json"

def load_users():
    """Charger les utilisateurs apprenants depuis le fichier JSON"""
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

# --- AUTHENTIFICATION ADMIN AVEC ST.SECRETS ---
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
            pwd_input = st.text_input("🔑 Mot de passe", type="password", placeholder="Entrez votre mot de passe", key="admin_pwd_input")
        
        if st.button("Se connecter", use_container_width=True, type="primary"):
            try:
                # Accéder aux secrets
                admins_dict = st.secrets.get("admins", {})
                
                # Vérifier si l'email existe et le mot de passe correspond
                if email_input in admins_dict:
                    if admins_dict[email_input] == pwd_input:
                        st.session_state.admin_authenticated = True
                        st.session_state.authenticated_admin_email = email_input
                        st.rerun()
                    else:
                        st.error("❌ Mot de passe incorrect")
                else:
                    st.error("❌ Adresse email non trouvée")
            except Exception as e:
                st.error("⚠️ Erreur : Vérifiez que les secrets sont configurés dans .streamlit/secrets.toml")
        
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
    
    df_quiz = load_quiz_data()
    users_data = load_users()
    
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
    
    # Quiz Details
    st.markdown("""
    <div class="card">
        <h2>📋 Détail des Questions</h2>
    """, unsafe_allow_html=True)
    
    if df_quiz is not None and len(df_quiz) > 0:
        display_df = df_quiz[['question', 'reponse', 'explication']].copy()
        display_df.columns = ['Question', 'Réponse', 'Explication']
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("📋 Aucun quiz disponible. Importer un fichier CSV.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Export button
    if df_quiz is not None and len(df_quiz) > 0:
        csv = df_quiz.to_csv(index=False, sep=";")
        st.download_button(
            label="📥 Télécharger les questions (CSV)",
            data=csv,
            file_name=f"quiz_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- TAB 2: UTILISATEURS ---
with menu[1]:
    users_data = load_users()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h2 style='color: #1e293b;'>👥 Gestion des Apprenants</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Stats apprenants
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
    
    # Table d'utilisateurs
    st.markdown("<h3>📊 Liste des Apprenants</h3>", unsafe_allow_html=True)
    
    if users_data:
        # Préparer les données pour affichage
        display_users = []
        for idx, user in enumerate(users_data):
            display_users.append({
                "ID": idx + 1,
                "Nom": user.get('nom', ''),
                "Prénom": user.get('prenom', ''),
                "Email": user.get('email', ''),
                "Username": user.get('username', ''),
                "Status": user.get('status', 'actif'),
                "Date Inscription": user.get('date_creation', '')
            })
        
        df_display = pd.DataFrame(display_users)
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
        
        # Actions sur utilisateurs
        st.markdown("---")
        st.markdown("<h3>⚙️ Gestion</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_names = [f"{u.get('nom', '')} {u.get('prenom', '')}" for u in users_data]
            user_to_block = st.selectbox(
                "Sélectionnez un apprenant pour bloquer/débloquer",
                user_names,
                key="block_select"
            )
            if st.button("🚫 Bloquer/Débloquer", use_container_width=True):
                for user in users_data:
                    if f"{user.get('nom', '')} {user.get('prenom', '')}" == user_to_block:
                        user['status'] = 'bloqué' if user.get('status', 'actif') == 'actif' else 'actif'
                        break
                save_users(users_data)
                st.success("✅ Statut mis à jour")
                st.rerun()
        
        with col2:
            user_to_delete = st.selectbox(
                "Sélectionnez un apprenant à supprimer",
                user_names,
                key="delete_select"
            )
            if st.button("🗑️ Supprimer", use_container_width=True):
                users_data = [u for u in users_data if f"{u.get('nom', '')} {u.get('prenom', '')}" != user_to_delete]
                save_users(users_data)
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
        st.info("📭 Aucun apprenant inscrit pour le moment")

# --- TAB 3: IMPORTER QUIZ ---
with menu[2]:
    st.markdown("<h2 style='color: #1e293b;'>📤 Importer des Quiz</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f0f3f7; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0d6efd;">
        <strong>📝 Format attendu :</strong><br>
        Colonnes : <code>question, a, b, c, d, reponse, explication, categorie</code><br>
        Séparateur : <code>;</code> (point-virgule)
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"], key="quiz_uploader")
    
    if uploaded_file is not None:
        try:
            df_new = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
            
            st.success("✅ Fichier chargé avec succès !")
            
            st.markdown("### Aperçu du fichier")
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
                    st.success("✅ Quiz mis à jour avec succès !")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur de lecture : {e}")

# --- TAB 4: PARAMÈTRES ---
with menu[3]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>🔐 Sécurité</h3>", unsafe_allow_html=True)
        st.info("✅ Authentification via st.secrets activée")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.authenticated_admin_email = None
            st.rerun()
    
    with col2:
        st.markdown("<h3>📊 Données</h3>", unsafe_allow_html=True)
        st.info("📂 Stockage : JSON + CSV")
        
        if st.button("💾 Exporter tout", use_container_width=True):
            # Exporter les apprenants
            users_data = load_users()
            df_users = pd.DataFrame(users_data)
            csv_users = df_users.to_csv(index=False)
            st.download_button(
                label="Télécharger utilisateurs",
                data=csv_users,
                file_name=f"utilisateurs_backup_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    st.markdown("""
    <div style="margin-top: 2rem; padding: 1.5rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #0d6efd;">
        <h4 style="margin-bottom: 0.5rem;">ℹ️ À propos</h4>
        <p style="color: #64748b; margin: 0.3rem 0;">
            <strong>Campus Réussite</strong> v2.1 (Amélioré)<br>
            Plateforme d'apprentissage interactive<br>
            © 2024 — Tous droits réservés
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #e2e8f0;">
    <p>Campus Réussite — Tableau de bord administrateur v2.1</p>
</div>
""", unsafe_allow_html=True)
