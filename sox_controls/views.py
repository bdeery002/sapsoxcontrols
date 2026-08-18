from django.shortcuts import get_object_or_404, render
import markdown2
from .models import SoxControl, BusinessProcess, SubProcess, ProcessNarrative
from mysite.constants import TEMPLATE_REGISTRY as T

def load_workflow(request, workflow_name):
    """Returns the SVG partial for the requested workflow tab."""
    try:
        process = BusinessProcess.objects.get(slug=workflow_name)
    except BusinessProcess.DoesNotExist:
        return render(request, T["SOX_WORKFLOW_NOT_FOUND"]["path"], {"workflow_name": workflow_name})

    # Explicitly order by descending (overrides model's ascending default)
    primary = process.sub_processes.filter(is_primary_flow=True).order_by('sequence_order')
    secondary = process.sub_processes.filter(is_primary_flow=False).order_by('sequence_order')

    return render(request, T["SOX_WORKFLOW"]["path"], {
        "process": process,
        "primary_nodes": primary,
        "secondary_nodes": secondary,
    })


def index(request):
    """Main dashboard — handles full page loads and HTMX live-filtering."""
    f_sub  = request.GET.get('filter_sub', '')
    f_short = request.GET.get('filter_short', '')
    f_desc = request.GET.get('filter_desc', '')
    f_risk = request.GET.get('filter_risk', '')
    
    # Order by business process name, then by sequence_order descending
    controls = SoxControl.objects.select_related('sub_process__business_process').order_by(
        'sub_process__business_process__name', 'sequence_order'
    )

    if f_sub:
        controls = controls.filter(sub_process__name__icontains=f_sub)
    if f_short:
            controls = controls.filter(short_description__icontains=f_short)
    if f_desc:
        controls = controls.filter(control_description__icontains=f_desc)
    if f_risk:
        controls = controls.filter(risk__icontains=f_risk)

    context = {
        "controls": controls,
        "processes": BusinessProcess.objects.prefetch_related("sub_processes").all(),
    }

    if request.headers.get('HX-Request'):
        return render(request, T["SOX_ROWS"]["path"], context)

    return render(request, T["SOX_INDEX"]["path"], context)


def filter_by_process(request, process_slug):
    """Called by HTMX when a tab is clicked. Filters controls by BusinessProcess."""
    controls = SoxControl.objects.select_related(
        'sub_process__business_process'
    ).filter(sub_process__business_process__slug=process_slug).order_by('sequence_order')

    return render(request, T["SOX_ROWS"]["path"], {"controls": controls})


def filter_by_subprocess(request, subprocess_slug):
    """Called by HTMX when an SVG node is clicked. Filters controls by SubProcess."""
    controls = SoxControl.objects.select_related(
        'sub_process__business_process'
    ).filter(sub_process__slug=subprocess_slug).order_by('sequence_order')

    return render(request, T["SOX_ROWS"]["path"], {"controls": controls})

def control_detail(request, control_id):
    """Display detailed information for a single control."""
    try:
        control = SoxControl.objects.select_related('sub_process__business_process').get(
            control_id=control_id
        )
    except SoxControl.DoesNotExist:
        return render(request, T["SOX_CONTROL_NOT_FOUND"]["path"], {"control_id": control_id})
    
    context = {
        "control": control,
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, T["SOX_CONTROL_DETAIL"]["path"], context)

def process_narrative(request, slug):
    narrative = get_object_or_404(
        ProcessNarrative, slug=slug, is_published=True
    )
    content_html = markdown2.markdown(narrative.content)
    return render(request, "sox_controls/process_narrative.html", {
        "narrative": narrative,
        "content_html": content_html,
    })