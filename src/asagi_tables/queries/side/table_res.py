from . import (
	board as b,
	map_join_table,
	backup_suffix as suf,
)

def restore_table_mysql(st: str) -> str:
	return f"rename table `{b}_{st}_{suf}` to `{b}_{st}`;"

def restore_table_sqlite(st: str) -> str:
	return f"alter table `{b}_{st}_{suf}` rename to `{b}_{st}`;"

def restore_table_postgresql(st: str) -> str:
	return f'alter table if exists "{b}_{st}_{suf}" rename to "{b}_{st}";'

def mysql(filter_tables: set[str] | None = None) -> str:
	return map_join_table(restore_table_mysql, filter_tables)

def sqlite(filter_tables: set[str] | None = None) -> str:
	return map_join_table(restore_table_sqlite, filter_tables)

def postgresql(filter_tables: set[str] | None = None) -> str:
	return map_join_table(restore_table_postgresql, filter_tables)
