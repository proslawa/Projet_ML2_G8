import { motion } from 'framer-motion'

export default function TeamCard({ member, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="glass-card p-6 group text-center"
    >
      <div className="relative mx-auto mb-5 w-20 h-20">
        <div
          className={`w-full h-full rounded-2xl bg-gradient-to-br ${member.gradient} flex items-center justify-center text-2xl font-syne font-bold text-white shadow-lg transition-transform duration-300 group-hover:scale-105`}
        >
          {member.initials}
        </div>
        <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-400 border-2 border-[var(--bg-secondary)]" />
      </div>

      <h3 className="font-syne font-bold text-lg text-inherit">{member.name}</h3>
      <p className="mt-1 text-sm text-brand-glow">{member.role}</p>

      {member.description && (
        <p className="mt-3 text-sm leading-6 opacity-70 max-w-sm mx-auto">
          {member.description}
        </p>
      )}

      {member.github && (
        <p className="mt-3 text-xs uppercase tracking-widest opacity-50">
          GitHub ·{' '}
          <a
            href={`https://github.com/${member.github}`}
            target="_blank"
            rel="noreferrer noopener"
            className="text-brand-glow hover:underline underline-offset-4 transition-colors"
            aria-label={`Ouvrir le profil GitHub de ${member.name}`}
          >
            {member.github}
          </a>
        </p>
      )}

      <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
        {member.skills.map((skill) => (
          <span
            key={skill}
            className="rounded-full border border-black/5 bg-black/5 px-3 py-1 text-xs font-medium opacity-70 dark:border-white/5 dark:bg-white/5"
          >
            {skill}
          </span>
        ))}
      </div>
    </motion.div>
  )
}
