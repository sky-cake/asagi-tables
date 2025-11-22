from . import (
	board as b,
	map_join_index,
)
from ...db import qi

board_table = qi(b)

mysql = map_join_index(
	lambda index: f"drop index {index.name} on {board_table};"
)

sqlite = map_join_index(
	lambda index: f"drop index if exists {qi(f'{b}_{index.name}')};"
)

postgresql = sqlite
