from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from mysite.constants import TEMPLATE_REGISTRY as T


@require_http_methods(["GET"])
def about(request):
    """Render the About page."""
    return render(request, T["ABOUT_INDEX"]["path"])
