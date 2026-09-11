from ai_screener.market_data.normalization.base import DataNormalizer
from ai_screener.market_data.normalization.registry import NormalizerRegistry


class NormalizerFactory:
    """Factory class for resolving normalizers by provider name."""

    @staticmethod
    def get_normalizer(provider_name: str) -> DataNormalizer:
        return NormalizerRegistry.get(provider_name)
