from ai_screener.core.exceptions import ProviderError
from ai_screener.market_data.normalization.base import DataNormalizer


class NormalizerRegistry:
    """Registry for market data normalizers, keyed by provider name."""

    _normalizers: dict[str, DataNormalizer] = {}

    @classmethod
    def register(
        cls,
        provider_name: str,
        normalizer: DataNormalizer,
    ) -> None:
        cls._normalizers[provider_name] = normalizer

    @classmethod
    def get(cls, provider_name: str) -> DataNormalizer:
        if provider_name not in cls._normalizers:
            raise ProviderError(
                f"No normalizer registered for provider '{provider_name}'."
            )
        return cls._normalizers[provider_name]

    @classmethod
    def registered_normalizers(cls) -> list[str]:
        return sorted(cls._normalizers.keys())
