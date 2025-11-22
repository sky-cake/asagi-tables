from . import (
	board as b,
	map_join_table,
	backup_suffix as suf,
)
from ...db import qi

def rename_table_mysql(st: str) -> str:
	return f"rename table {qi(f'{b}_{st}')} to {qi(f'{b}_{st}_{suf}')};"

def rename_table_sqlite(st: str) -> str:
	return f"alter table {qi(f'{b}_{st}')} rename to {qi(f'{b}_{st}_{suf}')};"

def rename_table_postgresql(st: str) -> str:
	return f'alter table if exists {qi(f"{b}_{st}")} rename to {qi(f"{b}_{st}_{suf}")};'

def mysql(filter_tables: set[str] | None = None) -> str:
	return map_join_table(rename_table_mysql, filter_tables)

def sqlite(filter_tables: set[str] | None = None) -> str:
	return map_join_table(rename_table_sqlite, filter_tables)

def postgresql(filter_tables: set[str] | None = None) -> str:
	return map_join_table(rename_table_postgresql, filter_tables)
