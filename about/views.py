from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from mysite.constants import TEMPLATE_REGISTRY as T
from sox_controls.models import BusinessProcess


@require_http_methods(["GET"])
def about(request):
    """Render the About page."""
    processes = BusinessProcess.objects.all()
    return render(request, T["ABOUT_INDEX"]["path"], {"processes": processes})
