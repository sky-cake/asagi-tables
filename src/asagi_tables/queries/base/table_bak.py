from . import (
	board as b,
	backup_suffix as suf,
)
from ...db import qi

board_table = qi(b)
backup_table = qi(f'{b}_{suf}')

mysql = f"rename table {board_table} to {backup_table};"

sqlite = f"alter table {board_table} rename to {backup_table};"

postgresql = f'alter table if exists {board_table} rename to {backup_table};'
