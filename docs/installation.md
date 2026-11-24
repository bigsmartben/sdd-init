# 安装与验证

在本仓源码目录使用 Python 3.11+ 和 uv。先用 `uvx --from . sdd-init inspect` 查看目标，再运行 `uvx --from . sdd-init install`。默认写入：

- `~/.codex/AGENTS.md`
- `~/.codex/agents/{architect,analyst,implementer,tester,devops,uat-observer}.toml`

同名文件内容有差异时，安装器在写入前列出冲突。先备份并手工合并需要保留的指令；使用自定义合并版本时，可在空目录用 `--home` 导出全套文件，再手动采用需要的部分。旧版已安装的用户级技能和项目链接需由其所有者单独清理。旧版 live-uat Skill 同样按此方式处理。新会话中可向 Main 发送 `【陪测】` 或 `/live-uat` 开测。该入口由 Main 的指令文本解释。使用 `/speckit.*` 前，目标项目需已有对应 Spec Kit 配置。

旧任务中的 `[Coder]` 标签由 Main 映射到 implementer。已有安装若含个人修改的 coder.toml，请核对后自行迁移；安装命令只写入本版分发文件。

## 开发验证

从仓库根目录执行。构建输出使用一个尚不存在的路径。

```powershell
python -B -m unittest discover -s tests -v
python -B scripts/build_release.py --output .build/codex-bundle
uv build --out-dir .build/dist
python -B scripts/smoke_package.py --from (Get-ChildItem .build/dist/*.whl | Select-Object -Last 1).FullName
```

冒烟检查在临时用户目录执行 inspect、首次安装及重复安装。实际陪测需在目标应用中由用户操作并确认。
