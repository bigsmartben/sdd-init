"""B1 retest evidence runner; run from project root, stdout is JSON."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src import order_service as service, storage, ui

def command(args, env=None):
    p = subprocess.run(args, cwd=ROOT, env=env, text=True, capture_output=True)
    return {'command': args, 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = {
    'batch': 'B1-R1',
    'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'head': command(['git', 'rev-parse', 'HEAD']),
    'worktree': command(['git', 'status', '--short']),
    'source_paths': {name: str(Path(module.__file__).resolve()) for name, module in [('service', service), ('storage', storage), ('ui', ui)]},
    'sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [*sorted((ROOT/'src').glob('*.py')), ROOT/'runtime.json', ROOT/'docs/issues/ISS-001.md', ROOT/'docs/test-reports/order/evidence/b1.json']},
}
with tempfile.TemporaryDirectory(prefix='b1-r1-', dir=ROOT/'docs/test-reports/order/evidence') as tmp:
    env = dict(os.environ, TMPDIR=tmp, PYTHONDONTWRITEBYTECODE='1')
    result['runtime'] = command([sys.executable, '-B', 'checks/runtime_details.py'], env)
    result['acceptance'] = {ac: command([sys.executable, '-B', 'checks/acceptance.py', '--scenario', ac], env) for ac in ['AC-1', 'AC-2', 'AC-3']}
    result['unittest'] = command([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], env)
    cases = []
    def test(case_id, expected, action):
        path = Path(tmp)/(case_id+'.sqlite')
        conn = storage.connect(path)
        events = []
        def observe(label):
            conn.close()
            new_conn = storage.connect(path)
            try:
                rows = new_conn.execute('SELECT order_id, status FROM orders ORDER BY order_id').fetchall()
            finally:
                new_conn.close()
            events.append({'stage': label, 'reopened_rows': rows})
            return rows
        try:
            actual = action(conn, observe, events)
            cases.append({'case':case_id, 'expected':expected, 'actual':actual, 'events':events, 'result':'PASS' if actual == expected else 'FAIL'})
        except Exception as exc:
            cases.append({'case':case_id, 'expected':expected, 'unexpected_error':repr(exc), 'events':events, 'result':'FAIL'})
        finally:
            conn.close()
    def pending(c, observe, events):
        service.create_order(c, 'ORDER-1')
        return observe('create committed') == [('ORDER-1','pending')]
    test('L-01', True, pending)
    def cancelled(c, observe, events):
        service.create_order(c, 'ORDER-1'); service.cancel_order(c, 'ORDER-1')
        return observe('cancel committed') == [('ORDER-1','cancelled')]
    test('L-02', True, cancelled)
    def paid(c, observe, events):
        service.create_order(c, 'ORDER-1')
        accepted = service.submit_order(c,'ORDER-1')
        events.append({'stage':'submit', 'accepted':accepted, 'status':service.read_status(c,'ORDER-1')})
        ui.mark_paid(c,'ORDER-1')
        return accepted is True and observe('paid committed') == [('ORDER-1','paid')]
    test('L-03', True, paid)
    def invalid(c, observe, events):
        outcomes=[]
        for value in ['', None, 42]:
            try: service.create_order(c,value); outcome='no exception'
            except Exception as exc: outcome=type(exc).__name__
            events.append({'input':value,'exception':outcome}); outcomes.append(outcome)
        rows=observe('invalid creates')
        return outcomes == ['ValueError']*3 and rows == []
    test('L-04',True,invalid)
    def missing(c, observe, events):
        outcomes=[]
        for name, fn in [('read',service.read_status),('cancel',service.cancel_order),('submit',service.submit_order),('set_status',lambda c,o:service.set_status(c,o,'paid'))]:
            try: fn(c,'MISSING'); outcome='no exception'
            except Exception as exc: outcome=type(exc).__name__
            events.append({'operation':name,'exception':outcome}); outcomes.append(outcome)
        return outcomes == ['ValueError']*4 and observe('missing service operations') == []
    test('L-05',True,missing)
    def missing_paid(c, observe, events):
        try: ui.mark_paid(c,'MISSING'); outcome='no exception'
        except Exception as exc: outcome=type(exc).__name__
        events.append({'operation':'mark_paid','exception':outcome})
        observe('missing paid operation')
        return outcome
    test('L-06','ValueError',missing_paid)
    def db_errors(c, observe, events):
        service.create_order(c,'ORDER-1')
        c.execute('PRAGMA query_only=ON')
        outcomes=[]
        for name,fn in [('create', lambda:service.create_order(c,'ORDER-2')), ('cancel',lambda:service.cancel_order(c,'ORDER-1')), ('submit',lambda:service.submit_order(c,'ORDER-1')),('set_status',lambda:service.set_status(c,'ORDER-1','paid')), ('mark_paid',lambda:ui.mark_paid(c,'ORDER-1'))]:
            try: value=fn(); outcome='returned '+repr(value)
            except sqlite3.DatabaseError as exc: outcome=type(exc).__name__
            events.append({'operation':name,'outcome':outcome});outcomes.append(outcome)
        return outcomes == ['OperationalError']*5 and observe('write failures') == [('ORDER-1','pending')]
    test('L-07',True,db_errors)
    def id_boundary(c, observe, events):
        for order_id in ['订-1', ' ']: service.create_order(c,order_id)
        return observe('nonempty strings') == [(' ','pending'),('订-1','pending')]
    test('L-08',True,id_boundary)
    def cancelled_sequence(c,observe,events):
        service.create_order(c,'ORDER-1');service.cancel_order(c,'ORDER-1')
        events.append({'stage':'cancel','status':service.read_status(c,'ORDER-1')})
        values=[service.submit_order(c,'ORDER-1'),service.submit_order(c,'ORDER-1')]
        events.append({'stage':'two submissions','accepted':values})
        return values == [False,False] and observe('repeat cancellation guard') == [('ORDER-1','cancelled')]
    test('L-09',True,cancelled_sequence)
    result['local_cases']=cases
    result['temp_directory']=tmp
result['temp_directory_removed']=not Path(tmp).exists()
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(result,ensure_ascii=False,indent=2))
