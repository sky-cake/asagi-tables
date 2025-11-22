from asagi_tables.queries import cmd_op_mapping
from asagi_tables.queries.templates import (
	get_template,
	render_template,
)
from asagi_tables.main import normalize_side_tables

def get_args():
	import sys
	if len(args := sys.argv[1:]) < 4:
		return None
	table_type, entity, command, *rest = args
	
	side_tables = None
	if '--only' in rest:
		only_idx = rest.index('--only')
		side_tables = rest[only_idx + 1:]
		rest = rest[:only_idx]
	
	boards = rest
	from asagi_tables.queries import cmd_op_mapping, entities, tabletype_modules
	if table_type not in tabletype_modules:
		table_types = list(tabletype_modules.keys())
		raise KeyError(f'Invalid table type: {table_type}', table_types)
	if entity not in entities:
		raise KeyError(f'Invalid entity: {entity}', entities)
	if not (op := cmd_op_mapping.get(command)):
		commands = list(cmd_op_mapping.keys())
		raise KeyError( f'Invalid command: {command}', commands )
	action = f'{entity}_{op}'
	populate_action = 'table_populate'
	if action not in tabletype_modules[table_type] and action != populate_action:
		raise KeyError(f'{entity} {command} not defined for {table_type}')
	return table_type, action, boards, side_tables

def test_command_operations():
	assert 'backup' in cmd_op_mapping

def test_get_template():
	template = get_template('mysql', 'base', 'table_bak')
	assert template.startswith('rename table `')
	assert template.endswith('`;')

def test_render_template():
	t = get_template('mysql', 'base', 'table_bak')
	r = render_template(t, 'hi')
	assert r == 'rename table `hi` to `hi_bak`;'

def test_normalize_side_tables_all_tables():
	result = normalize_side_tables(['threads', 'images', 'users', 'daily', 'deleted'])
	assert result == {'threads', 'images', 'users', 'daily', 'deleted'}

def test_normalize_side_tables_media_alias():
	result = normalize_side_tables(['media'])
	assert result == {'images'}

def test_normalize_side_tables_leading_underscore():
	result = normalize_side_tables(['_threads', '_images'])
	assert result == {'threads', 'images'}

def test_normalize_side_tables_mixed():
	result = normalize_side_tables(['threads', 'media', 'users'])
	assert result == {'threads', 'images', 'users'}

def test_normalize_side_tables_invalid():
	import pytest
	with pytest.raises(ValueError, match='Invalid side table'):
		normalize_side_tables(['invalid', 'threads'])

def test_normalize_side_tables_empty():
	result = normalize_side_tables([])
	assert result == set()

def test_get_args_with_only_flag():
	import sys
	original_argv = sys.argv
	try:
		sys.argv = ['asagi', 'side', 'table', 'add', 'board1', '--only', 'threads', 'images']
		result = get_args()
		assert result is not None
		table_type, action, boards, side_tables = result
		assert table_type == 'side'
		assert action == 'table_add'
		assert boards == ['board1']
		assert side_tables == ['threads', 'images']
	finally:
		sys.argv = original_argv

def test_get_args_with_only_single_table():
	import sys
	original_argv = sys.argv
	try:
		sys.argv = ['asagi', 'side', 'table', 'drop', 'board1', '--only', 'users']
		result = get_args()
		assert result is not None
		table_type, action, boards, side_tables = result
		assert side_tables == ['users']
	finally:
		sys.argv = original_argv

def test_get_args_without_only_flag():
	import sys
	original_argv = sys.argv
	try:
		sys.argv = ['asagi', 'side', 'table', 'add', 'board1']
		result = get_args()
		assert result is not None
		table_type, action, boards, side_tables = result
		assert side_tables is None
	finally:
		sys.argv = original_argv

def test_get_args_multiple_boards_with_only():
	import sys
	original_argv = sys.argv
	try:
		sys.argv = ['asagi', 'side', 'table', 'backup', 'board1', 'board2', '--only', 'threads']
		result = get_args()
		assert result is not None
		table_type, action, boards, side_tables = result
		assert boards == ['board1', 'board2']
		assert side_tables == ['threads']
	finally:
		sys.argv = original_argv

def test_side_table_add_filtered():
	template = get_template('mysql', 'side', 'table_add', {'threads'})
	rendered = render_template(template, 'test')
	assert 'test_threads' in rendered
	assert 'test_images' not in rendered
	assert 'test_users' not in rendered

def test_side_table_add_all_tables():
	template = get_template('mysql', 'side', 'table_add', None)
	rendered = render_template(template, 'test')
	assert 'test_threads' in rendered
	assert 'test_images' in rendered
	assert 'test_users' in rendered
	assert 'test_daily' in rendered
	assert 'test_deleted' in rendered

def test_side_table_add_filtered_multiple():
	template = get_template('mysql', 'side', 'table_add', {'threads', 'users'})
	rendered = render_template(template, 'test')
	assert 'test_threads' in rendered
	assert 'test_users' in rendered
	assert 'test_images' not in rendered
	assert 'test_daily' not in rendered

def test_side_table_del_filtered():
	template = get_template('mysql', 'side', 'table_del', {'images'})
	rendered = render_template(template, 'test')
	assert 'test_images' in rendered
	assert 'test_threads' not in rendered
	assert 'test_users' not in rendered

def test_side_table_bak_filtered():
	template = get_template('mysql', 'side', 'table_bak', {'daily'})
	rendered = render_template(template, 'test')
	assert 'test_daily' in rendered
	assert 'test_threads' not in rendered
