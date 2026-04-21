import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Campus Réussite - Apprendre", layout="centered")

# --- STYLE CSS PERSONNALISÉ (Pour rendre ça "Joli & Fluide") ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1B5E20; color: white; transform: scale(1.02); }
    .question-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_base_with_html=True)

# --- GESTION DU LOGO (Balise prête) ---
# Si tu mets un fichier nommé 'logo.png' dans ton GitHub, il s'affichera ici.
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    # Texte de remplacement élégant si le logo n'existe pas encore
    st.markdown("<h1 style='color: #2E7D32;'>🎓 Campus Réussite</h1>", unsafe_base_with_html=True)

st.write("---")

# --- CHARGEMENT DES QUIZ ---
if os.path.exists("data_quizzes.csv"):
    df_quiz = pd.read_csv("data_quizzes.csv")
    
    # Barre de progression
    total_q = len(df_quiz)
    st.sidebar.header("🏆 Progression")
    st.sidebar.progress(0) # À connecter plus tard à la progression réelle
    
    st.sidebar.write(f"Questions disponibles : **{total_q}**")
    user_name = st.sidebar.text_input("Ton Prénom / Nom", value="Candidat")

    # AFFICHAGE DES QUESTIONS EN CARTES
    for i, row in df_quiz.iterrows():
        st.markdown(f"""
            <div class='question-card'>
                <span style='color: #666; font-size: 0.8em;'>CATÉGORIE : {row['categorie'].upper()}</span>
                <h3 style='margin-top: 5px;'>Question {i+1}</h3>
                <p style='font-size: 1.1em;'>{row['question']}</p>
            </div>
        """, unsafe_base_with_html=True)
        
        # Options de réponse (Interactif)
        options = [row['a'], row['b'], row['c'], row['d']]
        choix = st.radio("Sélectionnez votre réponse :", options, key=f"q_{i}", label_visibility="collapsed")
        
        if st.button(f"Vérifier la réponse {i+1}", key=f"btn_{i}"):
            if choix == row['reponse']:
                st.success(f"🎯 Bravo {user_name} ! C'est la bonne réponse.")
                st.balloons()
            else:
                st.error(f"❌ Ce n'est pas tout à fait ça...")
                with st.expander("👉 Voir la solution expliquée"):
                    st.write(f"**La réponse correcte était :** {row['reponse']}")
                    st.write(f"**Explication :** {row['explication']}")
        st.write("") # Espace entre les questions
else:
    st.warning("👋 Bienvenue sur Campus Réussite ! Notre équipe prépare vos quiz. Revenez d'ici quelques instants.")
