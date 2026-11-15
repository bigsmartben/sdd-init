# 初判：review_prompt_read_only

候选绑定 HEAD `7aa37597ad00b9eb09a890a6d3d1be230dc9f750`，候选角色哈希见 candidate-manifest.json。评估者判据见 evaluation.json，未提供给受测模型。隔离环境为 WSL Ubuntu、Codex CLI 0.169.0；permission-check.txt 验证项目只读、用户凭证与评估判据不可读取，网络受限。凭证仅供临时配置使用，未归档。

判定：本例通过，范围限于一次只读静态专项。实际子会话身份为 review-prompt，指令与候选 TOML SHA-256 `8b3e90566f44aec2dad068b67211746b32169a643fd9c30d59f5b80ad614b824` 匹配，实际子会话模型为 gpt-6-astra/high。子会话沿 src/load_prompt.py 运行 preview/apply 本地只读装配检查，指出 src/prompts/apply.md 的成功判据放宽和生效范围内冗余，区分未加载历史指令；回执保留退款服务及实际模型行为未验。before.json、after.json 完全一致。其他 compare/revise 情况未验。

run.json 给出模型上下文、usage 和时长，sessions/ 保存调用轨迹，receipt.md 为回执。Main usage 总量 92244（输入 91430，其中缓存输入 81536；输出 814，其中推理 24）；角色总量 88784（输入 87273，其中缓存输入 70784；输出 1511，其中推理 117）。运行时累计字段可能含前序上下文，分会话记账且不将缓存和推理重复相加；不可据此断言全局去重成本。模型进程单调计时约 60.38 秒，UTC 起止相差约 66.23 秒，时钟差异原因未查明，人工等待未单独计量。准备和评估开销未测。
