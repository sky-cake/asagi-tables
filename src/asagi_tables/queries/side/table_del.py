from . import (
	board as b,
	map_join_table,
)
from ...db import qi

def drop_table_stmt(table: str) -> str:
	return f'drop table if exists {qi(f"{b}_{table}")};'

def mysql(filter_tables: set[str] | None = None) -> str:
	return map_join_table(drop_table_stmt, filter_tables)

def sqlite(filter_tables: set[str] | None = None) -> str:
	return mysql(filter_tables)

def postgresql(filter_tables: set[str] | None = None) -> str:
	return mysql(filter_tables)
