# AI Screener — Roadmap: Sprint 1 Close-Out Through Sprint 9+

Status key: ✅ done · 🔄 in progress · ⏳ not started

## Context

Sprint 0 (foundation: charter, PRD, HLD, LLD, governance docs) is complete.
Sprint 1 (Market Data Platform) built the ingestion pipeline for NSE
equities via Yahoo Finance through AIS-101.8 (persistence layer). This
document is the implementation roadmap from there through the rest of the
product vision: indicators, scanner, ranking, explainability, backtesting,
dashboard, portfolio/journal, and additional asset classes.

Binding constraints on every sprint below (see
[`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)
and [`CONTRIBUTING.md`](../../CONTRIBUTING.md)): Provider → Normalizer →
Pipeline → Service → Repository → Database flow, no bypassing repositories
from UI/other modules, config-over-hardcoding, one feature branch per
module, semantic commits, tests required, no secrets committed. This is
**not an automated trading bot** — no broker execution APIs, no live order
placement, in any sprint.

ADR-005 ("no strategy becomes part of AI Screener until historically
validated") is treated as a **hard gate**: Backtesting is sequenced before
the Dashboard, so no engine's output reaches a human-facing screen until
it has been run through historical validation.

## Sequencing

| # | Sprint | Branch | Tag | Status |
|---|--------|--------|-----|--------|
| 1a | Hermetic test infrastructure | `feature/market-data-platform` | — | ✅ |
| 1b | AIS-101.9 Market Data Service | `feature/market-data-platform` | `v0.2.0-market-data` | ✅ |
| 1c | Minimal CI workflow | `feature/market-data-platform` | — | ✅ |
| 2 | Indicator Engine | `feature/indicator-engine` | `v0.3.0-indicators` | ✅ |
| 3 | Scanner Engine | `feature/scanner-engine` | `v0.4.0-scanner` | ✅ |
| 4 | Ranking Engine | `feature/ranking-engine` | `v0.5.0-ranking` | ✅ |
| 5 | Explainability Engine | `feature/explainability-engine` | `v0.6.0-explainability` | ✅ |
| 6 | Backtesting | `feature/backtesting` | `v0.7.0-backtesting` | ✅ |
| 7 | Dashboard (PySide6) | `feature/dashboard` | `v0.8.0-dashboard` / `v1.0.0-beta` | ✅ |
| 8 | Portfolio + Trade Journal | `feature/portfolio`, `feature/journal` | `v0.9.x` | ✅ |
| 9+ | Mutual Funds + Crypto providers | one branch per provider | `v0.10.0+` | ✅ (MFAPI, CoinGecko, Binance, Bybit, KuCoin, CoinMarketCap — CMC unverified live, no key available) |

Dependency chain: 1 → 2 → 3 → 4 → 5 → 6 → 7, then 8 is independent and can
run any time after 1, and 9+ only depends on Sprint 1's pattern so it can
run in parallel with anything from Sprint 4 onward.

Scanner (Sprint 3) runs over a **configured watchlist**, not a full NSE
symbol-master feed — that ingestion is deferred to a later ticket.

## Sprint 1a — Hermetic test infrastructure ✅

Replaced the non-hermetic integration tests (which wrote into the real
`data/ai_screener.db` and hit live Yahoo Finance) with an in-memory SQLite
+ fake-provider pattern. See `tests/conftest.py` and
`tests/fakes/fake_provider.py`. A `live` pytest marker excludes
network-dependent tests from the default run (`pyproject.toml`
`addopts = "-m 'not live'"`).

## Sprint 1b — AIS-101.9: Market Data Service ✅

- `MarketDataService.download_history()` is now the single public entry
  point; orchestration (provider → normalizer → pipeline → repository) was
  moved out of `YahooFinanceProvider`, which now only fetches raw data.
- Added `NormalizerFactory`/`NormalizerRegistry` mirroring the provider
  pattern (`src/ai_screener/market_data/normalization/`).
- Added a unique constraint on `(symbol, datetime, asset_type, provider)`
  and upsert-on-conflict persistence (`MarketDataRepository.save()`), so
  re-downloads update existing rows instead of duplicating them.
- Adopted Alembic for schema migrations (`alembic/`); `initialize_database()`
  remains for hermetic test databases only.
- `MarketDataService.get_history()` is the read path for later sprints
  (indicators, scanner, dashboard, backtesting) — they must not call
  `MarketDataRepository` directly.
- Incremental fetch: omitting `start_date` on a symbol with existing data
  resolves to the day after the latest stored bar.
- Custom exceptions (`ProviderError`, `ValidationError`) are now raised
  instead of bare `ValueError`.
- Cleanup: removed the dead duplicate `market_data/models/market_data.py`;
  moved stray smoke scripts (`test.py`, `core/test_logger.py`) into
  `scripts/`; fixed a real secrets-hygiene gap (`.env`, the SQLite DB, and
  log files were tracked in git despite the docs describing them as
  gitignored — `.gitignore` was empty).

## Sprint 1c — Minimal CI ✅

`.github/workflows/ci.yml`: `uv sync` → ruff → black → mypy →
`pytest` (hermetic tests only) on PRs/pushes to `main`/`develop`.

## Sprint 2 — Indicator Engine

**Package:** `src/ai_screener/indicators/` (new).

- `indicators/base.py` — `Indicator` ABC: `compute(df, **params) -> pd.DataFrame`.
- `indicators/registry.py` — `IndicatorRegistry`, config-driven.
- `indicators/timeframe.py` — daily→weekly/monthly resampling (`open`=first, `high`=max, `low`=min, `close`=last, `volume`=sum).
- `indicators/calculators/cpr.py` — `CPRCalculator` (Pivot, BC, TC, Width %, Virgin CPR flag) — the product's core indicator.
- `indicators/calculators/{ema,rsi,atr,macd}.py` — hand-rolled in pandas/numpy, consistent with the rest of the codebase (no new TA library dependency).
- `indicators/service.py` — `IndicatorService`: `MarketDataService.get_history()` → run registered calculators → indicator snapshot per symbol/timeframe.
- CPR is computed by resampling daily bars in-process, not a separate monthly fetch.
- Indicator values are computed on demand for now; revisit persistence only if scanner performance requires it.

**Depends on:** Sprint 1b's `get_history()` and dedup fix.

**Testing:** pure unit tests against synthetic, hand-verifiable OHLCV data — assert against manually computed reference values, no DB/network.

## Sprint 3 — Scanner Engine

**Package:** `src/ai_screener/scanner/`.

- `scanner/conditions/base.py` — `Condition` ABC returning a structured `ConditionResult(passed, value, threshold, description)`, not a bare bool, so Sprint 5 doesn't need to retrofit richer outputs.
- `scanner/conditions/cpr_conditions.py` — `NarrowCPRCondition(max_width_pct)`.
- `scanner/conditions/{trend,volume,momentum}_conditions.py` — wrap Sprint 2's outputs.
- `scanner/rules.py` — `ScanStrategy` composing conditions via `AllOf`/`AnyOf`, loaded from config.
- `scanner/engine.py` — `ScannerEngine.scan(universe, strategy) -> list[ScanResult]`.
- `scanner/repositories/scan_result_repository.py` — new `scan_run`/`scan_result` tables; results are persisted (audit trail for ranking/explainability/backtesting/dashboard).
- Universe source: configured watchlist.

**Depends on:** Sprint 2's `IndicatorService` output shape.

## Sprint 4 — Ranking Engine

**Package:** `src/ai_screener/ranking/`.

- `ranking/factors.py` — pluggable `ScoringFactor` ABC (`CPRWidthFactor`, `TrendStrengthFactor`, `VolumeFactor`, `MomentumFactor`).
- `ranking/weights.py` — weighted-sum config.
- `ranking/engine.py` — `RankingEngine.rank(scan_results) -> list[RankedResult]`.

**To confirm before starting:** quantitative definition of "confidence" — not defined anywhere in current docs.

**Depends on:** Sprint 3's persisted `ScanResult`s only.

## Sprint 5 — Explainability Engine

**Package:** `src/ai_screener/explainability/`.

- `explainability/models.py` — `Reason(category, statement, value, evidence)`, `Explanation(symbol, reasons, confidence, generated_at)`.
- `explainability/builders/` — one builder per PRD category. `HistoricalPerformanceReasonBuilder` ships without real data until Sprint 6 exists (PRD already treats historical evidence as "when available").
- `explainability/service.py` — runs at scan-time and persists per scan result (new `explanation` table) — durable, audit-able artifacts per ADR-004.

**Depends on:** Sprint 3/4's structured `ConditionResult`/`ScoringFactor` outputs.

## Sprint 6 — Backtesting

**Package:** `src/ai_screener/backtesting/`.

- `backtesting/engine.py` — replays Sprint 3/4's evaluation logic bar-by-bar over historical windows. This is why Sprint 3's conditions are pure, stateless, date-parameterized functions — avoids look-ahead bias.
- `backtesting/simulator.py` — trade simulation (entry/exit/stop-loss/position sizing).
- `backtesting/metrics.py` — win rate, average return, max drawdown, etc.

**To confirm before starting:** entry/exit/stop-loss/position-sizing rules for the trade simulator — entirely unspecified in current docs.

**Depends on:** Sprint 2's indicators and Sprint 3/4's logic reused directly. Once validated, Sprint 5's `HistoricalPerformanceReasonBuilder` can be completed with real data.

## Sprint 7 — Dashboard (PySide6)

**Package:** `src/ai_screener/dashboard/`.

Calls `MarketDataService`, `ScannerEngine`, `RankingEngine`,
`ExplainabilityService` — never repositories directly. Only shows
strategies Sprint 6 has backtested (ADR-005 gate).

- `dashboard/app.py`, `dashboard/main_window.py`, `dashboard/views/scan_results_view.py`.
- `dashboard/viewmodels/` — thin adapters between service-layer DTOs and Qt models.
- `dashboard/widgets/explanation_panel.py` — renders `Explanation.reasons`.

**To confirm before starting:** `pytest-qt` as a new dev dependency, or structure viewmodels to avoid needing it.

## Sprint 8 — Portfolio + Trade Journal

**Packages:** `src/ai_screener/portfolio/`, `src/ai_screener/journal/` — two packages, two feature branches (ADR-007).

Standard CRUD over new tables through Service→Repository→Database; no
provider layer needed (user-entered data). Portfolio reads live prices via
`MarketDataService`. Independent of Sprints 2–7 — can run any time after
Sprint 1.

## Sprint 9+ — Mutual Funds + Crypto ✅ (MFAPI, CoinGecko, Binance, Bybit, KuCoin, CoinMarketCap)

Extends Sprint 1's Provider→Normalizer→Pipeline→Service→Repository
pattern — the intended proof the architecture scales to new asset classes.

- **Mutual Funds (done):** a fully parallel, sibling stack under `market_data/mutual_funds/` (`MFAPIProvider`, `FundNavNormalizer`, `MutualFundService`, `FundNavRepository`) against a sibling `fund_nav` table (`database/models.py`'s `FundNav`), rather than reusing the OHLCV `MarketData` schema — NAV doesn't fit `STANDARD_COLUMNS`. `expense_ratio`/`aum` columns exist but are nullable and unpopulated: mfapi.in's free API doesn't provide them; a future provider/enrichment source can fill them in without a schema change. Verified against the live API (`@pytest.mark.live`).
- **Crypto — all five sources done:** `CoinGeckoProvider`, `BinanceProvider`, `BybitProvider`, `KuCoinProvider`, `CoinMarketCapProvider` (each with a matching normalizer) reuse the existing `MarketDataProvider`/`MarketDataService`/`MarketData` schema and repository directly — the "more mechanical extension" the plan anticipated.
  - Since several exchanges can all serve `asset_type="crypto"` at once (unlike equities' one canonical source), `ProviderRegistry` grew a second lookup path — `register_named()` / `get_by_name()` — so a specific exchange can be addressed via `provider_name=` on `MarketDataService.download_history()`/`get_history()`, independent of `Settings.DEFAULT_CRYPTO_PROVIDER` (which picks what plain `asset_type="crypto"` resolves to, default `"coingecko"`). This also uncovered and fixed a real bug: `get_latest_datetime()`/`get_history()` didn't filter by provider, so two exchanges sharing a symbol string (e.g. both using "BTCUSDT") would have had their incremental-fetch and read-back logic silently mixed together — both now take an optional `provider` filter.
  - CoinGecko's free OHLC endpoint has no volume field, so its crypto candles report `volume=0.0`; any scanner condition depending on volume (e.g. `VolumeAboveAverageCondition`) won't be meaningful for CoinGecko-sourced crypto. Binance/Bybit/KuCoin all report real volume.
  - KuCoin's raw candle array order is `[time, open, close, high, low, volume, turnover]` — close before high/low, unlike every other provider's OHLC order. `KuCoinProvider` corrects this on the way in; verified live against a high/low-bracket sanity check, not just a shape check.
  - CoinMarketCap requires a paid-tier API key (`COINMARKETCAP_API_KEY`) not available while building this — implemented against their documented v2 OHLCV contract and unit-tested against a fabricated response matching that shape, but **not verified against the live API**. `ENABLE_COINMARKETCAP` defaults to `false`; its live test skips automatically without a key and will genuinely validate (or catch a wrong assumption in) this implementation the first time it runs with one.
  - Binance/Bybit/KuCoin's public market-data endpoints need no API key at all; the `*_API_KEY`/`*_SECRET_KEY` placeholders in `.env.example` are for future trading/account-level features, unused by anything implemented so far.

## Decisions locked in for this roadmap

- ADR-005 treated as a hard gate: Backtesting before Dashboard.
- Symbol universe: configured watchlist for V1 scanning.
- Alembic adopted in Sprint 1b.
- Scan results and explanations are persisted; indicator values computed on demand.
- Evidence-object design (`ConditionResult`, `ScoringFactor`) locked in from Sprint 3 onward.
- Mutual funds get a sibling schema rather than reusing the OHLCV schema.

## Verification approach (every sprint)

- `pytest` (hermetic, default) must pass with no network access and no writes to `data/ai_screener.db`.
- `ruff`, `black --check`, `mypy` (strict) must pass for changed files.
- Each sprint's integration test exercises its module end-to-end against in-memory SQLite using the Sprint 1a fixture pattern.
- The one live network check stays marked `@pytest.mark.live`, run manually, not in CI.
