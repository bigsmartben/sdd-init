# Plan：标准 Skill 目录链接

## 目标与边界

依据 [Spec FR-027／AC-027](../../specs/platform-independent-sdd/spec.md)，按本轮用户确认：目标项目直接提供 `.agents/skills/<技能名>/SKILL.md`，每个技能目录必须链接到用户级共享资源，不采用项目副本。工作流职责和步骤不变。

共享包结构不变；包锚点移到扫描目录外的 `.agents/sdd-workflow/`。新版 `init` 迁移标准旧嵌套链接，保护项目自有目录、非标准链接、定制配置和历史记录。本轮只改源码并隔离验证，不修改用户实际安装或其他项目，不做客户端发现验证、提交或远端交付。

## 执行清单

| Task | 实施与完成条件 | 状态与证据 |
| --- | --- | --- |
| T001 | 六个技能各建目录链接；同步共享锚点、导航、角色引用、忽略项和只读检查；重复执行不复制、不重建有效链接 | 完成。`govern.py`、`project_install.py` 和分发导航已同步；真实链接及共享更新由 `test_flat_skill_links.py` 覆盖。 |
| T002 | 标准旧链接可迁移；多链接失败可回滚，中断可恢复；兼容旧恢复日志并保护外部改动 | 完成。恢复日志 v3 逐项记录链接和进度；v1/v2 仍按旧路径恢复。30 项定向测试覆盖新装、迁移、冲突、链接身份变化及安装／恢复中断。 |
| T003 | 更新直接引用、文档校验边界、现有回归和包安装检查，保留其他未提交工作 | 完成。下列最终命令均通过；用户已确认的客户端识别问题不重复验证。 |

## 验证记录

环境：2026-11-15，Windows 11，Python 3.14.6，uv 0.11.20。所有安装验证使用临时 Skill、角色及目标项目目录，Windows 链接为 junction（目录联接）。

| 命令或范围 | 结果 |
| --- | --- |
| `python -B -X utf8 -m unittest discover -s tests -v` | 116 项通过，276.597 秒；包含 30 项扁平链接测试和 2 项新增文档读取边界测试。 |
| `uv build --out-dir .build/flat-skill-links/dist` | 源码包和 wheel 构建成功。 |
| `python -B scripts/smoke_package.py --from .build/flat-skill-links/dist/sdd_init-0.7.0-py3-none-any.whl` | 临时安装、重复安装、项目接入、真实目录链接、角色引用、只读检查及空恢复检查通过，临时目录清理完成。 |
| `python -B scripts/build_release.py --output .build/flat-skill-links/initializer` | 从维护源码生成分发目录成功。 |
| `python -B -X utf8 .build/flat-skill-links/initializer/scripts/test_govern.py` | 22 项通过，54.489 秒。 |
| 7 份直接受影响正文的 `doc_check.py --strict` | 零错误、零警告；分发导航引用另由安装回归核对。 |
| `git diff --check` | 通过。 |

机械检查范围：`docs/installation.md`、`docs/blueprint.md`、`specs/platform-independent-sdd/spec.md`、`source/initializer/assets/install.md` 及分发参考中的 `doc-check.md`、`git-delivery.md`、`sdd-repository-governance.md`。本记录及项目索引单独检查。

语义核对：标准入口位于扫描根的直接子目录；共享内容仍唯一，项目不持有工作流副本；旧受管入口可迁移，项目自有内容及原工作区改动保留。文档校验器允许标准技能链接读取同一共享包，但不放开其他外部目标。

未验证：Zed、dsh 等客户端发现行为（用户明确不要求重验）、原生 POSIX 链接发布、断电或文件系统损坏、用户实际安装迁移。旧项目需在更新初始化器后重新运行 `init` 才会转换项目链接布局。
