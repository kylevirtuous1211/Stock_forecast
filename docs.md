# Bug Fixes & Troubleshooting Log

## 1. Alpaca API 401 Unauthorized
- **Issue**: Received `401 Unauthorized` when querying historical data.
- **Cause**: The API keys provided (`CKGE...`) are for the Alpaca Paper Trading (Sandbox) environment, but the client was initialized for the Live environment by default.
- **Fix**: Initialized `StockHistoricalDataClient` with `sandbox=True`.

## 2. SIP Data Restriction
- **Issue**: API returned `{"message": "subscription does not permit querying recent SIP data"}` or empty data when querying `feed='iex'`.
- **Cause**: The free/paper plan has a 15-minute delay for SIP data and does not always have full IEX coverage for near-real-time queries.
- **Fix**: Modified queries to fetch data older than 15 minutes (or from the previous trading day) to ensure data availability.

## 3. KeyError: 'symbol' in Historical Service
- **Issue**: `KeyError: 'symbol'` when processing API responses.
- **Cause**: Alpaca API returns a MultiIndex DataFrame (timestamp, symbol) or sometimes an empty DataFrame. The code assumed `symbol` was a column.
- **Fix**: Added checks for empty DataFrames and logic to `reset_index` to ensure `symbol` and `timestamp` are available as columns.

## 4. Package Discovery Errors
- **Issue**: `uv` failed to install/run due to `setuptools` complaining about multiple top-level packages (`backend`, `model`).
- **Fix**: Explicitly configured `[tool.setuptools] packages = ["backend", "model"]` in `pyproject.toml`.
