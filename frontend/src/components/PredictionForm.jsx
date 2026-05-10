import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, RotateCcw, Loader2 } from 'lucide-react'
import { predictSingle } from '../utils/api'
import { getRiskLevel } from '../utils/risk'
import { defaultFormValues } from '../data/mockData'
import ChurnGauge from './ChurnGauge'

const fields = [
  { key: 'CreditScore', label: 'Credit Score', type: 'number', min: 350, max: 850, step: 1 },
  { key: 'Geography', label: 'Géographie', type: 'select', options: ['France', 'Germany', 'Spain'] },
  { key: 'Gender', label: 'Genre', type: 'select', options: ['Female', 'Male'] },
  { key: 'Age', label: 'Âge', type: 'number', min: 18, max: 92, step: 1 },
  { key: 'Tenure', label: 'Ancienneté (ans)', type: 'number', min: 0, max: 10, step: 1 },
  { key: 'Balance', label: 'Solde (€)', type: 'number', min: 0, max: 250898.09, step: 0.01 },
  { key: 'NumOfProducts', label: 'Nb de Produits', type: 'select', options: ['1', '2', '3', '4'] },
  { key: 'HasCrCard', label: 'Carte de Crédit', type: 'toggle' },
  { key: 'IsActiveMember', label: 'Membre Actif', type: 'toggle' },
  { key: 'EstimatedSalary', label: 'Salaire Estimé (€)', type: 'number', min: 11.58, max: 199992.48, step: 0.01 }
]

const numericConstraintByField = Object.fromEntries(
  fields.filter((f) => f.type === 'number').map((f) => [f.key, { min: f.min, max: f.max }])
)

export default function PredictionForm() {
  const [form, setForm] = useState({ ...defaultFormValues })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const update = (key, val) => setForm((prev) => ({ ...prev, [key]: val }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const payload = {
        ...form,
        CreditScore: Number(form.CreditScore),
        Age: Number(form.Age),
        Tenure: Number(form.Tenure),
        Balance: Number(form.Balance),
        NumOfProducts: Number(form.NumOfProducts),
        HasCrCard: Number(form.HasCrCard),
        IsActiveMember: Number(form.IsActiveMember),
        EstimatedSalary: Number(form.EstimatedSalary)
      }

      for (const [fieldName, bounds] of Object.entries(numericConstraintByField)) {
        const value = payload[fieldName]
        if (!Number.isFinite(value)) {
          throw new Error(`Le champ ${fieldName} doit être numérique.`)
        }
        if (value < bounds.min || value > bounds.max) {
          throw new Error(
            `Le champ ${fieldName} doit être entre ${bounds.min} et ${bounds.max}.`
          )
        }
      }

      const res = await predictSingle(payload)
      setResult(res)
    } catch (err) {
      setError(err?.message || 'Erreur lors de la prédiction.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setForm({ ...defaultFormValues })
    setResult(null)
    setError(null)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
      <div className="lg:col-span-3 space-y-0">
        <form onSubmit={handleSubmit} className="glass-card p-6 md:p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {fields.map((f) => (
              <div key={f.key}>
                <label className="form-label" htmlFor={`field-${f.key}`}>{f.label}</label>
                {f.type === 'number' && (
                  <input
                    id={`field-${f.key}`}
                    type="number"
                    className="form-input"
                    value={form[f.key]}
                    onChange={(e) => update(f.key, e.target.value)}
                    min={f.min}
                    max={f.max}
                    step={f.step}
                  />
                )}
                {f.type === 'select' && (
                  <select
                    id={`field-${f.key}`}
                    className="form-select"
                    value={form[f.key]}
                    onChange={(e) => update(f.key, e.target.value)}
                  >
                    {f.options.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                )}
                {f.type === 'toggle' && (
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      type="button"
                      className={`toggle-switch ${form[f.key] ? 'active' : ''}`}
                      onClick={() => update(f.key, form[f.key] ? 0 : 1)}
                      id={`field-${f.key}`}
                    />
                    <span className="text-sm opacity-60">{form[f.key] ? 'Oui' : 'Non'}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {error && (
            <div className="mt-6 text-sm text-red-500 bg-red-500/10 px-4 py-3 rounded-xl border border-red-500/20">
              {error}
            </div>
          )}

          <div className="flex gap-3 mt-8">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 rounded-xl
                         bg-brand text-white font-semibold text-sm
                         shadow-lg shadow-brand/20
                         hover:bg-brand-light disabled:opacity-60
                         transition-all duration-300"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              {loading ? 'Analyse en cours…' : 'Prédire le churn'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-2 px-5 py-3 rounded-xl
                         border border-black/10 dark:border-white/10 text-inherit opacity-60
                         hover:bg-black/5 dark:hover:bg-white/5 hover:opacity-100
                         transition-all duration-300"
            >
              <RotateCcw size={14} /> Réinitialiser
            </button>
          </div>
        </form>
      </div>

      <div className="lg:col-span-2 flex items-start justify-center">
        <AnimatePresence mode="wait">
          {result ? (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="glass-card p-8 flex flex-col items-center w-full"
            >
              <h3 className="font-syne font-semibold text-lg mb-6">Résultat de l'analyse</h3>
              <ChurnGauge probability={result.probability} threshold={result.threshold} />
              <div className="mt-6 w-full grid grid-cols-2 gap-3 text-center">
                <div className="bg-black/5 dark:bg-white/5 rounded-xl py-3 px-2">
                  <p className="text-[10px] opacity-50 uppercase tracking-wider mb-1 font-bold">Probabilité</p>
                  <p className="font-syne font-bold text-gold text-xl">
                    {(result.probability * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-black/5 dark:bg-white/5 rounded-xl py-3 px-2">
                  <p className="text-[10px] opacity-50 uppercase tracking-wider mb-1 font-bold">Seuil modèle</p>
                  <p className="font-syne font-bold text-brand-glow text-xl">
                    {result.threshold ?? 'Fixe'}
                  </p>
                </div>
              </div>
              <div className="mt-4 w-full bg-black/5 dark:bg-white/5 rounded-xl p-4">
                {(() => {
                  const risk = getRiskLevel(result.probability, result.threshold)

                  return (
                    <div className="grid grid-cols-1 gap-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-[10px] opacity-50 uppercase tracking-wider mb-1 font-bold">Classe prédite</p>
                          <p className="font-semibold">{risk.predictionLabel}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] opacity-50 uppercase tracking-wider mb-1 font-bold">Décision</p>
                          <p className={`font-bold ${risk.textClass}`}>{risk.decisionLabel}</p>
                        </div>
                      </div>

                      <div className="text-sm opacity-70">
                        {risk.isAtRisk
                          ? 'Client classé comme churner. Recommandation : contacter le client, proposer une offre de rétention.'
                          : 'Client classé comme non churner. Recommandation : surveillance régulière, pas d’action immédiate.'}
                      </div>
                    </div>
                  )
                })()}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card p-8 flex flex-col items-center justify-center w-full min-h-[340px] text-center"
            >
              <div className="w-16 h-16 rounded-2xl bg-brand-subtle flex items-center justify-center mb-4">
                <Send size={24} className="text-brand-glow" />
              </div>
              <p className="opacity-60 text-sm leading-relaxed">
                Remplissez le formulaire,<br />puis lancez la prédiction.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
