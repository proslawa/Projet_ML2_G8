import { motion } from 'framer-motion'
import MethodologyTimeline from '../components/MethodologyTimeline'
import { methodologySteps } from '../data/mockData'

export default function Methodology() {
  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-12"
        >
          <h1 className="font-syne font-bold text-3xl md:text-4xl text-inherit">
            <span className="text-gradient-brand">Méthodologie</span>
          </h1>
          <p className="mt-2 max-w-xl opacity-55">
            Des notebooks 01, 02, 03a et 03b : EDA, feature engineering, benchmark, rééquilibrage et tuning final.
          </p>
        </motion.div>

        <MethodologyTimeline steps={methodologySteps} />
      </div>
    </div>
  )
}
