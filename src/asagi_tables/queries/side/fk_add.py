from . import board as b
from ...db import qi

board_table = qi(b)
images_table = qi(f'{b}_images')
fk_constraint = qi(f'{b}_media_id_fk')

mysql = f'alter table {board_table} add constraint {fk_constraint} foreign key (media_id) references {images_table}(media_id);'

sqlite = ''

postgresql = f"alter table {board_table} add constraint {fk_constraint} foreign key (media_id) references {images_table}(media_id);"
