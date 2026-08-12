---
title: "多教师蒸馏论文整理"
date: 2026-08-12 11:21:41 +0800
categories:
  - llm
tags:
  - knowledge distillation
  - synthetic data
  - model routing
  - PerSyn
excerpt: "论文 PerSyn 的完整阅读笔记：用查询级路由器为每条提示选择兼顾质量与可学习性的教师，把多教师数据合成改写为先路由、再生成。"
toc: true
toc_label: "目录"
toc_sticky: true
read_time: true
---

> **论文**：[*Find Your Optimal Teacher: Personalized Data Synthesis via Router-Guided Multi-Teacher Distillation*](https://arxiv.org/abs/2510.10925)  
> **作者**：Hengyuan Zhang、Shiping Yang、Xiao Liang、Chenming Shang、Yuxuan Jiang、Chaofan Tao、Jing Xiong、Hayden Kwok-Hay So、Ruobing Xie、Angel X. Chang、Ngai Wong  
> **版本**：arXiv:2510.10925v2，2026-04-13（ACL 2026 Main Conference）  
> **研究任务**：为不同学生模型按提示选择最合适的教师，低成本合成个性化指令与数学推理训练数据

## 1. 主要方法

论文解决的是多教师数据蒸馏中“最强教师不一定最适合小学生模型”且全量并行生成成本高的问题，目标是按提示为特定学生选择既可学又高质量的教师（Sec. 1–2）。PerSyn 先在少量提示上收集所有教师的并行回答，用学生对回答 token 的平均对数似然定义可学习性奖励，再与奖励模型或数学正确性给出的质量奖励按默认 $$\alpha=0.4$$ 组合，为成对教师产生偏好标签并训练 Bradley–Terry 路由器（Eq. 1–3，Sec. 2.1，Sec. 2.3）。全量阶段中，路由器先把每条提示分配给得分最高的教师，教师仅生成自己收到的提示，合并为个性化数据集后再对学生做 SFT，因此把生成量从“提示数乘教师数”降到近似“提示数”并保留样本级教师匹配（Sec. 2.2）。

$$
\begin{aligned}
&\boldsymbol{r_l}(y_i^{\mathcal{M}_n},\theta) \\
&=\frac{1}{|y_i^{\mathcal{M}_n}|}
\sum_{t=1}^{|y_i^{\mathcal{M}_n}|} \\
&\quad \log p_{\pi}\!\bigl(
y_i^{\mathcal{M}_n(t)}
\mid \\
&\qquad y_i^{\mathcal{M}_n(<t)},x_i
\bigr).
\end{aligned}
\tag{1}
$$

$$
\begin{aligned}
\boldsymbol{r}(y_i^{\mathcal{M}_n},\theta)
&=(1-\alpha)\boldsymbol{r_q}(y_i^{\mathcal{M}_n}) \\
&\quad +\alpha\boldsymbol{r_l}(y_i^{\mathcal{M}_n},\theta).
\end{aligned}
\tag{2}
$$

$$
\begin{aligned}
&\mathbb{P}(C=B\succ A\mid Z=z,X=x) \\
&\qquad =\sigma\!\left(z^\top\pi(x)\right).
\end{aligned}
\tag{3}
$$

```text
输入：提示集 X，教师集 M，学生模型 θ，少量标注子集 X_sub
对 X_sub 中每个提示 x：
  收集所有教师的并行回答
  按式 (1) 与式 (2) 计算每个回答的奖励
  将教师排序展开为成对偏好样本 K
用 Bradley–Terry 损失在 K 上训练学生专属路由器 π
对 X 中每个提示 x：
  m* <- argmax π(x)
  仅由教师 m* 生成回答
合并回答得到个性化数据集 D，并用 D 对 θ 做 SFT
```

## 2. 与之前论文的不同或改进

Strong 只用单个最强模型，Mix 随机混合强弱教师，Family-Strong 选同族强教师，CAR 按整套数据的平均质量与兼容性选一个教师，这些方法要么忽略样本差异，要么仍需先让所有教师生成全量并行回答（Sec. 1，Sec. 3.1，Table 1）。PerSyn 把选择粒度降到 query 级，并用小规模并行响应训练路由器后执行“先路由再生成”，收益是更个性化且全量合成更省算力，代价是每个学生与任务设置都要单独训练路由器，并依赖奖励模型质量（Sec. 2.2–2.3，Appendix A.2，Appendix A.6）。

<div align="center">
  <img src="/images/blog/multi-teacher-distillation/persyn/figure-1-overview.png" alt="Figure 1: Generate then Select and Route then Generate">
  <br>
  <em>Figure 1：传统 Generate then Select 与 PerSyn 的 Route then Generate 范式对比</em>
</div>

## 3. 之前研究的做法与问题

传统知识蒸馏通常让一个能力最强的大模型为全部提示生成数据，并假设教师越强、回答越好，学生就学得越好（Sec. 1，Sec. 4）。Learnability Gap 路线指出强教师的复杂回答可能偏离小学生的分布，因此用强弱教师混合数据缓解难度失配（Sec. 1，Sec. 4）。Compatibility 路线进一步用质量与学生兼容性选择单个教师，或优先选择与学生同族的强教师（Sec. 1，Sec. 3.1，Sec. 4）。这些方法的共同瓶颈是教师选择停留在数据集级而非样本级，且 Mix、CAR 一类方案必须先生成每个提示的所有候选回答，成本随教师池规模线性增长（Sec. 1–2）。

## 4. 实验设计和结果

实验包含指令微调与数学推理两种设置，前者从 Magpie-Zoo 取 50K 条训练提示并在 IFEval、TruthfulQA、LiveBench 上评测，后者构建含 15 个教师并行回答的 10K 条 PerSyn-Math，并在 GSM8K、MATH、SVAMP 上评测（Sec. 3.1，Appendix A.1）。主实验使用五个 0.5B–3B 学生、指令场景 19 个教师、数学场景 15 个教师，对比 Strong、Mix、Family-Strong、CAR，并用 LLaMA-Factory 训练、统一零样本评测而 GSM8K 为 5-shot（Sec. 3.1，Appendix A.1，Appendix A.6）。PerSyn 在 30 个“学生模型 × 基准”结果中取得 28 个最佳值，五个学生的六任务平均分均最高，其中 Qwen2.5-3B 相对 Strong 在 IFEval、TruthfulQA、SVAMP 上分别提升 8.7%、7.6%、2.9%，Llama-3.2-3B 相对 CAR 在 MATH 上提升 7.5%（Table 2，Sec. 3.2）。

<div align="center">
  <img src="/images/blog/multi-teacher-distillation/persyn/table-2-main-results.png" alt="Table 2: Main results across five student models and six benchmarks">
  <br>
  <em>Table 2：五个学生模型在六个基准上的主结果，粗体为每组最佳值</em>
</div>

在 Qwen2.5-7B、Llama-3.1-8B、Gemma-2-9B、Qwen2.5-14B 的指令微调扩展实验中，PerSyn 相对 CAR 的平均性能分别提高 3.4%、3.6%、3.1%、2.7%，说明收益没有局限在小模型或单一模型族（Fig. 3，Table 7）。消融显示去掉可学习性或质量都会退化，去掉质量的损失更明显，并且 $$\alpha$$ 从 0.1 增至 0.4 时效果上升、此后下降，因此作者默认采用 $$\alpha=0.4$$（Fig. 2，Fig. 4，Sec. 3.3）。

<div align="center">
  <img src="/images/blog/multi-teacher-distillation/persyn/figure-2-ablation.png" alt="Figure 2: Ablation of learnability and quality rewards">
  <br>
  <em>Figure 2：质量奖励与可学习性奖励的消融，二者联合最好且质量更关键</em>
</div>

路由实验显示 Qwen2.5-1.5B 路由骨干用 2.5K 个并行提示即可构造指令场景 500K 或数学场景 250K 个成对偏好样本并达到稳定 Hit@3，最终学生效果接近 Oracle，作者还报告超过 95% 的提示被分配给较小教师，但少量复杂题仍需要 Long-CoT 教师（Fig. 5–7，Sec. 3.3，Appendix A.2）。

<div align="center">
  <img src="/images/blog/multi-teacher-distillation/persyn/figure-5-router-hit3.png" alt="Figure 5: Router Hit@3 versus pairwise training data size">
  <br>
  <em>Figure 5：不同路由骨干与偏好数据规模下的 Hit@3，约 500K 对后趋于稳定</em>
</div>

## 5. 结论和启发

作者结论是，面向学生与提示联合定制教师的 PerSyn 在指令微调和数学推理中总体优于数据集级单教师或混合教师策略，同时显著减少全量并行生成（Sec. 5）。最值得迁移的思想是把昂贵的“生成后搜索”改写为“用少量昂贵样本学习决策器，再在全量数据上先决策后执行”，这可以理解为一种可能推广到模型选择、工具路由和专家调度的通用设计（Sec. 2–3）。当前证据仍局限于最高 14B 的学生以及文本指令和数学任务，代码生成、多模态、专门领域与 32B/70B 学生上的泛化尚未验证，而且每个学生与设置都需要独立路由器（Limitations，Sec. 2.3）。
