import { ref, computed, onMounted, onUnmounted } from 'vue'

const SPINNER = '⣾⣽⣻⢿⡿⣟⣯⣷'

export function useSpinner() {
  const spinnerIdx = ref(0)
  let timer = null
  onMounted(() => { timer = setInterval(() => { spinnerIdx.value = (spinnerIdx.value + 1) % SPINNER.length }, 80) })
  onUnmounted(() => clearInterval(timer))
  return { spinnerChar: computed(() => SPINNER[spinnerIdx.value]) }
}
