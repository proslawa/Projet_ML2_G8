export const metrics = [
  {
    id: 'churn-rate',
    icon: 'TrendingDown',
    label: 'Taux de churn global',
    value: 21.16,
    suffix: '%',
    detail: 'Notebook 03b',
    color: '#EF4444'
  },
  {
    id: 'accuracy',
    icon: 'Target',
    label: 'Observations train',
    value: 132027,
    suffix: '',
    detail: 'Split 80/20',
    color: '#2563EB'
  },
  {
    id: 'clients',
    icon: 'Users',
    label: 'Observations test',
    value: 33007,
    suffix: '',
    detail: 'Hold-out final',
    color: '#8B5CF6'
  },
  {
    id: 'roc-auc',
    icon: 'Trophy',
    label: 'Features finales',
    value: 15,
    suffix: '',
    detail: 'Feature engineering',
    color: '#F59E0B'
  }
]

export const edaImages = [
  {
    id: 'target-dist',
    title: 'Distribution de la cible',
    subtitle: '21.16% de churners',
    src: '/figures/exited_distribution.png'
  },
  {
    id: 'pearson-corr',
    title: 'Corrélation Pearson',
    subtitle: 'Variables numériques principales',
    src: '/figures/pearson_correlation_matrix.png'
  },
  {
    id: 'age-band',
    title: 'Churn par tranche d’âge',
    subtitle: 'Explosion entre 40 et 60 ans',
    src: '/figures/age_band_churn.png'
  },
  {
    id: 'benchmark',
    title: 'Benchmark modèles',
    subtitle: 'GradientBoosting en tête',
    src: '/figures/benchmark_metrics.png'
  }
]

export const churnDistribution = [
  { name: 'Churners', value: 21.16, fill: '#EF4444' },
  { name: 'Non-Churners', value: 78.84, fill: '#2563EB' }
]

export const churnByAge = [
  { age: '< 30', churn: 8 },
  { age: '40-50', churn: 38.8 },
  { age: '50-60', churn: 60.9 }
]

export const churnByProducts = [
  { products: '1 produit', churn: 34.7 },
  { products: '2 produits', churn: 6.0 },
  { products: '3+ produits', churn: 88.0 }
]

export const scoreDistribution = [
  { bin: '0.0-0.1', count: 180 },
  { bin: '0.1-0.2', count: 260 },
  { bin: '0.2-0.3', count: 310 },
  { bin: '0.3-0.4', count: 400 },
  { bin: '0.4-0.5', count: 450 },
  { bin: '0.5-0.6', count: 390 },
  { bin: '0.6-0.7', count: 320 },
  { bin: '0.7-0.8', count: 240 },
  { bin: '0.8-0.9', count: 170 },
  { bin: '0.9-1.0', count: 120 }
]

export const modelBenchmark = [
  { model: 'GradientBoosting', accuracy: 86.56, recall: 58.59, rocAuc: 0.8897, f2Weighted: 0.8629, selected: true },
  { model: 'LightGBM', accuracy: 79.50, recall: 82.06, rocAuc: 0.8894, f2Weighted: 0.7971, selected: false },
  { model: 'RandomForest', accuracy: 85.67, recall: 56.21, rocAuc: 0.8738, f2Weighted: 0.8539, selected: false },
  { model: 'ExtraTrees', accuracy: 85.08, recall: 57.29, rocAuc: 0.8657, f2Weighted: 0.8488, selected: false },
  { model: 'XGBoost', accuracy: 80.33, recall: 79.17, rocAuc: 0.8822, f2Weighted: 0.8057, selected: false }
]

export const methodologySteps = [
  {
    id: 1,
    icon: '🔎',
    title: 'EDA et compréhension du churn',
    subtitle: 'Notebook 01 - qualité, distributions et relations',
    summary:
      'L’analyse exploratoire a débuté par la compréhension du dataset bancaire, la vérification de sa qualité et la séparation des variables quantitatives et qualitatives. Elle a ensuite permis d’étudier la structure globale des données, puis les liens entre chaque variable et la cible Exited.',
    details: [
      'Base analysée : 165 034 clients, 14 variables brutes, aucune valeur manquante ni doublon détecté.',
      'Variables étudiées : CreditScore, Age, Tenure, Balance, NumOfProducts, EstimatedSalary, Geography, Gender, HasCrCard, IsActiveMember et Exited.',
      'Analyse univariée : statistiques descriptives, histogrammes, boxplots, pie charts et barplots.',
      'Constats principaux : 21.16 % de churners, majorité de clients avec 1 ou 2 produits, France majoritaire et répartition actifs/inactifs équilibrée.',
      'Analyse bivariée : churn plus élevé chez les clients inactifs, allemands, femmes, plus âgés, avec balance élevée ou 3/4 produits.',
      'Analyse des relations : corrélations Pearson et Cramér’s V globalement faibles, limitant les risques de redondance forte entre variables.'
    ]
  },
  {
    id: 2,
    icon: '⚙️',
    title: 'Prétraitement et feature engineering',
    subtitle: 'Notebook 02 - dataset final de modélisation',
    summary:
      'Cette étape a transformé les données brutes en variables exploitables par les modèles de machine learning. Les identifiants sans valeur prédictive ont été retirés, les variables catégorielles encodées et de nouvelles variables métier ont été créées pour mieux représenter les comportements clients.',
    details: [
      'Suppression des identifiants non prédictifs : id, CustomerId et Surname.',
      'Contrôle des contraintes métier et des valeurs extrêmes avant la construction des variables finales.',
      'Encodage one-hot : Geography_Germany, Geography_Spain et Gender_Male, avec France et Female comme références implicites.',
      'Conservation des variables métier : CreditScore, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember et EstimatedSalary.',
      'Création de 4 ratios : Balance_per_Product, Tenure_Age_Ratio, Balance_Age_Ratio et Salary_Age.',
      'Sortie finale : 15 prédicteurs + Exited, soit 165 034 lignes x 16 colonnes pour la phase de modélisation.'
    ]
  },
  {
    id: 3,
    icon: '🏗️',
    title: 'Benchmark de modélisation',
    subtitle: 'Notebooks 03a et 03b - sans puis avec rééquilibrage',
    summary:
      'La modélisation a comparé plusieurs algorithmes de classification selon deux approches : une première sans traitement du déséquilibre de classes, puis une seconde avec une gestion native du déséquilibre. Cette comparaison a permis de mesurer l’apport réel du rééquilibrage pour détecter les clients churn.',
    details: [
      'Split stratifié 80/20 : 132 027 observations train et 33 007 observations test, avec un taux de churn conservé à 21.16 %.',
      'Préprocesseur commun : imputation médiane et standardisation dans un Pipeline sklearn.',
      'Validation croisée StratifiedKFold à 3 folds sur un échantillon benchmark de 30 000 observations.',
      'Notebook 03a : baseline sans correction du déséquilibre pour observer le biais vers la classe majoritaire non-churn.',
      'Notebook 03b : rééquilibrage natif via class_weight, scale_pos_weight ou is_unbalance selon les modèles.',
      'Modèles comparés : DummyClassifier, GaussianNB, DecisionTree, KNN, AdaBoost, RandomForest, ExtraTrees, GradientBoosting, XGBoost et LightGBM.'
    ]
  },
  {
    id: 4,
    icon: '🎯',
    title: 'Évaluation, tuning et choix final',
    subtitle: 'Notebook 03b - seuil 0.45 et Optuna',
    summary:
      'L’évaluation a été centrée sur la capacité à détecter les churners, car la classe positive est minoritaire. Le notebook 03b fixe un seuil de décision à 0.45 et sélectionne le modèle final sur la base des métriques les plus adaptées au contexte de rétention client.',
    details: [
      'Métriques suivies : accuracy, precision, recall, F1-score, F2-score, F2-weighted, AUC-ROC et Lift@10 %.',
      'F2-weighted retenu comme critère principal, car il valorise davantage le rappel tout en tenant compte de la précision.',
      'Seuil de classification fixé à 0.45 pour convertir les probabilités en prédictions churn / non-churn.',
      'Comparaison des modèles avec matrices de confusion, courbes ROC, courbes précision-rappel et rapports de classification.',
      'GradientBoosting sélectionné comme meilleur modèle final : accuracy 86.56 %, recall 58.59 %, precision 72.59 %, ROC-AUC 0.8897 et F2-weighted 0.8629.',
      'Optimisation Optuna appliquée au meilleur modèle, puis sauvegarde du pipeline final dans best_model/.'
    ]
  },
  {
    id: 5,
    icon: '🚀',
    title: 'Déploiement',
    subtitle: 'API FastAPI + frontend de scoring',
    summary:
      'La dernière étape a consisté à rendre le modèle exploitable dans l’application. Le pipeline sauvegardé est rechargé par l’API, qui applique le même feature engineering avant de retourner une probabilité, une classe prédite et un niveau de risque basé sur le seuil retenu.',
    details: [
      'API FastAPI/Uvicorn branchée sur le pipeline GradientBoosting final.',
      'Endpoints de scoring : /predict et /predict_batch pour les prédictions unitaires et batch.',
      'Seuil modèle conservé côté API à 0.45 afin d’aligner la prédiction applicative avec le notebook 03b.',
      'Frontend React/Vite : pages Overview, Méthodologie et Prédiction pour restituer les analyses et scorer les clients.',
      'Déploiement prévu via Render, avec configuration frontend par VITE_API_URL.'
    ]
  }
]

export const teamMembers = [
  {
    name: 'Ameth FAYE',
    role: 'Lead Data Scientist & Chef de projet',
    description: 'Pilotage du projet, coordination de l’équipe et supervision des analyses et modèles développés.',
    github: 'ameth08faye',
    skills: ['Pilotage', 'Analyse', 'Modélisation'],
    initials: 'AF',
    gradient: 'from-blue-500 to-cyan-400'
  },
  {
    name: 'Sarah-Laure FOGWOUNG',
    role: 'Data Analyst',
    description: 'Exploration, nettoyage et analyse des données afin d’identifier les facteurs liés au churn.',
    github: 'Sarahlaure',
    skills: ['EDA', 'Nettoyage', 'Data Storytelling'],
    initials: 'SF',
    gradient: 'from-purple-500 to-pink-400'
  },
  {
    name: 'Prosper Lawa FOUMSOU',
    role: 'ML Engineer',
    description: 'Développement, entraînement et évaluation des modèles de prédiction du churn.',
    github: 'proslawa',
    skills: ['Training', 'Evaluation', 'Pipeline'],
    initials: 'PL',
    gradient: 'from-amber-500 to-orange-400'
  },
  {
    name: 'Paul BALAFAI',
    role: 'ML Ops Engineer & Product',
    description: 'Déploiement de la solution, création du dashboard et mise en production de l’outil.',
    github: 'ruskovin',
    skills: ['Déploiement', 'Dashboard', 'Produit'],
    initials: 'PB',
    gradient: 'from-emerald-500 to-teal-400'
  }
]

export const defaultFormValues = {
  CreditScore: 656,
  Geography: 'France',
  Gender: 'Male',
  Age: 38,
  Tenure: 5,
  Balance: 55478,
  NumOfProducts: 2,
  HasCrCard: 1,
  IsActiveMember: 1,
  EstimatedSalary: 11500
}
