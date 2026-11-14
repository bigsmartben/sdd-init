"""Isolated, unconfirmed history candidates; never changes product modules.

Task H1: demonstrate loss of committed transitions in the current product.
Task H2: compare explicit transactional history and database triggers for ordered
persistence, bypass coverage, write failure atomicity and explicit rollback.
Run: python -B tests/experiments/sqlite_history_assessment.py
Only temporary SQLite files under this directory are created, then removed.
"""
import json
import platform
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui

SOURCE_HEAD = '43fea83f3e356c1f0bf91578bd0341c87ea7d8b7'
HISTORY_SCHEMA = '''CREATE TABLE history (
    seq INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL
)'''
EVENT_QUERY = 'SELECT seq, order_id, old_status, new_status FROM history ORDER BY seq'
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'passed': True})


def events(connection):
    return [list(row) for row in connection.execute(EVENT_QUERY)]


def logical_database(connection):
    return {
        'schema': connection.execute(
            'SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name'
        ).fetchall(),
        'orders': connection.execute('SELECT order_id, status FROM orders ORDER BY order_id').fetchall(),
    }


def attach(connection, trace):
    connection.set_trace_callback(trace.append)
    return connection


def baseline(directory):
    observations = []
    logical = []
    for name, paid in [('via_paid', True), ('without_paid', False)]:
        trace = []
        path = directory / (name + '.sqlite')
        connection = attach(storage.connect(path), trace)
        order_service.create_order(connection, 'order-1')
        observed = [order_service.read_status(connection, 'order-1')]
        order_service.submit_order(connection, 'order-1')
        observed.append(order_service.read_status(connection, 'order-1'))
        if paid:
            ui.mark_paid(connection, 'order-1')
            observed.append(order_service.read_status(connection, 'order-1'))
        order_service.cancel_order(connection, 'order-1')
        observed.append(order_service.read_status(connection, 'order-1'))
        connection.close()
        connection = attach(storage.connect(path), trace)
        snapshot = logical_database(connection)
        logical.append(snapshot)
        check(name + ': reconnect retains only cancelled', snapshot['orders'] == [('order-1', 'cancelled')])
        check(name + ': no history table', [row[1] for row in snapshot['schema'] if row[0] == 'table'] == ['orders'])
        observations.append({'path_label': name, 'observed_before_close': observed,
                             'after_reconnect': snapshot, 'sql_trace': trace})
        connection.close()
    check('different transition paths produce identical logical database', logical[0] == logical[1])
    check('baseline uses actual pending/submitted/paid/cancelled product path',
          observations[0]['observed_before_close'] == ['pending', 'submitted', 'paid', 'cancelled'])
    return observations


def explicit_create(connection, order_id):
    connection.execute('INSERT INTO orders VALUES (?, ?)', (order_id, 'pending'))
    connection.execute('INSERT INTO history(order_id, old_status, new_status) VALUES (?, NULL, ?)',
                       (order_id, 'pending'))


def explicit_transition(connection, order_id, status):
    old = order_service.read_status(connection, order_id)
    if old != status:
        connection.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
        connection.execute('INSERT INTO history(order_id, old_status, new_status) VALUES (?, ?, ?)',
                           (order_id, old, status))


def candidate(directory, mode):
    trace = []
    path = directory / (mode + '.sqlite')
    connection = attach(storage.connect(path), trace)
    connection.execute(HISTORY_SCHEMA)
    if mode == 'database_triggers':
        connection.executescript('''
        CREATE TRIGGER record_creation AFTER INSERT ON orders BEGIN
          INSERT INTO history(order_id, old_status, new_status)
          VALUES (NEW.order_id, NULL, NEW.status);
        END;
        CREATE TRIGGER record_transition AFTER UPDATE OF status ON orders
        WHEN OLD.status IS NOT NEW.status BEGIN
          INSERT INTO history(order_id, old_status, new_status)
          VALUES (NEW.order_id, OLD.status, NEW.status);
        END;
        ''')
        order_service.create_order(connection, 'order-1')
        order_service.submit_order(connection, 'order-1')
        ui.mark_paid(connection, 'order-1')
        order_service.cancel_order(connection, 'order-1')
    else:
        with connection:
            explicit_create(connection, 'order-1')
        for status in ['submitted', 'paid', 'cancelled']:
            with connection:
                explicit_transition(connection, 'order-1', status)
    connection.close()
    connection = attach(storage.connect(path), trace)
    recovered = events(connection)
    expected = [[1, 'order-1', None, 'pending'], [2, 'order-1', 'pending', 'submitted'],
                [3, 'order-1', 'submitted', 'paid'], [4, 'order-1', 'paid', 'cancelled']]
    check(mode + ': reconnect ordered creation and three transitions', recovered == expected)
    # The NULL old_status entry is creation, not a recovered pre-existing history.
    check(mode + ': creation is distinguishable from changes',
          len([row for row in recovered if row[2] is None]) == 1)
    if mode == 'database_triggers':
        order_service.set_status(connection, 'order-1', 'cancelled')
    else:
        with connection:
            explicit_transition(connection, 'order-1', 'cancelled')
        # Also exercise an actual same-value SQL UPDATE, independent of hook skip.
        connection.execute('UPDATE orders SET status = status WHERE order_id = ?', ('order-1',))
        connection.commit()
    check(mode + ': same-value update adds no change', events(connection) == recovered)
    connection.execute('''CREATE TRIGGER reject_history BEFORE INSERT ON history
        WHEN NEW.new_status = 'blocked' BEGIN SELECT RAISE(ABORT, 'injected history failure'); END''')
    connection.commit()
    failure = None
    try:
        if mode == 'database_triggers':
            order_service.set_status(connection, 'order-1', 'blocked')
        else:
            with connection:
                explicit_transition(connection, 'order-1', 'blocked')
    except sqlite3.IntegrityError as exc:
        failure = str(exc)
    check(mode + ': injected history failure observed', failure == 'injected history failure')
    check(mode + ': failure leaves status unchanged', order_service.read_status(connection, 'order-1') == 'cancelled')
    check(mode + ': failure leaves history unchanged', events(connection) == recovered)
    transaction_after_failure = connection.in_transaction
    # SQLite ABORT cancels the failing statement; the caller still ends the transaction.
    connection.rollback()
    if mode == 'database_triggers':
        connection.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('rollback-status', 'order-1'))
    else:
        explicit_transition(connection, 'order-1', 'rollback-status')
    check(mode + ': event visible inside transaction', events(connection)[-1][3] == 'rollback-status')
    connection.rollback()
    check(mode + ': explicit rollback restores status', order_service.read_status(connection, 'order-1') == 'cancelled')
    check(mode + ': explicit rollback removes event', events(connection) == recovered)
    # Existing UI writes bypass explicit candidate helpers but hit table triggers.
    ui.mark_paid(connection, 'order-1')
    bypass = events(connection)
    if mode == 'database_triggers':
        check(mode + ': actual UI bypass captured', bypass == recovered + [[5, 'order-1', 'cancelled', 'paid']])
    else:
        check(mode + ': actual UI bypass omitted', bypass == recovered)
    check(mode + ': actual UI changes current row', order_service.read_status(connection, 'order-1') == 'paid')
    connection.close()
    connection = attach(storage.connect(path), trace)
    check(mode + ': rollback/failure absent after reconnect',
          all(row[3] not in ['blocked', 'rollback-status'] for row in events(connection)))
    check(mode + ': final history survives reconnect', events(connection) == bypass)
    result = {'candidate_status': 'experimental, not confirmed design',
              'journal_mode': connection.execute('PRAGMA journal_mode').fetchone()[0],
              'recovered_before_bypass': recovered, 'after_actual_ui_write': events(connection),
              'final_orders': connection.execute('SELECT * FROM orders').fetchall(),
              'injected_failure': failure, 'transaction_open_after_failure': transaction_after_failure,
              'sql_trace': trace}
    connection.close()
    return result


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    check('source HEAD matches assigned version', head == SOURCE_HEAD)
    result = {'source_head': head, 'python_version': platform.python_version(),
              'sqlite_version': sqlite3.sqlite_version,
              'command': 'python -B tests/experiments/sqlite_history_assessment.py',
              'task_scope': ['H1 current implementation counterexample', 'H2 isolated candidate comparison'],
              'history_query': EVENT_QUERY,
              'limitations': [
                  'Sequential single-process experiments; concurrency, load and crash recovery not tested.',
                  'Candidate A helpers exist only in this experiment; production service commits are unchanged.',
                  'Triggers cover tested INSERT and status UPDATE paths, not deletion, REPLACE or schema bypass.',
                  'Sequence numbers order surviving inserted events; no global time or gap-free guarantee.',
                  'Creation event is distinguishable from changes; no historical backfill is inferred.',
                  'Logical equality compares schema and row values, not SQLite file bytes.',
                  'SQL trace is executed SQL observation; trigger execution may repeat outer SQL text.'
              ]}
    with tempfile.TemporaryDirectory(prefix='history-assessment-', dir=Path(__file__).parent) as temporary:
        directory = Path(temporary)
        probe = sqlite3.connect(directory / 'environment.sqlite')
        result['journal_mode'] = probe.execute('PRAGMA journal_mode').fetchone()[0]
        probe.close()
        result['baseline'] = baseline(directory)
        result['candidates'] = {mode: candidate(directory, mode)
                                for mode in ['explicit_service_history', 'database_triggers']}
    result['temporary_databases_removed'] = not directory.exists()
    check('temporary database directory cleaned', result['temporary_databases_removed'])
    result['assertions'] = checks
    result['assertion_count'] = len(checks)
    result['result'] = 'passed'
    output = Path(__file__).with_name('sqlite_history_assessment-output.json')
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'result': result['result'], 'assertions': len(checks),
                      'output': str(output.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
