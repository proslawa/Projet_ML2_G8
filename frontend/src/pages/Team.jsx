import { motion } from 'framer-motion'
import TeamCard from '../components/TeamCard'
import { teamMembers } from '../data/mockData'

export default function Team() {
  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-12 text-center"
        >
          <h1 className="font-syne font-bold text-3xl md:text-4xl text-inherit">
            Notre <span className="text-gradient-gold">Équipe</span>
          </h1>
          <p className="mt-2 max-w-lg mx-auto opacity-55">
            Les talents derrière le modèle de scoring ChurnScore
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {teamMembers.map((member, i) => (
            <TeamCard key={member.name} member={member} index={i} />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-16 glass-card p-8 text-center"
        >
          <h2 className="font-syne font-bold text-xl text-inherit mb-3">Stack Technique</h2>
          <div className="flex flex-wrap items-center justify-center gap-3 mt-4">
            {['Python', 'XGBoost', 'FastAPI', 'Docker', 'MLflow', 'React', 'Render', 'GitHub Actions'].map((tech) => (
              <span
                key={tech}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-black/5 dark:bg-white/5 text-inherit opacity-75 border border-black/5 dark:border-white/5 hover:border-brand/30 hover:opacity-100 transition-all duration-300"
              >
                {tech}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
