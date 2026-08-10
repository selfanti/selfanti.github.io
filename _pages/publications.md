---
permalink: /publications/
title: "Publications"
author_profile: true
---

{% if site.publications and site.publications.size > 0 %}
{% assign publications = site.publications | sort: "date" | reverse %}
<div class="publication-list">
  {% for publication in publications %}
  <article class="publication-item">
    <div class="publication-item__year">{{ publication.date | date: "%Y" }}</div>
    <div>
      <h2><a href="{{ publication.url }}">{{ publication.title }}</a></h2>
      {% if publication.authors %}<p class="publication-item__authors">{{ publication.authors }}</p>{% endif %}
      {% if publication.venue %}<p class="publication-item__venue">{{ publication.venue }}</p>{% endif %}
      {% if publication.excerpt %}<div class="publication-item__summary">{{ publication.excerpt }}</div>{% endif %}
    </div>
  </article>
  {% endfor %}
</div>
{% else %}
<div class="empty-state">
  <p class="eyebrow">PUBLICATIONS</p>
  <h2>暂无公开发表论文</h2>
  <p>目前没有可公开展示的正式发表成果。</p>
</div>
{% endif %}
