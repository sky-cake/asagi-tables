from typing import Iterable
from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_a

from . import (
	RowProcessor,
	board_rows_gen,
	insert_sidetable_fresh,
	SideTable,
	media_row_gen,
	thread_row_gen,
	thread_columns,
	media_columns,
	BATCH_THREADS,
	BATCH_IMAGES,
)

def batch_total(collection: Iterable, batch_size: int) -> int:
	quotient, remainder = divmod(len(collection), batch_size)
	if remainder:
		quotient += 1
	return quotient

async def aggregate_posts(board: str, after_doc_id: int=0):
	row_processor = RowProcessor()
	async for row_batch in tqdm_a(board_rows_gen(board, after_doc_id), desc=f'load posts'):
		row_processor.process_rows(row_batch)
	return row_processor

def normalize_side_table_names(side_tables: list[str]) -> list[str]:
	normalized = []
	for st in side_tables:
		st = st.lstrip('_')
		if st == 'images' or st == 'media':
			normalized.append('images')
		elif st == 'threads':
			normalized.append('threads')
		elif st in ('users', 'daily', 'deleted'):
			print(f'Warning: Side table "{st}" cannot be populated, only threads and images are supported')
	return normalized

async def populate_single_thread(boards: list[str], side_tables: list[str] | None = None):
	if not boards:
		return
	
	if side_tables is None:
		side_tables = ['threads', 'images']
	
	normalized_tables = normalize_side_table_names(side_tables)
	if not normalized_tables:
		print('No valid side tables specified')
		return
	
	for board in boards:
		print('Populating:', board, 'side tables:', ', '.join(normalized_tables))

		rp = await aggregate_posts(board)
		threads, medias = rp.threads, rp.medias

		if 'threads' in normalized_tables:
			for row_batch in tqdm(thread_row_gen(threads), desc=f'insert threads', total=batch_total(threads, BATCH_THREADS)):
				await insert_sidetable_fresh(SideTable.threads, thread_columns, board, row_batch)
		
		if 'images' in normalized_tables:
			for row_batch in tqdm(media_row_gen(medias), desc=f'insert medias', total=batch_total(medias, BATCH_IMAGES)):
				await insert_sidetable_fresh(SideTable.media, media_columns, board, row_batch)
