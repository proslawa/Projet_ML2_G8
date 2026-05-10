import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import {
  churnDistribution,
  churnByAge,
  churnByProducts,
  scoreDistribution,
  edaImages
} from '../data/mockData'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-4 py-2.5 !rounded-lg text-sm shadow-xl border border-black/5 dark:border-white/5">
      {label && <p className="opacity-40 text-[10px] font-bold uppercase tracking-widest mb-1">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="font-bold text-inherit">
          {p.name} : <span style={{ color: p.fill || p.stroke || p.color }}>{p.value}</span>
        </p>
      ))}
    </div>
  )
}

function ChartCard({ title, subtitle, children, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="glass-card p-6"
    >
      <h3 className="font-syne font-bold text-lg text-inherit mb-0.5">{title}</h3>
      <p className="text-sm opacity-50 mb-6 font-dm">{subtitle}</p>
      {children}
    </motion.div>
  )
}

export default function ChartSection() {
  const [isDark, setIsDark] = useState(true)
  const hasImages = Array.isArray(edaImages) && edaImages.length > 0

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'))
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    setIsDark(document.documentElement.classList.contains('dark'))
    return () => observer.disconnect()
  }, [])

  const GR = isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'
  const AX = isDark ? '#7A9180' : '#4A5E52'
  const TEXT = isDark ? '#E8EDE9' : '#111827'

  return (
    <section className="max-w-7xl mx-auto px-6 mt-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="mb-12 text-center"
      >
        <h2 className="font-syne font-bold text-2xl md:text-4xl">
          Analyse <span className="text-gradient-gold">Décisionnelle</span>
        </h2>
        <p className="opacity-50 mt-3 text-lg font-dm">Visualisation des segments clients et des facteurs de risque</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {hasImages ? (
          edaImages.map((img, i) => (
            <ChartCard key={img.id} title={img.title} subtitle={img.subtitle} index={i}>
              <div className="rounded-xl overflow-hidden border border-black/5 dark:border-white/5 bg-black/[0.02] dark:bg-white/[0.02]">
                <img src={img.src} alt={img.title} className="w-full h-[280px] object-contain" />
              </div>
            </ChartCard>
          ))
        ) : (
          <>
            <ChartCard title="Distribution Churn" subtitle="Churners vs Non-Churners" index={0}>
              <div className="h-[280px]">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={churnDistribution} cx="50%" cy="50%" innerRadius={70} outerRadius={110} paddingAngle={3} dataKey="value" strokeWidth={0}>
                      {churnDistribution.map((e, i) => <Cell key={i} fill={e.fill} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: '11px', fontWeight: 'bold', textTransform: 'uppercase' }} />
                    <text x="50%" y="46%" textAnchor="middle" fill={TEXT} className="text-2xl font-bold font-syne">21.16%</text>
                    <text x="50%" y="56%" textAnchor="middle" fill={AX} className="text-[10px] font-bold uppercase tracking-widest">Churn Rate</text>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Churn par Tranche d'Âge" subtitle="Taux de churn segmenté par âge" index={1}>
              <div className="h-[280px]">
                <ResponsiveContainer>
                  <BarChart data={churnByAge} barCategoryGap="20%">
                    <CartesianGrid strokeDasharray="3 3" stroke={GR} vertical={false} />
                    <XAxis dataKey="age" tick={{ fill: AX, fontSize: 11, fontWeight: 'bold' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: AX, fontSize: 11, fontWeight: 'bold' }} axisLine={false} tickLine={false} unit="%" domain={[0, 40]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="churn" name="Churn" radius={[6, 6, 0, 0]} maxBarSize={48}>
                      {churnByAge.map((_, i) => <Cell key={i} fill={i === 0 ? '#EF4444' : i === 1 ? '#B8973E' : '#1B5E3B'} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Churn par Nb de Produits" subtitle="Impact du nombre de produits bancaires" index={2}>
              <div className="h-[280px]">
                <ResponsiveContainer>
                  <AreaChart data={churnByProducts}>
                    <defs>
                      <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1B5E3B" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#1B5E3B" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={GR} vertical={false} />
                    <XAxis dataKey="products" tick={{ fill: AX, fontSize: 11, fontWeight: 'bold' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: AX, fontSize: 11, fontWeight: 'bold' }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="churn" name="Churn" stroke="#1B5E3B" strokeWidth={3} fill="url(#areaGrad)" dot={{ r: 5, fill: '#1B5E3B', stroke: TEXT, strokeWidth: 2 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Distribution Score de Churn" subtitle="Répartition des probabilités prédites" index={3}>
              <div className="h-[280px]">
                <ResponsiveContainer>
                  <BarChart data={scoreDistribution} barCategoryGap="8%">
                    <CartesianGrid strokeDasharray="3 3" stroke={GR} vertical={false} />
                    <XAxis dataKey="bin" tick={{ fill: AX, fontSize: 10, fontWeight: 'bold' }} axisLine={false} tickLine={false} angle={-35} textAnchor="end" height={50} />
                    <YAxis tick={{ fill: AX, fontSize: 11, fontWeight: 'bold' }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" name="Clients" radius={[4, 4, 0, 0]} maxBarSize={40}>
                      {scoreDistribution.map((_, i) => {
                        // Blend from Brand Green to Gold
                        return <Cell key={i} fill={i < 5 ? '#1B5E3B' : '#B8973E'} />
                      })}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>
          </>
        )}
      </div>
    </section>
  )
}
