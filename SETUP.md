# mazhar.in — Static Site Architecture & Setup Guide

A high-performance, strictly static personal portfolio and technical blog for **Syed Mazhar Ali** (`mazhar.in`), Senior Physics Trainer & Education Tools Developer.

---

## Architecture Highlights
- **Strictly Static**: Pure HTML5, modern CSS custom properties (Inter + JetBrains Mono), and vanilla JavaScript.
- **Zero Build Dependencies**: Runs on standard Python 3.13 (`python build.py`) with **zero external libraries** or package installs (`no node_modules`, `no pip install`).
- **Mathematical Physics Ready**: KaTeX integrated via CDN with automatic inline (`$...$`) and block (`$$...$$`) LaTeX equation rendering.
- **Interactive Mechanics Engine**: Embedded client-side canvas simulator running real-time non-linear dynamics and vector telemetry at 60 FPS.
- **Dark & Light Mode**: Automated system preference detection with manual override persisted to `localStorage`.
- **SEO & Social**: Structured data (`Person` and `BlogPosting` JSON-LD), OpenGraph, and Twitter Cards.
- **Permalink Preservation**: Compiles both `/<slug>/index.html` (preserving original WordPress permalinks) and `/blog/<slug>.html`.

---

## Directory Structure
```
mazhar.in/
├── index.html                   # Landing page, dual-core showcase, projects, blog preview
├── build.py                     # Standalone Python 3 static site & blog compiler
├── render.yaml                  # Render Blueprint configuration for automated deployment
├── SETUP.md                     # Website setup & publishing instructions (this file)
├── README.md                    # GitHub Profile README (for github.com/mazhar-in)
├── blog/
│   ├── index.html               # Article directory
│   ├── deconstructing-rotational-dynamics.html
│   └── building-sub-second-katex-quiz-engines.html
├── content/
│   └── posts/                   # Source Markdown (.md) posts
│       ├── working-with-ai.md
│       ├── it-is-really-tough-to-write-everyday.md
│       ├── how-to-integrate-latex-to-the-website.md
│       ├── testing-latex.md
│       ├── the-first-post.md
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

This compiles your post into:
- `blog/<slug>.html`
- `<slug>/index.html` (preserving root permalinks: `https://mazhar.in/<slug>/`)
- Updates `blog/index.html`
- Injects the latest articles into `index.html`

---

## Deploying on Render via GitHub

### Step 1: Push Changes to GitHub
Commit and push changes from your local repository:
```bash
git add .
git commit -m "Update content"
git push origin main
```

### Step 2: Render Static Site Configuration
When configuring on [dashboard.render.com](https://dashboard.render.com/):
- **Service Type**: Static Site (or Blueprint using `render.yaml`)
- **Repository**: `mazhar-in/mazhar-in`
- **Branch**: `main`
- **Build Command**: `python build.py`
- **Publish Directory**: `.`

Render will automatically run `python build.py` on every `git push` and deploy your site to the global CDN in seconds.

### Step 3: Custom Domain (`mazhar.in`)
In Render **Settings** → **Custom Domains**, add `mazhar.in` and `www.mazhar.in`. Point your DNS records to the Render target host.
