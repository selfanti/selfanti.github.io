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
  - CalibForge
  - SETA
  - TMax
  - agent training
excerpt: "五篇命令行智能体任务合成论文的直接拼接式阅读报告：RST、CLI-Universe、CalibForge、SETA 与组合式数据生成及开放 RL 配方 TMax。"
toc: true
toc_label: "目录"
toc_sticky: true
read_time: true
---

本文按加入顺序直接拼接五份报告，不把五种方法改写成一套统一框架：第一篇关注如何递归地把已有任务变难，第二篇关注如何从能力规格出发构造并筛选高信号任务，第三篇关注如何用多个 solver 的相对行为把候选任务校准到可学习区间，第四篇关注如何从真实来源合成环境并按模型能力自适应调节难度，第五篇关注如何用组合式合成数据与稳定化 RL 配方训练小型终端智能体。

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

先前的 terminal 数据集和环境生成方法主要从仓库、文档、执行轨迹或固定模板一次性构造样本，通常扩大的是任务来源或数量，而不是在同一任务契约上连续增加可执行工作（Sec. 2）。RST 把参考解的增长作为改写起点，同时重写 verifier 与公开指令并复用已通过任务，在十五轮内得到 37,484 个任务、约每个通过任务 $$0.05$$ 的成本，但代价是方法依赖初始任务的可验证性、改写算子覆盖和后续去重（Sec. 4–5，Fig. 3）。

![Figure 3：从 seed 到更长、更严格任务的单轮改写](/images/blog/command-line-task-synthesis/rst/rst-round.png)

*Figure 3 原图：RST 在增加步骤和状态依赖的同时加严断言，并在 sandbox 中重新验证。*

### 3. 之前研究的做法与问题

人工编写或收集成功轨迹可以提供可靠的终端环境和测试，但论文指出单个长时域任务的成本常在数百到数千美元，难以支撑大规模训练（Sec. 1）。
从仓库、文档、模板或既有 benchmark 直接转换的流水线容易生成指令含糊、执行路径浅或测试脆弱的样本，即使脚本能运行也未必提供强学习信号（Sec. 1–2）。
只用 taxonomy 枚举技能可以扩展覆盖面，却通常缺少对环境状态、参考解、私有 verifier 和公开契约的联合校验（Sec. 2）。
弱过滤的自训练或递归生成还可能在重复采样中放大奖励误设、不可解任务和近重复样本，因此需要可执行的 oracle 与契约一致性检查（Sec. 2–3）。

### 4. 实验设计和结果

实验以 TerminalWorld 的 639 个已验证任务为 bootstrap，逐轮生成并统计产量、结构增长、契约一致性、域与算子多样性，再在各轮匹配子集上用固定推理设置评测 DeepSeek-V4-Pro 的 $$\mathrm{pass@4}$$ 和 verifier partial credit，训练效用则用 Qwen3.5-27B、Qwen3.5-122B-A10B 的 SFT 及 Qwen3.5-27B 的 PPO 检验（Sec. 5）。
从 $$R_1$$ 到 $$R_{15}$$，每 1,000 次 seed 尝试的通过任务产量保持在 498.2–572.2，候选通过率保持在 74.5%–81.5%，而中位参考解长度从 67 行增至 374 行、命令数从 40 增至 244、CLI 工具数从 17 增至 71，指令长度只从 85 增至 122 个词（Sec. 5.1，Fig. 1，Fig. 7）。
在 solver 和推理配置不变时，DeepSeek-V4-Pro 的 $$\mathrm{pass@4}$$ 从 $$R_1$$ 的 90% 单调降至 $$R_{15}$$ 的 2.5%，平均 partial credit 从 0.970 降至 0.170，说明结构增长确实转化成了更高的 agent 难度而不是单纯变长（Sec. 5.2，Fig. 12–15）。
递归仍保留广泛覆盖：$$R_{15}$$ 使用了 40 个 rewrite operator 中的 36 个，最大单一算子占比 8.0%，且与 Terminal-Bench 2、Terminal-Bench Hard 和 LHTB 的抽样任务没有匹配的 13-token 窗口（Sec. 5.3，Table 2，Fig. 18–22）。

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
局限在于论文只报告到 15 轮，$$R_{15}$$ 仍有 p95 近重复相似度 0.703，且结论主要基于 Qwen3.5、DeepSeek-V4-Pro 和现有 terminal benchmark，规模外推、跨生成模型稳定性及更强去重仍待验证（Sec. 5.3，Sec. 6）。

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

## CalibForge: Adversarial Solver Calibration for Scaling Learnable Terminal Tasks

> **论文**：[*CalibForge: Adversarial Solver Calibration for Scaling Learnable Terminal Tasks*](https://arxiv.org/abs/2608.06352v1)<br>
> **作者**：Fanzhe Meng、Guoxin Chen、Jiale Zhao、Shuang Sun、Zhiyu Lin、Wayne Xin Zhao、Ruihua Song、Ji-Rong Wen、Kai Jia<br>
> **版本**：arXiv:2608.06352v1，2026-08-06，27 页<br>
> **研究任务**：自动合成既可执行、可验证，又能为终端智能体提供有效训练信号的命令行任务。

### 1. 主要方法

论文要解决的是自动合成的终端任务常常虽然形式合法，却过于简单、过于困难或无法区分不同能力水平的 solver，因而难以形成高价值训练数据的问题（Sec. 1）。CalibForge 先由 author agent 从线索出发构造 instruction、Docker 环境、初始文件与 tests，通过 structural validation 和 self-solving 后，再用 multi-solver 或 contrastive solver 的验证结果筛选可学习区间（Sec. 2.1–2.3）。

$$
\begin{aligned}
C_{\mathrm{multi}}(\mathbf{y})
  &= \mathbf{1}\!\left[
     0 < \sum_{i=1}^{K} y_i < K
     \right], \\
C_{\mathrm{con}}(y_{\mathrm{s}},y_{\mathrm{w}})
  &= \mathbf{1}\!\left[
     y_{\mathrm{s}}=1 \land y_{\mathrm{w}}=0
     \right].
\end{aligned}
$$

当行为条件不满足时，author agent 会利用 pass/fail、步数、自评、失败诊断和完整轨迹修改任务并重新验证，最多迭代 50 轮，这使 solver 从事后评测器变成任务构造过程中的对抗性校准信号（Sec. 2.3，Fig. 2）。

![Figure 2：CalibForge 方法总览](/images/blog/command-line-task-synthesis/calibforge/calibforge-overview.png)

*Figure 2 原图：任务编写、双阶段验证与两种 adversarial solver calibration 的完整闭环。*

核心伪代码（据 Algorithm 1 压缩）：

~~~text
CALIBFORGE(clue, calibration_spec, R_max = 50)
  spec <- WIDE_SEARCH_AND_SPECIFY(clue)
  task <- CONSTRUCT_TASK(spec)
  while not VALIDATE_AND_SELF_SOLVE(task)
    task <- REPAIR(task)

  for round <- 1 ... R_max
    feedback <- PROBE_AND_VERIFY(task, calibration_spec)
    outcomes <- VERIFIED_OUTCOMES(feedback)
    if CALIBRATION_CRITERION(outcomes)
      return RETAIN(task)
    task <- REVISE(task, feedback)
    while not VALIDATE_AND_SELF_SOLVE(task)
      task <- REPAIR(task)

  return DISCARD
~~~

### 2. 与之前论文的不同或改进

已有终端任务合成方法主要从规格、能力分类、软件仓库、轨迹或技能图生成可执行任务，并用环境构建、测试和单个 solver 的可解性检查来把关，但通常不主动控制任务处于哪个模型能力区间（Sec. 4）。CalibForge 改为根据多个异构 solver 的分歧或指定 strong-pass/weak-fail 关系反复改写任务，在等量 1,300 个任务的消融中把 TB2 准确率从 No Solver 的 22.47% 和 Single Solver 的 24.34% 提高到 Multi Solver 的 29.21% 与 Contrast Solver 的 31.09%，代价是需要多次独立求解和最多 50 轮校准（Table 3，Sec. 3.4）。

![Figure 1：先前任务筛选与 CalibForge 对比](/images/blog/command-line-task-synthesis/calibforge/calibforge-comparison.png)

*Figure 1 原图：从无 solver 或单 solver 检查，转向 multi-solver 分歧与 stronger/weaker 对比校准。*

### 3. 之前研究的做法与问题

终端智能体训练依赖同时对齐 instruction、初始文件、依赖、运行时状态和 verifier 的可执行任务，任何一部分失配都会使样本失去训练价值（Sec. 4）。
规格驱动方法从种子、领域描述和命令行能力分类扩写任务，artifact 或 trajectory 驱动方法从软件环境、仓库与既有轨迹派生任务，skill 驱动方法则围绕技能或技能图组织生成（Sec. 4）。
这些路线通常把环境构建和执行验证当作主要质量门槛，但“能够构建且有人能解”并不等于任务难度合适，也无法排除所有 solver 都能轻易通过的浅层解法（Sec. 1，Sec. 2.2）。
只依赖一个 solver 的 pass/fail 还会把任务质量绑定到单一模型的盲区，难以利用不同模型暴露的互补路径与失败模式（Sec. 2.3）。
已有 behavioral feedback 更多用于动态 benchmark、curriculum 或改善 solver 自身的下一次尝试，而不是持续修改正在构造的可执行任务本身（Sec. 4）。

### 4. 实验设计和结果

DeepSeek-V4-Pro 负责 authoring，multi-solver 使用 DeepSeek-V4-Flash、GLM-5 和 Kimi K2.5，contrastive calibration 使用 DeepSeek-V4-Pro 与 DeepSeek-V4-Flash，最终收集 5,431 个任务，其中 1,263 个来自 multi-solver、4,168 个来自 contrastive calibration（Sec. 3.1）。
作者用 DeepSeek-V4-Pro 在统一 scaffold 下蒸馏通过测试的轨迹，对 Qwen3-30B-A3B-Instruct 与 Qwen3.5-35B-A3B 做 10 个 epoch 的全参数 SFT，并在去污染后评测 Terminal-Bench 2.0、731 题 SWE-bench Pro 和 Doc2Repo（Sec. 3.1，Appx. D–E）。
在 Terminal-Bench 2.0 上，两种模型分别达到 32.58% 和 47.57%，比同 backbone 下最强 baseline 的 26.22% 和 40.82% 高 6.36 与 6.75 个百分点（Table 1）。
在 SWE-bench Pro 上相对 base model 的提升分别为 27.68 与 3.03 个百分点，在 Doc2Repo 上则为 30.04 与 3.85 个百分点，表明观察到的收益可迁移到仓库级软件工程任务（Table 1）。
等量任务消融显示 Single Solver 只比 No Solver 高 1.87 个百分点，而 Multi Solver 和 Contrast Solver 分别高 6.74 与 8.62 个百分点，并且 Multi Solver 的保留轨迹数更少，因此结果不支持“收益仅来自更多轨迹”的解释（Table 3）。
Contrastive calibration 首次 probe 只有 19% 满足目标关系，经过反馈修改后最终 96% 被接受，其中 53% 在五次 probe 内完成、93% 在二十次内完成，说明它既在筛选任务，也在把原本不匹配的候选逐步推向目标区间（Fig. 8，Fig. 9）。

![Figure 8：Contrastive calibration 的初始与最终状态](/images/blog/command-line-task-synthesis/calibforge/calibration-outcomes.png)

*Figure 8 原图：初次 strong-pass/weak-fail 仅占 19%，反复修改与 re-probing 后最终接受率达到 96%。*

![Figure 9：Contrastive calibration 的累计保留曲线](/images/blog/command-line-task-synthesis/calibforge/retention-funnel.png)

*Figure 9 原图：校准预算与累计保留率之间的关系，较难候选形成明显长尾。*

### 5. 结论和启发

论文的核心结论是，相比仅验证任务能否运行或由单个 solver 解出，用相对 solver 行为定义并迭代逼近“可学习区间”能够产出更有效的终端智能体训练数据（Sec. 5）。
最值得迁移的思想是把模型失败视为可操作的构造反馈，让数据生成器根据真实轨迹定位 shortcut、歧义、脆弱测试和难度错配，而不是一次生成后只做保留或丢弃（Sec. 2.3，Appx. B）。
需要注意的是，可学习区间取决于所选 solver 集合或 strong/weak 配对，而且持续 probing 会增加显著构造成本，后续工作需要研究更便宜且能跨模型泛化的校准信号（Sec. 2.3，Fig. 9）。

## SETA: Scaling Environments for Terminal Agents

> **论文**：[*SETA: Scaling Environments for Terminal Agents*](https://arxiv.org/abs/2607.10891v1)<br>
> **作者**：Qijia Shen、Zhiqi Huang、Vamsidhar Kamanuru、Aznaur Aliev、Jay Rainton、Ahmed Awelkair、Zhichen Zeng、Jiajun Li、Shi Dong、Yueming Yuan、Boyuan Ma、Qizheng Zhang、Jiwei Fu、Yuzhen Mao、Wendong Fan、Ping Nie、Philip Torr、Bernard Ghanem、Changran Hu、Jonathan Lingjie Li、Urmish Thakker、Guohao Li<br>
> **版本**：arXiv:2607.10891v1，2026-07-12，32 页<br>
> **研究任务**：从有现实依据的来源持续构造可执行、可验证的终端环境，并根据训练模型的能力边界自适应调节任务难度与技术上下文。

### 1. 主要方法

论文解决的是终端智能体强化学习缺少大规模、真实有据、环境可执行且验证可靠的训练任务问题，因为终端任务必须同时定义交互环境、指令、解答脚本和测试逻辑（Abstract，Sec. 1）。SETA 由 SETA-Synth 和 SETA-Evol 两条流水线组成，前者把 Ask Ubuntu、Stack Overflow、Unix/Linux StackExchange、Kaggle 与 NL2Bash 等来源转成标准化 Docker 环境，后者根据训练模型的通过率选择增加难度、降低难度或改变上下文的演化算子，并在每次改写后复用统一验证（Sec. 2）。这种“来源落地 + 环境演化 + 执行验证”的组合同时扩大任务规模、控制可学习难度并保留技术多样性，因此能把数据分布推向更有强化学习信号的能力前沿（Sec. 2，Sec. 3）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/seta/seta-synth-pipeline.png" alt="Figure 1: SETA-Synth pipeline">
  <br>
  <em>Figure 1：SETA-Synth 将多种有现实依据的来源转成经过自验证和 rollout 审计的可执行终端环境。</em>
</div>

核心流程（据 Fig. 1–2、Sec. 2 压缩）：

```text
SETA(source_pool, existing_pool, training_model)
  synth_pool <- {}
  for source in source_pool:
    draft <- IDEA_AGENT(source, source_adapter, base_prompt)
    task  <- DATAPOINT_AGENT(draft)
    while not BUILD_AND_SELF_VALIDATE(task):
      task <- REPAIR(task)
    if ALL_ROLLOUTS_FAIL(task):
      if TRAJECTORY_JUDGE(task) == DESIGN_FLAW:
        discard task
      else:
        add task to synth_pool
    else:
      add task to synth_pool

  evol_pool <- {}
  for task in synth_pool ∪ existing_pool:
    r <- PASS_RATE(training_model, task)
    op <- INCREASE_DIFFICULTY if r > 0.5
          else CHANGE_CONTEXT if 0 < r <= 0.5
          else DECREASE_DIFFICULTY
    evolved <- APPLY_OPERATOR(task, op)
    if BUILD_AND_SELF_VALIDATE(evolved):
      add evolved to evol_pool

  return synth_pool ∪ evol_pool
```
{: .paper-pseudocode }

### 2. 与之前论文的不同或改进

先前终端任务路线多依赖人工 benchmark、仓库或轨迹转换、taxonomy 生成，虽然能提供可执行样本或扩大覆盖面，却通常缺少来源 grounding、统一验证和随训练模型能力变化的难度控制（Sec. 1–2）。SETA 把来源适配、Docker 环境实例化、no-op/oracle 双向测试、全失败任务的 Trajectory Judge 与按通过率选算子的环境级演化串成一条闭环，得到 4,567 个环境并以 560 个训练环境支撑 GRPO，但代价是需要多阶段 agent 生成、独立 rollout 审计和反复构建验证（Sec. 2–3）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/seta/seta-evol-pipeline.png" alt="Figure 2: SETA-Evol pipeline">
  <br>
  <em>Figure 2：SETA-Evol 根据任务通过率在增加难度、改变上下文和降低难度之间自适应选择环境级改写策略。</em>
</div>

### 3. 之前研究的做法与问题

人工编写的终端 benchmark 和基于仓库的 SWE 环境通常具有较强验证性，但规模和任务类型受限，且 GitHub issue 或 pull request 这类自然监督并不覆盖广泛的系统运维、数据处理和机器学习流程（Sec. 1–2）。
Self-Instruct、WizardLM 和 Evol-Instruct 等方法主要演化文本指令、示例或代码，不能直接保证环境状态、交互工具、测试逻辑与公开指令一致（Sec. 2）。
TermiGen、TerminalTraj 和 Endless Terminals 等终端合成路线扩大了任务或轨迹数量，但论文认为它们较少同时利用人类验证来源、可执行环境和 RL 友好的自适应难度（Sec. 2，Table 1）。
只做 Docker 构建、no-op 和 oracle 检查还可能漏掉“测试要求了指令没有说明的约定”，因为解答脚本和测试可能共享同一个隐藏假设；SETA 因此对全 rollout 失败任务增加了独立 Trajectory Judge（Sec. 2.1，Appendix）。

### 4. 实验设计和结果

SETA-Env 包含 4,567 个验证环境，其中 3,255 个由 SETA-Synth 生成、1,312 个由 SETA-Evol 演化，覆盖 14 个技术类别，并用四个模型的任务级共识通过率 $$\bar r_t=\tfrac{1}{4}\sum_m\tilde r_{t,m}$$ 描述难度分布（Sec. 2.3，Fig. 3）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/seta/seta-env-stats.png" alt="Figure 3: SETA-Env dataset statistics">
  <br>
  <em>Figure 3：SETA-Env 的类别覆盖、共识难度分布以及从 Qwen3-8B 到 GPT-5.4/Kimi-K2.5 的模型特定通过情况。</em>
</div>

作者使用 CAMEL Terminal Toolkit，在 Qwen3-8B 上以 GRPO 和动态采样训练，因计算约束从 SETA-Env 过滤并均匀采样 560 个环境，另在 DeepSeek-V4-Flash 上用同一 harness 做跨 backbone 验证（Sec. 3.1）。
主结果中，表格报告的 Qwen3-8B SETA (RL) 在 Terminal-Bench 1.0/2.0 的 8 次重复均值为 $$17.8\pm1.2\%$$ 和 $$10.7\pm1.3\%$$，论文另报告最佳单次 TB2.0 为 $$12\%$$，相对最佳 Qwen3-8B base 的 $$3.6\%$$ 约提升 3.3 倍（Table 1，Sec. 3.2）。
在不同模型族上，DeepSeek-V4-Flash 的 TB2.0 pass@1 从 $$40\%$$ 提升到 $$43.0\pm2.5\%$$，pass@5 从 $$54\%$$ 提升到 $$58\%$$；同一 Qwen3-8B 训练信号还把 CRUST-Bench、CompileBench 和 QuixBugs 的 pass@4 从 15%/6.7%/7.5% 提升到 24%/40%/15.0%（Sec. 3.2–3.3）。
SETA-Evol 的配对分析显示，降低难度后 Qwen3-8B 任务中位通过率从 6% 移到 38%，增加难度后从 83% 移到 69%，改变上下文的 553 对中有 46.1% 跨越技术类别边界，说明演化确实同时改变了难度和技术语境（Sec. 2.3，Fig. 4）。
训练曲线中平均 reward 的平滑趋势从约 0.3 上升到约 0.6，平均每轮返回字符数从接近 0 上升到约 6,500，作者据此观察到 RL 模型逐渐形成更长的、基于执行反馈的规划，而不只是立即调用命令（Sec. 3.4，Fig. 5）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/seta/seta-training-trend.png" alt="Figure 5: SETA RL training curves">
  <br>
  <em>Figure 5：SETA-Env 上的 RL 训练过程中，平均 reward 与每轮返回字符数的平滑曲线均呈上升趋势。</em>
</div>

### 5. 结论和启发

论文结论是，SETA 用来源 grounding、统一验证和模型感知的环境演化构成了可扩展的终端 RL 环境生成框架，并在 Qwen3-8B 与 DeepSeek-V4-Flash 上取得了跨模型收益（Sec. 4）。
最值得迁移的思想是把“可学习任务”定义成一组可执行契约，再让训练模型的通过率反过来决定下一步是加难、降难还是换上下文，而不是固定地把所有任务向同一方向改写。
局限在于实验只覆盖两个模型族和终端交互，训练环境还需经过基模型难度过滤，且论文没有证明更大模型、更大训练预算或 GUI/多模态环境中的扩展性（Sec. 4）。

## TMax: A simple recipe for terminal agents

> **论文**：[*TMax: A simple recipe for terminal agents*](https://arxiv.org/abs/2606.23321v1)<br>
> **作者**：Hamish Ivison、Junjie Oscar Yin、Rulin Shao、Teng Xiao、Nathan Lambert、Hannaneh Hajishirzi<br>
> **版本**：arXiv:2606.23321v1，2026-06-22，20 页<br>
> **研究任务**：低成本生成大规模、难度可控且领域均衡的终端 RL 环境，并给出可复现的开放强化学习配方来训练小参数终端智能体。

### 1. 主要方法

论文解决的是开放终端智能体研究同时缺少大规模复杂环境和稳定 RL 基线的问题，因为既有工作多集中于 bug fixing、简单命令任务或仅用 SFT 验证合成数据（Abstract，Sec. 1–2）。TMax 先从 domain、skill type、primitive skills、persona、language、task complexity、command complexity、fixture 和 verifier 九个轴分层采样任务签名，再让 Gemini-3-Pro 生成 instruction、Dockerfile、unit-test verifier 与源文件，只以 Docker 构建保证可执行性，随后用 Qwen 3.5/3 系列模型在 mini-SWE-agent harness 中进行 DPPO 训练（Sec. 3–4，Fig. 2）。这套设计用组合采样显式控制覆盖与难度，用 RL 中的零方差组过滤替代昂贵的 teacher 解题验证，并以 FP32 LM head、token masking 和大 group size 缓解训练/推理数值偏差与长时域崩塌（Sec. 3–5）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/tmax/tmax-data-pipeline.png" alt="Figure 2: TMax data pipeline">
  <br>
  <em>Figure 2：TMax 从九个结构化轴组合任务标准，再生成可执行环境并送入统一终端 harness。</em>
</div>

核心流程（据 Fig. 2、Sec. 3–4 压缩）：

```text
GENERATE_TMAX_DATA(num_tasks)
  pool <- {}
  repeat num_tasks times:
    axes <- HIERARCHICAL_SAMPLE(
      domain, skill_type, primitive_skills, persona,
      language, task_complexity, command_complexity,
      fixture, verifier)
    task <- GEMINI_3_PRO_GENERATE(COMPOSE(axes))
    if BUILD_DOCKER(task):
      add task to pool
  return pool

TRAIN_TMAX(base_model, pool)
  repeat for each RL step:
    groups <- ROLLOUT(base_model, pool, group_size = 32)
    groups <- FILTER(groups, reward_standard_deviation > 0)
    mask tokens with excessive inference/trainer divergence
    UPDATE_TOKEN_LEVEL_DPPO(groups, fp32_lm_head = true)
  return base_model
```
{: .paper-pseudocode }

### 2. 与之前论文的不同或改进

先前终端数据主要从仓库和既有任务改编，或从 taxonomy/seed 生成后再用 teacher rollout 验证，常见问题是软件工程域偏置、任务过易、环境数量有限以及生成验证成本高（Sec. 2–3）。TMax 改用九轴组合采样、persona、非文本 fixture 与五类 verifier 扩大覆盖和难度范围，并只保留单次 Docker 构建、把可解性软过滤推迟到 RL rollout 阶段，从而发布 14,600 个环境，但代价是完全依赖强生成模型且未在生成阶段逐题证明可解（Sec. 3，Table 1）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/tmax/tmax-domain-composition.png" alt="Figure 3: domain composition across terminal datasets">
  <br>
  <em>Figure 3：相比若干既有数据集集中于一两个领域，TMax 在九个终端领域上的任务占比更均衡。</em>
</div>

### 3. 之前研究的做法与问题

仓库和 issue 驱动的方法天然适合构造可执行 bug-fixing 环境，却难覆盖环境搭建、系统管理、数据科学、模型训练和从零开发等更广泛的终端工作（Sec. 2.1）。
taxonomy 或 seed 驱动方法能够脱离现有仓库合成新任务，但若不显式控制复杂度、persona、输入 artifact 和 verifier，任务容易集中在文件操作等浅层模式，或形成“几乎都能解／几乎都不能解”的双峰难度（Sec. 2.1，Sec. 3）。
多数近期终端数据工作只用 SFT 展示价值，而已有开放 RL 配方的上下文较短、数据较少，或只比初始 SFT checkpoint 提升约一个百分点，难以作为研究训练稳定性的强基线（Sec. 2.2）。
长达数十步的 sandbox 交互还放大了 inference/trainer logprob 偏差、资源争用和 rollout 超时，使普通 GRPO 在数百步后容易发生 reward collapse（Sec. 5.2）。

### 4. 实验设计和结果

实验以 14,600 个 TMax RL 环境为主数据，另从 2,200 个环境生成 16,500 条 SFT 轨迹，其中 8,000 条成功，并在 2B、4B、9B、27B 的 Qwen 3.5/3.6 及 Qwen 3 8B 上测试最多 500 步 DPPO、32 rollouts/group、8 prompts/batch 和 65,536-token 训练上下文（Sec. 3.3–4.1，Appendix A.6）。
在 Gemini-3-Flash-Preview 对每个数据集固定抽取 250 题、每题 8 次 rollout 的测试中，TMax 的 pass@1/4/8 为 42%/50%/53%，按 $$\mathrm{Balance}=\exp(-\sum_i p_i\log p_i)/N$$ 计算的 domain 与 skill-type 平衡度为 0.998 和 0.732，且与 TB2/TB-Lite 的 13-gram overlap 均为 0%（Table 1，Appendix A.3–A.4）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/tmax/tmax-pass-at-k.png" alt="Figure A1: pass-at-k difficulty curves">
  <br>
  <em>Figure A1：TMax 与 CLI-Gym 处于最难区间，而且 TMax 在增加到 8 次采样后仍保持最低 pass@8。</em>
</div>

以 Qwen 3.5 9B 为相同起点时，TMax 数据训练得到的 TB-Lite/TB2.1 为 $$57.2\pm2.5$$ 和 $$28.8\pm1.4$$，高于 TermiGen、Endless Terminals、OpenThinker-Agent、TerminalTraj、CLI-Gym 与 SWE-Smith 的对应 RL 结果（Table 2）。
在 TB2.0 的五次平均中，TMax-9B 达到 27.2%，超过论文列出的其他 10B 以下模型及若干 32B 数据配方，TMax-27B 则达到 42.7%，但这些分数使用论文自有简单 harness 与 Daytona backend，不能和 TB2.1/本地 Podman 结果混为一谈（Fig. 1，Table 8）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/tmax/tmax-terminal-bench.png" alt="Figure 1: TMax Terminal-Bench 2.0 performance">
  <br>
  <em>Figure 1：TMax 系列在 32B 以下模型的 TB2.0 参数量—性能曲线上形成新的开放配方 Pareto 前沿。</em>
</div>

泛化实验中，Qwen 3.5 9B 的 SWE-Bench Verified 从 $$44.0\pm2.0$$ 升到 $$53.5\pm0.6$$，terminal-harness 下 AIME'24/25 从 $$73.3\pm2.7$$ 升到 $$91.1\pm1.6$$，并且在 OpenHands、mini-SWE-agent 和 Terminus-2 上均至少提升约 9 分（Table 4–5）。
训练分析同时发现旧 SFT mixture 会降低 Qwen 3.5 9B 的 TB-Lite 表现，而普通 GRPO 在 300 步附近明显崩塌，DPPO、FP32 LM head 和 32-rollout group 能减轻但没有消除不稳定性（Sec. 5，Fig. 6–8）。

<div align="center">
  <img src="/images/blog/command-line-task-synthesis/tmax/tmax-dppo-vs-grpo.png" alt="Figure 7: DPPO versus GRPO training stability">
  <br>
  <em>Figure 7：DPPO 在后期仍出现下降，但相比 GRPO 限制了训练 reward collapse 的严重程度。</em>
</div>

### 5. 结论和启发

论文结论是，九轴组合式环境生成与结果奖励驱动的 DPPO 配方可以用 9B 模型取得 27.2% TB2.0，并在模型尺寸、模型族、任务和 harness 之间表现出可迁移收益（Sec. 4–6）。
最值得迁移的思想是把生成阶段的昂贵“逐题证明可解”改成便宜的环境构建门槛，再依靠训练策略的多次 rollout 和零方差过滤持续选择当前模型真正能学习的任务。
局限在于数据完全由 Gemini-3-Pro 合成且尚未证明能超越生成器能力，训练在长时域下仍不稳定、容器基础设施昂贵，并且 TMax 的最佳数字依赖较短上下文和自有简单 harness，跨论文比较必须严格对齐 benchmark 版本、sandbox backend 与推理设置（Sec. 6）。
