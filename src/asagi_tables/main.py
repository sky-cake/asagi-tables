import sys
import asyncio

from .queries import (
	cmd_op_mapping,
	entities,
	tabletype_modules,
)
from .db import db_type, close_pool, run_script
from .side_populate.singlethread import populate_single_thread
from .queries.templates import (
	get_template,
	render_template,
)

populate_action = 'table_populate'

def normalize_side_tables(side_tables: list[str]) -> set[str]:
	normalized = set()
	for st in side_tables:
		st = st.lstrip('_')

		# media is handled as an alias for images (because SideTable.media = 'images' in the enum)
		if st == 'media':
			normalized.add('images')
		elif st in ('threads', 'images', 'users', 'daily', 'deleted'):
			normalized.add(st)
	return normalized

async def execute_action(table_type: str, action: str, boards: list[str], side_tables: list[str] | None = None):
	if table_type == 'side' and action == populate_action:
		await populate_single_thread(boards, side_tables)
		return
	
	filter_tables = None
	if table_type == 'side' and side_tables:
		filter_tables = normalize_side_tables(side_tables)
	
	if not (template := get_template(db_type, table_type, action, filter_tables)):
		print(f'Empty template for {table_type} {action} {db_type}')
		return
	for board in boards:
		queries = render_template(template, board)
		print('Executing:', table_type, action, board)
		# print(queries)
		await run_script(queries)

def get_args():
	if len(args := sys.argv[1:]) < 4:
		return None
	table_type, entity, command, *rest = args
	
	side_tables = None
	if '--only' in rest:
		only_idx = rest.index('--only')
		side_tables = rest[only_idx + 1:]
		rest = rest[:only_idx]
	
	boards = rest
	if table_type not in tabletype_modules:
		table_types = list(tabletype_modules.keys())
		raise KeyError(f'Invalid table type: {table_type}', table_types)
	if entity not in entities:
		raise KeyError(f'Invalid entity: {entity}', entities)
	if not (op := cmd_op_mapping.get(command)):
		commands = list(cmd_op_mapping.keys())
		raise KeyError( f'Invalid command: {command}', commands )
	action = f'{entity}_{op}'
	if action not in tabletype_modules[table_type] and action != populate_action:
		raise KeyError(f'{entity} {command} not defined for {table_type}')
	return table_type, action, boards, side_tables

async def main():
	if not (args := get_args()):
		print('Invalid or not enough arguments (min 4)')
		# figure out how to print help menu
		return
	table_type, action, boards, side_tables = args
	await execute_action(table_type, action, boards, side_tables)

def run():
	loop = asyncio.new_event_loop()
	loop.set_task_factory(asyncio.eager_task_factory)
	try:
		loop.run_until_complete(main())
	except Exception as e:
		raise e
	except KeyboardInterrupt: pass
	finally:
		loop.run_until_complete(close_pool())
		loop.close()
