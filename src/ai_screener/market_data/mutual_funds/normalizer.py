import pandas as pd

from ai_screener.market_data.models.fund_nav_schema import FUND_NAV_STANDARD_COLUMNS


class FundNavNormalizer:
    """Normalizes MFAPIProvider's raw output into the fund_nav schema."""

    def normalize(self, df: pd.DataFrame, scheme_code: str) -> pd.DataFrame:
        data = df.copy()

        data["scheme_code"] = scheme_code
        data["provider"] = "mfapi"

        return data[FUND_NAV_STANDARD_COLUMNS]
