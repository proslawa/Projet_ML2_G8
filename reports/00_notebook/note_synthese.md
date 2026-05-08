# Note de Synthèse : Initialisation et Ingestion (Phase 0)

**Projet :** Bank Churn ML  
**Date :** 08 avril 2026  
**Objet :** Mise en place de l'infrastructure technique et validation d'ingestion (classification)

---

## 1. État d'avancement et objectifs

La phase d'initialisation vise à rendre le projet **opérationnel** pour l'équipe :

- Hydra est configuré pour centraliser les paramètres.
- Les chemins de données sont externalisés dans `configs/data/paths.yaml`.
- La base brute est référencée (Drive) et téléchargeable automatiquement si absente.
- La configuration CI (GitHub Actions) et le suivi d'expériences (MLflow) sont prêts.

## 2. Conformité aux bonnes pratiques

- **Modularité :** séparation claire `src/` (logique) et `notebooks/` (exploration).
- **Traçabilité :** MLflow configuré avec un `experiment_name` dédié.
- **Portabilité :** chemins relatifs, résolus via Hydra + `project_root`.
- **Collaboration :** configuration CI standardisée pour l'équipe.

## 3. Diagnostic initial des données (à compléter)

Ce diagnostic sera complété après un premier chargement propre :

- Taille du dataset (lignes/colonnes)
- Valeurs manquantes
- Types de variables (numériques, catégorielles)
- Distribution de la cible `Churn`

## 4. Prochaines étapes

- Lancer un premier notebook d'exploration (EDA).
- Identifier la cible et les variables explicatives.
- Préparer le plan de cleaning et de feature engineering adapté à une tâche de classification.

---

**Livrables Phase 0 :**

- [x] Structure projet prête
- [x] Configuration Hydra initiale
- [x] Chemins de données configurés
- [x] MLflow prêt
- [x] CI GitHub Actions paramétrée
