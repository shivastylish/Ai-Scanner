#: Recognized quote-currency suffixes for exchange trading-pair symbols
#: (e.g. "BTCUSDT" -> "USDT", "BTC-USDT" -> "USDT"), longest first so
#: "USDT" matches before a hypothetical shorter overlapping suffix would.
_KNOWN_QUOTE_CURRENCIES = ("USDT", "BUSD", "USDC", "USD", "BTC", "ETH")


def infer_quote_currency(symbol: str) -> str:
    """Best-effort quote currency for an exchange pair symbol.

    Exchange APIs don't return the quote currency as a separate field
    the way CoinGecko's `vs_currency` parameter does, so this is
    inferred from the symbol itself. Falls back to "USD" when no known
    suffix matches - a reasonable default, not a guarantee of accuracy.
    """

    normalized = symbol.upper().replace("-", "").replace("_", "").replace("/", "")

    for quote in _KNOWN_QUOTE_CURRENCIES:
        if normalized.endswith(quote):
            return quote

    return "USD"
