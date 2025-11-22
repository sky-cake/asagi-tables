"""
Tests to verify that all table/procedure/trigger names are properly quoted using qi()
"""
from asagi_tables.queries.templates import get_template, render_template


def _is_quoted(identifier: str, sql: str) -> bool:
	"""Check if an identifier is quoted in SQL (accepts either backticks or double quotes)"""
	return f'`{identifier}`' in sql or f'"{identifier}"' in sql


def test_table_names_quoted():
	"""Test that table names are quoted in base table operations"""
	board_name = 'test_board'

	template = get_template('mysql', 'base', 'table_del')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)

	template = get_template('mysql', 'base', 'table_bak')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)
	assert _is_quoted(f'{board_name}_bak', rendered)

	template = get_template('mysql', 'base', 'table_res')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)
	assert _is_quoted(f'{board_name}_bak', rendered)


def test_side_table_names_quoted():
	"""Test that side table names are quoted"""
	board_name = 'test_board'
	
	template = get_template('mysql', 'side', 'table_del', {'threads'})
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_threads', rendered)
	
	template = get_template('mysql', 'side', 'table_add', {'threads', 'images'})
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_threads', rendered)
	assert _is_quoted(f'{board_name}_images', rendered)


def test_procedure_names_quoted():
	"""Test that procedure names are quoted in MySQL trigger_add"""
	board_name = 'test_board'
	template = get_template('mysql', 'base', 'trigger_add')
	rendered = render_template(template, board_name)
	
	assert _is_quoted(f'update_thread_{board_name}', rendered)
	assert _is_quoted(f'create_thread_{board_name}', rendered)
	assert _is_quoted(f'delete_thread_{board_name}', rendered)
	assert _is_quoted(f'insert_image_{board_name}', rendered)
	assert _is_quoted(f'delete_image_{board_name}', rendered)
	
	assert f'CALL `insert_image_{board_name}`' in rendered or f'CALL "insert_image_{board_name}"' in rendered
	assert f'CALL `create_thread_{board_name}`' in rendered or f'CALL "create_thread_{board_name}"' in rendered
	assert f'CALL `update_thread_{board_name}`' in rendered or f'CALL "update_thread_{board_name}"' in rendered


def test_trigger_names_quoted():
	"""Test that trigger names are quoted"""
	board_name = 'test_board'
	
	template = get_template('mysql', 'base', 'trigger_add')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'before_ins_{board_name}', rendered)
	assert _is_quoted(f'after_ins_{board_name}', rendered)
	assert _is_quoted(f'after_del_{board_name}', rendered)
	
	template = get_template('sqlite', 'base', 'trigger_add')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_before_ins_media_op', rendered)
	assert _is_quoted(f'{board_name}_after_ins_op', rendered)
	assert _is_quoted(f'{board_name}_after_del_media', rendered)
	
	template = get_template('postgresql', 'base', 'trigger_add')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_after_delete', rendered)
	assert _is_quoted(f'{board_name}_before_insert', rendered)
	assert _is_quoted(f'{board_name}_after_insert', rendered)


def test_function_names_quoted():
	"""Test that PostgreSQL function names are quoted"""
	board_name = 'test_board'
	template = get_template('postgresql', 'base', 'trigger_add')
	rendered = render_template(template, board_name)
	
	assert _is_quoted(f'{board_name}_update_thread', rendered)
	assert _is_quoted(f'{board_name}_create_thread', rendered)
	assert _is_quoted(f'{board_name}_insert_image', rendered)
	assert _is_quoted(f'{board_name}_delete_image', rendered)
	
	assert f'PERFORM `{board_name}_update_thread`' in rendered or f'PERFORM "{board_name}_update_thread"' in rendered
	assert f'PERFORM `{board_name}_create_thread`' in rendered or f'PERFORM "{board_name}_create_thread"' in rendered
	assert f'SELECT `{board_name}_insert_image`' in rendered or f'SELECT "{board_name}_insert_image"' in rendered


def test_constraint_names_quoted():
	"""Test that constraint names are quoted in FK operations"""
	board_name = 'test_board'
	
	template = get_template('mysql', 'side', 'fk_add')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_media_id_fk', rendered)
	
	template = get_template('mysql', 'side', 'fk_del')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_media_id_fk', rendered)
	
	template = get_template('postgresql', 'side', 'fk_add')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_media_id_fk', rendered)
	
	template = get_template('postgresql', 'side', 'fk_del')
	rendered = render_template(template, board_name)
	assert _is_quoted(f'{board_name}_media_id_fk', rendered)


def test_table_names_in_update_statements():
	"""Test that table names in UPDATE statements are quoted"""
	board_name = 'test_board'
	
	template = get_template('mysql', 'base', 'table_upd')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)
	assert _is_quoted(f'{board_name}_images', rendered)
	
	template = get_template('sqlite', 'base', 'table_upd')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)
	assert _is_quoted(f'{board_name}_images', rendered)
	
	template = get_template('postgresql', 'base', 'table_upd')
	rendered = render_template(template, board_name)
	assert _is_quoted(board_name, rendered)
	assert _is_quoted(f'{board_name}_images', rendered)


def test_index_names_quoted():
	"""Test that index names are quoted where appropriate"""
	board_name = 'test_board'
	
	template = get_template('sqlite', 'base', 'index_del')
	rendered = render_template(template, board_name)
	assert f'`{board_name}_' in rendered or f'"{board_name}_' in rendered
