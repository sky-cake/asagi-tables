from . import board as b
from ...db import qi

board_table = qi(b)
images_table = qi(f'{b}_images')

mysql = f"""
update {board_table}
inner join {images_table} using(media_hash)
set
	{board_table}.media_id = {images_table}.media_id
where
	{board_table}.media_hash is not null
	and {board_table}.media_id = 0;
"""

sqlite = f"""
update {board_table} set
	media_id = images.media_id
from (
	select media_hash, media_id
	from {images_table}
) as images
where
	{board_table}.media_hash is not null
	and {board_table}.media_id = 0
	and images.media_hash = {board_table}.media_hash;
"""

postgresql = f'''
update {board_table} set
	media_id = {images_table}.media_id
from {images_table} where
	{board_table}.media_hash is not null
	and {board_table}.media_id = 0
	and {images_table}.media_hash = {board_table}.media_hash;
'''