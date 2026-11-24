# 初始维护仓库验证（2026-11-02）

> 历史资料，记录旧版 SDD 工作流。当前产品范围见[项目文档索引](index.md)。

范围：维护源导入、构建、初始分发保护行为及 Skill 静态结构。关联 [Issue #1](https://github.com/bigsmartben/sdd-init/issues/1) 的 AC-001/002；不表示新工作流 AC-003～007 完成。

## 结果

- `python -B -m unittest discover -s tests -v`：最终 3/3 通过。覆盖分发 ZIP 和共享资源与维护源字节一致、两个独立输出目录构建结果相同、拒绝覆盖既有输出和维护源、隔离临时项目中安装幂等且保留已有 Blueprint。
- `python -B scripts/build_release.py`：构建成功，产物位于忽略目录 `.build/sdd-init/`；未安装到用户级目录或其他项目。
- 使用 skill-creator 的 `quick_validate.py` 检查构建的 sdd-init 及五个项目 Skill：6/6 静态验证通过，仅证明 frontmatter 和结构检查。
- `baselines/import-manifest.json` 的 50 个导入文件 SHA-256 与导入源码一致。Git 对 `source/` 禁用文本归一化，保留导入字节；后续维护改动仍由 Git 历史追踪，不改写原始导入哈希。
- 新增维护文件的 `git diff --cached --check` 通过；包含原样导入来源的全范围检查保留一项既有问题：`source/initializer/SKILL.md` 文件尾多余空行。本次不为消除历史格式提示修改原始来源。

## 首轮失败与修正

安装集成测试首轮遇到 Windows 子进程输出采用本机编码而父进程按 UTF-8 解码，导致 UnicodeDecodeError；未记为通过。测试子进程改为显式 `-X utf8` 后，3 项检查重新执行全部通过。未修改导入的安装器实现。

## 未验证与限制

- 未运行导入安装器的完整旧回归套件；新流程的 Issue 解析、HTML 固定版本、状态证据与迁移尚未实施或验收。
- 未执行产品测试、真实模型、浏览器原型操作或独立架构审查。
- 隔离安装证据不能证明在现有产品仓库升级安全，也不授权升级。
- CI 与远端提交结果由实际 GitHub 回执核对；本文件不提前宣称远端检查通过。
