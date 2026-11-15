"""B1 integration retest evidence; run from project root with Python -B."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui


def command(args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return dict(command=args, exit=result.returncode, stdout=result.stdout, stderr=result.stderr)


network_events = []
sys.addaudithook(lambda event, args: network_events.append(event) if event.startswith('socket.') else None)
results = []


def scenario(case, expected, operation):
    events = []
    directory = tempfile.TemporaryDirectory(prefix='b1-retest-')
    path = Path(directory.name) / 'orders.sqlite'
    connections = []

    def connect():
        connection = storage.connect(path)
        connections.append(connection)
        events.append({'action': 'open_file_database', 'file': str(path)})
        return connection

    def observe(connection, order='ORDER-1'):
        value = service.read_status(connection, order)
        events.append({'action': 'read_status', 'order': order, 'status': value})
        return value

    try:
        actual = operation(connect, observe, events)
        verdict = 'PASS' if actual == expected else 'FAIL'
    except Exception as exc:
        actual = {'unexpected_exception': type(exc).__name__, 'message': str(exc)}
        verdict = 'FAIL'
    finally:
        for connection in connections:
            connection.close()
        directory.cleanup()
    results.append(dict(case=case, expected=expected, actual=actual, result=verdict,
                        events=events, database_removed=not path.exists()))


def raised(call):
    try:
        call()
    except Exception as exc:
        return type(exc).__name__
    return 'no exception'


def paid(connect, observe, events):
    outcomes = {}
    for starting in ('pending', 'submitted', 'cancelled', 'paid'):
        c = connect()
        service.create_order(c, starting)
        if starting == 'submitted':
            service.submit_order(c, starting)
        elif starting == 'cancelled':
            service.cancel_order(c, starting)
        elif starting == 'paid':
            ui.mark_paid(c, starting)
        events.append({'action': 'before_mark_paid', 'order': starting, 'status': observe(c, starting)})
        ui.mark_paid(c, starting)
        events.append({'action': 'mark_paid', 'order': starting})
        c.close()
        outcomes[starting] = observe(connect(), starting)
    return outcomes


def invalid(connect, observe, events):
    c = connect()
    outcomes = {repr(value): raised(lambda value=value: service.create_order(c, value)) for value in ('', None, 1)}
    service.create_order(c, 'A')
    service.create_order(c, '订单-2')
    outcomes['valid_nonempty'] = [observe(c, 'A'), observe(connect(), '订单-2')]
    outcomes['row_count'] = c.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    events.append({'action': 'invalid_and_valid_creation', 'results': outcomes})
    return {'valid_nonempty': outcomes['valid_nonempty']}


def missing(connect, observe, events):
    c = connect()
    outcomes = {
        'read': raised(lambda: service.read_status(c, 'MISSING')),
        'cancel': raised(lambda: service.cancel_order(c, 'MISSING')),
        'submit': raised(lambda: service.submit_order(c, 'MISSING')),
        'set_status': raised(lambda: service.set_status(c, 'MISSING', 'paid')),
    }
    events.append({'action': 'missing_service_operations', 'results': outcomes})
    return outcomes


def paid_missing(connect, observe, events):
    c = connect()
    service.create_order(c, 'ORDER-1')
    outcome = raised(lambda: ui.mark_paid(c, 'MISSING'))
    events.append({'action': 'mark_paid_missing', 'exception': outcome})
    c.close()
    return {'exception': outcome, 'existing_status': observe(connect())}


def database_error(connect, observe, events):
    c = connect()
    service.create_order(c, 'ORDER-1')
    c.close()
    calls = {
        'create': lambda: service.create_order(c, 'NEW'),
        'read': lambda: service.read_status(c, 'ORDER-1'),
        'cancel': lambda: service.cancel_order(c, 'ORDER-1'),
        'submit': lambda: service.submit_order(c, 'ORDER-1'),
        'set_status': lambda: service.set_status(c, 'ORDER-1', 'paid'),
        'mark_paid': lambda: ui.mark_paid(c, 'ORDER-1'),
    }
    outcomes = {name: raised(call) for name, call in calls.items()}
    events.append({'action': 'closed_connection_operations', 'results': outcomes})
    outcomes['persisted_status'] = observe(connect())
    return outcomes


def isolation(connect, observe, events):
    c = connect()
    for order in ('CANCEL', 'SUBMIT', 'PAID', 'UNTOUCHED'):
        service.create_order(c, order)
    service.cancel_order(c, 'CANCEL')
    accepted = service.submit_order(c, 'CANCEL')
    service.submit_order(c, 'SUBMIT')
    ui.mark_paid(c, 'PAID')
    c.close()
    reopened = connect()
    return dict(cancel_submit=accepted, states={order: observe(reopened, order) for order in ('CANCEL', 'SUBMIT', 'PAID', 'UNTOUCHED')})


def recovery(connect, observe, events):
    c = connect()
    service.create_order(c, 'ORDER-1')
    events.append({'action': 'create', 'status': observe(c)})
    service.cancel_order(c, 'ORDER-1')
    events.append({'action': 'cancel', 'status': observe(c)})
    c.close()
    c = connect()
    before = observe(c)
    returns = []
    for _ in range(2):
        returns.append(service.submit_order(c, 'ORDER-1'))
        events.append({'action': 'submit_cancelled', 'return': returns[-1], 'status': observe(c)})
    c.close()
    return dict(before=before, returns=returns, after=observe(connect()))


output = {
    'batch': 'B1 integration retest after fix',
    'started_utc': datetime.now(timezone.utc).isoformat(),
    'version': command(['git', 'rev-parse', 'HEAD']),
    'initial_worktree': command(['git', 'status', '--short']),
    'product_diff': command(['git', 'diff', 'HEAD', '--', 'src', 'checks', 'tests', 'runtime.json', 'specs', 'docs/contracts', 'docs/issues/ISS-001.md']),
    'runtime': command([sys.executable, '-B', 'checks/runtime_details.py']),
    'basis_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ('specs/order/spec.md', 'specs/order/quickstart.md', 'docs/contracts/order.md', 'docs/issues/ISS-001.md', 'docs/test-reports/order/evidence/b1.json')},
    'evidence_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
for ac in ('AC-1', 'AC-2', 'AC-3'):
    raw = command([sys.executable, '-B', 'checks/acceptance.py', '--scenario', ac])
    result = json.loads(raw['stdout'])[0]
    results.append(dict(case=ac, result=result['result'], actual=result, raw=raw))
scenario('IT-01', {'valid_nonempty': ['pending', 'pending']}, invalid)
scenario('IT-02', {name: 'ValueError' for name in ('read', 'cancel', 'submit', 'set_status')}, missing)
scenario('IT-03', {name: 'paid' for name in ('pending', 'submitted', 'cancelled', 'paid')}, paid)
scenario('IT-04', {'exception': 'ValueError', 'existing_status': 'pending'}, paid_missing)
scenario('IT-05', {**{name: 'ProgrammingError' for name in ('create', 'read', 'cancel', 'submit', 'set_status', 'mark_paid')}, 'persisted_status': 'pending'}, database_error)
scenario('IT-06', {'cancel_submit': False, 'states': {'CANCEL': 'cancelled', 'SUBMIT': 'submitted', 'PAID': 'paid', 'UNTOUCHED': 'pending'}}, isolation)
scenario('IT-07', {'before': 'cancelled', 'returns': [False, False], 'after': 'cancelled'}, recovery)
results.append(dict(case='IT-08', expected=[], actual=network_events, result='PASS' if not network_events else 'FAIL', observation='Python audit socket events during derived in-process local scenarios IT-01 through IT-07; no network interception or replacement components'))
output['results'] = results
output['counts'] = {verdict: sum(row['result'] == verdict for row in results) for verdict in ('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN')}
output['finished_utc'] = datetime.now(timezone.utc).isoformat()
print(json.dumps(output, ensure_ascii=False, indent=2))
raise SystemExit(1 if output['counts']['FAIL'] else 3 if output['counts']['BLOCKED'] else 0)
