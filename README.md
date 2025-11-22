# Asagi Tables

- Python cli to manage [Asagi schema](https://github.com/bibanon/asagi_schema) tables
- Supports mysql/mariadb, sqlite and postgresql. Postgresql has not been tested.

To run the CLI, you can use Python's module execution:

```bash
# From the src directory
cd src
python -m asagi_tables base table add BOARD
python -m asagi_tables side table add BOARD --only threads images
```

**Note:** The `asagi.toml` config file will be automatically found if it's in either your current working directory or the project root directory.

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

## Cli
### Config file
- Copy `asagi.tpl.toml` to `asagi.toml` and adapt contents as needed
- The `asagi.toml` file can be placed in either:
  - The **current working directory** where you run the CLI commands (checked first)
  - The **project root directory** (where `asagi.tpl.toml` or `pyproject.toml` is located, checked second)
- If `asagi.toml` is not found, `config.toml` will be tried in the same locations
- Same keys used as in [Ayase-Quart](https://github.com/sky-cake/ayase-quart)

**Example:**
```bash
# Recommended: Place asagi.toml in the project root and run from there
cd /path/to/asagi-tables-master/
# asagi.toml is in the project root
python -m asagi_tables base table add BOARD

# Or run from any directory with asagi.toml in that directory
cd /home/user/myproject/
# asagi.toml should be in /home/user/myproject/
asagi base table add BOARD
```

### Available commands
- `BOARD` is one or more boards
- For side table operations, `--only` can specify which tables to operate on (default: all side tables: `threads`, `images`, `users`, `daily`, `deleted`)
- For `populate`, only `threads` and `images` are supported (default: both)
```sh
asagi base table add BOARD
asagi base table drop BOARD
asagi base table backup BOARD
asagi base table restore BOARD
asagi base table update BOARD
asagi base index add BOARD
asagi base index drop BOARD
asagi base trigger add BOARD
asagi base trigger drop BOARD
asagi side table add BOARD [--only threads|images|users|daily|deleted]
asagi side table drop BOARD [--only threads|images|users|daily|deleted]
asagi side table backup BOARD [--only threads|images|users|daily|deleted]
asagi side table restore BOARD [--only threads|images|users|daily|deleted]
asagi side table populate BOARD [--only threads|images]
asagi side index add BOARD
asagi side index drop BOARD
```

## Library
- No side table populating from here
- Use your own database connection to execute the rendered templates

```python
from asagi_tables import get_template, render_templates

template = get_template('mysql', 'side', 'table', 'backup')

rendered = render_templates(template, 'news')
print(rendered)

rendered_many = render_templates(template, ['g', 'ck', 'news'])
print(rendered_many)
```

## Development
- See [development.md](./docs/development.md)
