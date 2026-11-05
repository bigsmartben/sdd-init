# SDD 本地观测资源（契约 1.0.0）

规范以[架构原则](../../references/architecture-rules.md)及[观测基线](../../references/observability-baseline.md)为准。以下端点、SDK 和后端描述属于参考实现及历史验证环境，不是通用架构选型；本机共享栈当前运行状态未在本轮验证。

以下历史接入示例使用的共享栈位于本机 `C:/Users/24598/Projects/otel-stack`；该示例复用共享 Compose，项目侧配置身份、端点、接入与记录策略；目标项目的部署及共享方式由其已确认环境设计确定。此目录的参考契约由 sdd-init 分发；初始化器只安装资源，不启动栈或修改业务。SQLite 非必需。实际共享栈版本和部署以其仓库为准。

`event-1.0.0.schema.json` 定义 UTF-8 JSON 对象，所有字段必须存在，未知用 null 或明确的 unknown；时间为十进制 Unix 纳秒字符串，避免跨语言整数精度损失。event_id 是每条事实的 UUID；重试同一事实保留 ID。sequence 在同一 call/stage 中标识顺序，无法得知时为 null。stage 记录真实事实（如 received、generated、sent、presented），不得以生成推定呈现。流式片段、中断和顺序由独立事件表达；观测不保存原始音视频字节，可记录合法业务／测试资产标识，标识本身不证明资产落地。不得采集凭证。

JSON 为 OTLP LogRecord body；resource `project`、`service.name`、`service.version`、`service.instance.id` 与事件的同名身份一致，`deployment.environment` 由项目配置。OTLP timestamp 对应 event_time，observed timestamp 对应 observed_time；trace/span 字段也放 OTLP 原生上下文，未知时不构造零 ID。Loki 将 project 和 service_name 用于低基数索引；会话、请求、调用、实例和 trace 等保持 body 或结构化元数据，不将其提升为索引标签。现有 Loki 默认资源标签须实际检查；本契约不自行证明高基数配置已收敛。

save_state 是写入该事件时已知的事实，不会自动随传输更新。应用内受理、Collector 接收和后端回读是不同边界：OTLP 成功不证明后端持久化；后续状态或回读证据应通过 event_id 关联记录。缺失、队列饱和、崩溃、写入失败应由独立健康/缺失证据暴露；诊断本身也可能不可达，不能声称无限故障无损。结构合法不等于 OBS-01/02/03 已通过。每个项目必须确认缓冲、限额、退出、恢复与媒体策略，并以真实故障、文字回读与媒体载荷拒收验证。

宿主 OTLP HTTP: `http://127.0.0.1:4318`；外部 Compose 加入外部 `otel` 网络用 `http://otel-collector:4318`。Android 模拟器通常以 `10.0.2.2` 访问宿主，但现有监听仅回环，须验证虚拟化网络及安全转发；真机需要明确授权的安全隧道或绑定策略，不擅自开放公网。Grafana 可选。

Java: 在 `java` 目录执行 `mvn -B compile exec:java -Dexec.mainClass=local.sdd.Example`（PowerShell 将 `-Dexec.mainClass=local.sdd.Example` 用引号括住）。示例使用 OpenTelemetry Java SDK 1.50.0 和 OTLP HTTP，固定消息及资源，打印 event ID 与 trace ID。`python check.py --project sdd-java-example --event-id <ID>` 只查询最近范围，再以 Tempo `/api/traces/<trace_id>` 查询链路。2026-10-29 在共享栈已回读一条示例日志及对应 trace；示例只示范编码和传输，SDK 队列丢弃、退出与断电、原始交互、媒体和业务隔离均未验证，也没有完整丢失计数，不能直接声称满足 OBS-01/02。示例中的应用结果是 unknown，成功 flush 不是后端持久化证据；生产适配需正确 JSON 转义、实际阶段和原始数据。Maven 运行可能出现 OkHttp 线程退出警告。

当前状态：契约草案及映射，Java 样例及 Node/Python/Go/Rust 的单条日志回读；各语言完整故障隔离和原始交互验收尚未完成，不能当作基线通过证据。上述历史共享栈记录的保留策略为无限期，磁盘会增长；该记录不替代项目确认的容量、轮转和保留策略。

Java 隔离探针：`mvn -q compile exec:java -Dexec.mainClass=local.sdd.IsolationProbe` 测试固定字节媒体的文件写入、force 与回读，以及受控慢写、容量饱和、失败和退出超时。它是隔离示例，计数只在进程内，未接入实际业务、OTLP 契约或独立持久缺失台账；不能据此证明强制记录或崩溃无损。

Java 历史业务示例包含媒体文件写入，与现行观测边界冲突，整改前不得执行该媒体写入示例；历史运行事实不代表当前规则通过。现行观测范围包含日志、指标及链路，媒体仅允许合法元数据或资产标识，须另以拒收和隔离证据验证。

Node.js 样例：在 `node` 目录执行 `npm ci --ignore-scripts` 后 `node example.js`。使用锁定的 OpenTelemetry Node Logs SDK、HTTP exporter，实际写入一条原始文本事件并输出 event_id；使用 `python ../check.py --project sdd-node-example --event-id <ID>` 回读。2026-10-29 已验证该文本事件在共享 Loki 回读。示例展示协议与字段映射，并记录输入和生成输出；自动埋点不记录原始交互，媒体、独立缺失台账、故障隔离、崩溃与退出边界未验证，不能视为 OBS 基线通过。

Python：在虚拟环境安装 `pip install -r requirements.lock`，运行 `python example.py`；Go：Go 1.24 下运行 `go run .`，依赖由 go.mod/go.sum 固定。均使用 OpenTelemetry SDK 和 OTLP/HTTP，经共享 Loki 已回读 UTF-8 原始输入和生成输出；查询项目分别为 `sdd-python-example` 和 `sdd-go-example`。这两个示例展示输入输出日志和契约映射，缺少媒体拒收、缺失台账、故障隔离与崩溃边界验证，不能作为 OBS 通过证据。

Rust：Rust 1.85.1 下运行 `cargo run --locked`，使用 OpenTelemetry Rust SDK 0.27.1 和 OTLP HTTP exporter 0.27.0；2026-10-29 容器中编译运行、Loki 回读原始文本。已回读输入和生成输出；媒体拒收、缺失台账、故障隔离和崩溃边界未验证。

Android：`android` 是自定义 OTLP/JSON HTTP 适配示例，不是 OpenTelemetry Android SDK；AGP 8.13.0、Gradle 8.14.3、compileSdk 35，使用 `gradle :app:assembleDebug`。已离线构建，但未连接设备，端到端 UNVERIFIED。测试前可对已授权连接的设备执行 `adb reverse tcp:14318 tcp:4318`，应用访问设备回环 127.0.0.1:14318；宿主 Collector 仍仅绑定回环，不需开放公网。仅为开发示例启用明文，生产应另选安全传输。它只发输入文本，没有完整输出、媒体拒收证据、可持久缺失台账或停机恢复；队列被拒只在内存计数。

各语言的实际验证与缺口见 `language-status.json`；状态仅指局部自验。
