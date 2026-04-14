<template>
  <div class="panel">

    <div class="prompt">mlens@imdb:~$ <span class="cmd">ranking --metric</span></div>
    <div class="toolbar">
      <button
        v-for="m in METRICS" :key="m"
        :class="['model-btn', metric === m && 'active']"
        @click="metric = m"
      >{{ m }}</button>
      <button class="action-btn" @click="loadRuns()" :disabled="loading" style="margin-left:auto">
        <span v-if="loading" class="spinner">{{ spinnerChar }}</span>
        <span v-else>[ refresh ]</span>
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <template v-if="sortedRuns.length">
      <div class="rank-header">
        <span class="col-rank">#</span>
        <span class="col-name">model</span>
        <span class="col-val">{{ metric }}</span>
      </div>
      <div
        v-for="(run, i) in sortedRuns" :key="run.name"
        :class="['rank-row', selectedRun?.name === run.name && 'rank-row--selected', i === 0 && 'rank-row--best']"
        @click="selectedRun = run"
      >
        <span class="col-rank">{{ i + 1 }}</span>
        <span class="col-name">{{ run.name }}</span>
        <span class="col-val" :class="i === 0 && 'best'">{{ run[metric]?.toFixed(4) ?? '—' }}</span>
      </div>
    </template>

    <div v-else-if="!loading" class="empty">// no runs found</div>

  </div>

  <div class="panel">

    <template v-if="runs.length">
      <div class="prompt">mlens@imdb:~$ <span class="cmd">heatmap --metric {{ metric }}</span></div>
      <div class="heatmap-wrap">
        <div class="heatmap" :style="{ gridTemplateColumns: `90px repeat(${classifiers.length}, 1fr)` }">
          <div class="hcell corner" />
          <div v-for="clf in classifiers" :key="clf" class="hcell header">{{ clf }}</div>
          <template v-for="emb in embeddings" :key="emb">
            <div class="hcell row-label">{{ emb }}</div>
            <div
              v-for="clf in classifiers" :key="clf"
              class="hcell data"
              :style="cellStyle(emb, clf)"
              :title="`${emb}_${clf}: ${getValue(emb, clf)}`"
            >{{ getValue(emb, clf) }}</div>
          </template>
        </div>
      </div>

      <template v-if="selectedRun">
        <div class="prompt" style="margin-top: 20px">
          mlens@imdb:~$ <span class="cmd">detail -- {{ selectedRun.name }}</span>
        </div>
        <div class="detail-grid">
          <div class="detail-row" v-for="m in ALL_METRICS" :key="m.key">
            <span class="detail-key">{{ m.label }}</span>
            <div class="detail-track">
              <div class="detail-bar" :style="{ width: ((selectedRun[m.key] ?? 0) * (m.scale ?? 1) * 100) + '%' }" />
            </div>
            <span class="detail-val">{{ selectedRun[m.key]?.toFixed(m.digits ?? 4) ?? '—' }}</span>
          </div>
        </div>
      </template>

      <div v-else class="awaiting">// click a row to see details</div>

      <div class="prompt" style="margin-top: 20px">mlens@imdb:~$ <span class="cmd">compare --all</span></div>
      <div class="chart-wrap">
        <Bar :data="chartData" :options="chartOptions" />
      </div>
    </template>

    <div v-else-if="!loading" class="awaiting">mlens@imdb:~$ <span>awaiting data...</span></div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useSpinner } from '../composables/useSpinner.js'
import { useRuns } from '../composables/useRuns.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const METRICS = ['accuracy', 'f1', 'roc_auc', 'precision', 'recall', 'mcc']
const ALL_METRICS = [
  { key: 'accuracy',  label: 'accuracy',  digits: 4 },
  { key: 'f1',        label: 'f1',        digits: 4 },
  { key: 'roc_auc',   label: 'roc_auc',   digits: 4 },
  { key: 'precision', label: 'precision', digits: 4 },
  { key: 'recall',    label: 'recall',    digits: 4 },
  { key: 'mcc',       label: 'mcc',       digits: 4 },
  { key: 'log_loss',  label: 'log_loss',  digits: 4, scale: 0.1 },
]

const metric = ref('accuracy')
const selectedRun = ref(null)

const { runs, loading, error, loadRuns } = useRuns()
const { spinnerChar } = useSpinner()

const runMap = computed(() => new Map(runs.value.map(r => [r.name, r])))
const embeddings = computed(() => [...new Set(runs.value.map(r => r.name.split('_')[0]))].sort())
const classifiers = computed(() => [...new Set(runs.value.map(r => r.name.split('_').slice(1).join('_')))].sort())
const sortedRuns = computed(() => [...runs.value].sort((a, b) => (b[metric.value] ?? 0) - (a[metric.value] ?? 0)))
const minVal = computed(() => Math.min(...runs.value.map(r => r[metric.value] ?? 1)))
const maxVal = computed(() => Math.max(...runs.value.map(r => r[metric.value] ?? 0)))

function getValue(emb, clf) {
  const run = runMap.value.get(`${emb}_${clf}`)
  return run?.[metric.value] != null ? run[metric.value].toFixed(4) : '—'
}

function cellStyle(emb, clf) {
  const run = runMap.value.get(`${emb}_${clf}`)
  if (!run || run[metric.value] == null) return { background: '#222', color: '#333' }
  const t = (run[metric.value] - minVal.value) / (maxVal.value - minVal.value || 1)
  const r2 = Math.round(17 + t * (245 - 17))
  const g2 = Math.round(17 + t * (158 - 17))
  const b2 = Math.round(17 + t * (11  - 17))
  return { background: `rgb(${r2},${g2},${b2})`, color: t > 0.45 ? '#111' : '#666' }
}

// Bar chart: compare all models on accuracy, f1, roc_auc
const CHART_METRICS = ['accuracy', 'f1', 'roc_auc', 'mcc']
const CHART_COLORS  = ['#e05555', '#f87171', '#fca5a5', '#fecaca']

const chartData = computed(() => ({
  labels: sortedRuns.value.map(r => r.name),
  datasets: CHART_METRICS.map((m, i) => ({
    label: m,
    data: sortedRuns.value.map(r => r[m] ?? 0),
    backgroundColor: CHART_COLORS[i],
    borderColor: CHART_COLORS[i],
    borderWidth: 0,
  })),
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#aaa', font: { family: 'Courier New', size: 11 } } },
    tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(4)}` } },
  },
  scales: {
    x: {
      ticks: { color: '#555', font: { family: 'Courier New', size: 10 }, maxRotation: 45 },
      grid: { color: '#222' },
    },
    y: {
      min: 0, max: 1,
      ticks: { color: '#555', font: { family: 'Courier New', size: 10 } },
      grid: { color: '#222' },
    },
  },
}
</script>

<style scoped>
.toolbar { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }

.rank-header {
  display: flex; gap: 8px;
  font-size: 11px; color: #444; letter-spacing: 1px;
  border-bottom: 1px solid var(--border); padding-bottom: 4px;
}
.rank-row {
  display: flex; gap: 8px;
  font-size: 13px; padding: 5px 4px;
  border-bottom: 1px solid #242424;
  cursor: pointer; transition: background 0.1s;
}
.rank-row:hover { background: #242424; }
.rank-row--selected { background: #252525; }
.col-rank { width: 20px; color: #444; }
.col-name { flex: 1; }
.col-val { width: 70px; text-align: right; color: var(--primary-dim); }
.best { color: var(--accent) !important; }

.heatmap-wrap { overflow-x: auto; }
.heatmap { display: grid; gap: 2px; }
.hcell { padding: 5px 8px; font-size: 12px; text-align: center; }
.corner { background: transparent; }
.header { color: #444; background: #222; font-size: 11px; }
.row-label { color: var(--primary); background: #222; text-align: left; }
.data { font-weight: 500; }

.detail-grid { display: flex; flex-direction: column; gap: 10px; }
.detail-row { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.detail-key { width: 80px; color: #555; }
.detail-track { flex: 1; height: 2px; background: var(--border); }
.detail-bar { height: 100%; background: var(--accent); transition: width 0.4s; }
.detail-val { width: 55px; text-align: right; color: var(--primary-dim); }

.chart-wrap { height: 200px; }
</style>
