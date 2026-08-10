---
title: "命令行任务合成论文合集"
date: 2026-08-10 15:00:00 +0800
categories:
  - llm
tags:
  - terminal agents
  - task synthesis
  - RST
  - CLI-Universe
  - agent training
excerpt: "两篇命令行智能体任务合成论文的直接拼接式阅读报告：递归验证的 RST 与可执行过滤的 CLI-Universe。"
toc: true
toc_label: "目录"
toc_sticky: true
read_time: true
---

本文按原论文顺序直接拼接两份报告，不把两种方法改写成一套统一框架：第一篇关注如何递归地把已有任务变难，第二篇关注如何从能力规格出发构造并筛选高信号任务。

## Recursive Synthesis for Long-Horizon Terminal Tasks（RST）

> **论文**：[*Recursive Synthesis for Long-Horizon Terminal Tasks*](https://arxiv.org/abs/2608.05466v1)  
> **作者**：Zhongzhi Li、Yucheng Shi、Zongxia Li、Ruhan Wang、Anhao Li、Zixun Huang、Junyao Yang、Lei Ke、Ninghao Liu、Haitao Mi、Leowei Liang  
> **版本**：arXiv:2608.05466v1，2026-08-05，35 页  
> **研究任务**：在保持 instruction、环境、参考解和 verifier 一致的前提下，低成本地批量合成长时域命令行智能体任务，并让任务难度随轮次持续增长。

### 1. 主要方法

论文解决的是长时域 terminal-agent 训练数据昂贵且难以保持任务契约一致的问题，因为一个可用样本必须同时包含可运行环境、公开指令、参考解和私有验证器（Abstract，Sec. 1）。RST 从 639 个已验证的 bootstrap seed 出发，在每一轮选择可行的 rewrite operator，先扩展 `solve.sh` 的可执行路径，再同步修改环境、verifier 和 instruction，并通过静态检查、反捷径审计以及 fresh sandbox 执行来接受或丢弃候选（Sec. 3–4，Fig. 2–3）。这种“解法先行、验证对齐、通过后再 reseed”的闭环把每个被接受任务都绑定到可执行的可解性证据，因此可以在递归增加状态依赖和中间产物时抑制不可解样本的累积（Sec. 4.3–4.4）。

![Figure 2：RST 的递归任务合成与训练闭环](/images/blog/command-line-task-synthesis/rst/rst-loop.png)

*Figure 2 原图：seed 任务经 agent 改写、验证后进入 verified pool，并可用于后续训练与再合成。*

### 2. 与之前论文的不同或改进

先前的 terminal 数据集和环境生成方法主要从仓库、文档、执行轨迹或固定模板一次性构造样本，通常扩大的是任务来源或数量，而不是在同一任务契约上连续增加可执行工作（Sec. 2）。RST 把参考解的增长作为改写起点，同时重写 verifier 与公开指令并复用已通过任务，在十五轮内得到 37,484 个任务、约每个通过任务 $0.05$ 的成本，但代价是方法依赖初始任务的可验证性、改写算子覆盖和后续去重（Sec. 4–5，Fig. 3）。

![Figure 3：从 seed 到更长、更严格任务的单轮改写](/images/blog/command-line-task-synthesis/rst/rst-round.png)

*Figure 3 原图：RST 在增加步骤和状态依赖的同时加严断言，并在 sandbox 中重新验证。*

### 3. 之前研究的做法与问题

人工编写或收集成功轨迹可以提供可靠的终端环境和测试，但论文指出单个长时域任务的成本常在数百到数千美元，难以支撑大规模训练（Sec. 1）。
从仓库、文档、模板或既有 benchmark 直接转换的流水线容易生成指令含糊、执行路径浅或测试脆弱的样本，即使脚本能运行也未必提供强学习信号（Sec. 1–2）。
只用 taxonomy 枚举技能可以扩展覆盖面，却通常缺少对环境状态、参考解、私有 verifier 和公开契约的联合校验（Sec. 2）。
弱过滤的自训练或递归生成还可能在重复采样中放大奖励误设、不可解任务和近重复样本，因此需要可执行的 oracle 与契约一致性检查（Sec. 2–3）。

### 4. 实验设计和结果

实验以 TerminalWorld 的 639 个已验证任务为 bootstrap，逐轮生成并统计产量、结构增长、契约一致性、域与算子多样性，再在各轮匹配子集上用固定推理设置评测 DeepSeek-V4-Pro 的 $\mathrm{pass@4}$ 和 verifier partial credit，训练效用则用 Qwen3.5-27B、Qwen3.5-122B-A10B 的 SFT 及 Qwen3.5-27B 的 PPO 检验（Sec. 5）。
从 $R_1$ 到 $R_{15}$，每 1,000 次 seed 尝试的通过任务产量保持在 498.2–572.2，候选通过率保持在 74.5%–81.5%，而中位参考解长度从 67 行增至 374 行、命令数从 40 增至 244、CLI 工具数从 17 增至 71，指令长度只从 85 增至 122 个词（Sec. 5.1，Fig. 1，Fig. 7）。
在 solver 和推理配置不变时，DeepSeek-V4-Pro 的 $\mathrm{pass@4}$ 从 $R_1$ 的 90% 单调降至 $R_{15}$ 的 2.5%，平均 partial credit 从 0.970 降至 0.170，说明结构增长确实转化成了更高的 agent 难度而不是单纯变长（Sec. 5.2，Fig. 12–15）。
递归仍保留广泛覆盖：$R_{15}$ 使用了 40 个 rewrite operator 中的 36 个，最大单一算子占比 8.0%，且与 Terminal-Bench 2、Terminal-Bench Hard 和 LHTB 的抽样任务没有匹配的 13-token 窗口（Sec. 5.3，Table 2，Fig. 18–22）。

![Figure 1：不同递归轮次上的 solver 难度与轨迹长度](/images/blog/command-line-task-synthesis/rst/rst-difficulty.png)

*Figure 1 原图：DeepSeek-V4-Pro 与 GPT-5.6-sol 在更高轮次上通过率下降，而通过任务的轨迹变长。*

Qwen3.5 轨迹的 SFT 随轮次增加而稳定提升：Qwen3.5-27B 在 Terminal-Bench 2、Terminal-Bench Hard 和 LHTB 上从 41.20/22.67/18.10 提升到 47.94/28.33/22.44，Qwen3.5-122B-A10B 则从 43.82/20.00/18.85 提升到 49.44/30.00/23.63（Sec. 5.4，Table 3）。

![Figure 23：逐轮 SFT 对三个终端 benchmark 的影响](/images/blog/command-line-task-synthesis/rst/rst-sft.png)

*Figure 23 原图：加入更晚轮次采集的轨迹后，两种 Qwen3.5 模型在 TB2、TB Hard 和 LHTB 上均上升。*

在包含全部 37,484 个合成任务的 verifier-based PPO 中，平均 verifier reward 的五步移动平均约从 0.11 升至 0.14 以上，平均交互轮数从约 19–20 增至 30 以上；独立评测的 Qwen3.5-27B-RL 在三个 benchmark 上达到 49.44%、32.00% 和 22.07%，相对 base 的相对增益为 20.00%、41.16% 和 21.93%（Sec. 5.5，Table 4，Fig. 24）。

![Figure 24：合成任务上的 PPO reward 与轨迹长度](/images/blog/command-line-task-synthesis/rst/rst-rl.png)

*Figure 24 原图：PPO 训练过程中 verifier reward 和平均 trajectory turns 同步增加。*

### 5. 结论和启发

论文结论是，solution-first 的递归改写可以在十五轮内以稳定的验证吞吐构造越来越难的 terminal tasks，并且这些任务产生的轨迹能改善 SFT 与 verifier-based RL（Sec. 6）。
最值得迁移的思想是把“任务变难”落实为新的状态依赖、工具调用、产物和断言，再让参考解、私有测试和公开指令一起更新，而不是只扩写自然语言描述。
局限在于论文只报告到 15 轮，$R_{15}$ 仍有 p95 近重复相似度 0.703，且结论主要基于 Qwen3.5、DeepSeek-V4-Pro 和现有 terminal benchmark，规模外推、跨生成模型稳定性及更强去重仍待验证（Sec. 5.3，Sec. 6）。

## CLI-Universe: Towards Verifiable Task Synthesis Engine for Terminal Agents

> **论文**：[*CLI-Universe: Towards Verifiable Task Synthesis Engine for Terminal Agents*](https://arxiv.org/abs/2606.22883v1)  
> **作者**：Zhanbo Hua、Yifan Yao、Weihao Xie、Yongchi Zhao、Minghao Liu、Ruizhi Qiu、Zhewei Huang、Zun Wang、Yiyan Ji、Yunhai Ye、Letian Zhu、Xinping Lei、Han Li、Zhiyuan Ma、Zili Wang、Zhaoxiang Zhang、Jiaheng Liu  
> **版本**：arXiv:2606.22883v1，2026-06-22，20 页  
> **研究任务**：从能力规格出发构造真实、可执行、可验证且具有非平凡难度的命令行智能体任务，并用少量高信号轨迹训练模型。

### 1. 主要方法

论文解决现有 terminal-agent 合成数据常有指令含糊、执行路径浅和测试脆弱，导致“任务数量增加但学习信号不增加”的问题（Abstract，Sec. 1）。CLI-Universe 先沿 domain、skill type、capability 和 engineering pillar 四个维度采样候选，再通过对仓库、文档、issue、教程和用例的 evidence-guided deep research 形成 blueprint，随后把 blueprint 实例化为带资源和依赖的 Docker 环境，并用 rubric-gated tests、hint-conditional filtering 和 fail-to-pass 检查收集合格轨迹（Sec. 3，Fig. 1）。这种 inside-out 流程先规定想训练的能力，再用现实材料和双向可执行验证约束环境与监督，因此能在有限轨迹数量下提高每个样本的信息密度（Sec. 3–4）。

![Figure 1：CLI-Universe 的 blueprint、环境和可执行验证流水线](/images/blog/command-line-task-synthesis/cli-universe/cli-workflow.png)

*Figure 1 原图：候选想法经过证据研究、环境实现和 fail-to-pass 过滤后才成为训练任务。*

### 2. 与之前论文的不同或改进

先前路线主要依靠从现有基础设施抽取任务，或让 LLM 按技能/领域 taxonomy 生成任务，能够扩大来源与覆盖面，却较少为每个样本提供环境真实性、测试正确性和非平凡难度的联合保证（Sec. 1–2）。CLI-Universe 将“能力规格 → 证据落地 → Docker 实现 → 角色分离的测试/解答 → 提示条件过滤 → fail-to-pass”串成硬过滤链，移除任一模块都会使 1k 任务消融的 TB2.0 分数下降 3.4–6.2 分，但代价是约三分之二候选被丢弃且依赖多个 LLM agent 的质量（Sec. 3–4，Fig. 2–3）。

![Figure 3(a)：移除 CLI-Universe 组件后的 TB2.0 消融](/images/blog/command-line-task-synthesis/cli-universe/cli-ablation.png)

*Figure 3(a) 原图：完整流水线为 26.7，去掉 asset strategy、query rubrics 或 test-case rubrics 后分别降至 20.5、23.3 和 22.8。*

### 3. 之前研究的做法与问题

人工设计的 Terminal-Bench 任务通常质量高但规模受限，而从仓库、Docker 配置、文档或轨迹直接转化的做法更容易得到表层相似、路径较短或测试不稳定的样本（Sec. 1–2）。
taxonomy 驱动的方法能系统枚举领域和技能，但若没有证据研究，候选可能退化为库调用、主观评分或缺少 ground truth 的简单包装；反过来，单纯资产挖掘也未必覆盖希望训练的能力组合（Sec. 3.2，Fig. 2a）。
已有流程常把测试“能运行”当作完成标准，缺少对 rubric、边界条件、初始失败状态和最终成功状态的双向检查，因而会把无效或过于简单的轨迹送入训练（Sec. 3.4）。
该方法仍把 ideation、环境构建、解答和测试生成交给 LLM agent，数据质量受底层模型能力约束，并且当前只验证 6,000 条轨迹和不超过 32B 的学生模型（Sec. 6）。

### 4. 实验设计和结果

实验使用 Qwen3 的 8B、14B 和 32B dense 模型，分别在 Kimi-K2.6 生成的 6,000 条 CLI-Universe 轨迹上做 SFT，以 Terminus 2 在 Terminal-Bench 1.0/2.0 的 avg@4 为主指标，并用 BFCL v4 与 VitaBench 测试跨 benchmark 泛化（Sec. 4）。
流水线从候选想法到验证任务的保留率为 100% → 70.0% → 56.0% → 42.0% → 33.6%，在 89 个 Terminal-Bench 2 任务上合成测试与官方解答的通过一致率为 91%，Codex/GPT-5.4 评估的语义匹配率为 88%（Sec. 3.2–3.4，Fig. 2）。

![Figure 2(d)：CLI-Universe 的逐阶段任务保留率](/images/blog/command-line-task-synthesis/cli-universe/cli-funnel.png)

*Figure 2(d) 原图：约三分之二候选在想法、blueprint、环境或 fail-to-pass 阶段被过滤。*

CLI-Universe-32B 在 TB2.0 达到 33.4%，超过同规模 SkillSynth-32B 的 29.6%、Nemotron-Terminal-32B 的 27.4% 和 TerminalTraj-32B 的 22.0%，相对未训练 Qwen3-32B 的 3.4% 提升 30.0 分，而 14B/8B 分别达到 23.0%/10.9%（Sec. 4.1，Table 1，Fig. 3b）。
相同 6k 轨迹量的对照显示，CLI-Universe-32B 的 33.4% 高于 Nemotron 的 28.9% 和 TerminalTraj 的 18.0%，而仅保留成功轨迹的 6k 方案也高于未过滤的 10k 轨迹方案 28.2%，支持“验证质量比原始数量更重要”的观察（Sec. 4.2.2，Sec. 4.3.2，Table 2）。

![Figure 4(a)：BFCL-v4 与 VitaBench 的跨 benchmark 泛化](/images/blog/command-line-task-synthesis/cli-universe/cli-generalization.png)

*Figure 4(a) 原图：32B 模型在 BFCL-v4 上从 46.7% 升至 58.0%，在 VitaBench 上从 15.4% 升至 27.0%。*

在 32B 学生上，CLI-Universe-32B 相对 Qwen3-32B 在 BFCL-v4 和 VitaBench 的 pass@1 分别提升 11.3 和 11.6 分，细粒度任务类别中 Data Processing、Machine Learning 和 Data Querying 的增益最大，但 Video Processing 与 Games 没有提升；失败归因还显示 CLI-Universe-32B 的失败更多来自执行侧的 step repetition，而四个 frontier 基线主要失败在 verification 侧（Sec. 4.4–4.5，Fig. 4–5）。

### 5. 结论和启发

论文结论是，结构化能力规格、证据引导的技术研究和多阶段可执行验证结合后，6,000 条高质量轨迹就能显著提升 8B–32B terminal agents，并迁移到其他 agentic benchmark（Sec. 5）。
最值得迁移的思想是把训练数据质量拆成可检查的契约：候选能力要有现实证据，环境要可复现，测试要过 rubric，提示要真正有用，且初始状态必须 fail、解答后必须 pass。
局限在于流水线仍受 LLM 生成器能力、6k 数据规模和 SFT 训练范式限制，与最强闭源模型仍有明显差距，后续需要验证更大模型、更大任务池以及基于这些任务的强化学习（Sec. 6）。
