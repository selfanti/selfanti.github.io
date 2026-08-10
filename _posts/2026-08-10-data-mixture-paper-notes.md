---
title: "数据混合论文阅读合集：UniMax、RegMix 与 Olmix"
date: 2026-08-10 10:00:00 +0800
categories:
  - llm
tags:
  - data mixture
  - pretraining
  - UniMax
  - RegMix
  - Olmix
excerpt: "三篇数据混合论文的完整阅读笔记，依次涵盖多语言采样、回归式 mixture 搜索与数据演化过程中的 mixture 复用。"
toc: true
toc_label: "目录"
toc_sticky: true
read_time: true
---

## UniMax：更公平且更有效的多语言预训练采样

> **论文**：*UniMax: Fairer and more Effective Language Sampling for Large-Scale Multilingual Pretraining*  
> **作者**：Hyung Won Chung、Noah Constant、Xavier Garcia、Adam Roberts、Yi Tay、Sharan Narang、Orhan Firat  
> **版本**：arXiv:2304.09151v1，2023-04-18，ICLR 2023，19 页  
> **研究任务**：在固定预训练预算下，为数据量高度不均衡的多种语言分配采样概率，同时兼顾高资源语言覆盖、低资源语言学习和重复数据导致的过拟合风险

### 1. 主要方法

论文解决多语言预训练中的语言平衡问题，即英语等高资源语言数据多出数个数量级，而简单增加低资源语言采样率又会造成大量重复与过拟合（Sec. 1）。UniMax 给定总字符预算 C 和每种语言最多重复轮数 N，按语料字符数从小到大遍历语言，将当前语言预算设为剩余预算均分值与 N·c_l 的较小者，最后归一化得到采样分布，并用对应分布单独训练 SentencePiece 词表（Sec. 3，Algorithm 1）。这种近似 water-filling 的分配一方面给数据充足的语言接近均匀的预算，另一方面显式封顶尾部语言的重复次数，因此可能同时减轻低资源语言欠采样与高温采样的记忆、浪费和规模化过拟合问题（Sec. 1，Sec. 3）。

### 2. 与之前论文的不同或改进

先前主流温度采样使用 q_l ∝ p_l^(1/τ) 把语料分布压平，但单个 τ 无法保证在平衡高、中资源语言的同时避免尾部语言被重复数十至上百轮，而完全均匀采样同样没有重复上限（Sec. 1–3）。UniMax 把间接调温改成“尽量均匀但每种语言最多 N 轮”的显式约束，因而在 1.2B 到 13B 参数范围内获得更稳定的下游收益，代价是分布依赖训练预算 C 与上限 N，并需要可靠的逐语言语料规模统计（Sec. 3–5）。

![Figure 1b：温度采样与 UniMax 的语言采样分布](/images/blog/data-mixture/unimax/figure-1b-sampling-distribution.png)

*Figure 1b 原图（方法对比）*

### 3. 之前研究的做法与问题

按原始语料比例采样或使用较低温度会让高资源语言主导训练，使低资源语言获得的更新不足并形成明显的 held-out loss 差距（Sec. 1，Sec. 5.1）。提高温度可以增加尾部语言权重，但在 mT5 式万亿 token 预算下，最低资源语言可能被重复超过 100 轮，从而增加过拟合、敏感内容记忆和无效训练循环（Sec. 1）。双层优化、可微数据选择或梯度对齐方法能动态调整语言权重，却需要验证效用或跨语言梯度信息，扩展到约百种语言和大型模型时计算与实现成本较高（Sec. 2）。既有消融多停留在 10 亿参数以下、较短训练或英语中心的机器翻译设置，因此容易低估数据重复在更大模型和更长训练中的危害（Sec. 2，Sec. 5.1）。

### 4. 实验设计和结果

实验使用提高语言识别阈值后过滤的 mC4，覆盖 101 种语言与 6 种拉丁转写变体，为每种采样策略训练独立的 256K SentencePiece 词表，并以 mT5 式 encoder-decoder、span corruption、250K 步和 1/8 字符预算训练 Large 1.2B、XL 3.7B、XXL 13B 模型，对比 τ = 1、τ = 3.33 与 UniMax，主要评测 TyDi QA GoldP 和 WMT21，另测 XNLI、XQuAD、MLQA 与 PAWS-X（Sec. 4）。训练曲线观察到 τ = 3.33 的 Yoruba loss 随模型放大而出现越来越明显的反弹，并在 1M 步长训练中约 300K 步后连 Large 模型也开始过拟合，而 UniMax 缩小英语与 Yoruba 的 loss 差距且未呈现同类趋势（Sec. 5.1，Fig. 2–3）。TyDi QA 平均 EM/F1 在 Large、XL、XXL 上分别为 83.3、83.9、84.4，高于 τ = 3.33 的 82.0、83.4、84.0 和 τ = 1 的 80.1、81.7、82.2（Fig. 4，Table 7）。WMT21 上 UniMax 在三个模型规模的平均 chrF 均最高且多数语言方向受益，在 Large 的 1/2 字符预算消融中也以 83.1 超过 τ = 3.33 的 82.8 和 τ = 1 的 81.2，而 N = 1/5/10 的 TyDi QA 为 82.2/81.5/81.8，显示禁止重复略优但差异较小（Sec. 5.2–5.3，Fig. 6，Table 2）。使用 UniMax 训练万亿 token 的 umT5 在多数规模与任务上优于 mT5，例如 XXL 的 XNLI 为 87.8 对 87.1、XQuAD 为 77.9/88.2 对 71.3/85.2、TyDi QA 为 81.2/89.7 对 79.5/88.7，但 PAWS-X 略低为 91.2 对 91.5（Sec. 6，Table 3）。作者因训练不稳定而省略 umT5-Large，且最终 umT5 同时改变了采样、语料日期和过滤规则，不过单独刷新 mC4 在 XNLI 上仅带来 0.1 分提升，而完整方案相对 mT5 提升 1.0 分，这支持采样是主要贡献但不能完全排除其他变化（Sec. 6，Appendix E，Table 6）。

![Figure 2b：高温采样下过拟合随模型规模加剧](/images/blog/data-mixture/unimax/figure-2b-temperature-overfitting.png)

*Figure 2b 原图（τ = 3.33 的 held-out loss）*

![Figure 4a：TyDi QA 随模型规模变化](/images/blog/data-mixture/unimax/figure-4a-tydi-scaling.png)

*Figure 4a 原图（UniMax 在三档规模均领先）*

![Figure 6 左：WMT21 平均 chrF 随模型规模变化](/images/blog/data-mixture/unimax/figure-6-left-wmt-scaling.png)

*Figure 6 左图原图（WMT21 主结果）*

### 5. 结论和启发

论文结论是带重复上限的近均匀采样比标准温度采样更适合大规模多语言预训练，其优势在多项任务和最高 13B 参数规模上仍然存在（Sec. 7）。最值得迁移的思想是把“公平覆盖”写成受资源上限约束的预算分配问题，让低资源数据的保护条件成为算法硬约束而不是通过温度间接调节。局限在于研究只验证了 mT5 式 encoder-decoder 与单语 CommonCrawl 数据，尚需测试 decoder-only、parallel data 和语言专属参数架构，同时公平分配单位也可能应从“每种语言相等”转向兼顾说话人口的 demographic utility（Sec. 7，Appendix B）。

---

## RegMix：把预训练数据配比转化为回归问题

> **论文**：*RegMix: Data Mixture as Regression for Language Model Pre-training*  
> **作者**：Qian Liu、Xiaosen Zheng、Niklas Muennighoff、Guangtao Zeng、Longxu Dou、Tianyu Pang、Jing Jiang、Min Lin  
> **版本**：arXiv:2407.01492v2，2025-01-23，ICLR 2025，36 页  
> **研究任务**：在多个预训练数据域之间自动分配采样比例，以较低的搜索成本找到能改善大模型验证损失和下游表现的数据混合方案

### 1. 主要方法

论文解决大语言模型预训练中的域级数据配比问题，即面对近乎无限的混合比例组合，如何在正式大规模训练前低成本找到高表现方案（Sec. 1）。RegMix 先从围绕原始数据分布构造的 Dirichlet 分布中采样多组 mixture 并短程训练大量超小代理模型，再把域权重向量作为输入、目标域验证损失等指标作为标签拟合 ridge 或 LightGBM 回归器，随后在百万级未训练 mixture 上快速预测并平均排名前 100 的方案，最后用该配比训练大模型（Sec. 3，Algorithm 1）。这一设计可能有效，是因为不同 mixture 的相对排名在模型规模和 token 预算变化时近似稳定，而回归器还能联合建模难以凭单域权重或人工直觉解释的跨域交互（Sec. 1，Sec. 3–5）。

![Figure 3：RegMix 从代理模型训练、回归拟合、mixture 模拟到大模型训练的完整流程](/images/blog/data-mixture/regmix/figure-3-method-overview.png)

*Figure 3 原图（方法流程）*

### 2. 与之前论文的不同或改进

最相关的先前方法如 DoReMi、DoGE 和在线数据混合通常依靠一个代理或最终模型进行较长训练并根据训练动态估计或持续调整域权重，数据 scaling-law 路线则尝试预设可解释的损失函数形式来外推 mixture 效果（Sec. 1–2）。RegMix 把它们改成许多可并行的短程 1M 代理实验加通用回归搜索，主实验的 mixture 搜索 FLOPs 为 3.5 × 10¹⁸、约为 DoReMi 的十分之一，但代价是依赖排名不变性、已知域标签、代理与大模型使用相同 tokenizer 等经验假设（Table 4，Sec. 6）。

![Figure 2：少量 token 的小模型排名被迁移到更多 token 的大模型](/images/blog/data-mixture/regmix/figure-2-rank-overview.png)

*Figure 2 原图（RegMix 的跨尺度预测路线）*

### 3. 之前研究的做法与问题

人工 mixture 通常依据“Wikipedia 等高质量数据应被上采样”的直觉设权重，但随着域数量、数据规模和目标任务增加，这种方案难以扩展且可能错过反直觉的域间互补（Sec. 1，Sec. 5.4）。Token-level 和 sample-level 方法能更细粒度地过滤训练数据，却常依赖启发式、perplexity、梯度或额外模型评分，并不直接给出可执行的域级预算分配（Sec. 2）。学习式 group-level 方法可离线估计固定权重或在线动态调权，但长程代理训练的成本会随正式预训练 token 数增长，作者还指出部分方法存在不稳定性（Sec. 1–2，Appendix G）。数据 scaling-law 方法试图用解析函数连接单域比例与损失，而论文日志显示多数域并无简单的 log-log 线性关系，完整 mixture 的交互可能超出这种低维假设（Sec. 5.5，Fig. 8）。这些路线还普遍假定样本所属域已知、各域数据近似无限并且代理与目标模型共享 tokenizer，因此在域边界模糊、数据重复受限或 tokenizer 改变时都缺少直接保证（Sec. 6）。

### 4. 实验设计和结果

主实验使用 Pile 中 17 个可用且无版权争议的域，以 512 × 1M 参数模型各训练 1B tokens 来拟合 ridge 与 LightGBM，并在未见过的 1M、60M 和 64 × 1B 参数模型 mixture 上测试，其中 1B 模型各训练 25B tokens，下游主表覆盖 14 项 0-shot 到 5-shot 任务并以 accuracy 或 normalized accuracy 评测（Sec. 4–5，Appendix C）。LightGBM 对未见 mixture 的 Spearman ρ 在 1M、60M、1B 设置分别为 98.45、98.64、97.12，明显高于线性回归的 90.08、89.26、88.01，附录中跨 1M、60M、280M、1B 与不同 token 预算的两两相关系数也保持在 0.94–0.99，这些观察支持但不能证明排名不变性（Table 2，Fig. 15）。

![Figure 15：不同模型规模与 token 预算下的 mixture 排名相关性](/images/blog/data-mixture/regmix/figure-15-rank-heatmap.png)

*Figure 15 原图（Spearman 排名相关热图）*

在 64 个不同 mixture 的 1B 模型中，仅改变数据配比就让单项下游分数最多相差 14.6 分，出现在 Lambada，逐任务最优模型相对最差模型的平均差为 4.2 分，而 RegMix 预测的 mixture 在这 64 个候选方案中取得最低验证损失（Table 3，Fig. 2）。主下游比较中 RegMix 平均分为 47.3，高于 Human 的 45.1、DoReMi 的 46.8 和 Pile-CC-only 的 46.8，并在 14 项任务中的 7 项最优，不过 DoReMi 与 ODM 的公开权重被重归一化到可用的 17 个域，作者承认这可能使它们低于原始条件下的表现（Table 4）。64 个 1B 模型的相关性分析显示 Pile-CC 验证损失与多数下游任务最相关而 Wikipedia 并非最强指标，HellaSwag 与 Pile-CC 的相关系数接近 1，且超过 85% 的 C4 URL 域与 Pile-CC 呈很强相关，但这些结果只是相关性而不是因果证据（Sec. 5.2，Fig. 5）。

![Figure 5(a)：不同 Pile 域验证损失与下游任务表现的相关性](/images/blog/data-mixture/regmix/figure-5a-domain-task.png)

*Figure 5(a) 原图（Pile-CC 行呈现最广泛的强相关）*

v2 附录进一步报告 7B 模型训练 100B tokens 时 RegMix 在 13 项任务的平均分为 56.5、Human 为 54.5，使用 512 × 1M 代理得到的 mixture 与使用 128 × 1B 代理得到的 mixture 平均分几乎相同，同时在 100 个 FineWeb URL 域实验中 LightGBM 对 1M 和 60M 未见 mixture 的 ρ 分别达到 99.53 与 98.80（Table 5，Table 10–11）。

![Figure 1：7B 模型在 25B 到 100B training tokens 下的 RegMix 与 Human 对比](/images/blog/data-mixture/regmix/figure-1-7b.png)

*Figure 1 PDF 页面原图裁剪（保留坐标轴、图例和图注）*

### 5. 结论和启发

论文的核心结论是数据 mixture 可以被视为一个可学习的性能响应面，许多廉价且多样的代理实验足以筛出比人工方案更好的大模型预训练配比，并在本文设置中显著降低自动搜索成本（Sec. 7）。最值得迁移的思想是，当昂贵配置在不同规模间保持相对排序时，应优先并行采集覆盖广的廉价探针来学习 surrogate 或 ranking，再把完整预算集中到少量高排名候选，而不是要求代理训练复刻最终训练全程。局限在于该方法仍是经验性的并依赖排名不变性、明确域边界、相同 tokenizer 与近似无限域数据，v2 主文局限段仍称只验证到 1B 而修订附录已经加入 7B 结果，说明更广泛的 70B 规模、跨 tokenizer、未知域和数据重复约束仍需系统验证（Sec. 6，Appendix I）。

---

## Olmix：贯穿语言模型开发周期的数据混合框架

> **论文**：*Olmix: A Framework for Data Mixing Throughout LM Development*  
> **作者**：Mayee F. Chen、Tyler Murray、David Heineman、Matt Jordan、Hannaneh Hajishirzi、Christopher Ré、Luca Soldaini、Kyle Lo  
> **版本**：arXiv:2602.12237v1，2026-02-12，58 页  
> **研究任务**：在训练数据域不断增删、修订和拆分的真实 LM 开发过程中，可靠地选择数据混合比例，并降低每次域更新后重新搜索混合比例的计算成本

### 1. 主要方法

论文解决数据混合在真实 LM 开发中的两个问题，即离线混合方法的 proxy、swarm、回归和优化配置缺乏共识，以及数据域持续演化时每次从头重算 mixture 的成本不断累积（Sec. 1）。Olmix 先用七项实证研究确定 Olmix Base 的配置，再提出 Mixture Reuse，把未受更新影响的域按旧比例聚合成一个 virtual domain，只重新估计其总权重和受影响域权重，Partial Mixture Reuse 还可选择性重算部分未受影响域（Sec. 3–4，Algorithm 1–2）。前一部分提高 proxy surrogate 与目标模型表现的一致性，后一部分把搜索维度从 m′ 降为 1 加集合 D_comp 的元素数，且理论上性能差距由旧比例偏离新最优比例的 reuse gap 与两组域对相同任务的 coupling 共同控制（Sec. 3.3–4.4，Theorem 1–2）。

![Figure 1：数据域演化与反复重算 mixture 的 LM 开发周期](/images/blog/data-mixture/olmix/figure-1-development-cycle.png)

*Figure 1 原图（问题与整体流程）*

### 2. 与之前论文的不同或改进

最相关的离线方法通常训练多个静态 mixture 的小型 proxy models、拟合 mixture 到性能的回归函数并优化预测性能，但其设计选择常缺乏统一依据且默认域集合固定，在线方法则在一次最终训练中动态调权而不是处理训练前的数据版本演化（Sec. 2–3.1）。Olmix 一方面给出可直接执行的离线配置清单，另一方面用 Full 和 Partial Mixture Reuse 冻结旧域的相对比例并只在低维空间重算，因此可覆盖 add、remove、partition、revise 更新并显著节省 proxy runs，代价是复用失效风险取决于 reuse gap 与 coupling，Partial Reuse 还需要判断哪些旧域应重新计算（Sec. 4，Fig. 9）。

![Figure 9：全量重算、Partial Reuse 与 Full Reuse](/images/blog/data-mixture/olmix/figure-9-recomputation-strategies.png)

*Figure 9 原图（先前全量重算到本文复用策略）*

### 3. 之前研究的做法与问题

实践中常通过人工调权或穷举训练来选择 web、code、PDF 等域的比例，这可能消耗数千 GPU 小时且难以随数据版本快速迭代（Sec. 1）。函数拟合式离线方法虽然降低成本，却在 proxy 大小、swarm 数量与分布、回归模型、目标粒度及求解器上各自采用不同配置，好的回归拟合也不保证 proxy 到目标模型的迁移表现（Sec. 2–3）。这些方法通常假设数据无限且域集合固定，因此可能提出需要过度重复小域数据的不可执行 mixture，也无法经济地应对数据添加、删除、拆分或修订（Sec. 1–4）。动态或 embedding-based 方法能在训练中调权或为新增域估权，但前者处理的是单次训练内部变化，后者主要针对添加新域，并未统一覆盖多种更新操作或解释何时历史 mixture 可以安全复用（Sec. 2）。

### 4. 实验设计和结果

配置研究将 DCLM 划为 24 个 topic domains，用 Olmo 2 架构训练 1B decoder-only target models 至 100B tokens，并以 52 个 math、code 和 QA 任务的平均 BPB 为指标，同时训练不同大小、mixture 与数量的 proxy swarms（Sec. 3.3，Appendix D）。研究观察到至少 15M 参数的 proxy 与 1B target 的排名相关性超过 0.89，最终采用 30M proxy、K ≥ 3(m + 1)、topic-level sparse 与 source-level dense swarm、per-task log-linear regression、优化阶段的 repetition constraints，以及带 λ = 0.05 KL 正则的精确求解器（Sec. 3.3，Fig. 3–8，Table 2–4）。主实验让初始 24 个 DCLM 域经历五次 add、revise、remove 和 partition 更新后达到 64 个域，在 1B 模型、100B tokens、三个 swarm seeds、k = 4 与 R = 1T 下比较 Natural、Full Recomputation、Swarm Reuse、Full Mixture Reuse 和 Partial Mixture Reuse（Sec. 5.1，Table 5）。Full Mixture Reuse 用 216 次 proxy runs 获得相对 Natural 的 11.6% 提升，达到 Full Recomputation 832 次 runs 和 12.2% 提升的 95%，Partial Mixture Reuse 则以 272 次 runs 达到 12.0% 提升和 98% 的全量重算收益（Sec. 5.1，Fig. 10）。最佳 Partial Reuse mixture 在约 20K steps 达到 Natural 约 61K steps 的最终 BPB，数据效率提高 3.05×，而在更受数据约束的 R = 6T 设置下 Full Reuse 以 216 对 832 次 runs 获得 6.94% 对 6.97% 的提升（Sec. 5.1，Fig. 11，Appendix D，Fig. 24）。实验还观察到 reuse gap、1 − ρ* 与实际性能差距同步变化，针对高 coupling 的 software development 域进行 Partial Reuse 可缩小差距，并且 Full Reuse 在 add、remove、partition 的性能与 mixture 距离上均更接近全量重算，revise 后的 mixture TV distance 仅 0.21%，这些结果支持理论界在所测设置中的解释力（Sec. 5.2，Fig. 13–17，Appendix D，Fig. 26）。

![Figure 4：不同域数量下的 swarm sample complexity](/images/blog/data-mixture/olmix/figure-4-swarm-size.png)

*Figure 4 原图（K = O(m)，约 3(m + 1) 后误差接近零）*

![Figure 10：域持续演化时的性能提升与 proxy 成本](/images/blog/data-mixture/olmix/figure-10-cost-performance.png)

*Figure 10 原图（Mixture Reuse 的主成本收益）*

![Figure 11：Partial Mixture Reuse 的训练数据效率](/images/blog/data-mixture/olmix/figure-11-data-efficiency.png)

*Figure 11 原图（达到相同性能所需 steps 减少 3.05×）*

### 5. 结论和启发

论文结论是数据混合不应被视为最终预训练前的一次性决策，经过实证配置的离线混合器与历史 mixture 复用可以在数据持续演化时接近全量重算的性能并显著降低探索成本（Sec. 6）。最值得迁移的思想是把局部数据更新对应为局部优化维度，并用 reuse gap 与任务 coupling 判断哪些历史参数可以冻结、哪些需要重新估计。局限在于研究只覆盖 offline schema，理论依赖 log-linear 性能模型，Partial Reuse 的重算域选择仍需人工领域知识，而且主要结论尚待更大模型规模及 online mixing 方法验证（Sec. 6）。
