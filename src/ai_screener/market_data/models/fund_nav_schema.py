#: Mutual funds get a sibling schema rather than reusing STANDARD_COLUMNS
#: (see market_data/models/schema.py): a daily NAV has no open/high/low
#: or volume, so forcing it into the OHLCV shape would mean nulling out
#: most columns for no benefit. This is its own small, parallel
#: Provider -> Normalizer -> Service -> Repository stack (see
#: market_data/mutual_funds/), proving the architecture extends to a
#: genuinely different asset-class shape, not just OHLCV variants.
FUND_NAV_STANDARD_COLUMNS = [
    "scheme_code",
    "scheme_name",
    "fund_house",
    "date",
    "nav",
    "provider",
]
