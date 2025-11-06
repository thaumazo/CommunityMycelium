from django.shortcuts import render
from django.http import Http404
from pathlib import Path
import markdown
from django.conf import settings


def markdown_page(request, slug):
    markdown_dir = Path(__file__).resolve().parent / 'markdown'
    markdown_file = markdown_dir / f"{slug}.md"

    if not markdown_file.exists():
        raise Http404("Page not found")

    with open(markdown_file, 'r', encoding='utf-8') as file:
        md_content = file.read()

    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

    context = {
        'content': html_content,
        # Add dynamic context variables here, e.g., 'projects': Project.objects.all()
    }

    return render(request, 'pages/page.html', context)


def public_markdown_page(request, slug):
    # Check for URL_OVERRIDE in settings
    domain = settings.URL_OVERRIDE if settings.URL_OVERRIDE else request.get_host().split(':')[0].lower()

    # Set the default domain
    if domain not in ['metachrysalis.org', 'example.com', 'fraserlowland.org']:  # Add other allowed domains here
        domain = 'metachrysalis.org'

    # Construct the path to the markdown file based on the domain
    markdown_dir = Path(__file__).resolve().parent / 'markdown' / domain
    markdown_file = markdown_dir / f"{slug}.md"

    if not markdown_file.exists():
        raise Http404("Page not found")

    with open(markdown_file, 'r', encoding='utf-8') as file:
        md_content = file.read()

    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

    context = {
        'content': html_content,
    }

    return render(request, 'pages/page.html', context)