<template>
  <div class="window">

    <div class="titlebar">
      <pre class="ascii-logo">
<span style="color:#f5e6c8">███╗   ███╗██╗     ███████╗███╗   ██╗███████╗</span>
<span style="color:#dfc49a">████╗ ████║██║     ██╔════╝████╗  ██║██╔════╝</span>
<span style="color:#c49a6c">██╔████╔██║██║     █████╗  ██╔██╗ ██║███████╗</span>
<span style="color:#a0744a">██║╚██╔╝██║██║     ██╔══╝  ██║╚██╗██║╚════██║</span>
<span style="color:#7d5235">██║ ╚═╝ ██║███████╗███████╗██║ ╚████║███████║</span>
<span style="color:#5c3a22">╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝</span></pre>

      <nav class="nav">
        <button :class="['nav-btn', view === 'prediction' && 'active']" @click="view = 'prediction'">prediction</button>
        <button :class="['nav-btn', view === 'results'    && 'active']" @click="view = 'results'">results</button>
        <button :class="['nav-btn', view === 'run'         && 'active']" @click="view = 'run'">run</button>
      </nav>

    </div>

    <WelcomeModal />

    <div class="panels">
      <PredictionView v-if="view === 'prediction'" :models="models" />
      <ResultsView    v-else-if="view === 'results'" />
      <RunView        v-else />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHealth } from './api.js'
import PredictionView from './views/Prediction.vue'
import ResultsView    from './views/Results.vue'
import RunView        from './views/Run.vue'
import WelcomeModal   from './views/WelcomeModal.vue'

const view = ref('prediction')
const models = ref([])

onMounted(async () => {
  try {
    const result = await getHealth()
    models.value = result.models_loaded
  } catch {}
})
</script>

<style>
:root {
  --primary: #ffffff;
  --primary-dim: rgba(240,240,240,0.65);
  --bg: #161616;
  --bg-panel: #1c1c1c;
  --border: #2a2a2a;
  --font: 'Courier New', Courier, monospace;
  --positive: #4caf6e;
  --negative: #e05555;
  --accent: #c49a6c;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--primary);
  font-family: var(--font);
  font-size: 14px;
  font-weight: 500;
  -webkit-font-smoothing: antialiased;
}

.window {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

/* ── Titlebar ── */
.titlebar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 6px 16px;
  background: #252525;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  user-select: none;
  gap: 20px;
}

.ascii-logo {
  font-family: var(--font);
  font-size: 5px;
  line-height: 1.2;
  white-space: pre;
}

.nav { display: flex; gap: 2px; }

.nav-btn {
  background: none;
  border: none;
  color: var(--primary-dim);
  font-family: var(--font);
  font-size: 13px;
  padding: 4px 14px;
  cursor: pointer;
  transition: color 0.12s;
  border-bottom: 1px solid transparent;
}
.nav-btn:hover { color: var(--primary); }
.nav-btn.active { color: var(--primary); border-bottom-color: var(--accent); }


/* ── Panels ── */
.panels {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 14px 16px;
  gap: 14px;
}

/* ── Shared panel layout ── */
.panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px 22px;
  overflow-y: auto;
  gap: 12px;
  scrollbar-width: thin;
  scrollbar-color: #333 transparent;
}
.panel::-webkit-scrollbar { width: 3px; }
.panel::-webkit-scrollbar-track { background: transparent; }
.panel::-webkit-scrollbar-thumb { background: #444; border-radius: 2px; }
.panel::-webkit-scrollbar-thumb:hover { background: #666; }

.panel > * { flex-shrink: 0; }

/* ── Terminal prompt ── */
.prompt { font-size: 13px; color: var(--primary-dim); }
.prompt .cmd { color: var(--primary); }

/* ── Shared buttons ── */
.model-btn, .action-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--primary-dim);
  font-family: var(--font);
  font-size: 13px;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.1s;
}
.model-btn:hover, .action-btn:hover:not(:disabled) { border-color: #555; color: var(--primary); }
.model-btn.active { border-color: var(--accent); color: var(--primary); background: #252525; }
.action-btn:disabled { opacity: 0.25; cursor: not-allowed; }
.model-btn:disabled { opacity: 0.3; cursor: default; }

/* ── Shared status ── */
.empty    { font-size: 13px; color: #444; }
.error    { font-size: 13px; color: var(--negative); }
.awaiting { font-size: 13px; color: #444; }
.spinner  { font-size: 15px; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.blink { animation: blink 1.2s infinite; }
</style>
