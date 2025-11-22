from . import (
	board as b,
	map_join_index,
	TI,
)
from ...db import qi

def drop_index_mysql(table: str, index: TI) -> str:
	return f'drop index {index.name} on {qi(f"{b}_{table}")};'

def drop_index_sqlite(table: str, index: TI) -> str:
	return f'drop index if exists {qi(f"{b}_{table}_{index.name}")};'

def mysql(*args) -> str:
	return map_join_index(drop_index_mysql)

def sqlite(*args) -> str:
	return map_join_index(drop_index_sqlite)

def postgresql(*args) -> str:
	return sqlite()
