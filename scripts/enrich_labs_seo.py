#!/usr/bin/env python3
"""
Enriches all tools in labs/ with:
- Full Google SEO tags (<title>, <meta description>, canonical URL)
- Open Graph tags
- Schema.org WebApplication JSON-LD
- Workbench metadata (lab-category, lab-status, lab-hook, lab-tech, lab-tags)
- Tactical floating back link to The Workbench
"""

import re
from pathlib import Path

LABS_META = {
    'projectile-motion': {
        'title': '2D Projectile Motion Vector Simulator | Mazhar\'s Lab',
        'desc': 'Interactive 2D kinematics projectile simulation with live velocity components, vector dynamics, and analytical telemetry for physics researchers.',
        'category': 'Kinetic Toys & Reflex Mechanics',
        'status': 'Finished Machine',
        'hook': '2D vector launch trajectory engine with live kinematics telemetry and real-time velocity components.',
        'tech': 'Canvas, KaTeX, Vanilla JS',
        'tags': 'Kinematics, Vectors, Mechanics, Simulation'
    },
    'vector-arena': {
        'title': 'Vector Arena: Directional Combat Engine | Mazhar\'s Lab',
        'desc': 'Directional physics arena exploring the tactile physical weight and momentum of vectors through real-time canvas combat mechanics.',
        'category': 'Kinetic Toys & Reflex Mechanics',
        'status': 'Playground',
        'hook': 'Exploring the physical weight of vectors through directional combat.',
        'tech': 'Canvas, SVG, Audio / TTS',
        'tags': 'Vectors, Game Loop, Combat, Physics'
    },
    'kineticflux': {
        'title': 'KineticFlux: The Differential Physics Engine | Mazhar\'s Lab',
        'desc': 'Tactile differential physics engine modeling vector fields, particle flux, drag dynamics, and continuous kinetic forces.',
        'category': 'Kinetic Toys & Reflex Mechanics',
        'status': 'Finished Machine',
        'hook': 'Differential physics engine exploring real-time vector fields and particle flux.',
        'tech': 'Canvas, KaTeX, Audio / TTS',
        'tags': 'Flux, Vector Fields, Differential, Physics Sandbox'
    },
    'integralforge': {
        'title': 'IntegralForge: The Accumulation Engine | Mazhar\'s Lab',
        'desc': 'Interactive calculus engine visually modeling Riemann sums, continuous area accumulation, and dynamic integral transformations.',
        'category': 'Calculus & Math Machines',
        'status': 'Playground',
        'hook': 'The accumulation engine: visual Riemann sums, area transformations, and continuous calculus.',
        'tech': 'Canvas, KaTeX, Audio / TTS',
        'tags': 'Calculus, Riemann Sums, Area Under Curve, Math Visualization'
    },
    'powercraft': {
        'title': 'PowerCraft: The Power Rule Crucible | Mazhar\'s Lab',
        'desc': 'Fast-paced differential calculus game loop and polynomial crafting engine exploring dynamic derivative reflexes.',
        'category': 'Calculus & Math Machines',
        'status': 'Living Prototype',
        'hook': 'The power rule crucible: rapid differential calculus game loop and polynomial crafting.',
        'tech': 'Canvas, KaTeX, Audio / TTS',
        'tags': 'Calculus, Derivatives, Power Rule, Math Game'
    },
    'vectoreels': {
        'title': 'VectoReels: Physics in a Scroll | Mazhar\'s Lab',
        'desc': 'Vertical bite-sized tactile feed turning fundamental vector mechanics and directionality into interactive micro-simulations.',
        'category': 'Eduscrolling & Micro-Feeds',
        'status': 'Living Prototype',
        'hook': 'Vertical kinetic micro-feed turning vector mechanics into bite-sized tactile cards.',
        'tech': 'Canvas, SVG, Tailwind, Audio / TTS',
        'tags': 'Eduscrolling, Vectors, Micro Feed, Interactive'
    },
    'eduscroll-atoms': {
        'title': 'Eduscroll: Atomic Structure Feed | Mazhar\'s Lab',
        'desc': 'High-density atomic physics card swiper feed and rapid cognitive flashcard engine with live orbital visuals.',
        'category': 'Eduscrolling & Micro-Feeds',
        'status': 'Playground',
        'hook': 'High-density atomic structure rapid swiper feed and cognitive flashcards.',
        'tech': 'Canvas, KaTeX, Tailwind, Audio / TTS',
        'tags': 'Eduscrolling, Atomic Physics, Micro Cards, Modern Physics'
    },
    'fluids-dpp-generator': {
        'title': 'Fluids Master DPP Generator & Problem Engine | Mazhar\'s Lab',
        'desc': 'Algorithmic Daily Practice Problem (DPP) generator producing randomized hydrostatic problem sets, KaTeX equations, and SVG diagrams.',
        'category': 'Algorithmic Generators & Tools',
        'status': 'Finished Machine',
        'hook': 'Master DPP & question generator with dynamic KaTeX equations and SVG hydrostatic diagrams.',
        'tech': 'SVG, KaTeX, Tailwind, JavaScript',
        'tags': 'DPP Generator, Fluid Mechanics, Hydrostatics, Algorithmic'
    },
    'combinatorial-generator': {
        'title': 'Combinatorial Question Generator Engine | Mazhar\'s Lab',
        'desc': 'Algorithmic question synthesizer using combinatorial permutation patterns and procedural parameter binding.',
        'category': 'Algorithmic Generators & Tools',
        'status': 'Playground',
        'hook': 'Interactive combinatorial question generator engine with procedural variable synthesis.',
        'tech': 'Tailwind, JavaScript, MathJax',
        'tags': 'Combinatorics, Question Generator, Procedural, Math'
    },
    'trigmaster-blitz': {
        'title': 'TrigMaster Blitz: Competitive Trigonometry Arena | Mazhar\'s Lab',
        'desc': 'Competitive trigonometry reflex arena testing angle conversions, identities, and trigonometric transformations at high speed.',
        'category': 'Oddities & Uncategorized',
        'status': 'Playground',
        'hook': 'Fast-paced competitive trigonometry arena with instant evaluation and streak scoring.',
        'tech': 'SVG, KaTeX, Tailwind, Audio / TTS',
        'tags': 'Trigonometry, Game Loop, Math Reflex, Speed Drill'
    },
    'device-workbench': {
        'title': 'Multi-Viewport Device Simulator & Layout Workbench | Mazhar\'s Lab',
        'desc': 'Tactile viewport and device simulator workbench for previewing interactive web apps across mobile, tablet, and desktop viewports.',
        'category': 'Oddities & Uncategorized',
        'status': 'Living Prototype',
        'hook': 'LockInRank layout preview & multi-viewport responsive device simulator.',
        'tech': 'SVG, Tailwind, JavaScript',
        'tags': 'Viewport, Device Simulator, Dev Tool, Responsive'
    }
}

def enrich_all_labs():
    labs_dir = Path(__file__).resolve().parent.parent / "labs"
    for slug, m in LABS_META.items():
        file_path = labs_dir / slug / "index.html"
        if not file_path.exists():
            print(f"  [MISSING] {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        meta_block = f"""  <title>{m['title']}</title>
  <meta name="description" content="{m['desc']}">
  <link rel="canonical" href="https://mazhar.in/labs/{slug}/">
  <meta name="lab-category" content="{m['category']}">
  <meta name="lab-status" content="{m['status']}">
  <meta name="lab-hook" content="{m['hook']}">
  <meta name="lab-tech" content="{m['tech']}">
  <meta name="lab-tags" content="{m['tags']}">
  <!-- Open Graph / SEO -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{m['title']}">
  <meta property="og:description" content="{m['desc']}">
  <meta property="og:url" content="https://mazhar.in/labs/{slug}/">
  <!-- Schema.org WebApplication -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "{m['title']}",
    "description": "{m['desc']}",
    "url": "https://mazhar.in/labs/{slug}/",
    "applicationCategory": "EducationalApplication",
    "author": {{
      "@type": "Person",
      "name": "Syed Mazhar Ali",
      "url": "https://mazhar.in"
    }}
  }}
  </script>"""

        # Replace existing title if present or inject after <head>
        if re.search(r'<title>.*?</title>', content, flags=re.DOTALL):
            content = re.sub(r'<title>.*?</title>', f'<title>{m["title"]}</title>', content, flags=re.DOTALL)

        # Remove previous lab meta tags
        content = re.sub(r'<meta\s+name="lab-[^"]+"[^>]*>\s*', '', content)

        # Inject meta block after <head>
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n{meta_block}\n", 1)
        elif "<HEAD>" in content:
            content = content.replace("<HEAD>", f"<HEAD>\n{meta_block}\n", 1)

        # Top floating navigation bar if not present
        nav_bar = """<div style="position: fixed; top: 12px; left: 16px; z-index: 99999; display: flex; align-items: center; gap: 8px;">
  <a href="../index.html" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.8rem; font-weight: 600; color: #00f2fe; background: rgba(10, 15, 29, 0.88); border: 1px solid rgba(0, 242, 254, 0.35); border-radius: 9999px; text-decoration: none; backdrop-filter: blur(8px); box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: all 0.2s;">
    <span>&larr; The Workbench</span>
  </a>
</div>"""
        if "WORKBENCH_NAV" not in content and "<body>" in content:
            content = content.replace("<body>", f"<body>\n<!-- WORKBENCH_NAV -->\n{nav_bar}\n", 1)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] Enriched SEO & Metadata: {slug}")

if __name__ == "__main__":
    enrich_all_labs()
