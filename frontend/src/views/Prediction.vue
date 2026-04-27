<template>
  <div class="panel">

    <div class="prompt">mlens@imdb:~$ <span class="cmd">review</span></div>
    <div class="input-row">
      <span class="caret">&gt;</span>
      <textarea
        ref="textareaEl"
        class="textarea"
        v-model="text"
        placeholder="type a movie review..."
        :disabled="loading || explainLoading"
        @keydown.enter.exact.prevent="handleSubmit"
        @input="autoResize"
        rows="3"
      />
    </div>

    <div class="prompt" style="margin-top: 20px">mlens@imdb:~$ <span class="cmd">--model</span></div>
    <div class="model-groups">
      <div v-for="(groupModels, group) in modelGroups" :key="group" class="model-group">
        <span class="group-label">{{ group }}</span>
        <div class="group-btns">
          <button
            v-for="m in groupModels" :key="m"
            :class="['model-btn', selectedModel === m && 'active']"
            :disabled="!hasText || loading || explainLoading"
            @click="selectAndPredict(m)"
          >{{ m.split('_').slice(1).join('_') }}</button>
        </div>
      </div>
    </div>

    <div v-if="loading || explainLoading" class="loading-status">
      <span class="spinner">{{ spinnerChar }}</span>
      <span v-if="loading">predicting</span>
      <span v-if="loading && explainLoading"> · </span>
      <span v-if="explainLoading">explaining</span>
    </div>

    <div class="hint">mlens@imdb:~$ Shift+Enter for new line · click a model to predict</div>

  </div>

  <div class="panel">

    <div v-if="predictError" class="error">{{ predictError }}</div>

    <template v-if="prediction">
      <div class="prompt">mlens@imdb:~$ <span class="cmd">result</span></div>
      <div class="result-main">
        <span class="result-label" :class="prediction.label">{{ prediction.label.toUpperCase() }}</span>
        <span class="result-conf">{{ (prediction.confidence * 100).toFixed(1) }}%</span>
      </div>
      <div class="proba-bars">
        <div v-for="(prob, name) in prediction.probabilities" :key="name" class="proba-row">
          <span class="proba-name">{{ name }}</span>
          <div class="proba-track"><div class="proba-fill" :class="name" :style="{ width: (prob * 100) + '%' }" /></div>
          <span class="proba-val">{{ (prob * 100).toFixed(1) }}%</span>
        </div>
      </div>
      <div class="meta">model — {{ prediction.model_name }}</div>
    </template>

    <div v-if="explainError" class="error" style="margin-top: 16px">{{ explainError }}</div>

    <template v-if="explanation">
      <div class="prompt" style="margin-top: 24px">mlens@imdb:~$ <span class="cmd">explain --lime</span></div>
      <div class="lime-bars">
        <div v-for="[word, weight] in sortedExplanation" :key="word" class="lime-row">
          <span class="lime-word">{{ word }}</span>
          <div class="lime-track">
            <div class="lime-fill" :class="weight >= 0 ? 'pos' : 'neg'"
              :style="{ width: (Math.abs(weight) / maxWeight * 100) + '%' }" />
          </div>
          <span class="lime-val" :class="weight >= 0 ? 'pos' : 'neg'">
            {{ weight >= 0 ? '+' : '' }}{{ weight.toFixed(3) }}
          </span>
        </div>
      </div>
    </template>

    <div v-if="!prediction && !predictError" class="awaiting">
      mlens@imdb:~$ <span>awaiting query...</span>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { predict, explain } from '../api.js'
import { useSpinner } from '../composables/useSpinner.js'

const props = defineProps({ models: { type: Array, default: () => [] } })
const textareaEl = ref(null)
const text = ref('')
const selectedModel = ref('')
const loading = ref(false)
const prediction = ref(null)
const predictError = ref(null)
const explanation = ref(null)
const explainError = ref(null)
const explainLoading = ref(false)

const hasText = computed(() => text.value.trim().length > 0)
const canSubmit = computed(() => hasText.value && selectedModel.value)
const sortedExplanation = computed(() =>
  explanation.value ? [...explanation.value].sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])) : []
)
const maxWeight = computed(() =>
  sortedExplanation.value.length ? Math.max(...sortedExplanation.value.map(([, w]) => Math.abs(w)), 0.001) : 1
)

const modelGroups = computed(() => {
  const groups = {}
  for (const m of props.models) {
    const prefix = m.split('_')[0]
    if (!groups[prefix]) groups[prefix] = []
    groups[prefix].push(m)
  }
  return groups
})

function autoResize() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

watch(text, val => { if (!val) nextTick(autoResize) })

const { spinnerChar } = useSpinner()

function selectAndPredict(model) {
  if (!hasText.value || loading.value) return
  if (model === selectedModel.value) return
  selectedModel.value = model
  handleSubmit()
}

async function handleSubmit() {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  explainLoading.value = true
  prediction.value = null
  explanation.value = null
  predictError.value = null
  explainError.value = null

  await Promise.all([
    predict(text.value, selectedModel.value)
      .then(r => { prediction.value = r })
      .catch(e => { predictError.value = e.message })
      .finally(() => { loading.value = false }),
    explain(text.value, selectedModel.value)
      .then(r => { explanation.value = r.explanation })
      .catch(e => { explainError.value = e.message })
      .finally(() => { explainLoading.value = false }),
  ])
}
</script>

<style scoped>
.model-groups { display: flex; flex-direction: column; gap: 10px; }
.model-group { display: flex; align-items: center; gap: 10px; }

.group-label {
  width: 44px;
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  flex-shrink: 0;
}

.group-btns { display: flex; flex-wrap: wrap; gap: 5px; }

.input-row { display: flex; gap: 8px; align-items: flex-start; }
.caret { color: var(--primary-dim); padding-top: 2px; flex-shrink: 0; }
.textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--primary);
  font-family: var(--font);
  font-size: inherit;
  resize: none;
  outline: none;
  line-height: 1.8;
  overflow-y: auto;
  max-height: 220px;
  scrollbar-width: thin;
  scrollbar-color: #333 transparent;
}
.textarea::-webkit-scrollbar { width: 3px; }
.textarea::-webkit-scrollbar-track { background: transparent; }
.textarea::-webkit-scrollbar-thumb { background: #444; border-radius: 2px; }
.textarea::-webkit-scrollbar-thumb:hover { background: #666; }
.textarea::placeholder { color: #3a3a3a; }

.loading-status { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--primary-dim); }

.hint { font-size: 12px; color: #3a3a3a; margin-top: auto; }

.result-main { display: flex; align-items: baseline; gap: 14px; }
.result-label { font-size: 26px; font-weight: 700; letter-spacing: 3px; }
.result-label.positive { color: var(--positive); }
.result-label.negative { color: var(--negative); }
.result-conf { color: var(--primary-dim); font-size: 15px; }
.meta { font-size: 12px; color: #444; }

.proba-bars { display: flex; flex-direction: column; gap: 8px; }
.proba-row { display: flex; align-items: center; gap: 10px; }
.proba-name { width: 65px; font-size: 12px; color: var(--primary-dim); }
.proba-track { flex: 1; height: 2px; background: var(--border); }
.proba-fill { height: 100%; transition: width 0.4s; }
.proba-fill.positive { background: var(--positive); }
.proba-fill.negative { background: var(--negative); }
.proba-val { width: 45px; text-align: right; font-size: 12px; color: var(--primary-dim); }

.lime-bars { display: flex; flex-direction: column; gap: 7px; }
.lime-row { display: flex; align-items: center; gap: 10px; }
.lime-word { width: 110px; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lime-track { flex: 1; height: 2px; background: var(--border); }
.lime-fill { height: 100%; transition: width 0.3s; }
.lime-fill.pos { background: var(--positive); }
.lime-fill.neg { background: var(--negative); }
.lime-val { width: 55px; text-align: right; font-size: 12px; }
.lime-val.pos { color: var(--positive); }
.lime-val.neg { color: var(--negative); }
</style>
