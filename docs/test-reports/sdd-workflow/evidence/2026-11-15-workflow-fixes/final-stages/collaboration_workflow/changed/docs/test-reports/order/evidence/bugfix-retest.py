"""Targeted bugfix verification: real temporary SQLite, no network."""
from pathlib import Path
import hashlib
import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui

results = []
def check(name, action):
    try:
        details = action()
        results.append({'case': name, 'result': 'PASS', 'details': details})
    except Exception as error:
        results.append({'case': name, 'result': 'FAIL', 'error': repr(error)})

def expect_error(call, expected):
    try:
        call()
    except expected as error:
        return type(error).__name__
    raise AssertionError(f'Expected {expected.__name__}')

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'orders.sqlite'
    c = storage.connect(path)
    try:
        service.create_order(c, 'CANCEL')
        service.cancel_order(c, 'CANCEL')
        service.create_order(c, 'NORMAL')
        service.create_order(c, 'PAID')
        service.create_order(c, 'OTHER')
        def cancelled():
            trace = []
            c.set_trace_callback(trace.append)
            before = c.total_changes
            result = service.submit_order(c, 'CANCEL')
            c.set_trace_callback(None)
            assert result is False
            assert c.total_changes == before
            assert not any(sql.lstrip().upper().startswith(('UPDATE', 'INSERT', 'DELETE', 'COMMIT', 'BEGIN')) for sql in trace)
            assert service.read_status(c, 'CANCEL') == 'cancelled'
            return {'accepted': result, 'changes': c.total_changes-before, 'trace': trace, 'status': 'cancelled'}
        check('ORDER-001 original + no write/commit', cancelled)
        def normal():
            assert service.submit_order(c, 'NORMAL') is True
            assert service.read_status(c, 'NORMAL') == 'submitted'
            return {'accepted': True, 'status': 'submitted'}
        check('AC-1 pending submission', normal)
        def missing_paid():
            trace=[]
            c.set_trace_callback(trace.append)
            before=c.total_changes
            error=expect_error(lambda:ui.mark_paid(c,'MISSING'),ValueError)
            c.set_trace_callback(None)
            assert c.total_changes==before
            assert not any(sql.lstrip().upper().startswith(('UPDATE','COMMIT','BEGIN')) for sql in trace)
            assert c.execute('SELECT count(*) FROM orders WHERE order_id=?',('MISSING',)).fetchone()[0]==0
            return {'exception':error,'changes':0,'trace':trace}
        check('ORDER-002 missing + no write/commit',missing_paid)
        def paid():
            assert ui.mark_paid(c,'PAID') is None
            assert service.read_status(c,'PAID')=='paid'
            assert service.read_status(c,'OTHER')=='pending'
            return {'paid':'paid','other':'pending','return':None}
        check('Existing paid + order isolation',paid)
        def repeat_submission():
            assert service.submit_order(c,'NORMAL') is True
            assert service.read_status(c,'NORMAL')=='submitted'
            return {'accepted':True,'status':'submitted'}
        check('Preserve already submitted path',repeat_submission)
        def paid_submission():
            service.create_order(c,'PAID-SUBMIT')
            ui.mark_paid(c,'PAID-SUBMIT')
            assert service.submit_order(c,'PAID-SUBMIT') is True
            assert service.read_status(c,'PAID-SUBMIT')=='submitted'
            return {'accepted':True,'status':'submitted','basis':'Existing non-cancelled behavior retained without new transition policy'}
        check('Preserve non-cancelled paid submit path',paid_submission)
        for name,operation in [('read',service.read_status),('cancel',service.cancel_order),('submit',service.submit_order),('set_status',lambda conn,oid:service.set_status(conn,oid,'paid'))]:
            check('Missing '+name, lambda operation=operation:{'exception':expect_error(lambda:operation(c,'MISSING'),ValueError)})
    finally:
        c.close()
    def persistence():
        reopened=storage.connect(path)
        try:
            expected={'CANCEL':'cancelled','NORMAL':'submitted','PAID':'paid','OTHER':'pending','PAID-SUBMIT':'submitted'}
            actual={oid:service.read_status(reopened,oid) for oid in expected}
            assert actual==expected
            return actual
        finally:
            reopened.close()
    check('Close/reopen all states',persistence)
    for name,operation in [('create',service.create_order),('read',service.read_status),('cancel',service.cancel_order),('submit',service.submit_order),('set_status',lambda conn,oid:service.set_status(conn,oid,'paid')),('mark_paid',ui.mark_paid)]:
        check('Closed connection '+name,lambda operation=operation:{'exception':expect_error(lambda:operation(c,'NORMAL'),sqlite3.ProgrammingError)})
output={'phase':'Bugfix independent targeted retest','executed_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').glob('*.py'))},'frozen_integration_sha256':hashlib.sha256((ROOT/'checks/order_integration.py').read_bytes()).hexdigest(),'cases':results,'summary':{'total':len(results),'pass':sum(r['result']=='PASS' for r in results),'fail':sum(r['result']=='FAIL' for r in results)},'environment':'Temporary file SQLite; connections closed and temporary directory cleaned; no external call'}
print(json.dumps(output,ensure_ascii=False,indent=2))
raise SystemExit(bool(output['summary']['fail']))
