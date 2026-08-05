from abc import ABC, abstractmethod

import pandas as pd


class DataNormalizer(ABC):

    @abstractmethod
    def normalize(
        self,
        df: pd.DataFrame,
        symbol: str,
    ) -> pd.DataFrame:
        ...