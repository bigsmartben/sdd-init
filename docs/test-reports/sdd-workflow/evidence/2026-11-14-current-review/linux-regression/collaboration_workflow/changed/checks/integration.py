"""Public-entry integration regression using real per-case file SQLite."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui


def reopened(path, order='ORDER-1'):
    connection = storage.connect(path)
    try:
        return service.read_status(connection, order)
    finally:
        connection.close()


def raises(action, kind):
    try:
        action()
    except Exception as error:
        return {'exception': type(error).__name__, 'expected': kind.__name__, 'matches': isinstance(error, kind)}
    return {'exception': None, 'expected': kind.__name__, 'matches': False}


def run(case):
    if case == 'AC-3':
        runtime = json.loads((ROOT / 'runtime.json').read_text())
        return {'case': case, 'result': 'BLOCKED', 'observed': runtime,
                'reason': 'Real external endpoint and calling permission absent; no network call or simulation performed.'}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        try:
            if case == 'NEW-2':
                observed = [raises(lambda value=value: service.create_order(connection, value), ValueError)
                            for value in ('', None, 0)]
                good = all(item['matches'] for item in observed)
            elif case == 'MISSING-1':
                actions = {'read_status': lambda: service.read_status(connection, 'MISSING'),
                           'cancel_order': lambda: service.cancel_order(connection, 'MISSING'),
                           'submit_order': lambda: service.submit_order(connection, 'MISSING'),
                           'set_status': lambda: service.set_status(connection, 'MISSING', 'paid'),
                           'mark_paid': lambda: ui.mark_paid(connection, 'MISSING')}
                observed = {name: raises(action, ValueError) for name, action in actions.items()}
                good = all(item['matches'] for item in observed.values())
            else:
                service.create_order(connection, 'ORDER-1')
                if case == 'NEW-1':
                    observed = {'state': reopened(path)}
                    good = observed['state'] == 'pending'
                elif case in ('AC-1', 'AC-2'):
                    if case == 'AC-2':
                        service.cancel_order(connection, 'ORDER-1')
                    before = reopened(path)
                    accepted = service.submit_order(connection, 'ORDER-1')
                    observed = {'before': before, 'accepted': accepted, 'persisted': reopened(path)}
                    good = accepted is (case == 'AC-1') and observed['persisted'] == ('submitted' if case == 'AC-1' else 'cancelled')
                elif case == 'CANCEL-1':
                    service.cancel_order(connection, 'ORDER-1')
                    observed = {'persisted': reopened(path)}
                    good = observed['persisted'] == 'cancelled'
                elif case in ('PAID-1', 'PAID-2', 'PAID-3'):
                    if case == 'PAID-2':
                        service.submit_order(connection, 'ORDER-1')
                    if case == 'PAID-3':
                        service.cancel_order(connection, 'ORDER-1')
                    before = reopened(path)
                    ui.mark_paid(connection, 'ORDER-1')
                    observed = {'before': before, 'persisted': reopened(path)}
                    good = observed['persisted'] == 'paid'
                elif case == 'STATUS-1':
                    observed = []
                    for status in ('submitted', 'cancelled', 'paid', 'pending'):
                        service.set_status(connection, 'ORDER-1', status)
                        observed.append({'requested': status, 'persisted': reopened(path)})
                    good = all(item['requested'] == item['persisted'] for item in observed)
                elif case == 'DB-1':
                    connection.execute('PRAGMA query_only=ON')
                    actions = {'create_order': lambda: service.create_order(connection, 'ORDER-2'),
                               'cancel_order': lambda: service.cancel_order(connection, 'ORDER-1'),
                               'submit_order': lambda: service.submit_order(connection, 'ORDER-1'),
                               'set_status': lambda: service.set_status(connection, 'ORDER-1', 'paid'),
                               'mark_paid': lambda: ui.mark_paid(connection, 'ORDER-1')}
                    observed = {name: raises(action, sqlite3.OperationalError) for name, action in actions.items()}
                    observed['persisted'] = reopened(path)
                    good = all(item['matches'] for name, item in observed.items() if name != 'persisted') and observed['persisted'] == 'pending'
                elif case == 'ISOLATION-1':
                    service.create_order(connection, '订单-β')
                    service.cancel_order(connection, 'ORDER-1')
                    ui.mark_paid(connection, '订单-β')
                    accepted = service.submit_order(connection, 'ORDER-1')
                    observed = {'accepted': accepted, 'first': reopened(path), 'second': reopened(path, '订单-β')}
                    good = accepted is False and observed['first'] == 'cancelled' and observed['second'] == 'paid'
                elif case == 'RECOVERY-1':
                    connection.execute('PRAGMA query_only=ON')
                    failure = raises(lambda: service.submit_order(connection, 'ORDER-1'), sqlite3.OperationalError)
                    connection.rollback()
                    connection.execute('PRAGMA query_only=OFF')
                    accepted = service.submit_order(connection, 'ORDER-1')
                    observed = {'failure': failure, 'accepted_after_recovery': accepted, 'persisted': reopened(path)}
                    good = failure['matches'] and accepted is True and observed['persisted'] == 'submitted'
                else:
                    raise ValueError(case)
            return {'case': case, 'result': 'PASS' if good else 'FAIL', 'observed': observed}
        finally:
            connection.close()


CASES = ('NEW-1', 'NEW-2', 'AC-1', 'CANCEL-1', 'AC-2', 'PAID-1', 'PAID-2', 'PAID-3',
         'STATUS-1', 'MISSING-1', 'DB-1', 'ISOLATION-1', 'RECOVERY-1', 'AC-3')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'src').glob('*.py'))}
    results = [run(case) for case in ([args.case] if args.case else CASES)]
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'src').glob('*.py'))}
    output = {'time': datetime.now(timezone.utc).isoformat(),
              'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'python': sys.version, 'sqlite': sqlite3.sqlite_version,
              'source_sha256': before, 'source_stable_during_run': before == after,
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'runtime': json.loads((ROOT / 'runtime.json').read_text()), 'results': results,
              'counts': {state: sum(row['result'] == state for row in results) for state in ('PASS', 'FAIL', 'BLOCKED', 'NOT RUN')}}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if before != after or any(row['result'] == 'FAIL' for row in results) else 3 if any(row['result'] == 'BLOCKED' for row in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
