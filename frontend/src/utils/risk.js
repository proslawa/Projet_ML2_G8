export const DEFAULT_DECISION_THRESHOLD = 0.45

export function normalizeThreshold(threshold) {
  const value = Number(threshold)
  return Number.isFinite(value) && value >= 0 && value <= 1
    ? value
    : DEFAULT_DECISION_THRESHOLD
}

export function getRiskLevel(probability, threshold = DEFAULT_DECISION_THRESHOLD) {
  const score = Number(probability) || 0
  const limit = normalizeThreshold(threshold)
  const isAtRisk = score >= limit

  return {
    isAtRisk,
    label: isAtRisk ? 'Risque élevé' : 'Risque faible',
    shortLabel: isAtRisk ? 'Élevé' : 'Faible',
    predictionLabel: isAtRisk ? 'Churner' : 'Non churner',
    decisionLabel: isAtRisk ? 'À risque' : 'Stable',
    color: isAtRisk ? '#EF4444' : '#10B981',
    glowClass: isAtRisk ? 'gauge-glow-red' : 'gauge-glow-green',
    textClass: isAtRisk
      ? 'text-red-600 dark:text-red-400'
      : 'text-emerald-600 dark:text-emerald-400',
    badgeClass: isAtRisk
      ? 'bg-red-500/15 text-red-600 dark:text-red-400'
      : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
  }
}
