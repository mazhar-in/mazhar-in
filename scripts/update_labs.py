#!/usr/bin/env python3
"""
MAZHAR.IN - The Experimental Workbench Auto-Discovery & SEO Indexer
Zero-dependency Python 3 script that:
1. Scans labs/ for local experimental tool directories (ignoring '_' or '.' prefixes).
2. Loads data/graduated_products.json for flagship platforms graduated from the lab.
3. Parses metadata (<title>, <meta name="description">, <meta name="lab-category">,
   <meta name="lab-status">, <meta name="lab-hook">, <meta name="lab-tech">, <meta name="lab-tags">).
4. Generates labs/manifest.json with updated schema (status: "graduated" | "experimental", live_url, origin_story).
5. Pre-renders tactile list rows into labs/index.html across Graduated and Thematic Shelves.
6. Updates sitemap.xml with full Google SEO crawlability.
"""

import os
import re
import sys
import json
import html
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

ROOT_DIR = Path(__file__).resolve().parent.parent
LABS_DIR = ROOT_DIR / "labs"
LABS_INDEX_FILE = LABS_DIR / "index.html"
MANIFEST_FILE = LABS_DIR / "manifest.json"
GRADUATED_FILE = ROOT_DIR / "data" / "graduated_products.json"
SITEMAP_FILE = ROOT_DIR / "sitemap.xml"

# The 5 Creative Archetypes & their order
SHELVES = [
    {
        "id": "kinetic-toys",
        "num": "01 //",
        "name": "Kinetic Toys & Reflex Mechanics",
        "desc": "Interactive physics sandboxes, game loops, tactile simulations",
        "aliases": ["kinetic", "physics", "reflex", "mechanics"]
    },
    {
        "id": "calculus-machines",
        "num": "02 //",
        "name": "Calculus & Math Machines",
        "desc": "Visual accumulation engines, dynamic derivatives, geometric curiosities",
        "aliases": ["calculus", "math", "accumulation", "derivative"]
    },
    {
        "id": "eduscrolling",
        "num": "03 //",
        "name": "Eduscrolling & Micro-Feeds",
        "desc": "Vertical bite-sized feeds, card swipers, fast-paced cognitive experiments",
        "aliases": ["eduscrolling", "feed", "swipe", "scroll"]
    },
    {
        "id": "algorithmic-generators",
        "num": "04 //",
        "name": "Algorithmic Generators & Tools",
        "desc": "Combinatorial question engines, procedural builders, academic DPP engines",
        "aliases": ["algorithmic", "generator", "dpp", "combinatorial", "edtech", "utilities"]
    },
    {
        "id": "oddities",
        "num": "05 //",
        "name": "Oddities & Uncategorized",
        "desc": "Unconventional scripts, visual widgets, and random interactive sketches",
        "aliases": ["oddities", "research", "widget", "uncategorized"]
    }
]

GRADUATED_SHELF = {
    "id": "graduated",
    "num": "00 //",
    "name": "Graduated to Production",
    "desc": "Experiments that began as raw laboratory sparks and grew up into full-scale production platforms",
    "aliases": ["graduated", "production"]
}


class MetaExtractor(HTMLParser):
    """Extracts title and meta tags from an HTML file."""
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""
        self.meta_tags = {}

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta":
            name = attr_dict.get("name") or attr_dict.get("property")
            content = attr_dict.get("content", "")
            if name:
                self.meta_tags[name.lower()] = content

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def map_to_shelf(raw_category: str) -> dict:
    """Maps any raw category string to one of the 5 creative archetypes."""
    cat_lower = raw_category.lower()
    for shelf in SHELVES:
        if shelf["name"].lower() == cat_lower:
            return shelf
        for alias in shelf["aliases"]:
            if alias in cat_lower:
                return shelf
    return SHELVES[-1]  # Default to Oddities


def parse_lab_dir(lab_path: Path):
    """Parses a local lab tool directory and returns experimental tool metadata."""
    index_file = lab_path / "index.html"
    if not index_file.exists():
        return None

    slug = lab_path.name
    with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()

    parser = MetaExtractor()
    try:
        parser.feed(html_content)
    except Exception:
        pass

    # Extract clean title
    raw_title = parser.title.strip()
    if not raw_title:
        title = slug.replace("-", " ").title()
    else:
        title = re.sub(r'\s*\|\s*(Mazhar\'s Lab|The Experimental Workbench|mazhar\.in).*$', '', raw_title, flags=re.I).strip()
        if not title:
            title = raw_title

    desc = parser.meta_tags.get("description", "Interactive experimental tool and simulation.")
    raw_category = parser.meta_tags.get("lab-category", "Oddities & Uncategorized")
    shelf = map_to_shelf(raw_category)
    category = shelf["name"]

    hook = parser.meta_tags.get("lab-hook", desc)
    raw_tier = parser.meta_tags.get("lab-status", "Playground")

    # Tech stack parsing
    tech_str = parser.meta_tags.get("lab-tech", "")
    if tech_str:
        tech = [t.strip() for t in tech_str.split(",") if t.strip()]
    else:
        tech = ["Canvas", "Vanilla JS"]

    # Tags parsing
    tags_str = parser.meta_tags.get("lab-tags", "")
    if tags_str:
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    else:
        tags = [shelf["name"]]

    mtime = index_file.stat().st_mtime
    mod_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    return {
        "slug": slug,
        "title": title,
        "description": desc,
        "hook": hook,
        "category": category,
        "shelf_id": shelf["id"],
        "shelf_num": shelf["num"],
        "status": "experimental",
        "experimental_tier": raw_tier,
        "live_url": f"labs/{slug}/index.html",
        "url": f"labs/{slug}/index.html",
        "is_external": False,
        "origin_story": "",
        "tech": tech,
        "tags": tags,
        "modified": mod_date
    }


def render_workbench_row(tool: dict, shelf_index_str: str) -> str:
    """Renders a single tool as a tactile workbench list row (graduated vs experimental)."""
    is_graduated = tool.get("status") == "graduated"

    if is_graduated:
        row_cls = "workbench-row workbench-row-graduated"
        status_html = '<span class="status-badge status-graduated"><span class="pulse-dot"></span><span>🚀 Graduated to Production</span></span>'
        origin_story = tool.get("origin_story", "")
        origin_html = f'''            <div class="workbench-origin-story">
              <span class="workbench-origin-label">PROTOTYPE SPARK //</span>
              <span>{html.escape(origin_story)}</span>
            </div>''' if origin_story else ""
        action_html = f'''            <a href="{html.escape(tool['live_url'])}" target="_blank" rel="noopener noreferrer" class="workbench-run-btn btn-graduated">
              <span>Launch Live Platform</span>
              <span style="font-size: 1.1em;">&nearr;</span>
            </a>'''
        title_link = f'<a href="{html.escape(tool["live_url"])}" target="_blank" rel="noopener noreferrer">{html.escape(tool["title"])}</a>'
    else:
        row_cls = "workbench-row"
        tier = tool.get("experimental_tier", "Playground")
        tier_lower = tier.lower()
        if "machine" in tier_lower or "finished" in tier_lower:
            status_cls = "status-machine"
        elif "playground" in tier_lower:
            status_cls = "status-playground"
        elif "prototype" in tier_lower:
            status_cls = "status-prototype"
        else:
            status_cls = "status-experimental"

        status_html = f'<span class="status-badge {status_cls}"><span class="pulse-dot"></span><span>⚡ {html.escape(tier)}</span></span>'
        origin_html = ""
        action_html = f'''            <a href="{tool['slug']}/index.html" class="workbench-run-btn">
              <span>Tinker in Lab</span>
              <span style="font-size: 1.1em;">&rarr;</span>
            </a>'''
        title_link = f'<a href="{tool["slug"]}/index.html">{html.escape(tool["title"])}</a>'

    tags_attr = html.escape(", ".join(tool.get("tags", [])))
    tech_attr = html.escape(", ".join(tool.get("tech", [])))
    tech_pills_html = "".join([f'<span class="tech-pill">{html.escape(t)}</span>' for t in tool.get("tech", [])])

    return f"""        <article class="{row_cls}" data-category="{html.escape(tool['category'])}" data-status="{html.escape(tool['status'])}" data-tags="{tags_attr}" data-tech="{tech_attr}">
          <div class="workbench-row-meta">
            <span class="workbench-index">{shelf_index_str}</span>
            {status_html}
          </div>
          <div class="workbench-row-info">
            <div class="workbench-row-title-wrap">
              <h3 class="workbench-row-title">{title_link}</h3>
            </div>
            <p class="workbench-row-hook">{html.escape(tool['hook'])}</p>
{origin_html}
            <div class="workbench-row-tech">
              {tech_pills_html}
            </div>
          </div>
          <div class="workbench-row-action">
{action_html}
          </div>
        </article>"""


def update_labs():
    print("=" * 65)
    print("  MAZHAR.IN - The Experimental Workbench Indexer & SEO Sync")
    print("=" * 65)

    if not LABS_DIR.exists():
        print(f"Error: Labs directory '{LABS_DIR}' not found.")
        return

    # 1. Discover local in-lab tools
    experimental_tools = []
    for item in sorted(LABS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith(("_", ".")):
            tool_meta = parse_lab_dir(item)
            if tool_meta:
                experimental_tools.append(tool_meta)
                print(f"  [OK] In-Lab Tool: [{tool_meta['category']}] {tool_meta['title']} ({tool_meta['url']})")

    # 2. Load Graduated Flagship Products
    graduated_tools = []
    if GRADUATED_FILE.exists():
        try:
            with open(GRADUATED_FILE, "r", encoding="utf-8") as f:
                raw_grad = json.load(f)
            today_str = datetime.now().strftime("%Y-%m-%d")
            for g in raw_grad:
                item = {
                    "slug": g.get("id"),
                    "title": g.get("title"),
                    "description": g.get("hook"),
                    "hook": g.get("hook"),
                    "category": g.get("category", "EdTech Utilities & CBT"),
                    "shelf_id": "graduated",
                    "shelf_num": "00 //",
                    "status": "graduated",
                    "experimental_tier": "Production",
                    "live_url": g.get("live_url"),
                    "url": g.get("live_url"),
                    "is_external": True,
                    "origin_story": g.get("origin_story", ""),
                    "tech": g.get("tech", []),
                    "tags": g.get("tags", ["Graduated"]),
                    "modified": today_str
                }
                graduated_tools.append(item)
                print(f"  [OK] Graduated Platform: [{item['category']}] {item['title']} -> {item['live_url']}")
        except Exception as e:
            print(f"  [WARN] Failed to load graduated products: {e}")

    # Combine all tools for manifest
    all_manifest_tools = graduated_tools + experimental_tools

    # 3. Write labs/manifest.json
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(all_manifest_tools, f, indent=2)
    print(f"  [OK] Generated manifest: labs/manifest.json ({len(all_manifest_tools)} total tools: {len(graduated_tools)} graduated, {len(experimental_tools)} experimental)")

    # 4. Group into Shelves & Pre-render Shelves HTML
    shelves_html = []

    # 4a. Shelf 00: Graduated to Production (if any)
    if graduated_tools:
        grad_rows = []
        for r_idx, tool in enumerate(graduated_tools, start=1):
            coord = f"00.{r_idx:02d}"
            grad_rows.append(render_workbench_row(tool, coord))

        shelf_block = f"""    <section class="workbench-shelf" id="shelf-graduated" data-shelf="Graduated">
      <div class="shelf-header">
        <div class="shelf-title-wrap">
          <span class="shelf-num" style="color: var(--accent-emerald);">{GRADUATED_SHELF['num']}</span>
          <h2 class="shelf-name">{html.escape(GRADUATED_SHELF['name'])}</h2>
        </div>
        <p class="shelf-desc">{html.escape(GRADUATED_SHELF['desc'])}</p>
      </div>
      <div class="workbench-rows">
{chr(10).join(grad_rows)}
      </div>
    </section>"""
        shelves_html.append(shelf_block)

    # 4b. Shelves 01-05: Thematic Experimental Shelves
    for s_idx, shelf in enumerate(SHELVES, start=1):
        shelf_tools = [t for t in experimental_tools if t["shelf_id"] == shelf["id"]]
        if not shelf_tools:
            continue

        rows_html = []
        for r_idx, tool in enumerate(shelf_tools, start=1):
            coord = f"{s_idx:02d}.{r_idx:02d}"
            rows_html.append(render_workbench_row(tool, coord))

        shelf_block = f"""    <section class="workbench-shelf" id="shelf-{shelf['id']}" data-shelf="{html.escape(shelf['name'])}">
      <div class="shelf-header">
        <div class="shelf-title-wrap">
          <span class="shelf-num">{shelf['num']}</span>
          <h2 class="shelf-name">{html.escape(shelf['name'])}</h2>
        </div>
        <p class="shelf-desc">{html.escape(shelf['desc'])}</p>
      </div>
      <div class="workbench-rows">
{chr(10).join(rows_html)}
      </div>
    </section>"""
        shelves_html.append(shelf_block)

    full_workbench_html = "\n\n".join(shelves_html)

    # 5. Inject into labs/index.html
    if LABS_INDEX_FILE.exists():
        with open(LABS_INDEX_FILE, "r", encoding="utf-8") as f:
            index_content = f.read()

        pattern = r'(<!-- LABS_WORKBENCH_START -->)(.*?)(<!-- LABS_WORKBENCH_END -->)'
        if re.search(pattern, index_content, flags=re.DOTALL):
            new_index = re.sub(
                pattern,
                f'\\1\n{full_workbench_html}\n    \\3',
                index_content,
                flags=re.DOTALL
            )
            with open(LABS_INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_index)
            print("  [OK] Injected tactile workbench shelves and list rows into labs/index.html")
        else:
            print("  [WARN] <!-- LABS_WORKBENCH_START --> comment markers not found in labs/index.html")

    # 6. Generate Google SEO sitemap.xml
    base_url = "https://mazhar.in"
    today = datetime.now().strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{base_url}/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{base_url}/projects/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{base_url}/labs/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{base_url}/blog/", "priority": "0.9", "changefreq": "weekly"},
    ]

    # Blog posts
    posts_dir = ROOT_DIR / "content" / "posts"
    if posts_dir.exists():
        for p in sorted(posts_dir.glob("*.md")):
            urls.append({
                "loc": f"{base_url}/{p.stem}/",
                "priority": "0.8",
                "changefreq": "monthly"
            })

    # In-lab tools
    for tool in experimental_tools:
        urls.append({
            "loc": f"{base_url}/labs/{tool['slug']}/",
            "priority": "0.85",
            "changefreq": "monthly"
        })

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in urls:
        sitemap_lines.append(f"""  <url>
    <loc>{u['loc']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>
  </url>""")
    sitemap_lines.append('</urlset>')

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))
    print(f"  [OK] Generated comprehensive SEO sitemap: sitemap.xml ({len(urls)} URLs)")

    print("=" * 65)
    print(f"  Workbench sync complete! ({len(graduated_tools)} graduated + {len(experimental_tools)} experimental)")
    print("=" * 65)


if __name__ == "__main__":
    update_labs()
