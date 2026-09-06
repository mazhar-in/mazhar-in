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

This compiles your post into `blog/<slug>.html`, regenerates `<slug>/index.html` (preserving root permalinks), `blog/index.html`, and updates the Latest Articles section on the homepage (`index.html`).

---

## Deploying on Render via GitHub

### Step 1: Create a GitHub Repository & Push
1. Create a new repository on your GitHub account: [github.com/new](https://github.com/new) (e.g. named `mazhar-in` or `mazhar.in`).
2. Add the remote and push the `main` branch from your local terminal:
```bash
git remote add origin https://github.com/mazhar-in/<YOUR_REPO_NAME>.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Log in to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** → **Static Site**.
3. Connect your GitHub repository (`mazhar-in/<YOUR_REPO_NAME>`).
4. Configure the build settings (or Render will automatically detect `render.yaml`):
   - **Name**: `mazhar-in`
   - **Branch**: `main`
   - **Build Command**: `python build.py`
   - **Publish Directory**: `.`
5. Click **Create Static Site**. Render will run `python build.py` and deploy your site to an `onrender.com` URL within seconds.

### Step 3: Add Custom Domain (`mazhar.in`)
1. In your Render Static Site dashboard, go to **Settings** → **Custom Domains**.
2. Add `mazhar.in` and `www.mazhar.in`.
3. Update your DNS records (at your domain registrar or Cloudflare) with the CNAME / ALIAS records provided by Render. Render will automatically issue free, renewing SSL certificates!
