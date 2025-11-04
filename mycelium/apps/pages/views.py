from django.shortcuts import render
from django.http import Http404
from pathlib import Path
import markdown


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
    markdown_dir = Path(__file__).resolve().parent / 'markdown'
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