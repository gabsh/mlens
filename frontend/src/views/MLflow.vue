<template>
  <div class="panel">

    <div class="prompt">mlens@imdb:~$ <span class="cmd">mlflow runs --experiment imdb</span></div>
    <div class="toolbar">
      <button
        v-for="m in SORT_OPTS" :key="m"
        :class="['model-btn', sortBy === m && 'active']"
        @click="sortBy = m"
      >{{ m }}</button>
      <button class="action-btn" @click="loadRuns()" :disabled="loading" style="margin-left:auto">
        <span v-if="loading" class="spinner">{{ spinnerChar }}</span>
        <span v-else>[ refresh ]</span>
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <template v-if="sortedRuns.length">
      <div class="run-header">
        <span class="c-rank">#</span>
        <span class="c-name">run</span>
        <span class="c-score">{{ sortBy }}</span>
        <span class="c-hw">time(s)</span>
        <span class="c-hw">inf(ms)</span>
        <span class="c-hw">cpu</span>
        <span class="c-hw">ram</span>
      </div>
      <div
        v-for="(run, i) in sortedRuns" :key="run.name"
        :class="['run-row', selectedRun?.name === run.name && 'run-row--selected']"
        @click="selectedRun = run"
      >
        <span class="c-rank muted">{{ i + 1 }}</span>
        <span class="c-name">{{ run.name }}</span>
        <span class="c-score" :class="i === 0 && 'best'">{{ run[sortBy]?.toFixed(3) ?? '—' }}</span>
        <span class="c-hw muted">{{ run.train_duration_sec ?? '—' }}</span>
        <span class="c-hw muted">{{ run.inference_ms ?? '—' }}</span>
        <span class="c-hw muted">{{ run.cpu_percent != null ? run.cpu_percent + '%' : '—' }}</span>
        <span class="c-hw muted">{{ run.ram_used_gb != null ? run.ram_used_gb + ' GB' : '—' }}</span>
      </div>
    </template>

    <div v-else-if="!loading" class="empty">// no runs found</div>

  </div>

  <div class="panel">

    <template v-if="selectedRun">
      <div class="prompt">mlens@imdb:~$ <span class="cmd">inspect -- {{ selectedRun.name }}</span></div>

      <div class="section-title">hardware</div>
      <div class="hw-grid">
        <div v-for="row in hwRows" :key="row.label" class="hw-row">
          <span class="hw-key">{{ row.label }}</span>
          <div v-if="row.pct != null" class="hw-track">
            <div class="hw-bar" :class="row.cls" :style="{ width: row.pct + '%' }" />
          </div>
          <span class="hw-val">{{ row.val }}</span>
        </div>
        <div v-if="!hwRows.length" class="empty">// no hardware metrics</div>
      </div>

      <div class="section-title" style="margin-top: 20px">performance (ref)</div>
      <div class="perf-grid">
        <div v-for="m in PERF_METRICS" :key="m.key" class="perf-row">
          <span class="perf-key">{{ m.label }}</span>
          <span class="perf-val">{{ selectedRun[m.key]?.toFixed(4) ?? '—' }}</span>
        </div>
      </div>
    </template>

    <div v-else-if="!loading" class="awaiting">
      mlens@imdb:~$ <span>select a run to inspect...</span>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSpinner } from '../composables/useSpinner.js'
import { useRuns } from '../composables/useRuns.js'

const SORT_OPTS   = ['train_duration_sec', 'inference_ms', 'cpu_percent', 'ram_used_gb']
const PERF_METRICS = [
  { key: 'accuracy',  label: 'accuracy'  },
  { key: 'f1',        label: 'f1'        },
  { key: 'roc_auc',   label: 'roc_auc'   },
  { key: 'mcc',       label: 'mcc'       },
]

const sortBy = ref('train_duration_sec')
const selectedRun = ref(null)

const { runs, loading, error, loadRuns } = useRuns()
const { spinnerChar } = useSpinner()

const sortedRuns = computed(() =>
  [...runs.value].sort((a, b) => (a[sortBy.value] ?? Infinity) - (b[sortBy.value] ?? Infinity))
)

const hwRows = computed(() => {
  const r = selectedRun.value
  if (!r) return []
  return [
    r.train_duration_sec != null && { label: 'train time',  val: r.train_duration_sec + 's',  pct: null,          cls: '' },
    r.inference_ms       != null && { label: 'inference',   val: r.inference_ms + 'ms',        pct: null,          cls: '' },
    r.cpu_percent        != null && { label: 'cpu',         val: r.cpu_percent + '%',           pct: r.cpu_percent, cls: '' },
    r.ram_used_gb        != null && { label: 'ram',         val: r.ram_used_gb + ' GB',         pct: r.ram_percent, cls: 'hw-bar--ram' },
  ].filter(Boolean)
})
</script>

<style scoped>
.toolbar { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }

.run-header {
  display: flex; gap: 6px;
  font-size: 10px; color: #444; letter-spacing: 1.2px; text-transform: uppercase;
  border-bottom: 1px solid var(--border); padding-bottom: 4px;
}
.run-row {
  display: flex; gap: 6px;
  font-size: 13px; padding: 5px 4px;
  border-bottom: 1px solid #242424;
  cursor: pointer; transition: background 0.1s;
}
.run-row:hover { background: #242424; }
.run-row--selected { background: #262626; border-left: 2px solid var(--accent); padding-left: 2px; }
.c-rank { width: 20px; }
.c-name { flex: 1; }
.c-score { width: 68px; text-align: right; }
.c-hw { width: 58px; text-align: right; }
.muted { color: #555; }
.best { color: var(--accent); }

.section-title {
  font-size: 11px; color: #444; letter-spacing: 1.2px; text-transform: uppercase;
  border-bottom: 1px solid var(--border); padding-bottom: 4px;
}

.hw-grid { display: flex; flex-direction: column; gap: 10px; }
.hw-row { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.hw-key { width: 70px; color: #555; }
.hw-track { flex: 1; height: 2px; background: var(--border); }
.hw-bar { height: 100%; background: var(--primary-dim); transition: width 0.4s; }
.hw-bar--ram { background: #4c9faf; }
.hw-val { width: 70px; text-align: right; color: var(--primary-dim); }

.perf-grid { display: flex; flex-wrap: wrap; gap: 8px 20px; }
.perf-row { display: flex; gap: 8px; font-size: 12px; }
.perf-key { color: #555; }
.perf-val { color: var(--primary-dim); }
</style>
