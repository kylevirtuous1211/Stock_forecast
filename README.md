# Stock_forecast
Plan:# Real-time Sector Forecasting

## Setup & Running via UV

This project uses `uv` for fast dependency management.

### Prerequisites
- Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or via pip)

### Installation
1. Install dependencies and set up virtual environment:
   ```bash
   uv sync
   ```

### Managing Dependencies
To add a new dependency:
```bash
uv add <package_name>
```

### Running the Server
```bash
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Tests
```bash
uv run backend/tests/test_api.py
uv run backend/tests/test_alignment.py
```
 models to buy and sell stocks
