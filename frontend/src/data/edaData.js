export const edaGraphics = [
  {
    id: 'eda-target',
    title: 'Distribution de la variable cible (Exited)',
    subtitle: 'Dataset déséquilibré : 21 % churn / 79 % non-churn',
    section: 'Cible',
    path: '/figures/exited_distribution.png',
    description: 'Environ 21 % des clients quittent la banque, contre 79 % qui restent ; le dataset est donc déséquilibré en faveur des non-churn.'
  },
  {
    id: 'eda-credit-score-distribution',
    title: 'Distribution de CreditScore',
    subtitle: 'Concentration entre 600 et 700',
    section: 'Variables numériques',
    path: '/figures/CreditScore_distribution.png',
    description: 'Les scores de crédit sont principalement concentrés entre 600 et 700, avec une moyenne proche de 656.'
  },
  {
    id: 'eda-age-distribution',
    title: 'Distribution de Age',
    subtitle: 'Majorité entre 30 et 50 ans',
    section: 'Variables numériques',
    path: '/figures/Age_distribution.png',
    description: 'La majorité des clients ont entre 30 et 50 ans, avec un âge moyen d’environ 38 ans.'
  },
  {
    id: 'eda-balance-distribution',
    title: 'Distribution de Balance',
    subtitle: 'Solde nul fréquent et soldes dispersés',
    section: 'Variables numériques',
    path: '/figures/Balance_distribution.png',
    description: 'Une grande partie des clients possède un solde nul, tandis que les autres présentent des soldes plus élevés et très dispersés.'
  },
  {
    id: 'eda-salary-distribution',
    title: 'Distribution de EstimatedSalary',
    subtitle: 'Répartition relativement homogène',
    section: 'Variables numériques',
    path: '/figures/EstimatedSalary_distribution.png',
    description: 'Les revenus estimés sont répartis de manière relativement homogène entre les clients.'
  },
  {
    id: 'eda-geography-distribution',
    title: 'Répartition géographique des clients',
    subtitle: 'France majoritaire',
    section: 'Profil client',
    path: '/figures/Geography_pie.png',
    description: 'La majorité des clients provient de France (≈ 57 %), devant l’Espagne et l’Allemagne (≈ 21 % chacune).'
  },
  {
    id: 'eda-gender-distribution',
    title: 'Répartition des clients par genre',
    subtitle: '56 % hommes / 44 % femmes',
    section: 'Profil client',
    path: '/figures/Gender_pie.png',
    description: 'Les hommes représentent environ 56 % des clients, contre 44 % de femmes.'
  },
  {
    id: 'eda-card-distribution',
    title: 'Détention d’une carte bancaire',
    subtitle: 'Environ 75 % équipés',
    section: 'Profil client',
    path: '/figures/HasCrCard_pie.png',
    description: 'Environ 75 % des clients possèdent une carte bancaire.'
  },
  {
    id: 'eda-activity-distribution',
    title: 'Statut d’activité des clients',
    subtitle: 'Actifs et inactifs presque équilibrés',
    section: 'Profil client',
    path: '/figures/IsActiveMember_pie.png',
    description: 'La répartition entre clients actifs et inactifs est globalement équilibrée (50,2 % contre 49,8 %).'
  },
  {
    id: 'eda-products-distribution',
    title: 'Répartition du nombre de produits détenus',
    subtitle: 'Majorité à 1 ou 2 produits',
    section: 'Profil client',
    path: '/figures/NumOfProducts_bar.png',
    description: 'La majorité des clients possède 1 ou 2 produits bancaires.'
  },
  {
    id: 'eda-tenure-distribution',
    title: 'Répartition de l’ancienneté des clients',
    subtitle: 'Ancienneté homogène entre 1 et 9 ans',
    section: 'Profil client',
    path: '/figures/Tenure_bar.png',
    description: 'L’ancienneté des clients est répartie de manière relativement homogène entre 1 et 9 ans.'
  },
  {
    id: 'eda-geography-churn',
    title: 'Taux de churn selon le pays du client',
    subtitle: 'Allemagne nettement plus risquée',
    section: 'Taux de churn',
    path: '/figures/Geography_churn.png',
    description: 'Le churn est nettement plus élevé en Allemagne (≈ 38 %) qu’en France et en Espagne (≈ 17 %).'
  },
  {
    id: 'eda-gender-churn',
    title: 'Taux de churn selon le genre du client',
    subtitle: 'Churn plus élevé chez les femmes',
    section: 'Taux de churn',
    path: '/figures/Gender_churn.png',
    description: 'Les femmes présentent un taux de churn plus élevé (≈ 28 %) que les hommes (≈ 16 %).'
  },
  {
    id: 'eda-card-churn',
    title: 'Taux de churn selon la carte bancaire',
    subtitle: 'Effet faible sur le churn',
    section: 'Taux de churn',
    path: '/figures/HasCrCard_churn.png',
    description: 'La possession d’une carte bancaire influence peu le churn.'
  },
  {
    id: 'eda-activity-churn',
    title: 'Taux de churn selon le statut d’activité',
    subtitle: 'Inactivité fortement associée au churn',
    section: 'Taux de churn',
    path: '/figures/IsActiveMember_churn.png',
    description: 'Les clients inactifs churnent davantage (≈ 30 %) que les clients actifs (≈ 12 %).'
  },
  {
    id: 'eda-products-churn',
    title: 'Taux de churn selon le nombre de produits',
    subtitle: 'Risque très élevé à 3 ou 4 produits',
    section: 'Taux de churn',
    path: '/figures/NumOfProducts_churn.png',
    description: 'Les clients ayant 3 ou 4 produits présentent un churn très élevé (> 85 %), contre ≈ 6 % pour ceux ayant 2 produits.'
  },
  {
    id: 'eda-tenure-churn',
    title: 'Taux de churn selon l’ancienneté',
    subtitle: 'Variation limitée selon Tenure',
    section: 'Taux de churn',
    path: '/figures/Tenure_churn.png',
    description: 'Le churn varie peu selon l’ancienneté des clients.'
  },
  {
    id: 'eda-credit-score-by-churn',
    title: 'Distribution de CreditScore selon le churn',
    subtitle: 'Distributions très proches',
    section: 'Comparaison churn',
    path: '/figures/CreditScore_kde_churn.png',
    description: 'Le score de crédit distingue peu les clients churn et non-churn ; les distributions restent proches.'
  },
  {
    id: 'eda-age-by-churn',
    title: 'Distribution de Age selon le churn',
    subtitle: 'Les churners sont plus âgés',
    section: 'Comparaison churn',
    path: '/figures/Age_kde_churn.png',
    description: 'Les clients churn sont en moyenne plus âgés que les clients non-churn.'
  },
  {
    id: 'eda-balance-by-churn',
    title: 'Distribution de Balance selon le churn',
    subtitle: 'Soldes plus élevés chez les churners',
    section: 'Comparaison churn',
    path: '/figures/Balance_kde_churn.png',
    description: 'Les clients churn possèdent généralement des soldes plus élevés que les non-churn.'
  },
  {
    id: 'eda-salary-by-churn',
    title: 'Distribution de EstimatedSalary selon le churn',
    subtitle: 'Peu de différence visible',
    section: 'Comparaison churn',
    path: '/figures/EstimatedSalary_kde_churn.png',
    description: 'Les revenus estimés présentent des distributions similaires entre churn et non-churn.'
  }
]

export const allAnalytics = [...edaGraphics]
