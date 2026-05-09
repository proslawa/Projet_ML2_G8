import logging
import pandas as pd
from .base import BaseCleaningStep

logger = logging.getLogger(__name__)


class OutlierCapper(BaseCleaningStep):
    """Capping des outliers par la méthode IQR.

    Les bornes sont calculées sur df_train uniquement (fit), puis appliquées
    via clip() — aucune ligne n'est supprimée, l'alignement X/y est conservé.
    Seules les colonnes listées dans 'columns' sont modifiées (jamais la cible).
    """

    def fit(self, df: pd.DataFrame) -> "OutlierCapper":
        factor = self.params.get("factor", 3.0)
        columns = self.params.get("columns", [])

        self._bounds = {}
        for col in columns:
            if col not in df.columns:
                logger.warning(f"OutlierCapper : colonne '{col}' absente, ignorée.")
                continue
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            self._bounds[col] = {
                "lower": q1 - factor * iqr,
                "upper": q3 + factor * iqr,
            }
            logger.info(
                f"  {col} : borne basse={self._bounds[col]['lower']:.2f},"
                f" borne haute={self._bounds[col]['upper']:.2f}"
            )
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("OutlierCapper : appelez fit() avant transform().")
        df = df.copy()
        for col, bounds in self._bounds.items():
            if col not in df.columns:
                continue
            n_out = ((df[col] < bounds["lower"]) | (df[col] > bounds["upper"])).sum()
            df[col] = df[col].clip(lower=bounds["lower"], upper=bounds["upper"])
            if n_out:
                logger.debug(f"  {col} : {n_out} valeurs cappées.")
        return df