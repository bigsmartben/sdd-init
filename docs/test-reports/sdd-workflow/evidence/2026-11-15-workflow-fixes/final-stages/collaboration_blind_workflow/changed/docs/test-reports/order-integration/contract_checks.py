"""Public-entry integration checks against the confirmed order contract."""
from pathlib import Path
import json
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui

network_events = []
def audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
        network_events.append(event)
        raise AssertionError('Network operation prohibited in local checks')
sys.addaudithook(audit)
results = []

def run(case, label, check):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        def persisted():
            with sqlite3.connect(path) as other:
                return other.execute('SELECT status FROM orders WHERE order_id = ?', ('ORDER-1',)).fetchone()[0]
        try:
            detail = check(connection, persisted)
            results.append(dict(case=case, label=label, result='PASS', detail=detail))
        except Exception as error:
            results.append(dict(case=case, label=label, result='FAIL', error=f'{type(error).__name__}: {error}'))
        finally:
            connection.close()

def require(condition, detail):
    if not condition:
        raise AssertionError(detail)

def raises(kind, call):
    try:
        call()
    except kind as error:
        return f'{type(error).__name__}: {error}'
    raise AssertionError(f'Expected {kind.__name__}; returned normally')

def create(c, p):
    service.create_order(c, 'ORDER-1')
    require(p() == 'pending' and not c.in_transaction, 'create did not commit pending')
    return 'pending visible from independent file connection; no open transaction'

def cancel(c, p):
    service.create_order(c, 'ORDER-1')
    service.cancel_order(c, 'ORDER-1')
    require(p() == 'cancelled' and not c.in_transaction, 'cancel did not commit')
    return 'cancelled visible from independent file connection'

def set_states(c, p):
    service.create_order(c, 'ORDER-1')
    for state in ('pending', 'submitted', 'cancelled', 'paid'):
        service.set_status(c, 'ORDER-1', state)
        require(p() == state and not c.in_transaction, f'{state} not committed')
    return 'all four documented legal states persisted'

def paid(c, p):
    service.create_order(c, 'ORDER-1')
    ui.mark_paid(c, 'ORDER-1')
    require(p() == 'paid' and not c.in_transaction, 'paid not committed')
    return 'paid visible from independent file connection'

def invalid(c, p):
    detail = [raises(ValueError, lambda value=value: service.create_order(c, value)) for value in ('', None, 17)]
    require(c.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == 0, 'invalid ID inserted')
    return detail

def database_closed(c, p):
    service.create_order(c, 'ORDER-1')
    c.close()
    return [raises(sqlite3.ProgrammingError, call) for call in (
        lambda: service.create_order(c, 'ORDER-2'), lambda: service.read_status(c, 'ORDER-1'),
        lambda: service.cancel_order(c, 'ORDER-1'), lambda: service.submit_order(c, 'ORDER-1'),
        lambda: service.set_status(c, 'ORDER-1', 'paid'), lambda: ui.mark_paid(c, 'ORDER-1'))]

def commit_failure(c, p):
    service.create_order(c, 'ORDER-1')
    c.execute('PRAGMA busy_timeout = 0')
    db_path = c.execute('PRAGMA database_list').fetchone()[2]
    other = sqlite3.connect(db_path)
    try:
        other.execute('BEGIN')
        other.execute('SELECT * FROM orders').fetchall()
        error = raises(sqlite3.OperationalError, lambda: service.submit_order(c, 'ORDER-1'))
        require(c.in_transaction, 'expected blocked commit transaction')
        require(other.execute('SELECT status FROM orders').fetchone()[0] == 'pending', 'uncommitted write visible')
    finally:
        c.rollback()
        other.rollback()
        other.close()
    require(p() == 'pending', 'rollback did not recover pending')
    return error + '; reader observed pending, rollback restored pending'

def no_write(c, p):
    service.create_order(c, 'ORDER-1')
    service.cancel_order(c, 'ORDER-1')
    statements = []
    before = c.total_changes
    c.set_trace_callback(statements.append)
    try:
        result = service.submit_order(c, 'ORDER-1')
    finally:
        c.set_trace_callback(None)
    require(result is False and c.total_changes == before and not c.in_transaction, 'cancelled submission mutated database')
    require(not any(s.lstrip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'REPLACE', 'BEGIN', 'COMMIT')) for s in statements), statements)
    require(p() == 'cancelled', 'cancelled lost')
    return dict(accepted=result, total_changes_delta=c.total_changes-before, statements=statements, persisted='cancelled')

run('CT-01', 'create pending + commit', create)
run('CT-02', 'cancel + commit', cancel)
run('CT-03', 'set_status documented legal states', set_states)
run('CT-04', 'mark_paid existing + commit', paid)
run('CT-05', 'reject empty/non-string create ID', invalid)
for case, name, operation in (
    ('CT-06', 'read_status', lambda c: service.read_status(c, 'MISSING')),
    ('CT-07', 'cancel_order', lambda c: service.cancel_order(c, 'MISSING')),
    ('CT-08', 'submit_order', lambda c: service.submit_order(c, 'MISSING')),
    ('CT-09', 'set_status', lambda c: service.set_status(c, 'MISSING', 'paid')),
    ('CT-10', 'mark_paid', lambda c: ui.mark_paid(c, 'MISSING'))):
    run(case, name + ' missing order raises ValueError', lambda c, p, operation=operation: raises(ValueError, lambda: operation(c)))
run('CT-11', 'closed DB exceptions propagate through public entries', database_closed)
run('CT-12', 'real file DB commit failure + rollback recovery', commit_failure)
run('CT-13', 'cancelled submit no writes', no_write)
results.append(dict(case='CT-14', label='local operations no network', result='PASS' if not network_events else 'FAIL', detail=network_events))
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(1 if any(row['result'] == 'FAIL' for row in results) else 0)
