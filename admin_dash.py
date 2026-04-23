import streamlit as st
import pandas as pd
import io
from database import db

st.set_page_config(
    page_title="Campus Réussite - Admin",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* HEADER */
    .admin-header {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .admin-header h1 { margin: 0; font-size: 2.5rem; }
    .admin-header p { margin: 0.5rem 0 0; opacity: 0.9; }
    
    /* CARD */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    .card h2 {
        margin-top: 0;
        color: #1e293b;
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 0.8rem;
    }
    
    /* STAT GRID */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; }
    
    /* UPLOAD ZONE */
    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        transition: all 0.3s ease;
    }
    .upload-zone:hover {
        border-color: #764ba2;
        background: #f0f1ff;
    }
    
    /* TABLE */
    .data-table {
        font-size: 0.9rem;
        overflow-x: auto;
    }
    
    /* BUTTONS */
    .btn-small {
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
    }
    .btn-success { background: #10b981; color: white; }
    .btn-danger { background: #ef4444; color: white; }
    .btn-primary { background: #667eea; color: white; }
    .btn-warning { background: #f59e0b; color: white; }
    
    /* TABS */
    .tab-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 0;
    }
    .tab {
        padding: 0.8rem 1.5rem;
        cursor: pointer;
        border: none;
        background: transparent;
        color: #6b7280;
        font-weight: 600;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    .tab:hover { color: #667eea; }
    .tab.active {
        color: #667eea;
        border-bottom-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTH ---
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Administration")
        email = st.text_input("Email")
        pwd = st.text_input("Mot de passe", type="password")
        
        if st.button("Se Connecter", use_container_width=True, type="primary"):
            try:
                admins = st.secrets.get("admins", {})
                if email in admins and admins[email] == pwd:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_email = email
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            except:
                st.error("⚠️ Erreur")
else:
    # --- HEADER ---
    st.markdown(f"""
    <div class="admin-header">
        <h1>🎓 Campus Réussite - Administration</h1>
        <p>👤 {st.session_state.admin_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Déconnexion", key="logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    st.divider()
    
    # --- TAB NAVIGATION ---
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = "dashboard"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.admin_tab = "dashboard"
            st.rerun()
    with col2:
        if st.button("📤 Importer", use_container_width=True):
            st.session_state.admin_tab = "import"
            st.rerun()
    with col3:
        if st.button("👥 Apprenants", use_container_width=True):
            st.session_state.admin_tab = "users"
            st.rerun()
    with col4:
        if st.button("💬 Feedback", use_container_width=True):
            st.session_state.admin_tab = "feedback"
            st.rerun()
    
    st.divider()
    
    # --- DASHBOARD ---
    if st.session_state.admin_tab == "dashboard":
        st.markdown("### 📊 Statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{len(db.get_all_users())}</div>
                <div class="stat-label">Apprenants</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{db.get_quiz_count()}</div>
                <div class="stat-label">Quiz Publiés</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{len(db.get_pending_quiz())}</div>
                <div class="stat-label">En Révision</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{len(db.get_all_feedback())}</div>
                <div class="stat-label">Feedbacks</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 📋 Quiz Publiés")
        quiz_list = db.get_all_quiz()
        if quiz_list:
            df = pd.DataFrame(quiz_list)
            df = df[['question', 'reponses_correctes', 'explication', 'categorie']].rename(columns={
                'question': 'Question',
                'reponses_correctes': 'Réponses',
                'explication': 'Explication',
                'categorie': 'Catégorie'
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun quiz publié")
    
    # --- IMPORT ---
    elif st.session_state.admin_tab == "import":
        st.markdown("### 📤 Importer des Quiz")
        
        # Upload CSV
        st.markdown("#### 1️⃣ Télécharger un fichier CSV")
        uploaded_file = st.file_uploader("Choisir un CSV", type=["csv"], key="import_csv")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                
                st.success(f"✅ Fichier chargé ({len(df)} lignes)")
                
                # Vérifier colonnes
                required_cols = ['question', 'a', 'b', 'c', 'd', 'reponses_correctes', 'explication', 'categorie']
                if not all(col in df.columns for col in required_cols):
                    st.error("❌ Colonnes manquantes. Vérifiez le format CSV")
                else:
                    st.markdown("#### 2️⃣ Aperçu des Données")
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    st.markdown("#### 3️⃣ Action")
                    if st.button("📥 Ajouter à la Révision", use_container_width=True, type="primary"):
                        for _, row in df.iterrows():
                            db.add_pending_quiz(
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
                        st.success(f"✅ {len(df)} quiz ajoutés à la révision")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
        
        st.divider()
        
        st.markdown("### ⏳ Quiz en Révision")
        pending = db.get_pending_quiz()
        
        if not pending:
            st.info("Aucun quiz en attente")
        else:
            for quiz in pending:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**Q{quiz['id']} : {quiz['question']}**")
                        st.markdown(f"Catégorie: {quiz['categorie']} | Source: {quiz['source_file']}")
                        
                        with st.expander("Voir détails"):
                            st.markdown(f"**A)** {quiz['option_a']}")
                            st.markdown(f"**B)** {quiz['option_b']}")
                            st.markdown(f"**C)** {quiz['option_c']}")
                            st.markdown(f"**D)** {quiz['option_d']}")
                            st.markdown(f"**Réponses:** {quiz['reponses_correctes']}")
                            st.markdown(f"**Explication:** {quiz['explication']}")
                        
                        # Modifier
                        with st.expander("✏️ Modifier"):
                            question = st.text_input("Question", value=quiz['question'], key=f"q_{quiz['id']}")
                            opt_a = st.text_input("A", value=quiz['option_a'], key=f"a_{quiz['id']}")
                            opt_b = st.text_input("B", value=quiz['option_b'], key=f"b_{quiz['id']}")
                            opt_c = st.text_input("C", value=quiz['option_c'], key=f"c_{quiz['id']}")
                            opt_d = st.text_input("D", value=quiz['option_d'], key=f"d_{quiz['id']}")
                            correct = st.text_input("Réponses (ex: A, B)", value=quiz['reponses_correctes'], key=f"r_{quiz['id']}")
                            expl = st.text_area("Explication", value=quiz['explication'], key=f"e_{quiz['id']}")
                            cat = st.text_input("Catégorie", value=quiz['categorie'], key=f"c2_{quiz['id']}")
                            
                            if st.button("Sauvegarder", key=f"save_{quiz['id']}"):
                                db.update_pending_quiz(quiz['id'], question, opt_a, opt_b, opt_c, opt_d, correct, expl, cat)
                                st.success("✅ Modifié")
                                st.rerun()
                    
                    with col2:
                        col_accept, col_reject = st.columns(2)
                        with col_accept:
                            if st.button("✅", key=f"accept_{quiz['id']}", help="Accepter"):
                                db.approve_pending_quiz(quiz['id'])
                                st.success("✅ Accepté")
                                st.rerun()
                        with col_reject:
                            if st.button("❌", key=f"reject_{quiz['id']}", help="Rejeter"):
                                db.reject_pending_quiz(quiz['id'])
                                st.info("❌ Rejeté")
                                st.rerun()
    
    # --- APPRENANTS ---
    elif st.session_state.admin_tab == "users":
        st.markdown("### 👥 Gestion des Apprenants")
        
        users = db.get_all_users()
        
        if users:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(users))
            with col2:
                active = len([u for u in users if u['status'] == 'actif'])
                st.metric("Actifs", active)
            with col3:
                blocked = len([u for u in users if u['status'] == 'bloqué'])
                st.metric("Bloqués", blocked)
            
            st.divider()
            
            df_users = pd.DataFrame(users)
            df_users = df_users[['nom', 'prenom', 'email', 'username', 'status', 'date_creation']].rename(columns={
                'nom': 'Nom',
                'prenom': 'Prénom',
                'email': 'Email',
                'username': 'Username',
                'status': 'Statut',
                'date_creation': 'Date'
            })
            
            st.markdown("#### Liste Complète")
            st.dataframe(df_users, use_container_width=True, height=400, hide_index=True)
            
            st.divider()
            
            st.markdown("#### Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                user_options = [f"{u['prenom']} {u['nom']}" for u in users]
                selected_user = st.selectbox("Sélectionner un apprenant", user_options)
                
                if st.button("🚫 Bloquer/Débloquer", use_container_width=True):
                    for u in users:
                        if f"{u['prenom']} {u['nom']}" == selected_user:
                            new_status = 'actif' if u['status'] == 'bloqué' else 'bloqué'
                            db.update_user_status(u['id'], new_status)
                            st.success(f"✅ Statut: {new_status}")
                            st.rerun()
            
            with col2:
                selected_user2 = st.selectbox("Sélectionner pour supprimer", user_options, key="del_user")
                
                if st.button("🗑️ Supprimer", use_container_width=True):
                    for u in users:
                        if f"{u['prenom']} {u['nom']}" == selected_user2:
                            db.delete_user(u['id'])
                            st.success("✅ Supprimé")
                            st.rerun()
        else:
            st.info("Aucun apprenant")
    
    # --- FEEDBACK ---
    elif st.session_state.admin_tab == "feedback":
        st.markdown("### 💬 Feedback des Apprenants")
        
        feedback_list = db.get_all_feedback()
        
        if feedback_list:
            for fb in feedback_list:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{fb['titre']}**")
                        st.markdown(f"De: {fb['email']} | Type: {fb['type']}")
                        st.markdown(f"Message: {fb['message']}")
                        st.caption(f"Date: {fb['date_creation']}")
                    with col2:
                        if st.button("✅ Lire", key=f"read_{fb['id']}"):
                            db.mark_feedback_as_read(fb['id'])
                            st.rerun()
        else:
            st.info("Aucun feedback")
