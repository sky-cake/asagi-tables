from . import board as b
from ...db import qi

board_table = qi(b)
threads_table = qi(f'{b}_threads')
images_table = qi(f'{b}_images')
daily_table = qi(f'{b}_daily')
users_table = qi(f'{b}_users')

# MySQL procedures
proc_update_thread = qi(f'update_thread_{b}')
proc_create_thread = qi(f'create_thread_{b}')
proc_delete_thread = qi(f'delete_thread_{b}')
proc_insert_image = qi(f'insert_image_{b}')
proc_delete_image = qi(f'delete_image_{b}')
proc_insert_post = qi(f'insert_post_{b}')
proc_delete_post = qi(f'delete_post_{b}')

# MySQL triggers
trigger_before_ins = qi(f'before_ins_{b}')
trigger_after_ins = qi(f'after_ins_{b}')
trigger_after_del = qi(f'after_del_{b}')

# SQLite triggers
trigger_before_ins_media_op = qi(f'{b}_before_ins_media_op')
trigger_before_ins_media_reply = qi(f'{b}_before_ins_media_reply')
trigger_after_ins_media = qi(f'{b}_after_ins_media')
trigger_after_ins_op = qi(f'{b}_after_ins_op')
trigger_after_ins_reply = qi(f'{b}_after_ins_reply')
trigger_after_ins_reply_ghost = qi(f'{b}_after_ins_reply_ghost')
trigger_after_del_media = qi(f'{b}_after_del_media')
trigger_after_del_op = qi(f'{b}_after_del_op')
trigger_after_del_reply = qi(f'{b}_after_del_reply')
trigger_after_del_reply_ghost = qi(f'{b}_after_del_reply_ghost')

# PostgreSQL functions
func_update_thread = qi(f'{b}_update_thread')
func_create_thread = qi(f'{b}_create_thread')
func_delete_thread = qi(f'{b}_delete_thread')
func_insert_image = qi(f'{b}_insert_image')
func_delete_image = qi(f'{b}_delete_image')
func_insert_post = qi(f'{b}_insert_post')
func_delete_post = qi(f'{b}_delete_post')
func_before_insert = qi(f'{b}_before_insert')
func_after_insert = qi(f'{b}_after_insert')
func_after_del = qi(f'{b}_after_del')

# PostgreSQL triggers
pg_trigger_after_delete = qi(f'{b}_after_delete')
pg_trigger_before_insert = qi(f'{b}_before_insert')
pg_trigger_after_insert = qi(f'{b}_after_insert')

mysql = f"""
drop procedure if exists {proc_update_thread};
drop procedure if exists {proc_create_thread};
drop procedure if exists {proc_delete_thread};
drop procedure if exists {proc_insert_image};
drop procedure if exists {proc_delete_image};
drop procedure if exists {proc_insert_post};
drop procedure if exists {proc_delete_post};

drop trigger if exists {trigger_before_ins};
drop trigger if exists {trigger_after_ins};
drop trigger if exists {trigger_after_del};

create procedure if not exists {proc_update_thread} (ins INT, tnum INT, subnum INT, timestamp INT, media INT, email VARCHAR(100))
BEGIN
	UPDATE
		{threads_table} op
	SET
		op.time_last = IF((ins AND subnum = 0), GREATEST(timestamp, op.time_last), op.time_last),
		op.time_bump = IF((ins AND subnum = 0), GREATEST(timestamp, op.time_bump), op.time_bump),
		op.time_ghost = IF((ins AND subnum != 0), GREATEST(timestamp, COALESCE(op.time_ghost, 0)), op.time_ghost),
		op.time_ghost_bump = IF((ins AND subnum != 0 AND (email IS NULL OR email != 'sage')), GREATEST(timestamp, COALESCE(op.time_ghost_bump, 0)), op.time_ghost_bump),
		op.time_last_modified = GREATEST(timestamp, op.time_last_modified),
		op.nreplies = IF(ins, (op.nreplies + 1), (op.nreplies - 1)),
		op.nimages = IF(media, IF(ins, (op.nimages + 1), (op.nimages - 1)), op.nimages)
	WHERE op.thread_num = tnum;
END;

create procedure if not exists {proc_create_thread} (num INT, timestamp INT)
BEGIN
	INSERT IGNORE INTO {threads_table} VALUES
		(num, timestamp, timestamp, timestamp, NULL, NULL, timestamp, 0, 0, 0, 0);
END;

create procedure if not exists {proc_delete_thread} (tnum INT)
BEGIN
	delete from {threads_table} WHERE thread_num = tnum;
END;

create procedure if not exists {proc_insert_image} (n_media_hash VARCHAR(25), n_media VARCHAR(50), n_preview VARCHAR(50), n_op INT)
BEGIN
	IF n_op = 1 THEN
		INSERT INTO {images_table} (media_hash, media, preview_op, total)
		VALUES (n_media_hash, n_media, n_preview, 1)
		ON DUPLICATE KEY UPDATE
			media_id = LAST_INSERT_ID(media_id),
			total = (total + 1),
			preview_op = COALESCE(preview_op, VALUES(preview_op)),
			media = COALESCE(media, VALUES(media));
	ELSE
		INSERT INTO {images_table} (media_hash, media, preview_reply, total)
		VALUES (n_media_hash, n_media, n_preview, 1)
		ON DUPLICATE KEY UPDATE
			media_id = LAST_INSERT_ID(media_id),
			total = (total + 1),
			preview_reply = COALESCE(preview_reply, VALUES(preview_reply)),
			media = COALESCE(media, VALUES(media));
	END IF;
END;

create procedure if not exists {proc_delete_image} (n_media_id INT)
BEGIN
	UPDATE {images_table} SET total = (total - 1) WHERE media_id = n_media_id;
END;

create trigger {trigger_before_ins} before insert on {board_table}
FOR EACH ROW
BEGIN
	IF NEW.media_hash IS NOT NULL THEN
		CALL {proc_insert_image}(NEW.media_hash, NEW.media_orig, NEW.preview_orig, NEW.op);
		SET NEW.media_id = LAST_INSERT_ID();
	END IF;
END;

create trigger {trigger_after_ins} after insert on {board_table}
FOR EACH ROW
BEGIN
	IF NEW.op = 1 THEN
		CALL {proc_create_thread}(NEW.num, NEW.timestamp);
	END IF;
	CALL {proc_update_thread}(1, NEW.thread_num, NEW.subnum, NEW.timestamp, NEW.media_id, NEW.email);
END;

create trigger {trigger_after_del} after delete on {board_table}
FOR EACH ROW
BEGIN
	CALL {proc_update_thread}(0, OLD.thread_num, OLD.subnum, OLD.timestamp, OLD.media_id, OLD.email);
	IF OLD.op = 1 THEN
		CALL {proc_delete_thread}(OLD.num);
	END IF;
	IF OLD.media_hash IS NOT NULL THEN
		CALL {proc_delete_image}(OLD.media_id);
	END IF;
END;
"""

sqlite = f"""
CREATE TRIGGER IF NOT EXISTS {trigger_before_ins_media_op}
BEFORE INSERT ON {board_table} FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.op = 1
BEGIN
	INSERT INTO {images_table} (media_hash, media, preview_op, total)
	VALUES (NEW.media_hash, NEW.media_orig, NEW.preview_orig, 1)
	ON CONFLICT (media_hash) DO UPDATE SET
		total = (total + 1),
		preview_op = COALESCE(preview_op, EXCLUDED.preview_op),
		media = COALESCE(media, EXCLUDED.media);
END;

CREATE TRIGGER IF NOT EXISTS {trigger_before_ins_media_reply}
BEFORE INSERT ON {board_table} FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.op = 0
BEGIN
	INSERT INTO {images_table} (media_hash, media, preview_reply, total)
	VALUES (NEW.media_hash, NEW.media_orig, NEW.preview_orig, 1)
	ON CONFLICT (media_hash) DO UPDATE SET
		total = (total + 1),
		preview_reply = COALESCE(preview_reply, EXCLUDED.preview_reply),
		media = COALESCE(media, EXCLUDED.media);
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_ins_media}
AFTER INSERT ON {board_table} FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.media_id = 0
BEGIN
	UPDATE {board_table} SET media_id = (
		SELECT media_id FROM {images_table} WHERE media_hash = NEW.media_hash
	) WHERE doc_id = NEW.doc_id;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_ins_op}
AFTER INSERT ON {board_table} FOR EACH ROW
WHEN NEW.op = 1
BEGIN
	INSERT OR IGNORE INTO {threads_table} (thread_num, time_op, time_last, time_bump, time_last_modified, nimages)
	VALUES (
		NEW.num, NEW.timestamp, NEW.timestamp, NEW.timestamp, NEW.timestamp,
		(NEW.media_hash IS NOT NULL)
	);
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_ins_reply}
AFTER INSERT ON {board_table} FOR EACH ROW
WHEN NEW.op = 0 AND NEW.subnum = 0
BEGIN
	UPDATE
		{threads_table}
	SET
		time_last = MAX(NEW.timestamp, time_last),
		time_bump = CASE WHEN (NEW.email = 'sage') THEN time_bump ELSE MAX(NEW.timestamp, COALESCE(time_bump, 0)) END,
		time_last_modified = MAX(NEW.timestamp, time_last_modified),
		nreplies = (nreplies + 1),
		nimages = nimages + (NEW.media_id IS NOT NULL)
	WHERE thread_num = NEW.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_ins_reply_ghost}
AFTER INSERT ON {board_table} FOR EACH ROW
WHEN NEW.op = 0 AND NEW.subnum != 0
BEGIN
	UPDATE
		{threads_table}
	SET
		time_ghost = MAX(NEW.timestamp, COALESCE(time_ghost, 0)),
		time_ghost_bump = CASE WHEN (NEW.email = 'sage') THEN time_ghost_bump ELSE MAX(NEW.timestamp, COALESCE(time_ghost_bump, 0)) END,
		time_last_modified = MAX(NEW.timestamp, time_last_modified),
		nreplies = (nreplies + 1),
		nimages = nimages + (NEW.media_id IS NOT NULL)
	WHERE thread_num = NEW.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_del_media}
AFTER DELETE ON {board_table} FOR EACH ROW
WHEN OLD.media_hash IS NOT NULL
BEGIN
	UPDATE {images_table} SET total = (total - 1) WHERE media_id = OLD.media_id;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_del_op}
AFTER DELETE ON {board_table} FOR EACH ROW
WHEN OLD.op = 1
BEGIN
	DELETE FROM {threads_table} WHERE thread_num = OLD.num;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_del_reply}
AFTER DELETE ON {board_table} FOR EACH ROW
WHEN OLD.op = 0 AND OLD.subnum = 0
BEGIN
	UPDATE
		{threads_table}
	SET
		time_last_modified = MAX(OLD.timestamp, time_last_modified),
		nreplies = (nreplies - 1),
		nimages = nimages - (OLD.media_id IS NOT NULL)
	WHERE thread_num = OLD.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS {trigger_after_del_reply_ghost}
AFTER DELETE ON {board_table} FOR EACH ROW
WHEN OLD.op = 0 AND OLD.subnum != 0
BEGIN
	UPDATE
		{threads_table}
	SET
		time_last_modified = MAX(OLD.timestamp, time_last_modified),
		nreplies = (nreplies - 1),
		nimages = nimages - (OLD.media_id IS NOT NULL)
	WHERE thread_num = OLD.thread_num;
END;
"""

postgresql = f'''
create or replace function {func_update_thread}(n_row {board_table}) RETURNS void AS $$
BEGIN
	UPDATE
		{threads_table} AS op
	SET
		time_last = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT MAX(timestamp) FROM {board_table} re WHERE
					re.thread_num = $1.thread_num AND re.subnum = 0)
			), op.time_op)
		),
		time_bump = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT MAX(timestamp) FROM {board_table} re WHERE
					re.thread_num = $1.thread_num AND (re.email <> 'sage' OR re.email IS NULL)
					AND re.subnum = 0)
			), op.time_op)
		),
		time_ghost = (
			SELECT MAX(timestamp) FROM {board_table} re WHERE
				re.thread_num = $1.thread_num AND re.subnum <> 0
		),
		time_ghost_bump = (
			SELECT MAX(timestamp) FROM {board_table} re WHERE
				re.thread_num = $1.thread_num AND re.subnum <> 0 AND (re.email <> 'sage' OR
					re.email IS NULL)
		),
		time_last_modified = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT GREATEST(MAX(timestamp), MAX(timestamp_expired)) FROM {board_table} re WHERE
					re.thread_num = $1.thread_num)
			), op.time_op)
		),
		nreplies = (
			SELECT COUNT(*) FROM {board_table} re WHERE
				re.thread_num = $1.thread_num
		),
		nimages = (
			SELECT COUNT(media_hash) FROM {board_table} re WHERE
				re.thread_num = $1.thread_num
		)
		WHERE op.thread_num = $1.thread_num;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_create_thread}(n_row {board_table}) RETURNS void AS $$
BEGIN
	IF n_row.op = false THEN RETURN; END IF;
	INSERT INTO {threads_table} SELECT $1.num, $1.timestamp, $1.timestamp,
			$1.timestamp, NULL, NULL, $1.timestamp, 0, 0, false, false WHERE NOT EXISTS (SELECT 1 FROM {threads_table} WHERE thread_num=$1.num);
	RETURN;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_delete_thread}(n_parent integer) RETURNS void AS $$
BEGIN
	delete from {threads_table} WHERE thread_num = n_parent;
	RETURN;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_insert_image}(n_row {board_table}) RETURNS integer AS $$
DECLARE
		img_id INTEGER;
BEGIN
	INSERT INTO {images_table}
		(media_hash, media, preview_op, preview_reply, total)
		SELECT n_row.media_hash, n_row.media_orig, NULL, NULL, 0
		WHERE NOT EXISTS (SELECT 1 FROM {images_table} WHERE media_hash = n_row.media_hash);

	IF n_row.op = true THEN
		UPDATE {images_table} SET total = (total + 1), preview_op = COALESCE(preview_op, n_row.preview_orig) WHERE media_hash = n_row.media_hash RETURNING media_id INTO img_id;
	ELSE
		UPDATE {images_table} SET total = (total + 1), preview_reply = COALESCE(preview_reply, n_row.preview_orig) WHERE media_hash = n_row.media_hash RETURNING media_id INTO img_id;
	END IF;
	RETURN img_id;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_delete_image}(n_media_id integer) RETURNS void AS $$
BEGIN
	UPDATE {images_table} SET total = (total - 1) WHERE id = n_media_id;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_insert_post}(n_row {board_table}) RETURNS void AS $$
DECLARE
	d_day integer;
	d_image integer;
	d_sage integer;
	d_anon integer;
	d_trip integer;
	d_name integer;
BEGIN
	d_day := FLOOR($1.timestamp/86400)*86400;
	d_image := CASE WHEN $1.media_hash IS NOT NULL THEN 1 ELSE 0 END;
	d_sage := CASE WHEN $1.email = 'sage' THEN 1 ELSE 0 END;
	d_anon := CASE WHEN $1.name = 'Anonymous' AND $1.trip IS NULL THEN 1 ELSE 0 END;
	d_trip := CASE WHEN $1.trip IS NOT NULL THEN 1 ELSE 0 END;
	d_name := CASE WHEN COALESCE($1.name <> 'Anonymous' AND $1.trip IS NULL, TRUE) THEN 1 ELSE 0 END;

	INSERT INTO {daily_table}
		SELECT d_day, 0, 0, 0, 0, 0, 0
		WHERE NOT EXISTS (SELECT 1 FROM {daily_table} WHERE day = d_day);

	UPDATE {daily_table} SET posts=posts+1, images=images+d_image,
		sage=sage+d_sage, anons=anons+d_anon, trips=trips+d_trip,
		names=names+d_name WHERE day = d_day;

	IF (SELECT trip FROM {users_table} WHERE trip = $1.trip) IS NOT NULL THEN
		UPDATE {users_table} SET postcount=postcount+1,
			firstseen = LEAST($1.timestamp, firstseen),
			name = COALESCE($1.name, '')
			WHERE trip = $1.trip;
	ELSE
		INSERT INTO {users_table} (name, trip, firstseen, postcount)
			SELECT COALESCE($1.name,''), COALESCE($1.trip,''), $1.timestamp, 0
			WHERE NOT EXISTS (SELECT 1 FROM {users_table} WHERE name = COALESCE($1.name,'') AND trip = COALESCE($1.trip,''));

		UPDATE {users_table} SET postcount=postcount+1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE name = COALESCE($1.name,'') AND trip = COALESCE($1.trip,'');
	END IF;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_delete_post}(n_row {board_table}) RETURNS void AS $$
DECLARE
	d_day integer;
	d_image integer;
	d_sage integer;
	d_anon integer;
	d_trip integer;
	d_name integer;
BEGIN
	d_day := FLOOR($1.timestamp/86400)*86400;
	d_image := CASE WHEN $1.media_hash IS NOT NULL THEN 1 ELSE 0 END;
	d_sage := CASE WHEN $1.email = 'sage' THEN 1 ELSE 0 END;
	d_anon := CASE WHEN $1.name = 'Anonymous' AND $1.trip IS NULL THEN 1 ELSE 0 END;
	d_trip := CASE WHEN $1.trip IS NOT NULL THEN 1 ELSE 0 END;
	d_name := CASE WHEN COALESCE($1.name <> 'Anonymous' AND $1.trip IS NULL, TRUE) THEN 1 ELSE 0 END;

	UPDATE {daily_table} SET posts=posts-1, images=images-d_image,
		sage=sage-d_sage, anons=anons-d_anon, trips=trips-d_trip,
		names=names-d_name WHERE day = d_day;

	IF (SELECT trip FROM {users_table} WHERE trip = $1.trip) IS NOT NULL THEN
		UPDATE {users_table} SET postcount=postcount-1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE trip = $1.trip;
	ELSE
		UPDATE {users_table} SET postcount=postcount-1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE (name = $1.name OR $1.name IS NULL) AND (trip = $1.trip OR $1.trip IS NULL);
	END IF;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_before_insert}() RETURNS trigger AS $$
BEGIN
	IF NEW.media_hash IS NOT NULL THEN
		SELECT {func_insert_image}(NEW) INTO NEW.media_id;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

create or replace function {func_after_insert}() RETURNS trigger AS $$
BEGIN
	IF NEW.op = true THEN
		PERFORM {func_create_thread}(NEW);
	END IF;
	PERFORM {func_update_thread}(NEW);
	PERFORM {func_insert_post}(NEW);
	RETURN NULL;
END;
$$ LANGUAGE plpgsql;

create or replace function {func_after_del}() RETURNS trigger AS $$
BEGIN
	PERFORM {func_update_thread}(OLD);
	IF OLD.op = true THEN
		PERFORM {func_delete_thread}(OLD.num);
	END IF;
	PERFORM {func_delete_post}(OLD);
	IF OLD.media_hash IS NOT NULL THEN
		PERFORM {func_delete_image}(OLD.media_id);
	END IF;
	RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER {pg_trigger_after_delete} AFTER DELETE ON {board_table}
	FOR EACH ROW EXECUTE PROCEDURE {func_after_del}();

CREATE TRIGGER {pg_trigger_before_insert} BEFORE INSERT ON {board_table}
	FOR EACH ROW EXECUTE PROCEDURE {func_before_insert}();

CREATE TRIGGER {pg_trigger_after_insert} AFTER INSERT ON {board_table}
	FOR EACH ROW EXECUTE PROCEDURE {func_after_insert}();
'''
