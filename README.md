# 王海涛个人主页

基于 [Academic Pages](https://github.com/academicpages/academicpages.github.io) 的 Jekyll 学术个人主页。

站点包含：

- 研究兴趣首页
- Publications 展示页
- Blog 展示页

## 本地运行

```bash
docker compose up
```

访问 `http://127.0.0.1:4000`。

## 添加论文

在 `_publications/` 中添加带有 YAML front matter 的 Markdown 文件。

## 添加博客

在 `_posts/` 中按 `YYYY-MM-DD-title.md` 格式添加 Markdown 文件。

## GitHub Pages

将仓库推送为 `selfanti/selfanti.github.io` 后，在仓库 Settings -> Pages 中选择从 `main` 分支发布。若使用其他仓库名，请同步修改 `_config.yml` 中的 `url`、`baseurl` 和 `repository`。
