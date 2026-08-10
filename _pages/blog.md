---
permalink: /blog/
title: "Blog"
author_profile: true
---

{% if site.posts.size > 0 %}
<div class="blog-list">
  {% for post in site.posts %}
  <article class="blog-item">
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y.%m.%d" }}</time>
    <div>
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      {% if post.excerpt %}<div class="blog-item__excerpt">{{ post.excerpt }}</div>{% endif %}
    </div>
  </article>
  {% endfor %}
</div>
{% else %}
<div class="empty-state">
  <p class="eyebrow">BLOG</p>
  <h2>暂无文章</h2>
  <p>研究笔记与阅读记录将在这里发布。</p>
</div>
{% endif %}
