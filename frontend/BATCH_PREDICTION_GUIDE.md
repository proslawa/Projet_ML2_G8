# Guide : Analyse Batch avec Données Brutes

## Vue d'ensemble

L'interface Batch (`Analyse Batch` dans la page Prédiction) permet de :
1. **Importer** un fichier CSV contenant un dataset complet (avec colonnes d'identifiant brutes)
2. **Appliquer automatiquement** le preprocessing et feature engineering
3. **Générer des prédictions** avec contrôle du seuil de décision
4. **Exporter** un rapport CSV enrichi avec les résultats

---

## Format d'entrée attendu

### Colonnes requises

Le CSV doit contenir **au minimum** les colonnes suivantes :

#### Colonnes d'identification (optionnelles mais recommandées)
- `id` : identifiant technique
- `CustomerId` : identifiant client
- `Surname` : nom du client

#### Colonnes de features (obligatoires)
- `CreditScore` : score de crédit (300–850)
- `Geography` : pays (France, Germany, Spain)
- `Gender` : sexe (Female, Male)
- `Age` : âge (18–120 ans)
- `Tenure` : ancienneté en années (0–50)
- `Balance` : solde bancaire en euros
- `NumOfProducts` : nombre de produits (1–4)
- `HasCrCard` : possession de carte crédit (0 ou 1)
- `IsActiveMember` : client actif (0 ou 1)
- `EstimatedSalary` : salaire estimé en euros

#### Colonne de cible (optionnelle)
- `Exited` : indicateur de churn réel (0 ou 1) — *non utilisée pour les prédictions, utile pour la validation*

### Exemple de structure CSV

```csv
id,CustomerId,Surname,CreditScore,Geography,Gender,Age,Tenure,Balance,NumOfProducts,HasCrCard,IsActiveMember,EstimatedSalary,Exited
1,15634602,Hargrave,619,France,Female,42,2,0.0,1,1,1,101348.88,1
2,15647311,Hill,850,Germany,Male,29,3,144750.7,2,1,1,83643.35,0
3,15619304,Barron,645,Spain,Female,44,2,0.0,1,1,0,198969.63,1
```

---

## Workflow d'utilisation

### 1. Préparer le CSV

Assurez-vous que votre fichier :
- ✅ Est un CSV valide (encodage UTF-8, délimiteur `,`)
- ✅ Contient toutes les colonnes de features décrites ci-dessus
- ✅ Contient les colonnes d'identification (id, CustomerId, Surname) pour traçabilité
- ✅ Pas de lignes vides au début ou fin

### 2. Uploader le fichier

1. Allez à la page **Prédiction** → onglet **Analyse Batch**
2. **Glissez-déposez** le fichier ou **cliquez** pour parcourir
3. Le système affiche un aperçu des premières lignes détectées

### 3. Configurer le seuil (optionnel)

*Note : Le seuil est appliqué lors de la prédiction sur le serveur. Pour l'ajuster après le calcul, utilisez l'export CSV et retrainez localement.*

### 4. Lancer l'analyse

1. Cliquez sur **Lancer le batch**
2. Le système :
   - Applique le preprocessing (suppression d'outliers, vérification des contraintes)
   - Exécute le feature engineering (encodages, ratios)
   - Génère les prédictions avec le modèle
3. Un tableau récapitulatif s'affiche

### 5. Consulter les résultats

Le tableau affiche :
- **Premiers colonnes** : identifiants + quelques features initiales
- **Score** : probabilité de churn (0–100%)
- **Prediction** : classe prédite (Churner / Non-Churner)
- **Risque** : niveau de risque (Faible, Moyen, Élevé)

#### Statistiques globales
- **Total clients** : nombre de lignes traitées
- **Sous le seuil** : clients stables (probabilité < seuil)
- **Au-dessus du seuil** : clients à risque (probabilité ≥ seuil)

### 6. Exporter le rapport

#### Option 1 : Rapport PDF (Recommandé pour présentation)
1. Cliquez sur **Rapport PDF**
2. Un fichier `churn_report.pdf` est généré avec :
   - **Page 1 - Résumé métier** :
     - Nombre total de clients traités
     - Charge à risque et charge stable
     - Taux moyen de churn estimé
     - Segments prioritaires à traiter en premier
   - **Page 2 - Analyse d'intervention** :
     - Taux de churn par géographie
     - Taux de churn par tranche d'âge
     - Taux de churn par statut actif/inactif
     - Taux de churn par nombre de produits détenus

#### Option 2 : Export CSV (Pour intégration données)
1. Cliquez sur **Export CSV**
2. Un fichier `churn_predictions.csv` est généré contenant :
   - Toutes les colonnes originales (id, CustomerId, Surname, features brutes)
   - `churn_probability` : probabilité prédite
   - `churn_prediction` : classe (Churner / Non-Churner)
   - `threshold_used` : seuil de décision appliqué
   - `risk_level` : niveau de risque (Faible, Moyen, Élevé)

---

## Backend API (pour intégrations)

### Endpoint : `POST /predict-batch-with-originals`

**Description** : Prédiction batch avec retour des colonnes originales

**Query parameters** (optionnel) :
- `threshold` (float, 0–1) : seuil de décision (par défaut : 0.45)

**Request body** :
```json
[
  {
    "id": 1,
    "CustomerId": "15634602",
    "Surname": "Hargrave",
    "CreditScore": 619,
    "Geography": "France",
    "Gender": "Female",
    "Age": 42,
    "Tenure": 2,
    "Balance": 0.0,
    "NumOfProducts": 1,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 101348.88
  }
]
```

**Response** :
```json
{
  "count": 1,
  "predictions": [0],
  "probabilities": [0.3974],
  "threshold": 0.45,
  "originals": [
    {
      "id": 1,
      "CustomerId": "15634602",
      "Surname": "Hargrave",
      ...
    }
  ],
  "report_pdf": "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo..."
}
```

**Champs de réponse** :
- `count` : nombre de clients traités
- `predictions` : liste des prédictions (0 = stable, 1 = churner)
- `probabilities` : liste des probabilités de churn (0–1)
- `threshold` : seuil de décision appliqué
- `originals` : données originales préservées pour traçabilité
- `report_pdf` : rapport PDF encodé en base64 (peut être vide si génération échouée)

Le PDF met désormais l'accent sur les indicateurs actionnables pour les équipes métier, plutôt que sur les statistiques brutes de probabilités.

**Exemple cURL** :
```bash
curl -X POST "http://localhost:8000/predict-batch-with-originals?threshold=0.3" \
  -H "Content-Type: application/json" \
  -d '[{"id": 1, "CustomerId": "15634602", "Surname": "Hargrave", "CreditScore": 619, "Geography": "France", "Gender": "Female", "Age": 42, "Tenure": 2, "Balance": 0.0, "NumOfProducts": 1, "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 101348.88}]'
```

---

## Validation et contraintes métier

Le preprocessing applique automatiquement les validations suivantes :

| Variable | Borne min | Borne max | Traitement |
|---|:---:|:---:|---|
| `CreditScore` | 300 | 850 | Clipping + médiane si hors plage |
| `Age` | 18 | 120 | Clipping + médiane si hors plage |
| `Tenure` | 0 | 50 | Clipping + médiane si hors plage |
| `Balance` | 0 | ∞ | Remplacé par 0 si négatif |
| `NumOfProducts` | 1 | 10 | Mode si hors plage |
| Binaires | 0 | 1 | Mode si hors plage |

### Outliers

Les outliers continus sont **cappés** (winsorisation IQR × 3) mais **pas supprimés**, pour préserver la taille de l'échantillon.

---

## Modèle et features utilisées

### Features finales (15 variables)

Le modèle utilise **15 variables** construites automatiquement :

#### Numériques (8)
- `CreditScore`, `Age`, `Tenure`, `Balance`
- `NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`

#### Encodées (3)
- `Geography_Germany` (1 si Allemagne, 0 sinon)
- `Geography_Spain` (1 si Espagne, 0 sinon)
- `Gender_Male` (1 si homme, 0 sinon)

#### Ratios construits (4)
- `Balance_per_Product` : solde par produit
- `Tenure_Age_Ratio` : ancienneté relative à l'âge
- `Balance_Age_Ratio` : solde relatif à l'étape de vie
- `Salary_Age` : revenu relatif à l'âge

---

## Dépannage

### Erreur : "Colonnes manquantes"
- Vérifiez que toutes les features obligatoires sont présentes
- Vérifiez l'orthographe exacte des noms de colonnes

### Erreur : "Preprocessing échoué"
- Assurez-vous que les valeurs numériques ne contiennent pas de séparateurs (ex. `1,000` au lieu de `1000`)
- Vérifiez que `Geography` ∈ {France, Germany, Spain}
- Vérifiez que `Gender` ∈ {Female, Male}

### Export CSV lent ou vide
- Si le batch est très volumineux (> 10k lignes), attendez quelques secondes supplémentaires
- Vérifiez que les prédictions sont complètes en consultant le tableau

---

## Exemple complet

Voir le fichier `data/raw/Bank_churn.csv` pour un exemple de dataset au format attendu.
