<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-white px-6 py-10">
    <div class="max-w-4xl mx-auto text-center">
      <!-- Logo optionnel -->
      <Logo />

      <h1 class="text-4xl md:text-5xl font-extrabold text-blue-800 mb-4">🎓 Campus Réussite</h1>
      <p class="text-lg text-gray-700 mb-8">
        La plateforme qui propulse ta réussite aux concours BEPC, BAC et Licence.  
        Quiz interactifs, suivi personnalisé, accès sécurisé — tout ce qu’il te faut pour briller 🌟
      </p>

      <div class="flex justify-center gap-4 flex-wrap mb-10">
        <NuxtLink to="/auth/register" class="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700">
          🔐 Créer mon compte
        </NuxtLink>
        <NuxtLink to="/tarifs" class="px-6 py-3 border border-blue-600 text-blue-600 rounded hover:bg-blue-50">
          📋 Voir les formules
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 text-left">
        <div class="bg-white rounded shadow p-4">
          <h3 class="text-lg font-bold text-green-600 mb-2">✅ Accès par abonnement</h3>
          <p class="text-gray-600 text-sm">Choisis une formule simple : 1 mois, 2 mois ou 1 an. Accès sécurisé et renouvelable.</p>
        </div>
        <div class="bg-white rounded shadow p-4">
          <h3 class="text-lg font-bold text-purple-600 mb-2">📚 Quiz interactifs</h3>
          <p class="text-gray-600 text-sm">Questions aléatoires, multi-réponses, explications. Prépare-toi comme un pro.</p>
        </div>
        <div class="bg-white rounded shadow p-4">
          <h3 class="text-lg font-bold text-blue-600 mb-2">🛠️ Plateforme évolutive</h3>
          <p class="text-gray-600 text-sm">Admin, tableau de bord, renouvellement, gestion des scores. Un vrai outil pédagogique.</p>
        </div>
      </div>

      <!-- Footer -->
      <footer class="mt-20 text-center text-sm text-gray-500">
        <p>© Campus Réussite {{ new Date().getFullYear() }} — Une solution numérique pour la réussite aux concours.</p>
      </footer>
    </div>
  </div>
</template>
