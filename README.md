# sdd-init

本仓库集中维护一套可复用、可验证、可分发的 SDD 工作方法与工具，使目标项目能够安装并执行一致的开发流程。`sdd-init` 是初始化入口；仓库同时维护后续开发、验证和交付所需的治理、Skills、模板及工具。

维护目标是让规则、文档与工具行为保持一致，并提供可追溯的维护来源、可重建的分发产物及可信的安装和升级验证。目标项目维护自己的业务需求、架构决定、产品实现和真实验收证据；本仓库维护供其使用的通用流程与资源。

治理升级的需求来源维护在 [Issue #1](https://github.com/bigsmartben/sdd-init/issues/1)。本次用户指定恢复五 Skill／五角色后的本地分发及验证见[实施证据](docs/workflow-evidence.md)；远端 Issue／Draft PR 仍保留此前方案，尚未同步本轮调整。本文件提供仓库定位与维护导航，[AGENTS.md](AGENTS.md) 约束仓库维护行为。

## 维护入口

用户安装、更新与仓库内调用见[安装说明](docs/installation.md)。Python 包入口位于 `src/sdd_init/`，打包配置位于 `pyproject.toml` 和 `setup.py`；打包复用现有资源构建器。

| 目录 | 维护内容 |
| --- | --- |
| `source/initializer/` | 用户级 sdd-init 入口、元数据、安装器、原有回归测试及专属模板 |
| `source/project/` | 五个项目 Skills、五个自定义角色、共享说明、模板、存量状态工具及观测参考资源的可编辑正文 |
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

当前分发入口为 sdd-doc、sdd-imp、sdd-test-loop、sdd-review-loop、sdd-commit；使用方式见[共享协作说明](source/project/.agents/sdd/references/governance.md)，五个角色的场景分工、默认模型及配置优先级见[执行协作](source/project/.agents/sdd/references/delegation.md)，实施 Plan 见 [Draft PR #2](https://github.com/bigsmartben/sdd-init/pull/2)。初始化只安装资源和导航，旧 Spec/Status 命令保留供存量记录使用，不作为新流程门禁。

构建后可运行 `python -B .build/sdd-init/scripts/test_govern.py` 验证安装及存量工具。已有退役 Skill 的项目会在安装前收到冲突提示，升级与迁移另按实际范围处理。原型托管、用户级安装与其他项目升级仍未执行；实际验证与限制见 [实施证据](docs/workflow-evidence.md)。

维护、构建、安装、升级与迁移分别按实际范围执行。仓库变更或构建成功不代表用户级安装或其他项目已升级；具体授权与验证要求见 [AGENTS.md](AGENTS.md)。
