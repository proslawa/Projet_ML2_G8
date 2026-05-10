import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { modelBenchmark } from '../data/mockData'

export default function MethodologyTimeline({ steps }) {
  const [openId, setOpenId] = useState(1)

  return (
    <div className="space-y-12">
      <div className="relative">
        {steps.map((step, i) => {
          const isOpen = openId === step.id
          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="relative pl-14 pb-10 last:pb-0"
            >
              {i < steps.length - 1 && (
                <div className="absolute left-[19px] top-[44px] bottom-0 w-[2px] bg-gradient-to-b from-accent-blue/40 to-accent-blue/5" />
              )}

              <div className={`absolute left-0 top-0 w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 ${
                isOpen
                  ? 'bg-accent-blue shadow-lg shadow-accent-blue/30'
                  : 'bg-navy-700 border border-navy-500/30'
              }`}>
                {step.icon}
              </div>

              <button
                onClick={() => setOpenId(isOpen ? null : step.id)}
                className="w-full text-left glass-card p-5 cursor-pointer group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs text-accent-blue font-semibold uppercase tracking-wider">
                      Étape {step.id}
                    </span>
                    <h3 className="font-syne font-bold text-lg text-inherit mt-1">{step.title}</h3>
                    <p className="text-sm opacity-55">{step.subtitle}</p>
                  </div>
                  <ChevronDown
                    size={20}
                    className={`opacity-55 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
                  />
                </div>

                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-4 border-t border-black/5 pt-4 dark:border-white/5">
                        {step.summary && (
                          <p className="text-sm leading-6 text-slate-700 dark:text-slate-300">
                            {step.summary}
                          </p>
                        )}
                        <ul className={`${step.summary ? 'mt-3' : ''} space-y-2`}>
                          {step.details.map((d, j) => (
                            <li key={j} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                              <span className="w-1.5 h-1.5 rounded-full bg-accent-blue/60 mt-1.5 shrink-0" />
                              {d}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </button>
            </motion.div>
          )
        })}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="glass-card p-6"
      >
        <h3 className="font-syne font-bold text-lg text-inherit mb-4">Comparaison des modèles</h3>
        <div className="overflow-x-auto rounded-lg">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5">
                <th className="text-left py-3 px-4 font-medium opacity-55">Modèle</th>
                <th className="text-center py-3 px-4 font-medium opacity-55">Accuracy</th>
                <th className="text-center py-3 px-4 font-medium opacity-55">Recall</th>
                <th className="text-center py-3 px-4 font-medium opacity-55">ROC-AUC</th>
                <th className="text-center py-3 px-4 font-medium opacity-55">F2-weighted</th>
              </tr>
            </thead>
            <tbody>
              {modelBenchmark.map((m) => (
                <tr
                  key={m.model}
                  className={`border-b border-navy-700/20 transition-colors ${
                    m.selected ? 'bg-accent-blue/5' : 'hover:bg-black/[0.02] dark:hover:bg-white/[0.02]'
                  }`}
                >
                  <td className="py-3 px-4 font-medium text-inherit flex items-center gap-2">
                    {m.selected && <span className="text-gold text-xs">✓</span>}
                    {m.model}
                    {m.selected && (
                      <span className="text-[10px] bg-gold/15 text-gold px-2 py-0.5 rounded-full font-semibold">
                        Sélectionné
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center opacity-75">{m.accuracy}%</td>
                  <td className="py-3 px-4 text-center opacity-75">{m.recall}%</td>
                  <td className="py-3 px-4 text-center opacity-75">{m.rocAuc}</td>
                  <td className="py-3 px-4 text-center opacity-75">{m.f2Weighted}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
