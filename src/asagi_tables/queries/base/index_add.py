from . import (
	board as b,
	TI,
	map_join_index,
)
from ...db import qi

board_table = qi(b)

def mysql_t(ti: TI):
	unique = ' unique' if ti.unique else ''
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	return f'alter table {board_table} add{unique} index {ti.name} ({columns});'

mysql = map_join_index(mysql_t)

def sqlite_t(ti: TI):
	unique = 'unique ' if ti.unique else ''
	columns = ', '.join(f'`{col}`' for col in ti.colummns)
	index_name = qi(f'{b}_{ti.name}')
	return f'create {unique}index if not exists {index_name} on {board_table}({columns});'

sqlite = map_join_index(sqlite_t)

def postgresql_t(ti: TI):
	index_name = qi(f'{b}_{ti.name}')
	return f'create index if not exists {index_name} on {board_table} ({ti.colummns[0]});'

postgresql = map_join_index(postgresql_t)
