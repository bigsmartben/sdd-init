import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
sys.path.insert(0, str(Path.cwd()))
from src import order_service as s, storage, ui
results=[]
def case(name, action):
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'orders.sqlite'
        c=storage.connect(path)
        try:
            details=action(c,path)
            results.append({'case':name,'result':'PASS',**details})
        except Exception as e:
            results.append({'case':name,'result':'FAIL','error':repr(e)})
        finally:
            c.close()
def read_reopened(path, ids):
    other=storage.connect(path)
    try:
        return [s.read_status(other,x) for x in ids]
    finally:
        other.close()
def cancel_submit(c,p):
    s.create_order(c,'A');s.create_order(c,'B');s.cancel_order(c,'A')
    accepted=s.submit_order(c,'A')
    assert accepted is False
    assert s.submit_order(c,'B') is True
    states=read_reopened(p,['A','B'])
    assert states==['cancelled','submitted'],states
    return {'cancel_submit_return':accepted,'reopened_states':states}
def payment(c,p):
    try:
        ui.mark_paid(c,'MISSING')
    except ValueError:
        pass
    else:
        raise AssertionError('missing payment did not raise ValueError')
    assert c.execute('SELECT count(*) FROM orders').fetchone()[0]==0
    for order_id, preparation in [('PENDING',None),('SUBMITTED',s.submit_order),('CANCELLED',s.cancel_order)]:
        s.create_order(c,order_id)
        if preparation:preparation(c,order_id)
        assert ui.mark_paid(c,order_id) is None
    statuses=read_reopened(p,['PENDING','SUBMITTED','CANCELLED'])
    assert statuses==['paid']*3,statuses
    return {'missing_error':'ValueError','reopened_statuses':statuses}
def failure(c,p,operation,commit):
    s.create_order(c,'A')
    expected=sqlite3.OperationalError
    if commit:
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('CREATE TABLE parent (id INTEGER PRIMARY KEY)')
        c.execute('CREATE TABLE child (id INTEGER REFERENCES parent(id) DEFERRABLE INITIALLY DEFERRED)')
        c.commit()
        c.execute('INSERT INTO child VALUES(99)')
        expected=sqlite3.IntegrityError
    else:
        c.execute('PRAGMA query_only=ON')
    try:
        operation(c,'A')
    except expected as e:
        error=type(e).__name__
    else:
        raise AssertionError('failure returned success')
    c.rollback()
    states=read_reopened(p,['A'])
    assert states==['pending'],states
    return {'error':error,'reopened_statuses':states}
case('BUG-001-original-and-AC-1-isolation',cancel_submit)
case('BUG-002-original-and-existing-payment',payment)
for label,op in [('submit',s.submit_order),('mark_paid',ui.mark_paid),('cancel',s.cancel_order)]:
    for commit in [False,True]:
        case(label+('-commit-failure' if commit else '-sql-failure'),lambda c,p,op=op,commit=commit:failure(c,p,op,commit))
output={'executor':'bugfix Agent independent of implementing sdd-coder','source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('src').glob('*.py'))},'python':sys.version,'sqlite':sqlite3.sqlite_version,'results':results}
print(json.dumps(output,ensure_ascii=False,indent=2))
sys.exit(any(r['result']!='PASS' for r in results))
