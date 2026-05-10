import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Filter } from 'lucide-react'

function AnalyticsCard({ title, subtitle, description, imagePath, index, section }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      className="group relative isolate overflow-hidden rounded-2xl bg-gradient-to-br from-white/60 to-white/40 dark:from-slate-800/40 dark:to-slate-900/40 border border-brand/20 backdrop-blur-lg hover:border-brand/40 transition-all duration-300"
    >
      {/* Hover accent */}
      <div className="pointer-events-none absolute -inset-px z-0 bg-gradient-to-r from-brand/0 via-brand/10 to-brand/0 opacity-0 group-hover:opacity-100 dark:via-brand/10 transition-opacity duration-300" />
      
      <div className="relative z-10 p-5 h-full flex flex-col">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-syne font-bold text-base md:text-lg text-slate-900 dark:text-slate-50 line-clamp-2">{title}</h3>
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand/15 text-brand dark:bg-brand/20 dark:text-brand-glow whitespace-nowrap ml-2">
              {section}
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-600 dark:text-slate-300 mb-3 line-clamp-1">{subtitle}</p>
        </div>

        {/* Image Container */}
        <div className="flex-1 mb-4 rounded-xl overflow-hidden border border-black/5 dark:border-white/5 bg-black/[0.02] dark:bg-white/[0.02] group-hover:bg-black/[0.04] dark:group-hover:bg-white/[0.04] transition-colors duration-300">
          <img 
            src={imagePath} 
            alt={title} 
            className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300" 
            loading="lazy"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.innerHTML = '<div class="w-full h-full flex items-center justify-center text-xs opacity-30">Image non disponible</div>'
            }}
          />
        </div>

        {/* Description */}
        <p className="text-xs text-slate-600/80 dark:text-slate-300/80 line-clamp-2 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  )
}

export default function AnalyticsGallery({ graphics = [], title = 'Analytics & Insights' }) {
  const [filter, setFilter] = useState('all')
  const [isDark, setIsDark] = useState(true)

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'))
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    setIsDark(document.documentElement.classList.contains('dark'))
    return () => observer.disconnect()
  }, [])

  // Extract unique sections
  const sections = ['all', ...new Set(graphics.map(g => g.section))]
  
  // Filter graphics
  const filtered = filter === 'all' 
    ? graphics 
    : graphics.filter(g => g.section === filter)

  return (
    <section className="max-w-7xl mx-auto px-6 py-16 relative z-20">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="mb-10 text-center"
      >
        <h2 className="font-syne font-bold text-2xl md:text-4xl">
          {title.split(' ').map((word, i) => (
            <span key={i}>
              {word === 'Insights' ? <span className="text-brand">{word}</span> : word}
              {i < title.split(' ').length - 1 ? ' ' : ''}
            </span>
          ))}
        </h2>
        <p className="opacity-50 mt-3 text-lg font-dm">Graphiques les plus pertinents du projet EDA & Modélisation</p>
      </motion.div>

      {/* Filter Buttons */}
      {sections.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-wrap gap-3 justify-center mb-10"
        >
          {sections.map(section => (
            <motion.button
              key={section}
              onClick={() => setFilter(section)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 capitalize ${
                filter === section
                  ? 'bg-brand text-white shadow-lg shadow-brand/30 scale-105'
                  : 'bg-brand/10 text-brand hover:bg-brand/20 border border-brand/20'
              }`}
              whileHover={{ scale: filter === section ? 1.08 : 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Filter size={14} className="inline mr-2" />
              {section === 'all' ? 'Tous' : section}
            </motion.button>
          ))}
        </motion.div>
      )}

      {/* Gallery Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.length > 0 ? (
          filtered.map((graphic, i) => (
            <AnalyticsCard
              key={graphic.id}
              title={graphic.title}
              subtitle={graphic.subtitle}
              description={graphic.description}
              imagePath={graphic.path}
              section={graphic.section}
              index={i}
            />
          ))
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="col-span-full text-center py-12"
          >
            <p className="opacity-50 text-lg">Aucun graphique disponible dans cette catégorie</p>
          </motion.div>
        )}
      </div>

      {/* Bottom Accent */}
      <div className="bg-gradient-radial-green h-32 -mb-20 opacity-20 mt-20" />
    </section>
  )
}
