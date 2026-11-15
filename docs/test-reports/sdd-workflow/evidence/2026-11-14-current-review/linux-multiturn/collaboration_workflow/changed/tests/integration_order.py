"""File-SQLite public API integration runner; JSON evidence, no network."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui


def run():
    results = []
    def case(identifier, action):
        with tempfile.TemporaryDirectory(prefix='order-integration-') as directory:
            path = Path(directory) / 'orders.sqlite'
            conn = storage.connect(path)
            try:
                actual = action(conn, path)
                results.append({'case': identifier, **actual})
            except Exception as error:
                results.append({'case': identifier, 'result': 'FAIL', 'unexpected_error': repr(error)})
            finally:
                conn.close()
    def persisted(conn, path, order_id):
        conn.close()
        reopened = storage.connect(path)
        try:
            return service.read_status(reopened, order_id)
        finally:
            reopened.close()
    def lifecycle(conn, path, operation):
        service.create_order(conn, 'ORDER-1')
        initial = service.read_status(conn, 'ORDER-1')
        accepted = None
        intermediate = None
        if operation == 'cancel-submit':
            service.cancel_order(conn, 'ORDER-1')
            intermediate = service.read_status(conn, 'ORDER-1')
            accepted = service.submit_order(conn, 'ORDER-1')
            expected = (False, 'cancelled')
        elif operation == 'submit':
            accepted = service.submit_order(conn, 'ORDER-1')
            expected = (True, 'submitted')
        elif operation == 'cancel':
            service.cancel_order(conn, 'ORDER-1')
            expected = (None, 'cancelled')
        elif operation == 'paid':
            ui.mark_paid(conn, 'ORDER-1')
            expected = (None, 'paid')
        elif operation == 'submitted-paid':
            accepted = service.submit_order(conn, 'ORDER-1')
            intermediate = service.read_status(conn, 'ORDER-1')
            ui.mark_paid(conn, 'ORDER-1')
            expected = (True, 'paid')
        elif operation == 'cancelled-paid':
            service.cancel_order(conn, 'ORDER-1')
            intermediate = service.read_status(conn, 'ORDER-1')
            ui.mark_paid(conn, 'ORDER-1')
            expected = (None, 'paid')
        else:
            expected = (None, 'pending')
        status = persisted(conn, path, 'ORDER-1')
        return {'result': 'PASS' if initial == 'pending' and (accepted, status) == expected else 'FAIL', 'initial': initial, 'intermediate': intermediate, 'accepted': accepted, 'persisted_status': status, 'expected': list(expected)}
    for identifier, operation in [('I01','create'),('I02','submit'),('I03','cancel'),('I04','cancel-submit'),('I05','paid'),('I06','submitted-paid'),('I07','cancelled-paid')]:
        case(identifier, lambda conn,path,operation=operation: lifecycle(conn,path,operation))
    def invalid(conn, path):
        errors = []
        for value in ('', None, 3):
            try:
                service.create_order(conn, value)
                errors.append('NO_ERROR')
            except ValueError:
                errors.append('ValueError')
        return {'result': 'PASS' if errors == ['ValueError'] * 3 and conn.execute('SELECT count(*) FROM orders').fetchone()[0] == 0 else 'FAIL', 'errors': errors}
    case('I08', invalid)
    def duplicate(conn,path):
        service.create_order(conn,'ORDER-1')
        try:
            service.create_order(conn,'ORDER-1')
            error = 'NO_ERROR'
        except sqlite3.IntegrityError:
            error = 'IntegrityError'
        status = persisted(conn,path,'ORDER-1')
        return {'result':'PASS' if error == 'IntegrityError' and status == 'pending' else 'FAIL','error':error,'persisted_status':status}
    case('I09',duplicate)
    def missing(conn,path,operation):
        try:
            operation(conn,'MISSING')
            error = 'NO_ERROR'
        except ValueError:
            error = 'ValueError'
        return {'result':'PASS' if error == 'ValueError' else 'FAIL','error':error,'row_count':conn.execute('SELECT count(*) FROM orders').fetchone()[0]}
    for identifier, operation in [('I10',service.cancel_order),('I11',service.submit_order),('I12',ui.mark_paid),('I13',lambda c,i:service.set_status(c,i,'paid'))]:
        case(identifier,lambda c,p,operation=operation:missing(c,p,operation))
    def database_failure(conn,path):
        service.create_order(conn,'ORDER-1')
        conn.execute('PRAGMA query_only = ON')
        errors = []
        for operation in (service.cancel_order, service.submit_order, ui.mark_paid):
            try:
                operation(conn,'ORDER-1')
                errors.append('NO_ERROR')
            except sqlite3.OperationalError:
                errors.append('OperationalError')
        status = persisted(conn,path,'ORDER-1')
        return {'result':'PASS' if errors == ['OperationalError']*3 and status == 'pending' else 'FAIL','errors':errors,'persisted_status':status}
    case('I14',database_failure)
    def isolation(conn,path):
        for identifier in ('A','订单-二'):
            service.create_order(conn,identifier)
        service.cancel_order(conn,'A')
        accepted = service.submit_order(conn,'订单-二')
        other = storage.connect(path)
        try:
            statuses = [service.read_status(other,i) for i in ('A','订单-二')]
        finally:
            other.close()
        return {'result':'PASS' if accepted is True and statuses == ['cancelled','submitted'] else 'FAIL','accepted':accepted,'persisted_statuses':statuses}
    case('I15',isolation)
    return {'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').glob('*.py'))},'python':sys.version,'sqlite':sqlite3.sqlite_version,'results':results}

if __name__ == '__main__':
    result = run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if any(item['result'] == 'FAIL' for item in result['results']) else 0)
