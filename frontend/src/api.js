async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const getHealth = () => request('/health')

export const getMlflowHealth = () => request('/health/mlflow')

export const getMetrics = () => request('/metrics')

export const predict = (text, modelName) =>
  request('/predict/', {
    method: 'POST',
    body: JSON.stringify({ text, model_name: modelName }),
  })

export const explain = (text, modelName, numFeatures = 10) =>
  request('/explain/', {
    method: 'POST',
    body: JSON.stringify({ text, model_name: modelName, num_features: numFeatures }),
  })

export const getRoc = () => request('/roc')
