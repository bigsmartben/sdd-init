# sdd-init

本仓库集中维护一套可复用、可验证、可分发的 SDD 工作方法与工具，使目标项目能够安装并执行一致的开发流程。`sdd-init` 是初始化入口；仓库同时维护后续开发、验证和交付所需的治理、Skills、模板及工具。

维护目标是让规则、文档与工具行为保持一致，并提供可追溯的维护来源、可重建的分发产物及可信的安装和升级验证。目标项目维护自己的业务需求、架构决定、产品实现和真实验收证据；本仓库维护供其使用的通用流程与资源。

当前治理升级的需求正文、职责边界、待决方案和验收条件统一维护在 [Issue #1](https://github.com/bigsmartben/sdd-init/issues/1)。本文件提供仓库定位与维护导航，[AGENTS.md](AGENTS.md) 约束仓库维护行为。

## 维护入口

| 目录 | 维护内容 |
| --- | --- |
| `source/initializer/` | 用户级 sdd-init 入口、元数据、安装器、原有回归测试及专属模板 |
| `source/project/` | 项目 Skills（当前五个）、共享治理、模板、项目状态工具及观测资源的可编辑正文 |
| `scripts/build_release.py` | 从上述来源构建独立的 sdd-init 安装目录和确定性 repo-payload.zip |
| `tests/` | 分发内容、可重现性和安装保护行为的验证 |
| `baselines/` | 导入前用户级安装包及文件哈希；仅用于追溯，不作为当前编辑入口 |
| `docs/inventory.md` | 导入范围、已知差异和实施限制 |

共享模板、治理及观测资源只在 `source/project/.agents/sdd/` 维护。构建时投影到安装器所需目录，避免维护两份现行正文。全局安装器和项目状态工具是两个独立执行入口，当前分别保留各自导入代码，不假定二者字节一致。

## 构建与检查

使用 Python 3.11 或更高版本；标准库即可执行：

```powershell
python -B scripts/build_release.py
python -B -m unittest discover -s tests -v
```

构建结果在 `.build/sdd-init/`，不会修改用户级安装或任何项目。默认拒绝覆盖已有构建目录；重复构建可指定新的空输出路径：

```powershell
python -B scripts/build_release.py --output .build/candidate/sdd-init
```

当前已建立维护源和可重建分发入口。候选仍保留旧 Spec 解析和状态模型，Issue #1 的新流程尚未完整实施；不要直接部署到正在开发的项目。现有安装器测试随产物保留，其全量结果须在实际改造任务中单独记录，不能用打包测试代替。

维护、构建、安装、升级与迁移分别按实际范围执行。仓库变更或构建成功不代表用户级安装或其他项目已升级；具体授权与验证要求见 [AGENTS.md](AGENTS.md)。
