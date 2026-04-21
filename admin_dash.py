import streamlit as st
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="Admin - Campus Réussite", layout="wide")

# --- SYSTÈME DE SÉCURITÉ MULTI-ADMIN ---
def check_password():
    """Vérifie les identifiants via les Secrets Streamlit."""
    if "authenticated" not in st.session_state:
        st.title("🔐 Administration - Campus Réussite")
        st.info("Veuillez vous identifier pour gérer la plateforme.")
        
        col1, col2 = st.columns(2)
        with col1:
            user_input = st.text_input("Nom d'administrateur")
        with col2:
            pw_input = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            # Vérification dans les secrets (Configurés sur Streamlit Cloud)
            try:
                admins = st.secrets["admin_accounts"]
                if user_input in admins and pw_input == admins[user_input]:
                    st.session_state.authenticated = True
                    st.session_state.admin_name = user_input
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects.")
            except KeyError:
                st.warning("⚠️ Les accès Admin ne sont pas encore configurés dans les Secrets.")
                # Mode secours pour le premier lancement local
                if user_input == "admin" and pw_input == "1234":
                    st.session_state.authenticated = True
                    st.rerun()
        return False
    return True

# --- CONTENU DU DASHBOARD ---
if check_password():
    # Barre latérale de navigation
    st.sidebar.title(f"Salut, {st.session_state.get('admin_name', 'Major')} !")
    menu = st.sidebar.radio("Navigation", ["📊 Statistiques", "📤 Importer des Quiz", "👥 Utilisateurs"])
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

    # --- PAGE 1 : STATISTIQUES ---
    if menu == "📊 Statistiques":
        st.title("🚀 Tableau de bord Campus Réussite")
        
        if os.path.exists("data_quizzes.csv"):
            df_stats = pd.read_csv("data_quizzes.csv")
            col1, col2, col3 = st.columns(3)
            col1.metric("Questions en ligne", len(df_stats))
            col2.metric("Catégories", len(df_stats['categorie'].unique()))
            col3.metric("État Serveur", "Opérationnel ✅")
            
            st.write("### Répartition par catégorie")
            st.bar_chart(df_stats['categorie'].value_counts())
        else:
            st.warning("Aucune donnée disponible. Commencez par importer un fichier CSV.")

    # --- PAGE 2 : IMPORTATION ---
    elif menu == "📤 Importer des Quiz":
        st.title("📥 Mise à jour des Quiz")
        st.write("Téléchargez votre fichier CSV pour mettre à jour la plateforme instantanément.")
        
        uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                # Vérification des colonnes nécessaires
                required_cols = ['question', 'a', 'b', 'c', 'd', 'reponse', 'explication', 'categorie']
                if all(col in df.columns for col in required_cols):
                    st.success("✅ Format de fichier valide !")
                    st.dataframe(df.head())
                    
                    if st.button("🚀 Publier les modifications"):
                        df.to_csv("data_quizzes.csv", index=False)
                        st.balloons()
                        st.success("La plateforme a été mise à jour !")
                else:
                    st.error(f"❌ Erreur : Le CSV doit contenir les colonnes : {', '.join(required_cols)}")
            except Exception as e:
                st.error(f"Erreur lors de la lecture : {e}")

    # --- PAGE 3 : GESTION UTILISATEURS ---
    elif menu == "👥 Utilisateurs":
        st.title("👥 Gestion des comptes")
        st.info("Cette section affichera les scores et les membres de la plateforme prochainement.")
        # Ici, on pourra plus tard lister les utilisateurs inscrits
