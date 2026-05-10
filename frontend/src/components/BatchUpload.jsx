import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileSpreadsheet, Download, AlertCircle, Loader2, Users } from 'lucide-react'
import Papa from 'papaparse'
import { predictBatchWithOriginals } from '../utils/api'
import { getRiskLevel } from '../utils/risk'

export default function BatchUpload() {
  const [file, setFile] = useState(null)
  const [records, setRecords] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState(null)

  const handleFile = useCallback((f) => {
    if (!f || !f.name.endsWith('.csv')) {
      setError('Veuillez sélectionner un fichier CSV.')
      return
    }
    setError(null)
    setFile(f)
    setResults(null)
    Papa.parse(f, {
      header: true,
      skipEmptyLines: true,
      complete: (res) => setRecords(res.data),
      error: () => setError('Erreur de lecture du fichier CSV.')
    })
  }, [])

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await predictBatchWithOriginals(records)
      setResults(res)
    } catch (err) {
      console.error('Batch prediction error:', err)
      const errorMsg = err?.response?.data?.detail || err?.message || 'Erreur lors de la prédiction batch.'
      setError(`Erreur: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const exportCSV = () => {
    if (!results) return
    // Use originals from API response if available, otherwise fall back to parsed records
    const originals = results.originals || records
    const rows = originals.map((r, i) => ({
      ...r,
      churn_probability: results.probabilities[i]?.toFixed(4),
      churn_prediction: results.predictions[i] === 1 ? 'Churner' : 'Non-Churner',
      threshold_used: results.threshold,
      risk_level: getRiskLevel(results.probabilities[i], results.threshold).shortLabel
    }))
    const csv = Papa.unparse(rows)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'churn_predictions.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadPDF = () => {
    if (!results || !results.report_pdf) return
    // Decode base64 PDF
    const binaryString = atob(results.report_pdf)
    const bytes = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    const blob = new Blob([bytes], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'churn_report.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }

  const riskStats = results ? {
    stable: results.probabilities.filter((p) => !getRiskLevel(p, results.threshold).isAtRisk).length,
    atRisk: results.probabilities.filter((p) => getRiskLevel(p, results.threshold).isAtRisk).length
  } : null

  return (
    <div className="space-y-6">
      <div
        className={`drop-zone p-10 text-center cursor-pointer transition-all ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => document.getElementById('csv-input').click()}
      >
        <input
          id="csv-input"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="w-16 h-16 rounded-2xl bg-brand-subtle flex items-center justify-center mx-auto mb-4">
          <Upload size={32} className="text-brand-glow" />
        </div>
        <p className="text-inherit opacity-70 text-sm">
          Glissez un fichier CSV ici ou <span className="text-brand-glow font-bold underline">parcourir</span>
        </p>
        <p className="opacity-40 text-xs mt-2">
          Rassurez vous que les colonnes nécessaires sont présentes dans le fichier importé (CreditScore, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary). Le preprocessing s'exécutera automatiquement.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-500 text-sm bg-red-500/10 px-4 py-3 rounded-xl border border-red-500/20">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {file && records.length > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-brand-subtle flex items-center justify-center">
                <FileSpreadsheet size={20} className="text-brand-glow" />
              </div>
              <div>
                <p className="text-inherit text-sm font-semibold">{file.name}</p>
                <p className="opacity-50 text-xs">{records.length} lignes détectées</p>
              </div>
            </div>
            <button
              onClick={handlePredict}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand text-white font-semibold text-sm shadow-lg disabled:opacity-60 transition-all hover:bg-brand-light"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Users size={14} />}
              {loading ? 'Analyse…' : 'Lancer le batch'}
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-black/5 dark:border-white/5">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-black/5 dark:bg-white/5">
                  {Object.keys(records[0] || {}).slice(0, 8).map((k) => (
                    <th key={k} className="px-4 py-3 text-left opacity-40 font-bold uppercase tracking-wider whitespace-nowrap">{k}</th>
                  ))}
                  {results && <th className="px-4 py-3 text-left text-gold font-bold uppercase tracking-wider">Score</th>}
                  {results && <th className="px-4 py-3 text-left text-gold font-bold uppercase tracking-wider">Prediction</th>}
                  {results && <th className="px-4 py-3 text-left text-gold font-bold uppercase tracking-wider">Risque</th>}
                </tr>
              </thead>
              <tbody>
                {records.slice(0, 10).map((row, i) => (
                  <tr key={i} className="border-t border-black/5 dark:border-white/5 hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors">
                    {Object.values(row).slice(0, 8).map((v, j) => (
                      <td key={j} className="px-4 py-3 opacity-80 whitespace-nowrap">{v}</td>
                    ))}
                    {results && (
                      <>
                        <td className="px-4 py-3 font-bold">{(results.probabilities[i] * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${results.predictions[i] ? 'bg-red-500/15 text-red-600 dark:text-red-400' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'}`}>
                            {results.predictions[i] ? 'CHURN' : 'OK'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${getRiskLevel(results.probabilities[i], results.threshold).badgeClass}`}>
                            {getRiskLevel(results.probabilities[i], results.threshold).shortLabel}
                          </span>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {records.length > 10 && (
            <p className="text-xs opacity-40 mt-3 text-center italic">
              Affichage des 10 premières lignes sur {records.length}
            </p>
          )}
        </motion.div>
      )}

      <AnimatePresence>
        {results && riskStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-4"
          >
            {[
              { label: 'Total clients', value: results.count, color: 'text-inherit' },
              { label: 'Sous le seuil', value: riskStats.stable, color: 'text-emerald-600 dark:text-emerald-400' },
              { label: 'Au-dessus du seuil', value: riskStats.atRisk, color: 'text-red-600 dark:text-red-400' }
            ].map((stat, idx) => (
              <div key={idx} className="glass-card p-5 text-center">
                <p className={`text-2xl font-syne font-bold ${stat.color}`}>{stat.value}</p>
                <p className="text-[10px] opacity-40 uppercase tracking-widest mt-1 font-bold">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {results && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-center gap-4 flex-wrap">
          <button
            onClick={downloadPDF}
            disabled={!results.report_pdf}
            className="flex items-center gap-2 px-8 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 font-bold text-sm hover:bg-red-500/15 transition-all shadow-lg shadow-red-500/5 disabled:opacity-50"
          >
            <Download size={16} /> Rapport PDF
          </button>
          <button
            onClick={exportCSV}
            className="flex items-center gap-2 px-8 py-3 rounded-xl bg-gold/5 border border-gold/20 text-gold font-bold text-sm hover:bg-gold/10 transition-all shadow-lg shadow-gold/5"
          >
            <Download size={16} /> Export CSV
          </button>
        </motion.div>
      )}
    </div>
  )
}
