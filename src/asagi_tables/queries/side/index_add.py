from . import (
	board as b,
	TI,
	map_join_index,
)
from ...db import qi

def st(table: str):
	return f'{b}_{table}'

def mysql_t(table: str, ti: TI):
	unique = ' unique' if ti.unique else ''
	index_name = qi(f'{b}_{table}_{ti.name}')
	return f'create{unique} index if not exists {index_name} on {qi(st(table))} ({columns});'

def mysql(*args) -> str:
	return map_join_index(mysql_t)

def sqlite_t(table: str, ti: TI):
	unique = 'unique ' if ti.unique else ''
	index = qi(f'{b}_{table}_{ti.name}')
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'create {unique}index if not exists {index} on {qi(f"{b}_{table}")}({columns});'

def sqlite(*args) -> str:
	return map_join_index(sqlite_t)

def postgresql_t(table: str, ti: TI):
	t = qi(st(table))
	index = qi(f'{st(table)}_{ti.name}')
	return f'create index if not exists {index} on {t} ({ti.colummns[0]});'

def postgresql(*args) -> str:
	return map_join_index(postgresql_t)
