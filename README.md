# sdd-init

一套可复用、可验证、可分发的 SDD（规格驱动开发）工作方法与工具，为目标项目提供初始化入口，以及后续开发、验证和交付所需的 Skills、角色、治理规则与模板。

本仓库维护通用流程、资源和安装工具；目标项目维护自己的业务需求、架构决定、产品实现及真实验收证据。具体需求以 [Spec](specs/platform-independent-sdd/spec.md) 为唯一正文，README 只提供定位与导航。

## 安装与使用

首次安装、更新命令、环境要求及冲突处理见[安装说明](docs/installation.md)。安装分为两个入口：

1. 安装用户级 `sdd-init` Skill。
2. 在目标仓库中调用 `sdd-init`，安装项目 Skills、角色和共享资源。

用户级入口更新与既有项目升级分别执行。安装和迁移的维护边界见 [AGENTS.md](AGENTS.md)。

## 项目能力入口

| 入口 | 用途 |
| --- | --- |
| [sdd-init](source/initializer/SKILL.md) | 初始化或升级项目中的 SDD 资源 |
| [sdd-doc](source/project/.agents/skills/sdd-doc/SKILL.md) | 整理和维护需求、设计、计划及验证记录 |
| [sdd-imp](source/project/.agents/skills/sdd-imp/SKILL.md) | 生成并执行 Plan／Task 清单，推进实施与修复 |
| [sdd-test-loop](source/project/.agents/skills/sdd-test-loop/SKILL.md) | 执行测试、反馈问题并复验 |
| [sdd-review-loop](source/project/.agents/skills/sdd-review-loop/SKILL.md) | 检查架构落地一致性并跟进复核 |
| [sdd-commit](source/project/.agents/skills/sdd-commit/SKILL.md) | 按授权完成 Git 与远端仓库交付 |
| [sdd-deploy](source/project/.agents/skills/sdd-deploy/SKILL.md) | 部署、启动或重启服务并检查就绪状态 |

项目分发包含六个项目 Skills 和五个自定义角色。协作规则见[仓库治理](source/project/.agents/sdd/references/sdd-repository-governance.md)，角色分工、默认模型与配置优先级见[执行协作](source/project/.agents/sdd/references/delegation.md)，项目文档入口见[文档索引](source/project/docs/index.md)。

## 源码与维护入口

| 路径 | 内容 |
| --- | --- |
| [src/sdd_init/](src/sdd_init/) | Python 包、CLI 与用户级安装器 |
| [pyproject.toml](pyproject.toml)、[setup.py](setup.py) | 包元数据、命令入口与打包配置 |
| [source/initializer/](source/initializer/) | 初始化 Skill、安装脚本、回归测试及专属资源 |
| [source/project/](source/project/) | 随项目分发的 Skills、角色及文档导航 |
| [source/project/.agents/sdd/](source/project/.agents/sdd/) | 共享模板、治理、检查工具及观测参考资源的唯一维护来源 |
| [scripts/build_release.py](scripts/build_release.py) | 安装目录与确定性资源 ZIP 的构建器 |
| [tests/](tests/) | 分发内容、构建可重现性及安装保护行为的测试 |
| [specs/](specs/) | 已确认需求及验收条件 |
| [docs/](docs/) | 安装指南、来源盘点及实施证据 |
| [baselines/](baselines/) | 历史导入包与文件哈希，仅供追溯 |

在 `source/` 中修改分发正文；`.build/`、wheel 和 ZIP 是生成产物，不作为编辑入口。共享资源在构建时投影到安装目录，不维护第二份现行正文。

## 构建与检查

使用 Python 3.11 或更高版本。以下命令从仓库根目录执行，仅依赖 Python 标准库：

```powershell
python -B scripts/build_release.py
python -B -m unittest discover -s tests -v
```

默认输出为 `.build/sdd-init/`，包含初始化资源、`assets/repo-payload.zip` 和构建清单。构建不会修改用户级安装或其他项目；已有输出目录不会被覆盖，重复构建需指定尚不存在的路径：

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
- [来源盘点](docs/inventory.md)与[导入清单](baselines/import-manifest.json)：导入范围、历史差异与来源追溯。
- [实施证据](docs/workflow-evidence.md)：实际验证记录及限制。
