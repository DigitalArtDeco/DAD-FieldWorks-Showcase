"""Render the current public Markdown notes as styled static HTML.

Requires the existing markdown-it-py development dependency. No browser or
runtime JavaScript is added. Historical source records are not rewritten.
"""
import html
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = {
    "current_public_status.md": ("Product scope", "The current DAD FieldWorks development scope, result views and exchange limits."),
    "claim_boundaries.md": ("Technical boundaries", "How to interpret the application views, material assumptions and development claims."),
    "company_screenshot_provenance.md": ("Image provenance", "The five supplied application images, their crops and their technical context."),
    "publication_notes.md": ("Website publication", "Public assets and the existing static website publication route.")
}

def slug(text):
    return re.sub(r"[^\w -]", "", text.lower()).replace(" ", "-")

def rewrite_link(href):
    parts = urlsplit(href)
    if not parts.scheme and not href.startswith("//"):
        if parts.path in PAGES:
            parts = parts._replace(path=parts.path.replace(".md", ".html"))
        elif parts.path == "README.md":
            parts = parts._replace(path="index.html")
        elif parts.path == "../docs/README.md":
            parts = parts._replace(path="index.html")
    return urlunsplit(parts)

def shell(title, description, body, header, footer, filename):
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)} | DigitalArtDeco Labs</title>
    <meta name="description" content="{html.escape(description, quote=True)}">
    <link rel="canonical" href="https://www.dadlabs.de/docs/{filename}">
    <link rel="stylesheet" href="../styles.css">
    <link rel="icon" href="../favicon.ico?v=field-sculpture" sizes="16x16 32x32 48x48 64x64">
  </head>
  <body class="company-site">
{header}
    <main id="main-content" class="docs-page">
{body}
    </main>
{footer}
  </body>
</html>
'''

def main():
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    header = re.search(r'    <a class="skip-link"[\s\S]*?</header>', home).group()
    header = header.replace('href="index.html"', 'href="../index.html"')
    header = header.replace('src="assets/', 'src="../assets/')
    header = re.sub(r'href="#(?!main-content)([^"]+)"', r'href="../index.html#\1"', header)
    footer = re.search(r'    <footer>[\s\S]*?</footer>', home).group()
    footer = footer.replace('href="impressum.html"', 'href="../impressum.html"').replace('href="datenschutz.html"', 'href="../datenschutz.html"')
    footer = footer.replace('href="docs/index.html"', 'href="index.html"')
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    for source, (label, description) in PAGES.items():
        tokens = md.parse((DOCS / source).read_text(encoding="utf-8"))
        title = tokens[1].content
        tokens = tokens[3:]
        toc = []
        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                heading = tokens[i+1].content
                anchor = slug(heading)
                token.attrSet("id", anchor)
                if token.tag == "h2":
                    toc.append(f'<a href="#{anchor}">{html.escape(heading)}</a>')
            if token.children:
                for child in token.children:
                    if child.type == "link_open":
                        child.attrSet("href", rewrite_link(child.attrGet("href")))
        content = md.renderer.render(tokens, md.options, {})
        filename = source.replace(".md", ".html")
        body = f'''      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Company</a><span aria-hidden="true">/</span><a href="index.html">Documentation</a><span aria-hidden="true">/</span><span>{label}</span></nav>
      <div class="docs-heading"><p class="eyebrow">DAD FieldWorks · Technical notes</p><h1>{html.escape(title)}</h1><p class="lead">{description}</p></div>
      <div class="docs-layout">
        <aside class="docs-sidebar"><details open><summary>On this page</summary><nav aria-label="On this page">{''.join(toc)}</nav></details><a class="docs-back" href="index.html">All documentation</a></aside>
        <article class="document-content">{content}
          <p class="source-link"><a href="{source}">Read the Markdown source</a></p>
        </article>
      </div>'''
        (DOCS / filename).write_text(shell(title, description, body, header, footer, filename), encoding="utf-8")
    cards = ''.join(f'<a class="doc-card" href="{name.replace(".md",".html")}"><h2>{label}</h2><p>{desc}</p><span>Read notes <span aria-hidden="true">↗</span></span></a>' for name,(label,desc) in PAGES.items())
    index = (DOCS / "README.md").read_text(encoding="utf-8")
    history = index.split("## Historical visual records", 1)[1]
    history = history.split("\nThe public notes",1)[0]
    history_html = md.render(history)
    body = f'''      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Company</a><span aria-hidden="true">/</span><span>Documentation</span></nav>
      <div class="docs-heading"><p class="eyebrow">DAD FieldWorks</p><h1>Product documentation.</h1><p class="lead">Technical context for the application, its current scope and the images on this website.</p></div>
      <div class="doc-card-grid">{cards}</div>
      <section class="docs-archive" id="historical-visual-records"><h2>Historical source documents</h2><p>Earlier publication records are retained in their original Markdown form. These source files describe earlier website states, not the current product presentation.</p><details><summary>Browse the dated source archive</summary>{history_html}</details></section>
      <p class="detail-link"><a href="evidence_contract_architecture.md">Architecture background (Markdown source)</a> · <a href="https://github.com/DigitalArtDeco/DAD-FieldWorks-Showcase">Public website repository</a></p>'''
    (DOCS / "index.html").write_text(shell("Product documentation", "Technical product notes and current application image provenance from DigitalArtDeco Labs.", body, header, footer, "index.html"), encoding="utf-8")
    print(f"Rendered {len(PAGES)+1} static documentation pages.")

if __name__ == "__main__":
    main()
