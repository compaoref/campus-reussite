import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Campus Réussite - Apprenant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour un design professionnel et dynamique
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
    
    /* Header Section */
    .header-container {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(13, 110, 253, 0.15);
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
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        flex-wrap: wrap;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        flex: 1;
        min-width: 250px;
    }
    
    .logo-area {
        width: 80px;
        height: 80px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .logo-area img {
        width: 70%;
        height: 70%;
        object-fit: contain;
    }
    
    .header-text h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        opacity: 0.95;
        font-size: 0.95rem;
        margin: 0;
    }
    
    .user-info {
        background: rgba(255, 255, 255, 0.15);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: fadeIn 0.8s ease-out 0.2s both;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .user-info p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    /* Main content */
    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem 2rem 1rem;
    }
    
    /* Stats Section */
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
        text-align: center;
        transition: all 0.3s ease;
        border-left: 4px solid #0d6efd;
    }
    
    .stat-card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #0d6efd;
        margin: 0;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Quiz Section */
    .quiz-container {
        background: white;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        padding: 2rem;
        animation: slideUp 0.6s ease-out 0.3s both;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .quiz-header {
        border-bottom: 2px solid #f0f3f7;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .quiz-header h2 {
        color: #0f172a;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .quiz-progress {
        background: #f0f3f7;
        height: 8px;
        border-radius: 4px;
        margin-top: 1rem;
        overflow: hidden;
    }
    
    .quiz-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #0d6efd 0%, #0251d9 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Question Card */
    .question-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #0d6efd;
        animation: fadeIn 0.4s ease-out;
    }
    
    .question-number {
        display: inline-block;
        background: #0d6efd;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .question-text {
        font-size: 1.2rem;
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    /* Options */
    .options-container {
        display: grid;
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }
    
    .option-item {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        background: white;
    }
    
    .option-item:hover {
        border-color: #0d6efd;
        background: #f6f8fb;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.1);
    }
    
    .option-label {
        width: 36px;
        height: 36px;
        background: #0d6efd;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }
    
    .option-text {
        flex: 1;
        display: flex;
        align-items: center;
        color: #0f172a;
        font-weight: 500;
    }
    
    .option-item input[type="radio"] {
        margin-right: 0.5rem;
        cursor: pointer;
    }
    
    /* Buttons */
    .button-group {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #0d6efd 0%, #0251d9 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    }
    
    .btn-primary:hover {
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.4);
        transform: translateY(-2px);
    }
    
    .btn-secondary {
        background: #f0f3f7;
        color: #0f172a;
        border: 2px solid #e5e7eb;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        border-color: #0d6efd;
        background: #f6f8fb;
    }
    
    /* Results */
    .result-container {
        background: #f0f3f7;
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 1rem;
        border-left: 4px solid #0d6efd;
    }
    
    .result-success {
        background: #ecfdf5;
        border-left-color: #10b981;
    }
    
    .result-success .result-title {
        color: #10b981;
    }
    
    .result-error {
        background: #fef2f2;
        border-left-color: #ef4444;
    }
    
    .result-error .result-title {
        color: #ef4444;
    }
    
    .result-title {
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .result-text {
        color: #4b5563;
        font-size: 0.95rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
        }
        
        .logo-section {
            justify-content: center;
            width: 100%;
        }
        
        .header-text h1 {
            font-size: 1.5rem;
        }
        
        .quiz-container {
            padding: 1.5rem;
        }
        
        .question-card {
            padding: 1.5rem;
        }
        
        .button-group {
            flex-direction: column;
        }
        
        .btn-primary, .btn-secondary {
            width: 100%;
        }
    }
    
    /* Streamlit overrides */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .st-emotion-cache-1v0mbno {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION SESSION STATE ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "df_quiz" not in st.session_state:
    st.session_state.df_quiz = None

# --- HEADER PROFESSIONNEL ---
def render_header():
    html = """
    <div class="header-container">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-area">
                    <span style="font-size: 2.5rem;">🎓</span>
                </div>
                <div class="header-text">
                    <h1>Campus Réussite</h1>
                    <p>Plateforme d'apprentissage interactive</p>
                </div>
            </div>
            <div class="user-info">
                <p><strong>📌 Mode</strong> Apprenant</p>
                <p><strong>🚀 Statut</strong> En cours</p>
                <p style="margin-top: 0.5rem; opacity: 0.9; font-size: 0.85rem;">Bonne chance ! 💪</p>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

render_header()

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_quiz_data():
    try:
        if os.path.exists("data_quizzes.csv"):
            try:
                df = pd.read_csv("data_quizzes.csv", encoding="utf-8", sep=";")
            except UnicodeDecodeError:
                df = pd.read_csv("data_quizzes.csv", encoding="latin1", sep=";")
            return df
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
    return None

df_quiz = load_quiz_data()

# --- MAIN CONTENT ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if df_quiz is None or len(df_quiz) == 0:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem; background: white; border-radius: 12px; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
        <h2 style="color: #0f172a; margin: 0.5rem 0;">Les quiz arrivent bientôt !</h2>
        <p style="color: #6b7280; margin: 0;">L'équipe pédagogique prépare du contenu intéressant pour vous.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- FORMULAIRE NOM D'UTILISATEUR ---
    col1, col2 = st.columns([2, 1])
    with col1:
        user_name = st.text_input(
            "👤 Entrez votre nom",
            value=st.session_state.user_name,
            key="user_input",
            placeholder="Votre nom complet"
        )
        st.session_state.user_name = user_name
    
    with col2:
        st.metric("Questions", len(df_quiz))
    
    st.markdown("---")
    
    # --- STATS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        completed = len([v for v in st.session_state.responses.values() if v])
        st.metric("✅ Complétées", completed)
    with col2:
        remaining = len(df_quiz) - completed
        st.metric("⏳ Restantes", remaining)
    with col3:
        if len(df_quiz) > 0:
            progress = (completed / len(df_quiz)) * 100
            st.metric("📊 Progression", f"{progress:.0f}%")
    
    st.markdown("---")
    
    # --- QUIZ CONTENT ---
    if not st.session_state.show_results:
        st.markdown("""
        <div class="quiz-container">
            <div class="quiz-header">
                <h2>🎯 Entraînement Interactif</h2>
                <div class="quiz-progress">
                    <div class="quiz-progress-bar" style="width: """ + 
                    str((st.session_state.current_question / len(df_quiz)) * 100) + 
                    """%"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Affichage de la question actuelle
        row = df_quiz.iloc[st.session_state.current_question]
        
        st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {st.session_state.current_question + 1} sur {len(df_quiz)}</div>
            <div class="question-text">{row['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Options
        options = [row['a'], row['b'], row['c'], row['d']]
        option_keys = ['a', 'b', 'c', 'd']
        
        st.markdown('<div class="options-container">', unsafe_allow_html=True)
        
        selected_option = st.radio(
            "Choisir votre réponse :",
            options,
            key=f"q_{st.session_state.current_question}",
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Boutons d'action
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("⬅️ Question Précédente", use_container_width=True):
                    st.session_state.current_question -= 1
