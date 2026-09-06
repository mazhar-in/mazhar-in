#!/usr/bin/env python3
"""
MAZHAR.IN - Zero-Dependency Static Blog & Site Generator
Compiles Markdown posts with frontmatter into static HTML with KaTeX math rendering.
Runs entirely on Python 3 standard library.
"""

import os
import re
import sys
import json
import html
from pathlib import Path
from datetime import datetime

# Directory Paths
ROOT_DIR = Path(__file__).resolve().parent
POSTS_DIR = ROOT_DIR / "content" / "posts"
TEMPLATES_DIR = ROOT_DIR / "templates"
BLOG_DIR = ROOT_DIR / "blog"
INDEX_FILE = ROOT_DIR / "index.html"

POST_TEMPLATE_FILE = TEMPLATES_DIR / "post_template.html"
BLOG_INDEX_TEMPLATE_FILE = TEMPLATES_DIR / "blog_index_template.html"


def parse_frontmatter(raw_content: str):
    """
    Extracts YAML-style frontmatter between --- markers and the markdown body.
    """
    frontmatter = {}
    body = raw_content

    if raw_content.startswith("---"):
        parts = raw_content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2].strip()
            for line in raw_fm.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()

                # Handle quoted strings
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # Handle lists e.g. ["Physics", "Mechanics"]
                elif val.startswith("[") and val.endswith("]"):
                    inner = val[1:-1]
                    val = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]

                frontmatter[key] = val

    return frontmatter, body


def markdown_to_html(md_text: str) -> str:
    """
    Converts Markdown to semantic HTML while strictly shielding math ($...$, $$...$$)
    and code blocks from inadvertent regex replacement.
    """
    placeholders = {}
    p_index = 0

    # Normalize line breaks
    text = md_text.replace("\r\n", "\n").replace("\r", "\n")

    # 1. Shield Code Blocks (```lang ... ```)
    def save_code_block(match):
        nonlocal p_index
        token = f"###PROTECTED_CODE_{p_index}###"
        p_index += 1
        lang = match.group(1).strip() if match.group(1) else "text"
        code_content = html.escape(match.group(2).strip("\n"))
        placeholders[token] = f'<pre><code class="language-{lang}">{code_content}</code></pre>'
        return f"\n\n{token}\n\n"

    text = re.sub(r'```([a-zA-Z0-9_\-]*)\n(.*?)\n```', save_code_block, text, flags=re.DOTALL)

    # 2. Shield Display Math ($$ ... $$)
    def save_display_math(match):
        nonlocal p_index
        token = f"###PROTECTED_MATH_DISPLAY_{p_index}###"
        p_index += 1
        math_content = match.group(1).strip()
        placeholders[token] = f'<div class="math-block">$$\n{math_content}\n$$</div>'
        return f"\n\n{token}\n\n"

    text = re.sub(r'\$\$(.*?)\$\$', save_display_math, text, flags=re.DOTALL)

    # 3. Shield Inline Math ($ ... $)
    def save_inline_math(match):
        nonlocal p_index
        token = f"###PROTECTED_MATH_INLINE_{p_index}###"
        p_index += 1
        math_content = match.group(1)
        placeholders[token] = f"${math_content}$"
        return token

    text = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', save_inline_math, text)

    # 4. Shield Inline Code (`code`)
    def save_inline_code(match):
        nonlocal p_index
        token = f"###PROTECTED_INLINE_CODE_{p_index}###"
        p_index += 1
        code_content = html.escape(match.group(1))
        placeholders[token] = f'<code>{code_content}</code>'
        return token

    text = re.sub(r'`([^`\n]+)`', save_inline_code, text)

    def process_inline_spans(span_text: str) -> str:
        """Parses bold, italics, links, images inside blocks."""
        # Bold
        span_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', span_text)
        # Italic
        span_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', span_text)
        # Images
        span_text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width:100%; border-radius: var(--radius-md); margin: 1.5rem 0;">', span_text)
        # Links
        span_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', span_text)
        return span_text

    def render_table(tbl_lines):
        if len(tbl_lines) < 2:
            return "\n".join(tbl_lines)
        header_cols = [process_inline_spans(c.strip()) for c in tbl_lines[0].strip("|").split("|")]
        rows = tbl_lines[2:] if len(tbl_lines) > 2 else []
        html_out = ['<div style="overflow-x:auto; margin: 1.75rem 0;"><table style="width:100%; border-collapse: collapse; border: 1px solid var(--border-subtle); background: var(--bg-glass-card); border-radius: var(--radius-md);"><thead><tr style="border-bottom: 2px solid var(--border-medium); background: var(--bg-tertiary);">']
        for h in header_cols:
            html_out.append(f'<th style="padding: 0.75rem 1rem; text-align: left; font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-primary);">{h}</th>')
        html_out.append('</tr></thead><tbody>')
        for r in rows:
            if not r.strip():
                continue
            cols = [process_inline_spans(c.strip()) for c in r.strip("|").split("|")]
            html_out.append('<tr style="border-bottom: 1px solid var(--border-subtle);">')
            for c in cols:
                html_out.append(f'<td style="padding: 0.65rem 1rem; font-size: 0.9rem; color: var(--text-secondary);">{c}</td>')
            html_out.append('</tr>')
        html_out.append('</tbody></table></div>')
        return "".join(html_out)

    # Split into discrete blocks separated by double (or more) newlines
    raw_blocks = re.split(r'\n{2,}', text.strip())
    rendered_blocks = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        # If it's a standalone protected block token (code or display math)
        if block.startswith("###PROTECTED_"):
            rendered_blocks.append(block)
            continue

        lines = block.split("\n")
        first_line = lines[0].strip()

        # Headings
        if first_line.startswith("#"):
            h_match = re.match(r'^(#{1,6})\s+(.*)$', first_line)
            if h_match:
                level = len(h_match.group(1))
                h_text = process_inline_spans(h_match.group(2))
                rendered_blocks.append(f'<h{level}>{h_text}</h{level}>')
                continue

        # Horizontal Rule
        if re.match(r'^(\-{3,}|\*{3,})$', first_line):
            rendered_blocks.append('<hr style="border:0; border-top: 1px solid var(--border-subtle); margin: 2.5rem 0;">')
            continue

        # Blockquote
        if first_line.startswith(">"):
            bq_lines = []
            for l in lines:
                cleaned_l = re.sub(r'^>\s?', '', l)
                bq_lines.append(process_inline_spans(cleaned_l))
            rendered_blocks.append(f'<blockquote><p>{"<br>".join(bq_lines)}</p></blockquote>')
            continue

        # Table
        if first_line.startswith("|") and first_line.endswith("|"):
            rendered_blocks.append(render_table(lines))
            continue

        # Check if block contains list items (either purely or following intro text)
        lines = block.split("\n")
        has_ul = any(l.strip().startswith(("- ", "* ")) for l in lines)
        has_ol = any(re.match(r'^\d+\.\s+', l.strip()) for l in lines)

        if has_ul or has_ol:
            sub_chunks = []
            cur_p = []
            cur_list = []
            cur_list_type = None

            for l in lines:
                l_strip = l.strip()
                is_ul_item = l_strip.startswith(("- ", "* "))
                is_ol_item = bool(re.match(r'^\d+\.\s+', l_strip))

                if is_ul_item or is_ol_item:
                    list_type = "ul" if is_ul_item else "ol"
                    if cur_p:
                        sub_chunks.append(f'<p>{process_inline_spans("<br>".join(cur_p))}</p>')
                        cur_p = []
                    if cur_list and cur_list_type != list_type:
                        sub_chunks.append(f'<{cur_list_type}>{"".join(cur_list)}</{cur_list_type}>')
                        cur_list = []
                    cur_list_type = list_type
                    content = l_strip[2:] if is_ul_item else re.sub(r'^\d+\.\s+', '', l_strip)
                    cur_list.append(f'<li>{process_inline_spans(content)}</li>')
                else:
                    if cur_list:
                        # continuation of last list item if indented, else back to p
                        if l.startswith("  ") or l.startswith("\t"):
                            cur_list[-1] = cur_list[-1][:-5] + "<br>" + process_inline_spans(l_strip) + "</li>"
                        else:
                            sub_chunks.append(f'<{cur_list_type}>{"".join(cur_list)}</{cur_list_type}>')
                            cur_list = []
                            cur_list_type = None
                            cur_p.append(l)
                    else:
                        cur_p.append(l)

            if cur_p:
                sub_chunks.append(f'<p>{process_inline_spans("<br>".join(cur_p))}</p>')
            if cur_list:
                sub_chunks.append(f'<{cur_list_type}>{"".join(cur_list)}</{cur_list_type}>')

            rendered_blocks.append("\n".join(sub_chunks))
            continue

        # Regular Paragraph
        processed_p = process_inline_spans("<br>".join(lines))
        rendered_blocks.append(f'<p>{processed_p}</p>')

    rendered = "\n\n".join(rendered_blocks)

    # 12. Restore Protected Placeholders
    for token, original_content in placeholders.items():
        rendered = rendered.replace(token, original_content)

    return rendered


def format_display_date(date_str: str) -> str:
    """Format YYYY-MM-DD into 'August 14, 2026'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except Exception:
        return date_str


def build_site():
    print("=" * 65)
    print("  MAZHAR.IN - Static Blog & Site Compiler")
    print("=" * 65)

    if not POSTS_DIR.exists():
        print(f"Error: Posts directory '{POSTS_DIR}' not found.")
        sys.exit(1)

    BLOG_DIR.mkdir(parents=True, exist_ok=True)

    with open(POST_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        post_template = f.read()

    with open(BLOG_INDEX_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        blog_index_template = f.read()

    # Collect and compile all markdown posts
    posts = []
    for md_path in POSTS_DIR.glob("*.md"):
        with open(md_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        fm, body = parse_frontmatter(raw_content)

        slug = fm.get("slug") or md_path.stem
        title = fm.get("title", slug.replace("-", " ").title())
        date = fm.get("date", "2026-01-01")
        tags = fm.get("tags", ["Physics"])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        description = fm.get("description", "")
        reading_time = fm.get("reading_time", "5 min read")

        html_body = markdown_to_html(body)
        formatted_date = format_display_date(date)

        tags_html = " ".join([f'<span class="tag-badge">#{t}</span>' for t in tags])
        tags_comma = ", ".join(tags)

        # Substitute into post template
        post_html = post_template
        post_html = post_html.replace("{{title}}", html.escape(title))
        post_html = post_html.replace("{{slug}}", slug)
        post_html = post_html.replace("{{date}}", date)
        post_html = post_html.replace("{{date_formatted}}", formatted_date)
        post_html = post_html.replace("{{description}}", html.escape(description))
        post_html = post_html.replace("{{reading_time}}", html.escape(reading_time))
        post_html = post_html.replace("{{tags_html}}", tags_html)
        post_html = post_html.replace("{{tags_comma}}", html.escape(tags_comma))
        post_html = post_html.replace("{{content}}", html_body)

        # 1. Write to blog/<slug>.html
        post_dest = BLOG_DIR / f"{slug}.html"
        with open(post_dest, "w", encoding="utf-8") as f:
            f.write(post_html)

        # 2. Write to root /<slug>/index.html to preserve exact permalinks (e.g. /working-with-ai/)
        slug_dir = ROOT_DIR / slug
        slug_dir.mkdir(parents=True, exist_ok=True)
        with open(slug_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(post_html)

        print(f"  [OK] Compiled post: blog/{slug}.html & {slug}/index.html")

        posts.append({
            "slug": slug,
            "title": title,
            "date": date,
            "date_formatted": formatted_date,
            "tags": tags,
            "tags_html": tags_html,
            "description": description,
            "reading_time": reading_time
        })

    # Sort posts in reverse chronological order
    posts.sort(key=lambda p: p["date"], reverse=True)

    # 1. Generate blog/index.html
    articles_list_html = []
    for p in posts:
        row = f"""
      <article class="article-row" onclick="window.location.href='../{p['slug']}/index.html'" style="cursor: pointer;">
        <div class="article-meta-date">
          <span>{p['date_formatted']}</span>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{p['reading_time']}</div>
        </div>
        <div class="article-info">
          <h3><a href="../{p['slug']}/index.html">{html.escape(p['title'])}</a></h3>
          <p class="article-summary">{html.escape(p['description'])}</p>
        </div>
        <div class="article-tags-wrap">
          {p['tags_html']}
        </div>
      </article>"""
        articles_list_html.append(row)

    blog_index_html = blog_index_template.replace("{{articles_list}}", "\n".join(articles_list_html))
    with open(BLOG_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(blog_index_html)
    print("  [OK] Generated article archive: blog/index.html")

    # 2. Update Latest Articles section in index.html (if file exists)
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_content = f.read()

        # Build homepage preview rows (take top 4)
        preview_rows = []
        for p in posts[:4]:
            row = f"""
        <article class="article-row" onclick="window.location.href='{p['slug']}/index.html'" style="cursor: pointer;">
          <div class="article-meta-date">
            <span>{p['date_formatted']}</span>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{p['reading_time']}</div>
          </div>
          <div class="article-info">
            <h3><a href="{p['slug']}/index.html">{html.escape(p['title'])}</a></h3>
            <p class="article-summary">{html.escape(p['description'])}</p>
          </div>
          <div class="article-tags-wrap">
            {p['tags_html']}
          </div>
        </article>"""
            preview_rows.append(row)

        preview_markup = "\n".join(preview_rows)

        # Regex replace between <!-- LATEST_ARTICLES_START --> and <!-- LATEST_ARTICLES_END -->
        pattern = r'(<!-- LATEST_ARTICLES_START -->)(.*?)(<!-- LATEST_ARTICLES_END -->)'
        if re.search(pattern, index_content, flags=re.DOTALL):
            new_index = re.sub(
                pattern,
                f'\\1\n{preview_markup}\n      \\3',
                index_content,
                flags=re.DOTALL
            )
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_index)
            print("  [OK] Injected latest articles into index.html")

    print("=" * 65)
    print(f"  Build complete! Total articles compiled: {len(posts)}")
    print("=" * 65)


if __name__ == "__main__":
    build_site()
