<template>
  <Teleport to="body">
    <div v-if="visible" class="overlay" @keydown.enter="close" tabindex="0" ref="overlayEl">
      <div class="modal">

        <pre class="logo">
<span style="color:#f5e6c8">███╗   ███╗██╗     ███████╗███╗   ██╗███████╗</span>
<span style="color:#dfc49a">████╗ ████║██║     ██╔════╝████╗  ██║██╔════╝</span>
<span style="color:#c49a6c">██╔████╔██║██║     █████╗  ██╔██╗ ██║███████╗</span>
<span style="color:#a0744a">██║╚██╔╝██║██║     ██╔══╝  ██║╚██╗██║╚════██║</span>
<span style="color:#7d5235">██║ ╚═╝ ██║███████╗███████╗██║ ╚████║███████║</span>
<span style="color:#5c3a22">╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝</span></pre>

        <p class="subtitle">mlens@imdb:~$ <span class="cmd">./welcome.sh</span></p>

        <div class="section">
          <p class="label">about</p>
          <p>
            <strong>mlens</strong> is a binary sentiment classification benchmark trained on the
            Stanford IMDB dataset (50k reviews). It benchmarks every combination of
            embedding × classifier, tracks experiments with MLflow, and serves
            predictions + LIME explanations via a FastAPI backend.
          </p>
        </div>

        <div class="section">
          <p class="label">embeddings</p>
          <div class="tags">
            <span class="tag">TF-IDF</span>
            <span class="tag">Bag of Words</span>
            <span class="tag coming">GloVe <em>coming soon</em></span>
            <span class="tag coming">BERT <em>coming soon</em></span>
          </div>
        </div>

        <div class="section">
          <p class="label">classifiers</p>
          <div class="tags">
            <span class="tag">Logistic Regression</span>
            <span class="tag">SVM</span>
            <span class="tag">Random Forest</span>
            <span class="tag">LightGBM</span>
            <span class="tag">XGBoost</span>
            <span class="tag">Naive Bayes</span>
            <span class="tag">MLP</span>
          </div>
        </div>

        <div class="section">
          <p class="label">stack</p>
          <div class="tags">
            <span class="tag">Python 3.11</span>
            <span class="tag">scikit-learn</span>
            <span class="tag">FastAPI</span>
            <span class="tag">MLflow</span>
            <span class="tag">LIME</span>
            <span class="tag">Vue 3</span>
            <span class="tag">Docker</span>
          </div>
        </div>

        <div class="section">
          <p class="label">source</p>
          <p>
            <a href="https://github.com/gabsh/mlens" target="_blank" class="link">
              github.com/gabsh/mlens
            </a>
          </p>
        </div>

        <div class="footer">
          <label class="dont-show">
            <input type="checkbox" v-model="dontShow" />
            don't show again
          </label>
          <button class="enter-btn" @click="close">press Enter to continue</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const visible = ref(false)
const dontShow = ref(false)
const overlayEl = ref(null)

onMounted(() => {
  if (!localStorage.getItem('mlens_welcome_dismissed')) {
    visible.value = true
    setTimeout(() => overlayEl.value?.focus(), 50)
  }
})

function close() {
  if (dontShow.value) localStorage.setItem('mlens_welcome_dismissed', '1')
  visible.value = false
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  outline: none;
}

.modal {
  width: 680px;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scrollbar-width: none;
}

.logo {
  font-family: var(--font);
  font-size: 5.5px;
  line-height: 1.2;
  white-space: pre;
  text-align: center;
}

.subtitle {
  font-size: 13px;
  color: var(--primary-dim);
}
.cmd { color: var(--primary); }

.section { display: flex; flex-direction: column; gap: 8px; }

.label {
  font-size: 11px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

p { font-size: 13px; color: var(--primary-dim); line-height: 1.7; }

.tags { display: flex; flex-wrap: wrap; gap: 6px; }

.tag {
  font-size: 12px;
  color: var(--primary-dim);
  border: 1px solid var(--border);
  padding: 2px 10px;
  border-radius: 2px;
}

.tag.coming {
  opacity: 0.45;
  border-style: dashed;
}
.tag.coming em { font-style: normal; font-size: 10px; margin-left: 4px; }

.link { color: var(--accent); text-decoration: none; }
.link:hover { text-decoration: underline; }

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.dont-show {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #444;
  cursor: pointer;
}
.dont-show input { accent-color: var(--accent); cursor: pointer; }

.enter-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--primary-dim);
  font-family: var(--font);
  font-size: 13px;
  padding: 6px 18px;
  cursor: pointer;
  transition: all 0.1s;
}
.enter-btn:hover { border-color: var(--accent); color: var(--primary); }
</style>
