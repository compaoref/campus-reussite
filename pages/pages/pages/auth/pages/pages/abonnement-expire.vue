<template>
  <div class="max-w-md mx-auto p-6 text-center">
    <h1 class="text-2xl font-bold text-red-700 mb-4">⏳ Accès expiré</h1>
    <p class="text-gray-600 mb-4">
      Votre période d’abonnement est terminée.  
      Pour continuer à accéder aux quiz et aux contenus, veuillez renouveler votre accès.
    </p>

    <NuxtLink to="/renouvellement" class="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700">
      🔄 Renouveler mon abonnement
    </NuxtLink>

    <p class="mt-4 text-sm text-gray-500">
      Une fois le paiement confirmé, votre compte sera réactivé par l’administrateur.
    </p>
  </div>
</template>
