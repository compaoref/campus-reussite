<template>
  <div class="max-w-xl mx-auto p-4">
    <h2 class="text-xl font-bold text-blue-700 mb-4 text-center">🧪 Quiz interactif</h2>

    <div v-if="quiz">
      <h3 class="text-lg font-semibold mb-3 text-gray-800">{{ quiz.question }}</h3>

      <div v-for="(option, i) in quiz.options" :key="i" class="mb-2">
        <label class="block border p-2 rounded cursor-pointer"
               :class="{
                 'bg-green-100': isAnswered && quiz.answer.includes(i + 1),
                 'bg-red-100': isAnswered && selected === i + 1 && !quiz.answer.includes(i + 1)
               }">
          <input type="radio" :value="i + 1" v-model="selected" :disabled="isAnswered" class="mr-2" />
          {{ option }}
        </label>
      </div>

      <button @click="valider" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" :disabled="isAnswered">
        ✅ Valider
      </button>

      <div v-if="isAnswered" class="mt-4 p-3 bg-gray-50 rounded">
        <p class="text-sm text-green-700 font-semibold">Explication :</p>
        <p class="text-sm text-gray-700">{{ quiz.explanation }}</p>
      </div>
    </div>

    <div v-else>
      <p class="text-gray-600 text-center">Chargement du quiz...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from '~/plugins/supabase.client'

const quiz = ref(null)
const selected = ref(null)
const isAnswered = ref(false)

onMounted(async () => {
  const { data } = await supabase
    .from('quizzes')
    .select('*')
    .eq('niveau', 'BEPC') // 🔄 à adapter selon la page (BAC, Licence, etc.)
    .order('created_at', { ascending: false })
    .limit(1)

  quiz.value = data[0]
})

function valider() {
  isAnswered.value = true
}
</script>
