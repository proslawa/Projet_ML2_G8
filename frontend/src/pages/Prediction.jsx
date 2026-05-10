import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Users } from 'lucide-react'
import PredictionForm from '../components/PredictionForm'
import BatchUpload from '../components/BatchUpload'

const tabs = [
  { id: 'single', label: 'Prédiction Unique', icon: User },
  { id: 'batch', label: 'Analyse Batch', icon: Users }
]

export default function Prediction() {
  const [activeTab, setActiveTab] = useState('single')

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10"
        >
          <h1 className="font-syne font-bold text-3xl md:text-4xl">
            Interface de <span className="text-gradient-gold">Prédiction</span>
          </h1>
          <p className="opacity-50 mt-2 max-w-xl font-dm">
            Évaluez le risque de churn d'un client ou analysez un fichier complet en batch pour une vision globale.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex gap-2 mb-8"
        >
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold tracking-wide transition-all duration-300 ${
                  isActive
                    ? 'bg-brand text-white shadow-lg shadow-brand/20'
                    : 'bg-black/5 dark:bg-white/5 opacity-60 hover:opacity-100 hover:bg-black/10 dark:hover:bg-white/10'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            )
          })}
        </motion.div>

        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {activeTab === 'single' ? <PredictionForm /> : <BatchUpload />}
        </motion.div>
      </div>
    </div>
  )
}
