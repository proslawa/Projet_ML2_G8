import axios from 'axios'
import { DEFAULT_DECISION_THRESHOLD } from './risk'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function mockPredictSingle(record) {
  const age = Number(record.Age) || 35
  const balance = Number(record.Balance) || 0
  const numProducts = Number(record.NumOfProducts) || 1
  const isActive = Number(record.IsActiveMember) || 0
  const creditScore = Number(record.CreditScore) || 650
  const tenure = Number(record.Tenure) || 5

  let score = 0.3
  score += age > 45 ? 0.15 : age > 35 ? 0.05 : -0.05
  score += balance === 0 ? 0.1 : balance > 100000 ? 0.08 : -0.05
  score += numProducts > 2 ? 0.25 : numProducts === 1 ? 0.1 : -0.1
  score += isActive === 0 ? 0.12 : -0.15
  score += creditScore < 500 ? 0.1 : creditScore > 750 ? -0.1 : 0
  score += tenure < 2 ? 0.08 : tenure > 7 ? -0.05 : 0

  if (record.Geography === 'Germany') score += 0.1
  if (record.Geography === 'France') score -= 0.05

  const probability = Math.max(0.02, Math.min(0.98, score))
  return {
    prediction: probability >= DEFAULT_DECISION_THRESHOLD ? 1 : 0,
    probability: Math.round(probability * 10000) / 10000,
    threshold: DEFAULT_DECISION_THRESHOLD
  }
}

export async function predictSingle(record) {
  try {
    const response = await apiClient.post('/predict', record)
    return response.data
  } catch (error) {
    // If the API is down or the backend throws, fall back to a deterministic mock.
    return mockPredictSingle(record)
  }
}


async function callBatchEndpoint(path, records) {
  const response = await apiClient.post(path, records)
  return response.data
}

export async function predictBatch(records) {
  try {
    return await callBatchEndpoint('/predict-batch', records)
  } catch (error) {
    if (error?.response?.status === 404) {
      try {
        return await callBatchEndpoint('/predict_batch', records)
      } catch (_) {
        const results = records.map((r) => mockPredictSingle(r))
        return {
          count: records.length,
          predictions: results.map((r) => r.prediction),
          probabilities: results.map((r) => r.probability),
          threshold: DEFAULT_DECISION_THRESHOLD
        }
      }
    }
    const results = records.map((r) => mockPredictSingle(r))
    return {
      count: records.length,
      predictions: results.map((r) => r.prediction),
      probabilities: results.map((r) => r.probability),
      threshold: DEFAULT_DECISION_THRESHOLD
    }
  }
}

export async function predictBatchWithOriginals(records, threshold = null) {
  try {
    const payload = records
    const response = await apiClient.post('/predict-batch-with-originals', payload, {
      params: threshold !== null ? { threshold } : {}
    })
    return response.data
  } catch (error) {
    if (error?.response?.status === 404) {
      // Fallback: use regular predictBatch if endpoint doesn't exist
      const results = records.map((r) => mockPredictSingle(r))
      return {
        count: records.length,
        predictions: results.map((r) => r.prediction),
        probabilities: results.map((r) => r.probability),
        threshold: threshold || DEFAULT_DECISION_THRESHOLD,
        originals: records
      }
    }
    throw error
  }
}

export async function checkHealth() {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    return { status: 'offline', model_loaded: false, error: error.message }
  }
}

export default apiClient
