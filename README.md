# sdd-init

SDD 治理与工作流的独立维护仓库。当前已导入现有维护资源并建立可重建分发入口；Issue / HTML 新流程的完整改造尚未完成，不能将本次建仓视为已升级其他项目。

需求与后续工作入口：[Issue #1](https://github.com/bigsmartben/sdd-init/issues/1)。其中区分用户已确认目标、建议方案、未决事项和验收条件；本文件不复制需求正文。

## 维护入口

| 目录 | 维护内容 |
| --- | --- |
| `source/initializer/` | 用户级 sdd-init 入口、元数据、安装器、原有回归测试及专属模板 |
| `source/project/` | 五个项目 Skill、共享治理、模板、项目状态工具及观测资源的可编辑正文 |
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

当前候选保留旧 Spec 解析和状态模型，尚不支持 Issue / HTML 完整基线；不要直接部署到正在开发的项目。现有安装器测试随产物保留，其全量结果须在实际改造任务中单独记录，不能用打包测试代替。
