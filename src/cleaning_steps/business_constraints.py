import logging
import pandas as pd
from .base import BaseCleaningStep

logger = logging.getLogger(__name__)


class BusinessConstraints(BaseCleaningStep):
    """Suppression des lignes qui violent les contraintes métier.

    Pas de fit nécessaire — les bornes sont fixes (définies en config).
    Le DataFrame complet (avec cible) est reçu et retourné, ce qui garantit
    que X et y restent alignés après suppression de lignes.
    """

    def fit(self, df: pd.DataFrame) -> "BusinessConstraints":
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        bounds = self.params.get("bounds", {})
        df = df.copy()
        mask = pd.Series(True, index=df.index)

        for col, limits in bounds.items():
            if col not in df.columns:
                logger.warning(f"BusinessConstraints : colonne '{col}' absente, ignorée.")
                continue
            col_mask = pd.Series(True, index=df.index)
            if limits.get("min") is not None:
                col_mask &= df[col] >= limits["min"]
            if limits.get("max") is not None:
                col_mask &= df[col] <= limits["max"]
            n_out = (~col_mask).sum()
            if n_out:
                logger.info(f"  {col} : {n_out} lignes hors bornes supprimées.")
            mask &= col_mask

        n_dropped = (~mask).sum()
        logger.info(f"BusinessConstraints : {n_dropped} lignes supprimées au total.")
        return df[mask].reset_index(drop=True)