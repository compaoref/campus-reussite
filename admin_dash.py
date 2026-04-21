import streamlit as st
import pandas as pd
import os, json, time, random, hashlib

st.set_page_config(page_title="Campus Réussite", layout="wide")

# ================== STYLE PREMIUM ==================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}
section[data-testid="stSidebar"] {background: #020617;}
h1,h2,h3 {color:#f1f5f9;}
.stButton>button {
    background: linear-gradient(90deg,#3b82f6,#6366f1);
    color:white;border-radius:10px;font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ================== PASSWORD ==================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================== USERS ==================
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        return json.load(open(USER_FILE))
    return {
        "admin@admin.com":{
            "password": hash_password("1234"),
            "role":"admin",
            "scores":[]
        }
    }

def save_users(u):
    json.dump(u, open(USER_FILE,"w"))

users = load_users()

# ================== QUIZ DATA ==================
@st.cache_data
def load_data():
    if os.path.exists("data_quizzes.csv"):
        return pd.read_csv("data_quizzes.csv")
    return pd.DataFrame()

df = load_data()

# ================== SESSION ==================
if "user" not in st.session_state:
    st.session_state.user = None

# ================== LOGIN ==================
if st.session_state.user is None:
    st.title("🔐 Connexion")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if email in users and users[email]["password"] == hash_password(password):
            st.session_state.user = {"email": email, "role": users[email]["role"]}
            st.rerun()
        else:
            st.error("Identifiants incorrects")

    st.stop()

# ================== USER ==================
user = st.session_state.user
role = user["role"]

# ================== SIDEBAR ==================
st.sidebar.title("🎓 Campus")
st.sidebar.write(user["email"])

if role == "admin":
    menu = st.sidebar.radio("Menu", [
        "📊 Dashboard","➕ Ajouter","📥 Import",
        "👥 Utilisateurs","🧠 Quiz","📊 Résultat","📈 Performances"
    ])
else:
    menu = st.sidebar.radio("Menu", [
        "🧠 Quiz","📊 Résultat","📈 Performances"
    ])

if st.sidebar.button("Déconnexion"):
    st.session_state.user = None
    st.rerun()

# ================== DASHBOARD ==================
if menu == "📊 Dashboard":
    if role != "admin": st.stop()

    st.title("📊 Dashboard")

    c1,c2,c3 = st.columns(3)
    c1.metric("Questions", len(df))
    c2.metric("Utilisateurs", len(users))
    
    scores = [s["score"] for u in users for s in users[u].get("scores",[])]
    c3.metric("Score moyen", round(sum(scores)/len(scores),2) if scores else 0)

    if scores:
        st.line_chart(scores)

# ================== ADD USER ==================
elif menu == "👥 Utilisateurs":
    if role != "admin": st.stop()

    st.title("👥 Utilisateurs")

    email = st.text_input("Email")
    pwd = st.text_input("Mot de passe", type="password")
    role_new = st.selectbox("Rôle",["apprenant","admin"])

    if st.button("Ajouter"):
        users[email] = {
            "password": hash_password(pwd),
            "role": role_new,
            "scores":[]
        }
        save_users(users)
        st.success("Ajouté")

    for u in users:
        st.write(u, "-", users[u]["role"])

# ================== IMPORT ==================
elif menu == "📥 Import":
    if role != "admin": st.stop()

    file = st.file_uploader("Importer Excel", type=["xlsx","csv"])
    if file:
        new_df = pd.read_excel(file)
        new_df.to_csv("data_quizzes.csv", index=False)
        st.success("Import réussi")

# ================== QUIZ ==================
elif menu == "🧠 Quiz":
    st.title("🧠 Test")

    if df.empty:
        st.warning("Aucune question")
    else:
        if "start" not in st.session_state:
            st.session_state.start = None
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "submitted" not in st.session_state:
            st.session_state.submitted = False

        if st.session_state.start is None:
            if st.button("Démarrer"):
                st.session_state.start = time.time()
                st.session_state.answers = {}
                st.session_state.submitted = False
                st.session_state.quiz = df.sample(frac=1)
                st.rerun()
            st.stop()

        # TIMER
        remain = 300 - int(time.time()-st.session_state.start)
        if remain <= 0:
            st.session_state.submitted = True
            st.error("Temps écoulé")
        else:
            st.warning(f"Temps restant: {remain}s")

        total = len(st.session_state.quiz)
        st.progress(len(st.session_state.answers)/total)

        for i,row in st.session_state.quiz.iterrows():
            choix = st.radio(row["question"],
                [row["a"],row["b"],row["c"],row["d"]],
                key=i,
                disabled=st.session_state.submitted)
            st.session_state.answers[i]=choix

        if not st.session_state.submitted:
            if st.button("Terminer"):
                st.session_state.submitted=True
                st.rerun()

        if st.session_state.submitted:
            score=0
            st.subheader("Correction")

            for i,row in st.session_state.quiz.iterrows():
                user_ans = st.session_state.answers.get(i)
                if user_ans == row["reponse"]:
                    st.success(f"{row['question']} ✔")
                    score+=1
                else:
                    st.error(f"{row['question']} ❌")
                    st.info(f"Réponse: {row['reponse']}")

            st.session_state.score = score
            st.success(f"Score: {score}/{total}")

            # SAVE SCORE
            email = user["email"]
            users[email]["scores"].append({
                "score":score,"total":total,"date":time.strftime("%Y-%m-%d")
            })
            save_users(users)

# ================== RESULT ==================
elif menu == "📊 Résultat":
    st.metric("Score", st.session_state.get("score",0))

    if st.button("Recommencer"):
        st.session_state.start=None
        st.session_state.answers={}
        st.session_state.submitted=False
        st.rerun()

# ================== PERFORMANCE ==================
elif menu == "📈 Performances":
    st.title("📈 Performances")

    hist = users[user["email"]].get("scores",[])
    if hist:
        dfp = pd.DataFrame(hist)
        st.dataframe(dfp)
        st.line_chart(dfp["score"])
    else:
        st.info("Aucune donnée")
