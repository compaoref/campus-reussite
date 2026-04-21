import streamlit as st
import pandas as pd
import os
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
        animation: slideDown 0.6s ease-out;
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
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
    
    /* Main content */
    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem 2rem 1rem;
    }
    
    /* Card styles */
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
    
    .card h3 {
        color: #1e293b;
        font-size: 1.2rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Stats Grid */
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
    
    /* Buttons */
    .btn {
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    }
    
    .btn-primary:hover {
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.4);
        transform: translateY(-2px);
    }
    
    .btn-secondary {
        background: #f0f3f7;
        color: #1e293b;
        border: 2px solid #e2e8f0;
    }
    
    .btn-secondary:hover {
        border-color: #0d6efd;
        background: #f6f8fb;
    }
    
    .btn-danger {
        background: #ef4444;
        color: white;
    }
    
    .btn-danger:hover {
        background: #dc2626;
    }
    
    .btn-success {
        background: #10b981;
        color: white;
    }
    
    .btn-success:hover {
        background: #059669;
    }
    
    /* Form styles */
    .form-group {
        margin-bottom: 1.2rem;
    }
    
    .form-group label {
        display: block;
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .form-group input,
    .form-group textarea,
    .form-group select {
        width: 100%;
        padding: 0.8rem;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 0.95rem;
        transition: border-color 0.3s ease;
    }
    
    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
        outline: none;
        border-color: #0d6efd;
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }
    
    .form-group textarea {
        min-height: 100px;
        resize: vertical;
    }
    
    /* Table styles */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    
    .data-table th {
        background: #f8fafc;
        color: #1e293b;
        padding: 1rem;
        text-align: left;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .data-table td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid #f0f3f7;
        color: #475569;
    }
    
    .data-table tr:hover {
        background: #f8fafc;
    }
    
    /* Action buttons in table */
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .action-buttons .btn {
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
    }
    
    /* Login screen */
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
    }
    
    .login-card p {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    /* Tabs */
    .tab-container {
        margin-top: 1.5rem;
    }
    
    .tab-buttons {
        display: flex;
        gap: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .tab-btn {
        padding: 0.8rem 1.2rem;
        background: transparent;
        border: none;
        cursor: pointer;
        color: #64748b;
        font-weight: 600;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    
    .tab-btn.active {
        color: #0d6efd;
        border-bottom-color: #0d6efd;
    }
    
    .tab-btn:hover {
        color: #1e293b;
    }
    
    /* Empty states */
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #64748b;
    }
    
    .empty-state h3 {
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-flex {
            flex-direction: column;
            text-align: center;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .data-table {
            font-size: 0.85rem;
        }
        
        .data-table th,
        .data-table td {
            padding: 0.6rem;
        }
        
        .action-buttons {
            flex-direction: column;
        }
        
        .action-buttons .btn {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
def check_admin_password():
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
            email = st.text_input("Email admin", type="default", key="admin_email")
        with col2:
            password = st.text_input("Mot de passe", type="password", key="admin_password")
        
        if st.button("Se connecter", use_container_width=True):
            # Vérification simple (À remplacer par une véritable authentification)
            if email == "admin@campus.fr" and password == "12345678":
                st.session_state.admin_authenticated = True
                st.session_state.admin_email = email
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
        
        st.markdown("""
                <p style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem;">
                    Démo: admin@campus.fr / 12345678
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False
    
    return True

# --- FUNCTIONS ---
@st.cache_data
def load_quiz_data():
    try:
        if os.path.exists("data_quizzes.csv"):
            try:
                df = pd.read_csv("data_quizzes.csv", encoding="utf-8", sep=";")
            except:
                df = pd.read_csv("data_quizzes.csv", encoding="latin1", sep=";")
            return df
    except Exception as e:
        st.error(f"Erreur : {e}")
    return None

# --- VÉRIFICATION AUTH ---
if not check_admin_password():
    st.stop()

# --- HEADER ---
st.markdown("""
<div class="admin-header">
    <div class="header-flex">
        <div>
            <h1>🎓 Campus Réussite</h1>
            <p>Tableau de bord administrateur</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="admin-badge">👤 Admin connecté</div>
            <div style="text-align: right; font-size: 0.9rem;">
                <div style="color: white; font-weight: 600;">""" + st.session_state.get('admin_email', 'Admin') + """</div>
                <div style="opacity: 0.9; font-size: 0.85rem;">Interface de gestion</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.tabs(["📊 Tableau de Bord", "📤 Importer des Quiz", "⚙️ Paramètres"])

# --- TAB 1: DASHBOARD ---
with menu[0]:
    df_quiz = load_quiz_data()
    
    if df_quiz is None or len(df_quiz) == 0:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h3>Aucun quiz disponible</h3>
            <p style="color: #64748b;">Importer des quiz pour commencer</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Stats
        st.markdown("""
        <h2 style="color: #1e293b; margin-bottom: 1rem; font-size: 1.5rem;">📈 Statistiques</h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(df_quiz)}</div>
                <div class="stat-label">Questions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            categories = df_quiz['categorie'].nunique() if 'categorie' in df_quiz.columns else 1
            st.markdown(f"""
            <div class="stat-card warning">
                <div class="stat-number">{categories}</div>
                <div class="stat-label">Catégories</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card success">
                <div class="stat-number">✅</div>
                <div class="stat-label">Actif</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card danger">
                <div class="stat-number">🔄</div>
                <div class="stat-label">À jour</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quiz Details
        st.markdown("""
        <div class="card">
            <h2>📋 Détail des Questions</h2>
        """, unsafe_allow_html=True)
        
        # Affichage de la table
        display_df = df_quiz[['question', 'reponse', 'explication']].copy()
        display_df.columns = ['Question', 'Réponse', 'Explication']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Export button
        csv = df_quiz.to_csv(index=False, sep=";")
        st.download_button(
            label="📥 Télécharger toutes les questions (CSV)",
            data=csv,
            file_name="quiz_export.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- TAB 2: IMPORT ---
with menu[1]:
    st.markdown("""
    <div class="card">
        <h2>📤 Importer des Quiz</h2>
        <p style="color: #64748b; margin-bottom: 1.5rem;">Sélectionnez un fichier CSV pour ajouter de nouveaux quiz</p>
    """, unsafe_allow_html=True)
    
    # Format info
    st.markdown("""
    <div style="background: #f0f3f7; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0d6efd;">
        <strong>📝 Format attendu :</strong><br>
        Colonnes : <code>question, a, b, c, d, reponse, explication, categorie</code><br>
        Séparateur : <code>;</code> (point-virgule)
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV",
        type=["csv"],
        key="quiz_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Détection du séparateur
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
                    st.info("💡 Rechargez l'app apprenant pour voir les changements")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la sauvegarde : {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur de lecture du fichier : {e}")
            st.info("Assurez-vous que le format est correct (séparateur : ;)")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Example file
    st.markdown("""
    <div class="card" style="margin-top: 1.5rem;">
        <h3>📥 Exemple de fichier</h3>
        <p style="color: #64748b;">Voici un exemple de structure CSV valide :</p>
    """, unsafe_allow_html=True)
    
    example_data = {
        "question": ["Quelle est la capitale de la France ?"],
        "a": ["Paris"],
        "b": ["Lyon"],
        "c": ["Marseille"],
        "d": ["Nice"],
        "reponse": ["Paris"],
        "explication": ["Paris est la capitale de la France depuis le 12ème siècle."],
        "categorie": ["Géographie"]
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    example_csv = example_df.to_csv(index=False, sep=";")
    st.download_button(
        label="📋 Télécharger l'exemple",
        data=example_csv,
        file_name="exemple_quiz.csv",
        mime="text/csv"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: SETTINGS ---
with menu[2]:
    st.markdown("""
    <div class="card">
        <h2>⚙️ Paramètres</h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Sécurité")
        if st.button("🔄 Changer le mot de passe admin"):
            st.info("Fonctionnalité disponible dans la prochaine version")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Données")
        
        df_quiz = load_quiz_data()
        if df_quiz is not None and len(df_quiz) > 0:
            if st.button("🗑️ Réinitialiser toutes les données", use_container_width=True):
                st.warning("Êtes-vous sûr ? Cette action est irréversible.")
                if st.button("Confirmer la réinitialisation"):
                    st.info("Fonctionnalité de confirmation en développement")
    
    st.markdown("""
        <div style="margin-top: 2rem; padding: 1.5rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #0d6efd;">
            <h4 style="margin-bottom: 0.5rem;">ℹ️ À propos</h4>
            <p style="color: #64748b; margin: 0.3rem 0;">
                <strong>Campus Réussite</strong> v2.0<br>
                Plateforme d'apprentissage interactive<br>
                © 2024 — Tous droits réservés
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #e2e8f0;">
    <p>Campus Réussite — Tableau de bord administrateur | Version 2.0</p>
</div>
""", unsafe_allow_html=True)
