import { motion } from 'framer-motion'
import { getRiskLevel } from '../utils/risk'

export default function ChurnGauge({ probability, threshold }) {
  const pct = Math.round((probability || 0) * 100)
  const risk = getRiskLevel(probability, threshold)
  const color = risk.color

  const radius = 80
  const circumference = 2 * Math.PI * radius
  const arc = circumference * 0.75
  const offset = arc - (arc * pct) / 100

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col items-center"
    >
      <div className={`relative ${risk.glowClass}`}>
        <svg width="200" height="200" viewBox="0 0 200 200" className="-rotate-[135deg]">
          {/* Background circle adaptive */}
          <circle
            cx="100" cy="100" r={radius}
            fill="none" stroke="currentColor" strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={`${arc} ${circumference}`}
            className="text-black/5 dark:text-white/5"
          />
          <motion.circle
            cx="100" cy="100" r={radius}
            fill="none" stroke={color} strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={`${arc} ${circumference}`}
            initial={{ strokeDashoffset: arc }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.2 }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-4xl font-syne font-bold"
            style={{ color }}
          >
            {pct}%
          </motion.span>
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="text-xs opacity-50 mt-1 font-medium tracking-wide uppercase"
          >
            Score de churn
          </motion.span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2 }}
        className="mt-4 px-5 py-2 rounded-full text-xs font-bold uppercase tracking-wider"
        style={{
          background: `${color}15`,
          color: color,
          border: `1px solid ${color}30`
        }}
      >
        {risk.label}
      </motion.div>
    </motion.div>
  )
}
