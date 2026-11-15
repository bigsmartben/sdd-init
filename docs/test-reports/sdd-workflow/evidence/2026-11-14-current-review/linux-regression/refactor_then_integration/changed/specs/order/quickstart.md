# 订单验收指南

## 1. 目标与范围

依据：[Spec](spec.md) AC-1、AC-2、AC-3、[订单函数契约](../../docs/contracts/order.md)。本轮已确认范围为新建、取消、提交、公开付款及真实外部回执；本地路径为 `storage.connect` → `order_service.create_order/cancel_order/submit_order` 与 `ui.mark_paid` → 关闭重开文件库。无 UI，不需要人工视觉判断。

所有订单正常输入为非空字符串且操作对象存在。执行者从契约推导空／非字符串、missing、真实数据库写异常、commit 故障及调用者恢复、多订单隔离和四种原状态付款组合，不新增状态限制或业务判据。提交 submitted/paid 后的再次提交无已确认结果，本指南不为其新增状态规则。公开付款四原状态全部可写 paid；取消后的提交仍必须按 AC-2 返回 false 并保持 cancelled。

## 2. 准备与启动

在隔离项目根目录操作，Python 3.11+ 与标准库 SQLite，无需安装依赖。实际候选为 HEAD `7a90ae57739b7ae93b554e0bd409259ab949a51e` 加第一阶段未提交的 `src/ui.py`、`tests/test_order.py` 改动；相关源码指纹见本轮[集成报告](../../docs/test-reports/order/integration.md)。先运行：

```bash
git rev-parse HEAD
git status --short
python -B checks/runtime_details.py
python -B checks/acceptance.py
```

runtime 证据必须与实际候选一致；哈希改变需重新核对影响，不能套用本轮结论。既有 acceptance 命令仅覆盖 AC-1/2/3，不包含付款和异常恢复。它输出各 AC 的实际 JSON，退出码 0 为全通过，1 为存在失败，3 为无失败但有阻塞。单场景可使用 `--scenario AC-1`、`--scenario AC-2`、`--scenario AC-3`。`python -B -m unittest discover -s tests -v` 为局部检查，不能替代本指南公开入口集成。

## 3. 场景验证

| 场景 | 依据与前置数据 | 操作与关键观察 | 通过判据与证据 |
| --- | --- | --- | --- |
| IT-01 | 新建；空文件数据库 | create ORDER-1，关闭重开 | pending 持久化；返回和重开状态 |
| IT-02 | AC-1；pending | submit，关闭重开 | true/submitted；公开返回和持久化 |
| IT-03 | 取消；pending | cancel、再 cancel，关闭重开 | 每一步 cancelled；中间与重开状态 |
| IT-04 | AC-2；pending | cancel，独立读取 cancelled，再 submit，关闭重开 | false/cancelled，不得覆盖取消 |
| IT-05 | 付款；pending | mark_paid，连接仍可读，关闭重开 | None/paid |
| IT-06 | 付款；经 submit 为 submitted | 同 IT-05 | None/paid |
| IT-07 | 付款；经 cancel 为 cancelled | 同 IT-05 | None/paid；付款无新增状态限制 |
| IT-08 | 付款；经首次 mark_paid 为 paid | 再 mark_paid，关闭重开 | None/paid |
| IT-09 | 非空字符串前置条件 | create 空串、None、123；随后合法创建 | 拒绝无效输入且无行；连接可继续合法创建 |
| IT-10 | missing；另有 EXISTS | read/cancel/submit/mark_paid missing；再付 EXISTS | 各抛 ValueError；EXISTS 保持 pending，再付款可持久化 |
| IT-11 | 数据库异常传播 | 对 create/cancel/submit/paid 分别开启 query_only，再恢复可写重试 | 原写失败抛异常、不返回成功；独立连接原状态不变；调用者恢复重试可持久化 |
| IT-12 | commit 异常传播及调用者连接归属 | 对四写入口包装真实连接只令 commit 抛异常；独立读取；调用者 rollback 后重试 | 同一异常上传；未提交写入未被别的连接看到；rollback 恢复；重试持久化。仅故障点注入，非真实磁盘 commit 故障 |
| IT-13 | 数据库异常边界 | 重复创建同 ID，引发真实 SQLite 唯一约束异常；rollback 后付款 | 数据库异常上传，原订单 pending，调用者仍可恢复付款 |
| IT-14 | 跨订单组合隔离 | 建 A/B，取消 A，提交并付款 B，关闭重开 | A cancelled、B paid，B submit true |
| IT-15 | AC-3；真实外部测试服务 | 只读 runtime；端点及授权齐备才由获授权者执行真实回执验证 | 缺端点或权限为 BLOCKED；本地、注入或模拟均不证明真实回执 |

以下内联命令复跑 IT-01～14，无需创建测试脚本文件。每一案例使用独立临时文件数据库，输出关键结果；计数按表中稳定 ID，一项包含多个子检查时全部满足才 PASS。故障注入仅用于 IT-12，其余均为真实 SQLite 操作。

```bash
python -B - <<'PY'
import json, sqlite3, tempfile
from pathlib import Path
from src import storage, order_service as s, ui
rows=[]
def emit(cid, facts, ok):
    rows.append({'case':cid,'result':'PASS' if ok else 'FAIL','actual':facts})
def error(call):
    try: call()
    except Exception as e: return e
    return None
with tempfile.TemporaryDirectory(prefix='order-integration-') as directory:
    root=Path(directory)
    def fresh(name):
        p=root/(name+'.sqlite'); return p,storage.connect(p)
    def disk(p,oid):
        c=storage.connect(p)
        try: return s.read_status(c,oid)
        finally: c.close()
    p,c=fresh('create'); ret=s.create_order(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
    emit('IT-01',[ret,state],ret is None and state=='pending')
    p,c=fresh('submit'); s.create_order(c,'ORDER-1'); ret=s.submit_order(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
    emit('IT-02',[ret,state],ret is True and state=='submitted')
    p,c=fresh('cancel'); s.create_order(c,'ORDER-1'); s.cancel_order(c,'ORDER-1'); before=s.read_status(c,'ORDER-1'); s.cancel_order(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
    emit('IT-03',[before,state],before==state=='cancelled')
    p,c=fresh('cancel-submit'); s.create_order(c,'ORDER-1'); s.cancel_order(c,'ORDER-1'); before=disk(p,'ORDER-1'); ret=s.submit_order(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
    emit('IT-04',[before,ret,state],before=='cancelled' and ret is False and state=='cancelled')
    for i,prior in enumerate(('pending','submitted','cancelled','paid'),5):
        p,c=fresh('paid-'+prior); s.create_order(c,'ORDER-1')
        if prior=='submitted': s.submit_order(c,'ORDER-1')
        elif prior=='cancelled': s.cancel_order(c,'ORDER-1')
        elif prior=='paid': ui.mark_paid(c,'ORDER-1')
        before=s.read_status(c,'ORDER-1'); ret=ui.mark_paid(c,'ORDER-1'); live=s.read_status(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
        emit(f'IT-{i:02}',[before,ret,live,state],before==prior and ret is None and live==state=='paid')
    p,c=fresh('invalid'); errs=[error(lambda oid=oid:s.create_order(c,oid)) for oid in ('',None,123)]; count=c.execute('SELECT count(*) FROM orders').fetchone()[0]; s.create_order(c,'RECOVER'); c.close(); state=disk(p,'RECOVER')
    emit('IT-09',[[str(e) for e in errs],count,state],all(isinstance(e,ValueError) for e in errs) and count==0 and state=='pending')
    p,c=fresh('missing'); s.create_order(c,'EXISTS'); errs=[error(lambda op=op:op(c,'MISSING')) for op in (s.read_status,s.cancel_order,s.submit_order,ui.mark_paid)]; before=s.read_status(c,'EXISTS'); ui.mark_paid(c,'EXISTS'); c.close(); state=disk(p,'EXISTS')
    emit('IT-10',[[str(e) for e in errs],before,state],all(isinstance(e,ValueError) for e in errs) and before=='pending' and state=='paid')
    ops=[('create',s.create_order,'pending'),('cancel',s.cancel_order,'cancelled'),('submit',s.submit_order,'submitted'),('paid',ui.mark_paid,'paid')]
    facts=[]; oks=[]
    for name,op,expected in ops:
        p,c=fresh('readonly-'+name); s.create_order(c,'EXISTS'); oid='NEW' if name=='create' else 'EXISTS'; c.execute('PRAGMA query_only=ON'); e=error(lambda:op(c,oid)); before=disk(p,'EXISTS'); c.rollback(); c.execute('PRAGMA query_only=OFF'); op(c,oid); c.close(); state=disk(p,oid)
        facts.append([name,type(e).__name__,str(e),before,state]); oks.append(isinstance(e,sqlite3.OperationalError) and before=='pending' and state==expected)
    emit('IT-11',facts,all(oks))
    class CommitFailure:
        def __init__(self,c,e): self.c,self.e=c,e
        def execute(self,*args): return self.c.execute(*args)
        def commit(self): raise self.e
    facts=[]; oks=[]
    for name,op,expected in ops:
        p,c=fresh('commit-'+name); s.create_order(c,'EXISTS'); oid='NEW' if name=='create' else 'EXISTS'; failure=sqlite3.OperationalError('injected commit failure'); wrapper=CommitFailure(c,failure); e=error(lambda:op(wrapper,oid)); before=disk(p,'EXISTS'); c.rollback()
        restored=isinstance(error(lambda:s.read_status(c,'NEW')),ValueError) if name=='create' else s.read_status(c,'EXISTS')=='pending'
        op(c,oid); c.close(); state=disk(p,oid); facts.append([name,str(e),e is failure,before,restored,state]); oks.append(e is failure and before=='pending' and restored and state==expected)
    emit('IT-12',facts,all(oks))
    p,c=fresh('duplicate'); s.create_order(c,'ORDER-1'); e=error(lambda:s.create_order(c,'ORDER-1')); c.rollback(); before=s.read_status(c,'ORDER-1'); ui.mark_paid(c,'ORDER-1'); c.close(); state=disk(p,'ORDER-1')
    emit('IT-13',[type(e).__name__,str(e),before,state],isinstance(e,sqlite3.IntegrityError) and before=='pending' and state=='paid')
    p,c=fresh('isolation'); s.create_order(c,'A'); s.create_order(c,'B'); s.cancel_order(c,'A'); ret=s.submit_order(c,'B'); ui.mark_paid(c,'B'); c.close(); a,b=disk(p,'A'),disk(p,'B')
    emit('IT-14',[ret,a,b],ret is True and a=='cancelled' and b=='paid')
print(json.dumps({'cases':rows,'temporary_directory_removed':not root.exists()},ensure_ascii=False,indent=2))
raise SystemExit(1 if any(r['result']=='FAIL' for r in rows) else 0)
PY
```

## 4. 异常与复位

脚本只操作 `TemporaryDirectory` 内的文件 SQLite，连接由调用者关闭，目录退出自动清理；每轮数据可直接重建。只读故障后调用者 rollback、关闭 query_only 再重试；commit 故障后在原真实连接 rollback、丢弃故障包装再重试；重复键失败后 rollback，保留原订单。不要将失败后未提交的同连接读值当作持久化成功。

AC-2 的差异应记录 Issue，不能修改预期使其通过。AC-3 当前不得访问网络；恢复条件是有权人员提供真实测试服务端点、调用权限和相应操作授权，再续验真实回执。本轮不自行配置外部服务或获取凭据。

## 5. 结果引用

实际版本、逐项结果、原始观察、Issue、Test Gate 与恢复条件见[本轮集成报告](../../docs/test-reports/order/integration.md)。第一阶段的架构与行为保持证据见[付款 Review](../../docs/test-reports/order/payment-review.md)及[原 Plan](../../docs/test-reports/order/payment-plan.md)，局部证据不替代本轮集成覆盖。
