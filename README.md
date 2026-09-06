# mazhar.in — Static Personal Website & Blog

A high-performance, strictly static personal portfolio and technical blog for **Syed Mazhar Ali** (`mazhar.in`), Senior Physics Trainer & Education Tools Developer.

## Architecture Highlights
- **Strictly Static**: Pure HTML5, modern CSS custom properties (Inter + JetBrains Mono), and vanilla JavaScript.
- **Zero Build Dependencies**: Runs on standard Python 3.13 (`python build.py`) with **zero external libraries** or package installs (`no node_modules`, `no pip install`).
- **Mathematical Physics Ready**: KaTeX integrated via CDN with automatic inline (`$...$`) and block (`$$...$$`) LaTeX equation rendering.
- **Interactive Mechanics Engine**: Embedded client-side canvas simulator running real-time non-linear dynamics and vector telemetry.
- **Dark & Light Mode**: Automated system preference detection with manual override persisted to `localStorage`.
- **SEO & Social**: Structured data (`Person` and `BlogPosting` JSON-LD), OpenGraph, and Twitter Cards.

---

## Directory Structure
```
mazhar.in/
├── index.html                   # Landing page, dual-core showcase, projects, blog preview
├── build.py                     # Standalone Python 3 static site & blog compiler
├── blog/
│   ├── index.html               # Article directory
│   ├── deconstructing-rotational-dynamics.html
│   └── building-sub-second-katex-quiz-engines.html
├── content/
│   └── posts/                   # Source Markdown (.md) posts
│       ├── deconstructing-rotational-dynamics.md
│       └── building-sub-second-katex-quiz-engines.md
├── templates/
│   ├── post_template.html       # Single blog post template with KaTeX CDN
│   └── blog_index_template.html # Article archive layout
└── assets/
    ├── css/
    │   └── style.css            # Complete design system & custom properties
    └── js/
        ├── main.js              # Theme manager, mobile navigation, code copying
        └── physics-sim.js       # Live HTML5 canvas physics simulation
```

---

## Publishing New Blog Posts

1. Create a new markdown file in `content/posts/<slug>.md`.
2. Include YAML frontmatter at the top:
```markdown
---
title: "Your Article Title"
date: "2026-09-10"
tags: ["Physics", "Electrodynamics", "JEE Advanced"]
description: "Brief summary of the article for previews and meta tags."
slug: "your-article-slug"
reading_time: "6 min read"
---

Your markdown content here with inline math like $E = mc^2$ and block equations:

$$
\oint \vec{B} \cdot d\vec{\ell} = \mu_0 I_{\text{enc}}
$$
```

3. Run the static compiler:
```bash
python build.py
```

This compiles your post into `blog/<slug>.html`, regenerates `blog/index.html`, and updates the Latest Articles section on the homepage (`index.html`).
