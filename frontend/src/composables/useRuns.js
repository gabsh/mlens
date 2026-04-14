import { ref, onMounted } from 'vue'
import { getMetrics } from '../api.js'

export function useRuns() {
  const runs = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function loadRuns(onLoaded) {
    loading.value = true; error.value = null
    try { runs.value = await getMetrics(); onLoaded?.() }
    catch (e) { error.value = e.message }
    finally { loading.value = false }
  }

  onMounted(() => loadRuns())
  return { runs, loading, error, loadRuns }
}
