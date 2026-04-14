<template>
  <Teleport to="body">
    <div v-if="visible" class="overlay" @keydown.enter="close" tabindex="-1" ref="overlayRef">
      <div class="modal">
        <div class="modal-titlebar">
          <span>mlens@imdb:~$ ./welcome.sh</span>
          <button class="close-btn" @click="close">✕</button>
        </div>

        <div class="modal-body">
          <pre class="ascii">
<span style="color:#f5e6c8">███╗   ███╗██╗     ███████╗███╗   ██╗███████╗</span>
<span style="color:#dfc49a">████╗ ████║██║     ██╔════╝████╗  ██║██╔════╝</span>
<span style="color:#c49a6c">██╔████╔██║██║     █████╗  ██╔██╗ ██║███████╗</span>
<span style="color:#a0744a">██║╚██╔╝██║██║     ██╔══╝  ██║╚██╗██║╚════██║</span>
<span style="color:#7d5235">██║ ╚═╝ ██║███████╗███████╗██║ ╚████║███████║</span>
<span style="color:#5c3a22">╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝</span></pre>

          <div class="section">
            <div class="section-title">// about</div>
            <p><span class="hl">mlens</span> is a binary sentiment classification benchmark trained on the <span class="hl">Stanford IMDB dataset</span> (50k reviews). It benchmarks every combination of embedding × classifier, tracks experiments with MLflow, and serves predictions + LIME explanations via a FastAPI backend.</p>
          </div>

          <div class="section">
            <div class="section-title">// embeddings</div>
            <div class="tags">
              <span class="tag">TF-IDF</span>
              <span class="tag">Bag of Words</span>
              <span class="tag coming">GloVe <em>coming soon</em></span>
              <span class="tag coming">BERT <em>coming soon</em></span>
            </div>
          </div>

          <div class="section">
            <div class="section-title">// classifiers</div>
            <div class="tags">
              <span class="tag">Logistic Regression</span>
              <span class="tag">SVM</span>
              <span class="tag">Random Forest</span>
              <span class="tag">LightGBM</span>
              <span class="tag">XGBoost</span>
              <span class="tag">Naive Bayes</span>
              <span class="tag coming">MLP <em>coming soon</em></span>
            </div>
          </div>

          <div class="section">
            <div class="section-title">// stack</div>
            <div class="stack-grid">
              <div class="stack-item"><span class="stack-key">embeddings</span><span class="stack-val">TF-IDF · Bag of Words</span></div>
              <div class="stack-item"><span class="stack-key">classifiers</span><span class="stack-val">scikit-learn · LightGBM · XGBoost</span></div>
              <div class="stack-item"><span class="stack-key">tracking  </span><span class="stack-val">MLflow</span></div>
              <div class="stack-item"><span class="stack-key">explainability</span><span class="stack-val">LIME</span></div>
              <div class="stack-item"><span class="stack-key">backend   </span><span class="stack-val">FastAPI (Python 3.11)</span></div>
              <div class="stack-item"><span class="stack-key">frontend  </span><span class="stack-val">Vue 3 + Vite · nginx</span></div>
              <div class="stack-item"><span class="stack-key">infra     </span><span class="stack-val">Docker</span></div>
              <div class="stack-item"><span class="stack-key">github    </span><span class="stack-val"><a class="gh-link" href="https://github.com/gabsh/mlens" target="_blank" rel="noopener">github.com/gabsh/mlens</a></span></div>
            </div>
          </div>

          <div class="footer">
            <button class="enter-btn" @click="close">
              [ Press Enter to continue ]
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const visible = ref(false)
const overlayRef = ref(null)

onMounted(() => {
  visible.value = true
  setTimeout(() => overlayRef.value?.focus(), 50)
})

function close() {
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
  z-index: 100;
  outline: none;
}

.modal {
  width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--primary-dim);
  background: var(--bg-panel);
  font-family: var(--font);
}

.modal-titlebar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  background: #252525;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  color: var(--primary-dim);
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 12px;
  font-family: var(--font);
  padding: 0;
}
.close-btn:hover { color: var(--primary); }

.modal-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scrollbar-width: none;
}
.modal-body::-webkit-scrollbar { display: none; }

.ascii {
  font-size: 9px;
  line-height: 1.2;
  white-space: pre;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  color: var(--primary);
  opacity: 0.65;
  font-size: 11px;
  letter-spacing: 0.08em;
}

p {
  color: var(--primary);
  opacity: 0.9;
  line-height: 1.7;
  font-size: 13px;
}

.hl { color: var(--primary); opacity: 1; font-weight: bold; }

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  border: 1px solid var(--primary-dim);
  color: var(--primary);
  padding: 2px 10px;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.tag.coming {
  opacity: 0.4;
  border-style: dashed;
}
.tag.coming em { font-style: normal; font-size: 10px; margin-left: 4px; }

.stack-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 24px;
}

.stack-item {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.stack-key {
  color: var(--primary);
  opacity: 0.6;
  white-space: pre;
  min-width: 80px;
}

.stack-val { color: var(--primary); opacity: 1; }

.gh-link {
  color: var(--primary);
  opacity: 0.85;
  text-decoration: none;
  border-bottom: 1px solid var(--primary-dim);
}
.gh-link:hover { opacity: 1; }

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}


.enter-btn {
  background: none;
  border: 1px solid var(--primary-dim);
  color: var(--primary);
  font-family: var(--font);
  font-size: 13px;
  padding: 6px 16px;
  cursor: pointer;
  transition: all 0.1s;
}
.enter-btn:hover {
  background: var(--primary);
  color: var(--bg);
}
</style>
