<template>
  <div class="max-w-4xl mx-auto mt-10 p-6">
    <h1 class="text-2xl font-bold text-blue-700 mb-6 text-center">🛠️ Tableau des abonnés</h1>

    <table class="w-full border text-sm">
      <thead class="bg-blue-50">
        <tr>
          <th class="border px-3 py-2">📧 Email</th>
          <th class="border px-3 py-2">🎯 Formule</th>
          <th class="border px-3 py-2">📅 Expiration</th>
          <th class="border px-3 py-2">💳 Paiement</th>
          <th class="border px-3 py-2">✅ Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="profil in profils" :key="profil.id">
          <td class="border px-3 py-2">{{ profil.email }}</td>
          <td class="border px-3 py-2">{{ convertirPlan(profil.plan) }}</td>
          <td class="border px-3 py-2">{{ profil.access_expires }}</td>
          <td class="border px-3 py-2">{{ profil.statut_paiement }}</td>
          <td class="border px-3 py-2 text-center">
            <button
              v-if="profil.statut_paiement === 'En attente'"
              @click="validerPaiement(profil.id)"
              class="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
            >
              Valider
            </button>
            <span v-else class="text-green-700 font-bold">✔️</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from '~/plugins/supabase.client'

const profils = ref([])

onMounted(async () => {
  const { data } = await supabase
    .from('profiles')
    .select('id, email, plan, access_expires, statut_paiement')
    .order('access_expires', { ascending: false })

  profils.value = data
})

function convertirPlan(val) {
  if (val === '1') return '1 mois'
  if (val === '2') return '2 mois'
  if (val === '12') return '1 an'
  return '–'
}

async function validerPaiement(id) {
  const { error } = await supabase
    .from('profiles')
    .update({ statut_paiement: 'Validé' })
    .eq('id', id)

  if (!error) {
    alert('✅ Paiement validé avec succès !')
    profils.value = profils.value.map(p =>
      p.id === id ? { ...p, statut_paiement: 'Validé' } : p
    )
  }
}
</script>
