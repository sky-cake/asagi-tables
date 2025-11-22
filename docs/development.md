# Development
- Trying out `uv`

## Setup
```sh
uv venv # 3.12+

# activate your venv

uv pip install -r pyproject.toml --all-extras # all optional dependencies
uv pip install -e .
```

## Running
- Cli
```sh
asagi base|side ENTITY OPERATION BOARD1 [BOARD2 [BOARD3]...]
```

- Tests
```sh
pytest
```

- Lint
```sh
ruff check --fix
```

## Wheel
- Build
```sh
uv build --wheel # wheel in dist/
```

- Install
```sh
pip install dist/asagi_tables-0.1.0-py3-none-any.whl[sqlite] # change db and version as needed
```

## Cleanup
```sh
rm -rf dist build .pytest_cache .ruff_cache src/*.egg-info
fd -I __pycache__ . -x rm -r # fd installed
find . -type d -name __pycache__ -exec rm -r {} + # fd not installed
```

## Running Tests

To run the test suite, first install the development dependencies:

```bash
# From the project root directory (where pyproject.toml is located)
pip install -e ".[dev]"
# or with uv
uv pip install -e ".[dev]"
```

Then run pytest:

```bash
# From the project root directory
# Run all tests
pytest -v

# Run a specific test file
pytest tests/test_queries.py
```

The project's `pyproject.toml` is configured to automatically set the Python path to `src/`, so tests can be run from the project root without additional setup.
