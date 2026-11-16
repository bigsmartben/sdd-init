# sdd-init

一套可复用、可验证、可分发的 SDD（规格驱动开发）工作方法与工具，为目标项目提供初始化入口，以及后续开发、验证和交付所需的 Skills、角色、治理规则与模板。

`sdd-init` 借鉴 GitHub Spec Kit 的规格驱动开发思路，帮助项目以更少的文档负担和流程切换，从已确认的需求推进到实现与验证。[GitHub Spec Kit](https://github.com/github/spec-kit)

sdd-workflow 的核心目标是让用户前置决定关键结果，Agent 基于有效的项目知识，围绕明确的交付目标长程自主执行，并以证据完成交付。预期与取舍见[sdd-workflow 白皮书](docs/sdd-workflow-whitepaper.md)。

文档按任务需要产出，实施方案、任务和局部证据使用同一份可执行清单，见[实施交接](source/project/.agents/sdd/references/delegation.md#实施交接)。

由主 Agent（Main）按本轮交付目标选择下表入口。主任务、对话框、Agent、Skill 和角色的区别见[术语与职责](source/project/.agents/sdd/references/sdd-repository-governance.md#术语与职责)。选择工作流和处理组合请求见[职责与交接](source/project/.agents/sdd/references/sdd-repository-governance.md#职责与交接)和[阶段授权与推进](source/project/.agents/sdd/references/sdd-repository-governance.md#阶段授权与推进)。

本仓库维护通用流程、资源和安装工具。sdd-init 的产品承诺与验收条件见 [Spec](specs/platform-independent-sdd/spec.md)。实际执行入口见下表。目标项目维护自身的业务需求、架构决定、产品实现及验收证据。

## 安装与使用

首次安装、更新命令、环境要求及冲突处理见[安装说明](docs/installation.md)。安装分为两个入口：

1. 安装用户级 `sdd-init` Skill、共享资源和通用 `review-prompt` 角色。
2. 在目标仓库中调用 `sdd-init`，接入用户级共享工作流。

用户级安装负责更新共享资源，项目初始化负责链接和引用。安装和迁移的维护边界见 [AGENTS.md](AGENTS.md)。

## 项目能力入口

| 入口 | 用途 |
| --- | --- |
| [sdd-init](source/initializer/SKILL.md) | 初始化或升级项目中的 SDD 资源 |
| [文档写入规则](source/project/.agents/sdd/references/document-writing.md#按对象读取与语义核对) | 查找各类产物归并使用的模板和核对要点 |
| [sdd-develop](source/project/.agents/skills/sdd-develop/SKILL.md) | 单个需求的规格、实施及点对点验收 |
| [sdd-architecture](source/project/.agents/skills/sdd-architecture/SKILL.md) | 仓库级架构蓝图设计与演化 |
| [sdd-coder](source/project/.agents/sdd/references/delegation.md#实施交接) | 接收明确工单，维护 Plan／Task，实施并交付局部证据 |
| [sdd-bugfix](source/project/.agents/skills/sdd-bugfix/SKILL.md) | 按请求恢复指定行为，验证归因、修复并定向复验 |
| [sdd-test-loop](source/project/.agents/skills/sdd-test-loop/SKILL.md) | 按请求执行全功能点集成回归，交付复跑指南、逐项证据及 Test Gate |
| [sdd-refactor](source/project/.agents/skills/sdd-refactor/SKILL.md) | 基于蓝图初始化与维护 Review 矩阵，按确认范围审查、生成重构工单及组织整改复核 |
| [sdd-deliver](source/project/.agents/skills/sdd-deliver/SKILL.md) | 仓库交付、构建发布、运行排障、流量、备份恢复与退役 |

共享契约见[仓库治理](source/project/.agents/sdd/references/sdd-repository-governance.md)，调度与角色入口见[执行协作](source/project/.agents/sdd/references/delegation.md)，项目文档入口可参考[索引示例](source/project/docs/index.md)。

## 源码与维护入口

| 路径 | 内容 |
| --- | --- |
| [src/sdd_init/](src/sdd_init/) | Python 包、CLI 与用户级安装器 |
| [pyproject.toml](pyproject.toml)、[setup.py](setup.py) | 包元数据、命令入口与打包配置 |
| [source/initializer/](source/initializer/) | 初始化 Skill、安装脚本、回归测试及专属资源 |
| [source/project/](source/project/) | 项目工作流 Skill、角色与共享资源源码 |
| [source/project/.agents/sdd/](source/project/.agents/sdd/) | 共享模板、治理、检查工具及观测参考资源的唯一维护来源 |
| [review-prompt](source/initializer/assets/user-agents/review-prompt.toml) | 用户级通用角色，审查运行时提示词，按授权修订与复验 |
| [sdd-workflow-review](.agents/skills/sdd-workflow-review/SKILL.md) | 用户显式发起后，按设计与判据执行本仓工作流全面评审、隔离回归及获授权后的修复复验 |
| [scripts/build_release.py](scripts/build_release.py) | 安装资源与哈希清单的构建器 |
| [tests/](tests/) | 分发内容、构建可重现性及安装保护行为的测试 |
| [specs/](specs/) | 已确认需求及验收条件 |
| [docs/](docs/) | 安装指南、来源盘点及实施证据 |
| [baselines/](baselines/) | 历史导入包与文件哈希，仅供追溯 |

在 `source/` 中修改分发正文。构建目录和 wheel 从源码生成。

## 构建与检查

使用 Python 3.11 或更高版本。以下命令从仓库根目录执行，仅依赖 Python 标准库：

```powershell
python -B scripts/build_release.py
python -B -m unittest discover -s tests -v
```

默认输出为 `.build/sdd-init/`，包含初始化资源、`shared/` 和构建清单。构建不会修改用户级安装或其他项目；已有输出目录不会被覆盖，重复构建需指定尚不存在的路径：

```powershell
python -B scripts/build_release.py --output .build/candidate/sdd-init
```

构建后可运行安装资源回归检查：

```powershell
python -B .build/sdd-init/scripts/test_govern.py
```

纯文档修改可对选定文件执行只读检查：

```powershell
python -B source/project/.agents/sdd/scripts/doc_check.py --root . README.md
```

检查范围与限制见[文档校验 CLI](source/project/.agents/sdd/references/doc-check.md)；Python 包构建与安装冒烟验证见[开发验证](docs/installation.md#开发验证)。旧治理命令的退役决定与当前实现边界见[蓝图](docs/blueprint.md#旧治理命令退役边界)。

## 进一步阅读

- [维护约定](AGENTS.md)：写入范围、授权与交付边界。
- [产品与架构蓝图](docs/blueprint.md)：全产品用例、分发安装链路、组件职责与架构边界。
- [工程协作职责 Spec](specs/platform-independent-sdd/spec.md)：已确认需求及验收条件。
- [sdd-workflow 白皮书](docs/sdd-workflow-whitepaper.md)：工作流预期、已确认设计策略、分工与关键取舍。
- [来源盘点](docs/inventory.md)与[导入清单](baselines/import-manifest.json)：导入范围、历史差异与来源追溯。
- [实施证据](docs/workflow-evidence.md)：实际验证记录及限制。
