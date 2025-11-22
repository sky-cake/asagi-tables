from . import board as b
from ...db import qi

board_table = qi(b)
fk_constraint = qi(f'{b}_media_id_fk')

mysql = f'alter table {board_table} drop foreign key {fk_constraint};'

sqlite = ''

postgresql = f"alter table {board_table} drop constraint {fk_constraint};"
