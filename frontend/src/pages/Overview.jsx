import { motion } from 'framer-motion'
import { TrendingUp, Target, Zap, Users } from 'lucide-react'
import MetricCard from '../components/MetricCard'
import AnalyticsGallery from '../components/AnalyticsGallery'
import { metrics } from '../data/mockData'
import { allAnalytics } from '../data/edaData'

export default function Overview() {
  const modelMetrics = [
    { label: 'Accuracy', value: 86.56, suffix: '%', icon: Target, description: 'Jeu de test - GradientBoosting' },
    { label: 'ROC-AUC', value: 0.8897, icon: TrendingUp, description: 'AUC finale après tuning' },
    { label: 'F2-weighted', value: 86.29, suffix: '%', icon: Zap, description: 'Critère de sélection principal' },
    { label: 'Lift@10%', value: 3.967, icon: Users, description: 'Campagne de rétention ciblée' }
  ]

  return (
    <>
      {/* Model Performance Metrics */}
      <section className="max-w-7xl mx-auto px-6 py-16 relative z-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-12 text-center"
        >
          <h2 className="font-syne font-bold text-2xl md:text-4xl">
            Performance <span className="text-brand">du Modèle</span>
          </h2>
          <p className="opacity-50 mt-3 text-lg font-dm">Métriques clés de validation et qualité</p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {modelMetrics.map((metric, i) => {
            const Icon = metric.icon
            return (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="group relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br from-white/80 to-white/50 dark:from-slate-800/50 dark:to-slate-900/50 border border-brand/20 backdrop-blur-xl hover:border-brand/40 transition-all duration-300"
              >
                {/* Background gradient accent */}
                <div className="absolute -top-8 -right-8 w-32 h-32 bg-brand/10 rounded-full blur-2xl group-hover:bg-brand/20 transition-colors duration-300" />
                
                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-brand/20 flex items-center justify-center group-hover:bg-brand/30 transition-colors duration-300">
                      <Icon className="text-brand" size={24} />
                    </div>
                  </div>
                  
                  <p className="text-2xl font-syne font-bold text-brand mb-2">{metric.value}</p>
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">{metric.label}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{metric.description}</p>
                </div>
              </motion.div>
            )
          })}
        </div>
      </section>

      {/* Business Metrics */}
      <section className="max-w-7xl mx-auto px-6 py-12 relative z-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-12 text-center"
        >
          <h2 className="font-syne font-bold text-2xl md:text-4xl">
            Indicateurs <span className="text-brand">Stratégiques</span>
          </h2>
          <p className="opacity-50 mt-3 text-lg font-dm">Suivi des performances et impact métier du modèle</p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {metrics.map((metric, i) => (
            <MetricCard key={metric.id} metric={metric} index={i} />
          ))}
        </div>
      </section>

      {/* Analytics & Insights Gallery */}
      <AnalyticsGallery graphics={allAnalytics} title="Analytics & Insights" />

      <div className="bg-gradient-radial-green h-40 -mt-20 opacity-30" />
    </>
  )
}
