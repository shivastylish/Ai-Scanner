from ai_screener.indicators.calculators import (
    ATRCalculator,
    CPRCalculator,
    EMACalculator,
    MACDCalculator,
    RSICalculator,
)
from ai_screener.indicators.registry import IndicatorRegistry


def register_default_indicators() -> None:
    IndicatorRegistry.register(CPRCalculator())
    IndicatorRegistry.register(EMACalculator())
    IndicatorRegistry.register(RSICalculator())
    IndicatorRegistry.register(ATRCalculator())
    IndicatorRegistry.register(MACDCalculator())
