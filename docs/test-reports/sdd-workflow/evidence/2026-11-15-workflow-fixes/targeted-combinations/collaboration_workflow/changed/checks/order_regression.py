"""Public-entry integration regression with a real temporary file SQLite per case."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui
from checks.acceptance import run as acceptance


def run_case(case):
    if case in ('AC-1', 'AC-3'):
        return acceptance(case)
    if case == 'AC-2':
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'orders.sqlite'
            connection = storage.connect(path)
            statements = []
            try:
                service.create_order(connection, 'ORDER-1')
                service.cancel_order(connection, 'ORDER-1')
                cancelled_status = service.read_status(connection, 'ORDER-1')
                before = connection.total_changes
                connection.set_trace_callback(statements.append)
                accepted = service.submit_order(connection, 'ORDER-1')
                changes = connection.total_changes - before
                connection.set_trace_callback(None)
            finally:
                connection.close()
            connection = storage.connect(path)
            try:
                persisted = service.read_status(connection, 'ORDER-1')
            finally:
                connection.close()
        reads_only = bool(statements) and all(sql.lstrip().upper().startswith('SELECT ') for sql in statements)
        ok = accepted is False and cancelled_status == persisted == 'cancelled' and changes == 0 and reads_only
        return {
            'scenario': case, 'result': 'PASS' if ok else 'FAIL',
            'accepted': accepted, 'cancelled_status_before_submit': cancelled_status,
            'persisted_status': persisted, 'expected_accepted': False,
            'expected_status': 'cancelled', 'submit_total_changes': changes,
            'expected_submit_total_changes': 0, 'submit_sql': statements,
            'submit_reads_only': reads_only,
        }
    observations = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'orders.sqlite'
        connection = storage.connect(path)
        def reopened(order_id='ORDER-1'):
            other = storage.connect(path)
            try:
                return service.read_status(other, order_id)
            finally:
                other.close()
        try:
            if case == 'CREATE':
                service.create_order(connection, 'ORDER-1')
                observations.append({'persisted_status': reopened(), 'expected': 'pending'})
            elif case == 'INVALID-ID':
                for order_id in ('', None, 0):
                    caught = None
                    try:
                        service.create_order(connection, order_id)
                    except Exception as error:
                        caught = type(error).__name__
                    observations.append({'input': order_id, 'exception': caught, 'expected': 'ValueError'})
                observations.append({'row_count': connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0], 'expected': 0})
            elif case == 'MISSING':
                for name, operation in (
                    ('cancel_order', service.cancel_order),
                    ('submit_order', service.submit_order),
                    ('set_status', lambda c, o: service.set_status(c, o, 'paid')),
                    ('mark_paid', ui.mark_paid),
                ):
                    caught = None
                    try:
                        operation(connection, 'MISSING')
                    except Exception as error:
                        caught = type(error).__name__
                    observations.append({'operation': name, 'exception': caught, 'expected': 'ValueError'})
            elif case == 'DB-ERROR':
                service.create_order(connection, 'ORDER-1')
                connection.execute('PRAGMA query_only = ON')
                for name, operation, order_id in (
                    ('create_order', service.create_order, 'ORDER-2'),
                    ('cancel_order', service.cancel_order, 'ORDER-1'),
                    ('submit_order', service.submit_order, 'ORDER-1'),
                    ('set_status', lambda c, o: service.set_status(c, o, 'paid'), 'ORDER-1'),
                    ('mark_paid', ui.mark_paid, 'ORDER-1'),
                ):
                    caught = None
                    try:
                        operation(connection, order_id)
                    except sqlite3.Error as error:
                        caught = type(error).__name__
                    observations.append({'operation': name, 'exception': caught, 'expected': 'OperationalError'})
                    connection.rollback()
                observations.append({'persisted_status': reopened(), 'expected': 'pending'})
                observations.append({'row_count': connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0], 'expected': 1})
            else:
                service.create_order(connection, 'ORDER-1')
                if case == 'CANCEL':
                    service.cancel_order(connection, 'ORDER-1')
                    expected = 'cancelled'
                elif case == 'SET-STATUS':
                    service.set_status(connection, 'ORDER-1', 'paid')
                    expected = 'paid'
                elif case.startswith('PAID-'):
                    if case == 'PAID-CANCELLED':
                        service.cancel_order(connection, 'ORDER-1')
                    elif case == 'PAID-SUBMITTED':
                        service.submit_order(connection, 'ORDER-1')
                    observations.append({'initial_status': reopened(), 'expected': case.removeprefix('PAID-').lower()})
                    ui.mark_paid(connection, 'ORDER-1')
                    expected = 'paid'
                else:
                    raise ValueError(case)
                observations.append({'persisted_status': reopened(), 'expected': expected})
        finally:
            connection.close()
    # Every observation contains exactly one measured field besides operation/input/expected.
    ok = all(next(value for key, value in row.items() if key not in ('operation', 'input', 'expected')) == row['expected'] for row in observations)
    return {'scenario': case, 'result': 'PASS' if ok else 'FAIL', 'observations': observations}


CASES = ('CREATE', 'AC-1', 'CANCEL', 'AC-2', 'PAID-PENDING', 'PAID-CANCELLED', 'PAID-SUBMITTED', 'SET-STATUS', 'INVALID-ID', 'MISSING', 'DB-ERROR', 'AC-3')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=CASES)
    args = parser.parse_args()
    results = [run_case(case) for case in ([args.scenario] if args.scenario else CASES)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row['result'] == 'FAIL' for row in results) else 3 if any(row['result'] == 'BLOCKED' for row in results) else 0

if __name__ == '__main__':
    raise SystemExit(main())
