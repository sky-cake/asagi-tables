from . import (
	board as b,
	backup_suffix as suf,
)
from ...db import qi

board_table = qi(b)
backup_table = qi(f'{b}_{suf}')

mysql = f"rename table {backup_table} to {board_table};"

sqlite = f"alter table {backup_table} rename to {board_table};"

postgresql = f'alter table if exists {backup_table} rename to {board_table};'
