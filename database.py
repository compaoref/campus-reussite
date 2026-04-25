import streamlit as st
import pandas as pd
from database import db

st.set_page_config(page_title="Campus Admin", layout="wide")

st.markdown("""
<style>
    .header { background: linear-gradient(90deg, #1e293b, #0f172a); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
    .card { background: white; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .stat { background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 1rem; border-radius: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- AUTH ---
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Administration")
        email = st.text_input("Email")
        pwd = st.text_input("Mot de passe", type="password")
        
        if st.button("Se Connecter", use_container_width=True, type="primary"):
            try:
                admins = st.secrets.get("admins", {})
                if email in admins and admins[email] == pwd:
                    st.session_state.admin_auth = True
                    st.session_state.admin_email = email
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            except:
                st.error("⚠️ Erreur")
else:
    # --- DASHBOARD ---
    st.markdown(f"""
    <div class="header">
        <h2 style="margin:0">🎓 Campus Réussite - Admin</h2>
        <p style="margin:0.5rem 0 0; opacity:0.9">👤 {st.session_state.admin_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Déconnexion", key="logout"):
        st.session_state.admin_auth = False
        st.rerun()
    
    st.divider()
    
    # --- TABS ---
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = "dashboard"
    
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
    
    # === DASHBOARD ===
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
            df = pd.DataFrame(quiz_list)
            df = df[['question', 'reponses_correctes', 'categorie']]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun quiz")
    
    # === GESTION QUIZ ===
    elif st.session_state.admin_tab == "quiz":
        st.markdown("### 🎯 Gestion des Quiz Publiés")
        
        quiz_list = db.get_all_quiz()
        st.write(f"**{len(quiz_list)} quiz publiés**")
        
        if not quiz_list:
            st.info("Aucun quiz publié")
        else:
            # Afficher les quiz
            for idx, q in enumerate(quiz_list):
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
                    if st.button("🗑️", key=f"del_quiz_{q['id']}", help="Supprimer ce quiz"):
                        if db.delete_quiz(q['id']):
                            st.success("✅ Quiz supprimé")
                            st.rerun()
                        else:
                            st.error("❌ Erreur")
                
                st.divider()
    
    # === IMPORT ===
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
                        if db.add_pending_quiz(
                            row['question'],
                            row['a'],
                            row['b'],
                            row['c'],
                            row['d'],
                            row['reponses_correctes'],
                            row['explication'],
                            row['categorie'],
                            uploaded_file.name
                        ):
                            count += 1
                    st.success(f"✅ {count} quiz ajoutés à la révision")
                    st.rerun()
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
                            st.rerun()
                
                with col2:
                    col_a, col_r = st.columns(2)
                    with col_a:
                        if st.button("✅", key=f"accept_{idx}_{q['id']}", help="Accepter"):
                            db.approve_pending_quiz(q['id'])
                            st.success("✅ Accepté")
                            st.rerun()
                    with col_r:
                        if st.button("❌", key=f"reject_{idx}_{q['id']}", help="Rejeter"):
                            db.reject_pending_quiz(q['id'])
                            st.info("❌ Rejeté")
                            st.rerun()
                
                st.divider()
    
    # === APPRENANTS ===
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
            df = pd.DataFrame(users)
            df = df[['nom', 'prenom', 'email', 'status']].copy()
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
                            st.rerun()
            
            with col2:
                selected2 = st.selectbox("Sélectionner pour supprimer", user_names, key="del")
                if st.button("🗑️ Supprimer", use_container_width=True):
                    for u in users:
                        if f"{u['prenom']} {u['nom']}" == selected2:
                            db.delete_user(u['id'])
                            st.success("✅ Supprimé")
                            st.rerun()
        else:
            st.info("Aucun apprenant")
    
    # === FEEDBACK ===
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
    
    # === DEBUG ===
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
            df = pd.DataFrame(quiz_list)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("❌ Aucun quiz dans la table quiz")
        
        st.divider()
        st.markdown("**Table: quiz_pending (Quiz en Révision)**")
        pending = db.get_pending_quiz()
        st.write(f"Nombre en attente: {len(pending)}")
        if pending:
            df = pd.DataFrame(pending)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun quiz en attente")
        
        st.divider()
        st.markdown("**Table: utilisateurs (Apprenants)**")
        users = db.get_all_users()
        st.write(f"Nombre d'apprenants: {len(users)}")
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df[['nom', 'prenom', 'email', 'status']], use_container_width=True)
        else:
            st.warning("❌ Aucun apprenant")
        
        st.divider()
        st.markdown("**Table: feedback**")
        feedback_list = db.get_all_feedback()
        st.write(f"Nombre de feedbacks: {len(feedback_list)}")
        if feedback_list:
            df = pd.DataFrame(feedback_list)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun feedback")
        
        st.divider()
        st.markdown("**Actions de Debug**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Rafraîchir"):
                st.rerun()
        with col2:
            if st.button("🗑️ Supprimer TOUS les quiz"):
                if st.checkbox("J'accepte de tout supprimer"):
                    quiz_list = db.get_all_quiz()
                    for q in quiz_list:
                        db.delete_quiz(q['id'])
                    st.success("✅ Tous les quiz supprimés")
                    st.rerun()
        with col3:
            if st.button("⚠️ Reset complète"):
                st.warning("Cette action supprimera toute la base!")
                if st.checkbox("JE SUIS SÛR"):
                    import os
                    db_path = db.get_db_path()
                    if os.path.exists(db_path):
                        os.remove(db_path)
                    st.success("✅ Base réinitialisée - Redémarrez les apps!")
                    st.rerun()
