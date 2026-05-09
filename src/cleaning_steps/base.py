from abc import ABC, abstractmethod
import pandas as pd


class BaseCleaningStep(ABC):
    """Classe de base pour toutes les étapes de nettoyage.

    Les DataFrames passés incluent la colonne cible afin que les suppressions
    de lignes (ex. business constraints) maintiennent l'alignement X / y.

    Contrat
    -------
    - fit(df_train)        : calcule les statistiques sur le train uniquement
    - transform(df)        : applique la transformation sans recalcul
    - fit_transform(df)    : raccourci fit + transform
    """

    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params
        self._fitted = False

    @abstractmethod
    def fit(self, df: pd.DataFrame) -> "BaseCleaningStep":
        """Calcule les statistiques nécessaires à partir du jeu d'entraînement."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applique la transformation (sans recalcul des statistiques)."""

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)