<template>
  <div class="max-w-xl mx-auto p-6">
    <h1 class="text-2xl font-bold text-blue-700 mb-6 text-center">🔄 Renouvellement d’abonnement</h1>

    <form @submit.prevent="soumettreRenouvellement" class="space-y-4">
      <input v-model="email" type="email" placeholder="📧 Adresse e-mail"
        class="w-full border rounded p-2" required />

      <select v-model="plan" class="w-full border rounded p-2" required>
        <option disabled value="">🎯 Choisir une nouvelle formule</option>
        <option value="1">1 mois — 3000 FCFA</option>
        <option value="2">2 mois — 5000 FCFA</option>
        <option value="12">1 an — 20000 FCFA</option>
      </select>

      <p class="text-sm text-gray-600" v-if="expiration">
        📅 Nouvel accès valable jusqu’au <strong>{{ expiration }}</strong>
      </p>

      <button type="submit"
        class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 w-full">
        🔓 Renouveler mon accès
      </button>
    </form>

    <p class="mt-4 text-center text-gray-500 text-sm">
      Votre demande sera validée manuellement après confirmation du paiement.
    </p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { supabase } from '~/plugins/supabase.client'

const email = ref('')
const plan = ref('')
const expiration = ref('')

watch(plan, () => {
  const mois = parseInt(plan.value)
  const date = new Date()
  date.setMonth(date.getMonth() + mois)
  expiration.value = date.toLocaleDateString()
})

async function soumettreRenouvellement() {
  const { data, error } = await supabase
    .from('renewals') // ⚠️ Table dédiée ou enregistrer dans profiles selon ton logique
    .insert([{
      email: email.value,
      plan: plan.value,
      nouvelle_expiration: expiration.value,
      statut: 'En attente'
    }])

  if (error) {
    alert('❌ Erreur : ' + error.message)
  } else {
    alert('✅ Demande envoyée ! Elle sera validée après confirmation du paiement.')
  }
}
</script>
