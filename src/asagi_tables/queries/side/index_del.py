from . import (
	board as b,
	map_join_index,
	TI,
)

def drop_index_mysql(table: str, index: TI) -> str:
	return f'drop index `{index.name}` on `{b}_{table}`;'

def drop_index_sqlite(table: str, index: TI) -> str:
	return f'drop index if exists `{b}_{table}_{index.name}`;'

mysql = map_join_index(drop_index_mysql)

sqlite = map_join_index(drop_index_sqlite)

postgresql = sqlite.replace('`', '"')
