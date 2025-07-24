<template>
  <div class="max-w-3xl mx-auto p-6">
    <h1 class="text-3xl font-bold text-blue-700 mb-4 text-center">📋 Formules d’abonnement</h1>
    <p class="text-gray-600 text-center mb-6">
      Accédez aux quiz éducatifs adaptés à votre niveau. Paiement mobile simple, accès sécurisé et renouvelable.
    </p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="border p-4 rounded shadow">
        <h2 class="text-xl font-semibold text-green-600 mb-2">🎯 1 mois</h2>
        <p class="text-sm text-gray-700 mb-2">Accès complet pendant 30 jours</p>
        <p class="font-bold text-lg text-green-800 mb-2">3000 FCFA</p>
        <p class="text-xs text-gray-500">Paiement par Orange ou Moov</p>
      </div>

      <div class="border p-4 rounded shadow bg-blue-50">
        <h2 class="text-xl font-semibold text-blue-600 mb-2">🚀 2 mois</h2>
        <p class="text-sm text-gray-700 mb-2">Pour un entraînement approfondi</p>
        <p class="font-bold text-lg text-blue-800 mb-2">5000 FCFA</p>
        <p class="text-xs text-gray-500">Paiement par Orange ou Moov</p>
      </div>

      <div class="border p-4 rounded shadow">
        <h2 class="text-xl font-semibold text-purple-600 mb-2">🏆 1 an</h2>
        <p class="text-sm text-gray-700 mb-2">Accès illimité pour toute l’année scolaire</p>
        <p class="font-bold text-lg text-purple-800 mb-2">20000 FCFA</p>
        <p class="text-xs text-gray-500">Paiement par Orange ou Moov</p>
      </div>
    </div>

    <div class="mt-10 bg-yellow-50 p-4 rounded text-center">
      <h3 class="text-lg font-semibold text-yellow-800 mb-2">💳 Comment payer ?</h3>
      <p class="text-gray-700 text-sm">Envoyez le montant correspondant à l’un des numéros suivants :</p>
      <ul class="text-sm mt-2 mb-4">
        <li>📱 Orange Money : <strong>54 16 72 86</strong></li>
        <li>📱 Moov Money : <strong>73 06 96 26</strong></li>
      </ul>
      <p class="text-sm text-gray-600 mb-2">Après paiement, cliquez ci-dessous pour créer votre compte :</p>

      <NuxtLink to="/auth/register" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
        🔐 Créer mon compte
      </NuxtLink>
    </div>
  </div>
</template>
