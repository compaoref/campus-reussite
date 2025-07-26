# 📘 Campus Réussite — Plateforme de quiz éducatifs avec abonnement

Campus Réussite est une application web interactive qui permet aux apprenants de préparer les concours BEPC, BAC, Licence et bien plus, grâce à des quiz dynamiques accessibles par abonnement à durée limitée.

---

## 🚀 Fonctionnalités clés

- ✅ Inscription et connexion sécurisées via Supabase
- 📆 Sélection de formules d’abonnement : 1 mois, 2 mois ou 1 an
- 🔒 Contrôle d’accès basé sur la date d’expiration
- 📋 Quiz par niveau : BEPC, BAC, Licence
- 📊 Enregistrement et suivi des scores
- 🧑‍💼 Interface admin pour ajout de quiz et suivi des abonnés
- 💳 Validation manuelle des paiements via mobile money

---

## 🛠️ Technologies utilisées

| Frontend      | Backend        | Base de données | Déploiement |
|---------------|----------------|------------------|-------------|
| Nuxt 3        | Supabase       | PostgreSQL        | GitHub Pages / Vercel |
| Tailwind CSS  | Middleware Nuxt| Tables `profiles`, `quizzes`, `scores` | Static hosting |

---

## 📦 Installation locale

```bash
npx nuxi init campus-reussite
cd campus-reussite
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
