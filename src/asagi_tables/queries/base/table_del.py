from . import board as b
from ...db import qi

board_table = qi(b)

mysql = f"drop table if exists {board_table};"

sqlite = mysql

postgresql = mysql
