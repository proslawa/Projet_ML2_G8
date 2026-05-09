import logging
import pandas as pd
from omegaconf import DictConfig, OmegaConf

from utils.config_loader import PROJECT_ROOT
from .load_data import save_metadata
from cleaning_steps import STEP_REGISTRY

logger = logging.getLogger(__name__)


def run_cleaning_pipeline(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    cfg: DictConfig,
) -> tuple:
    """Pipeline de nettoyage sans data leakage.

    Chaque étape est fittée sur df_train uniquement, puis appliquée à df_test.
    Les DataFrames incluent la colonne cible pour maintenir l'alignement X/y
    en cas de suppression de lignes (ex. BusinessConstraints).

    Paramètres
    ----------
    df_train : DataFrame d'entraînement complet (features + cible)
    df_test  : DataFrame de test complet (features + cible)
    cfg      : configuration Hydra (cleaning.pipeline + cleaning.steps)

    Retourne
    --------
    (df_train_clean, df_test_clean)

    Exemple d'utilisation
    ---------------------
    df_train_clean, df_test_clean = run_cleaning_pipeline(df_train, df_test, cfg)

    target = cfg.cleaning.target_col
    X_train, y_train = df_train_clean.drop(columns=[target]), df_train_clean[target]
    X_test,  y_test  = df_test_clean.drop(columns=[target]),  df_test_clean[target]
    """
    pipeline_order = list(cfg.cleaning.pipeline)
    steps_cfg = OmegaConf.to_container(cfg.cleaning.steps, resolve=True)

    if not pipeline_order:
        logger.info("Aucune étape de nettoyage — données retournées telles quelles.")
        return df_train.copy(), df_test.copy()

    logger.info(f"Pipeline de nettoyage : {pipeline_order}")

    for step_name in pipeline_order:
        if step_name not in STEP_REGISTRY:
            raise ValueError(
                f"Étape '{step_name}' inconnue. "
                f"Disponibles : {list(STEP_REGISTRY.keys())}"
            )

        params = steps_cfg.get(step_name, {})
        step = STEP_REGISTRY[step_name](name=step_name, params=params)

        logger.info(f"--- fit sur df_train : {step_name} ---")
        df_train = step.fit_transform(df_train)

        logger.info(f"--- transform sur df_test : {step_name} ---")
        df_test = step.transform(df_test)

    logger.info(
        f"Nettoyage terminé — train : {df_train.shape}, test : {df_test.shape}"
    )
    return df_train, df_test


def save_cleaned_data(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    cfg: DictConfig,
) -> None:
    """Sauvegarde df_train_clean et df_test_clean dans data/interim/."""
    interim_dir = (PROJECT_ROOT / cfg.data.interim.dir).resolve()
    interim_dir.mkdir(parents=True, exist_ok=True)

    train_path = interim_dir / "train_clean.csv"
    test_path  = interim_dir / "test_clean.csv"

    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)

    logger.info(f"Train nettoyé  -> {train_path}")
    logger.info(f"Test nettoyé   -> {test_path}")