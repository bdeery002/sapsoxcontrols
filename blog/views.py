import random
import markdown2
from django.shortcuts import render, redirect, get_object_or_404
from .models import Entry, EntryProposal


def index(request):
    entries = Entry.objects.all().order_by('title')
    return render(request, "blog/index.html", {"entries": entries})


def entry(request, title):
    entry = get_object_or_404(Entry, title__iexact=title)
    html_content = markdown2.markdown(entry.content)
    return render(request, "blog/entry.html", {
        "title": entry.title,
        "content": html_content
    })


def search(request):
    query = request.GET.get('q', '').strip()

    # Direct match — redirect straight to the entry
    exact = Entry.objects.filter(title__iexact=query).first()
    if exact:
        return redirect("blog:entry", title=exact.title)

    # Substring match
    results = Entry.objects.filter(title__icontains=query)
    return render(request, "blog/search_results.html", {
        "results": results,
        "query": query
    })


def propose_edit(request, title=None):
    """Handles both new entry proposals and edit proposals for existing entries."""
    existing_entry = None
    if title:
        existing_entry = get_object_or_404(Entry, title__iexact=title)

    if request.method == "POST":
        EntryProposal.objects.create(
            entry=existing_entry,
            proposed_title=request.POST.get("title", "").strip(),
            proposed_content=request.POST.get("content", "").strip(),
            proposer_name=request.POST.get("name", "").strip(),
            proposer_email=request.POST.get("email", "").strip(),
        )
        return render(request, "blog/proposal_submitted.html")

    return render(request, "blog/propose_edit.html", {
        "entry": existing_entry,
        "title": existing_entry.title if existing_entry else "",
        "content": existing_entry.content if existing_entry else "",
    })