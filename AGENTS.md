# Repository Instructions

本仓库是基于 Jekyll、Kramdown 和 Academic Pages 的个人学术主页。Agent 在创建或编辑博客时必须遵循以下规则。

## Blog Posts

- 博客文章存放在 `_posts/`。
- 文件名使用 `YYYY-MM-DD-english-slug.md`，例如 `2026-08-10-agent-evaluation-notes.md`。
- 除非用户明确要求，不要修改已有文章。
- 新文章至少包含 `title`、`date`、`categories` 和 `excerpt`。
- 推荐使用以下 front matter：

```yaml
---
title: "文章标题"
date: 2026-08-10 10:00:00 +0800
categories:
  - llm
tags:
  - code agent
excerpt: "显示在 Blog 列表中的简短摘要。"
toc: true
toc_label: "目录"
toc_sticky: true
read_time: true
---
```

## Math Formulas

站点通过 `_includes/footer/custom.html` 全局加载 MathJax 4，并使用 Kramdown 解析 Markdown。公式必须使用 Kramdown 兼容的分隔符。

### Inline Math

行内公式使用同一行内的双美元符号：

```markdown
策略写作 $$\pi_\theta(a \mid s)$$，其中 $$\theta$$ 是模型参数。
```

不要使用单美元符号。`$...$` 在当前配置中会原样显示，不会被 MathJax 渲染。

不要直接使用未转义的 `\(...\)`。Kramdown 会移除外层反斜杠。导入已有 Markdown 时，应将这种行内公式改为 `$$...$$`。

### Display Math

独立公式的起止 `$$` 必须分别单独占一行，并在公式块前后保留空行：

```markdown
$$
\mathcal{L}(\theta)
= -\sum_{i=1}^{N}\log p_\theta(y_i \mid x_i)
+ \lambda\lVert\theta\rVert_2^2.
$$
```

不要直接使用未转义的 `\[...\]`，因为 Kramdown 会破坏外层分隔符。

### Complex Math

多行公式使用 `aligned`，避免超长公式在窄屏幕上溢出：

```markdown
$$
\begin{aligned}
Q &= XW_Q, \\
K &= XW_K, \\
V &= XW_V, \\
\operatorname{Attention}(Q,K,V)
  &= \operatorname{softmax}\!\left(
     \frac{QK^{\mathsf T}}{\sqrt{d_k}}
     \right)V.
\end{aligned}
$$
```

矩阵和分段函数可以直接使用标准 LaTeX 环境：

```markdown
$$
A =
\begin{bmatrix}
a_{11} & a_{12} \\
a_{21} & a_{22}
\end{bmatrix},
\qquad
f(x)=
\begin{cases}
x^2, & x \ge 0, \\
-x,  & x < 0.
\end{cases}
$$
```

支持的常用命令包括 `\frac`、`\sum`、`\prod`、`\int`、`\sqrt`、`\mathbb`、`\mathcal`、`\operatorname`、`\lVert` 和 `\nabla`。

不要把需要渲染的公式放进反引号或 fenced code block；代码块中的 LaTeX 只会作为源码展示。

## Verification

添加含公式的文章后，Agent 必须：

1. 运行严格 Jekyll 构建，确认 Markdown 转换无错误。
2. 在浏览器中打开生成的文章，而不只检查源文件。
3. 确认页面生成了 `mjx-container` 元素。
4. 确认不存在 `mjx-merror` 元素。
5. 检查页面中没有残留未渲染的 `$...$`、`\(...\)` 或 `\[...\]`。
6. 对较长的公式检查桌面端和窄屏显示；必要时用 `aligned` 主动断行。

本地启动命令：

```bash
docker compose up
```

严格构建命令：

```bash
docker compose run --rm jekyll-site jekyll build \
  --strict_front_matter \
  --config _config.yml,_config_docker.yml
```
