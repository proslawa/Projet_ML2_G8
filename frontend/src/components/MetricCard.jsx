import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingDown, Target, Users, Trophy } from 'lucide-react'

const iconMap = {
  TrendingDown,
  Target,
  Users,
  Trophy
}

function useCountUp(end, duration = 2000, decimals = 0) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true
          const startTime = performance.now()
          const animate = (now) => {
            const elapsed = now - startTime
            const progress = Math.min(elapsed / duration, 1)
            const eased = 1 - Math.pow(1 - progress, 3)
            setCount(eased * end)
            if (progress < 1) requestAnimationFrame(animate)
          }
          requestAnimationFrame(animate)
        }
      },
      { threshold: 0.3 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [end, duration])

  const formatted =
    end >= 1000
      ? Math.round(count).toLocaleString('fr-FR')
      : decimals > 0
      ? count.toFixed(decimals)
      : count < 1
      ? count.toFixed(2)
      : Math.round(count).toString()

  return { ref, formatted }
}

export default function MetricCard({ metric, index }) {
  const Icon = iconMap[metric.icon] || Target
  const decimals = metric.value < 1 ? 3 : metric.value >= 1000 ? 0 : 2
  const { ref, formatted } = useCountUp(metric.value, 2200, decimals)

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="glass-card p-6 group cursor-default"
      id={`metric-${metric.id}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
          style={{
            background: `rgba(184,151,62,0.05)`,
            border: `1px solid rgba(184,151,62,0.1)`
          }}
        >
          <Icon size={20} style={{ color: metric.color }} />
        </div>
        <span className="text-[10px] text-inherit opacity-50 font-bold uppercase tracking-widest bg-black/5 dark:bg-white/5 px-2.5 py-1 rounded-full">
          {metric.detail}
        </span>
      </div>

      <p className="text-sm opacity-60 font-medium mb-1 font-dm">{metric.label}</p>
      <p className="text-3xl font-syne font-bold text-inherit">
        {formatted}
        {metric.suffix && (
          <span className="text-lg opacity-40 ml-0.5">{metric.suffix}</span>
        )}
      </p>

      <div className="mt-4 h-0.5 rounded-full bg-black/5 dark:bg-white/5 overflow-hidden">
        <motion.div
          initial={{ width: '0%' }}
          whileInView={{ width: '100%' }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, delay: 0.3 + index * 0.1, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, ${metric.color}, ${metric.color}40)` }}
        />
      </div>
    </motion.div>
  )
}
