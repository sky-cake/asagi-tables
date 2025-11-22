# Asagi Tables

- Python cli to manage [Asagi schema](https://github.com/bibanon/asagi_schema) tables
- Supports mysql/mariadb, sqlite and postgresql. Postgresql has not been tested.

## Installing

```bash
uv venv
source .venv/bin/activate

# install option 1
pip install "asagi-tables[sqlite,cli] @ git+https://github.com/sky-cake/asagi-tables.git"

# install option 2
git clone https://github.com/sky-cake/asagi-tables
cd asagi-tables
uv pip install -e .
```


### Config file
- Copy `asagi.tpl.toml` to `asagi.toml` and adapt contents as needed
- The `asagi.toml` file can be placed in either:
  - The current working directory where you run the CLI commands (checked first)
  - The project root directory (where `asagi.tpl.toml` or `pyproject.toml` is located, checked second)
- If `asagi.toml` is not found, `config.toml` will be tried in the same locations
- Same keys used as in [Ayase-Quart](https://github.com/sky-cake/ayase-quart)

**Examples:**
```bash
asagi base table add g ck k
asagi side table add g ck k --only threads deleted
asagi side table populate g ck k --only threads
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
asagi base table update BOARD # backfills media_id in the base table by matching media_hash with the images table
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
