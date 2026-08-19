from django.shortcuts import render
from .models import ITGCControl, ITGCLayer, ITGCCategory, ItgcNarrative
from mysite.constants import TEMPLATE_REGISTRY as T


def load_workflow(request, workflow_name):
    """Returns the SVG partial for the requested ITGC layer tab."""
    try:
        layer = ITGCLayer.objects.get(slug=workflow_name)
    except ITGCLayer.DoesNotExist:
        return render(request, T["ITGC_WORKFLOW_NOT_FOUND"]["path"], {"workflow_name": workflow_name})

    primary = layer.categories.filter(is_primary_flow=True).order_by('sequence_order')
    secondary = layer.categories.filter(is_primary_flow=False).order_by('sequence_order')

    return render(request, T["ITGC_WORKFLOW"]["path"], {
        "layer": layer,
        "primary_nodes": primary,
        "secondary_nodes": secondary,
    })

def index(request):
    """Main ITGC dashboard — handles full page loads and HTMX live-filtering."""
    f_cat = request.GET.get('filter_cat', '')
    f_desc = request.GET.get('filter_desc', '')
    f_risk = request.GET.get('filter_risk', '')

    controls = ITGCControl.objects.select_related('itgc_category__itgc_layer').order_by(
        'itgc_category__itgc_layer__name', 'sequence_order'
    )

    if f_cat:
        controls = controls.filter(itgc_category__name__icontains=f_cat)
    if f_desc:
        controls = controls.filter(control_description__icontains=f_desc)
    if f_risk:
        controls = controls.filter(risk__icontains=f_risk)

    layers = ITGCLayer.objects.prefetch_related("categories").all()

    # Map each category to its published narrative.
    narrative_by_category = {}
    for narrative in ItgcNarrative.objects.prefetch_related(
        "categories"
    ).filter(is_published=True):
        for category in narrative.categories.all():
            narrative_by_category.setdefault(category.pk, narrative)

    # Build (layer, [(category, narrative), ...]) for the template.
    layer_categories = []
    for layer in layers:
        categories = [
            (category, narrative_by_category.get(category.pk))
            for category in layer.categories.all()
        ]
        if any(narrative for _, narrative in categories):
            layer_categories.append((layer, categories))

    context = {
        "controls": controls,
        "layers": layers,
        "layer_categories": layer_categories,
    }

    if request.headers.get('HX-Request'):
        return render(request, T["ITGC_ROWS"]["path"], context)

    return render(request, T["ITGC_INDEX"]["path"], context)


def filter_by_layer(request, layer_slug):
    """Filter controls by ITGC Layer."""
    controls = ITGCControl.objects.select_related(
        'itgc_category__itgc_layer'
    ).filter(itgc_category__itgc_layer__slug=layer_slug).order_by('sequence_order')

    return render(request, T["ITGC_ROWS"]["path"], {"controls": controls})


def filter_by_category(request, category_slug):
    """Filter controls by ITGC Category."""
    controls = ITGCControl.objects.select_related(
        'itgc_category__itgc_layer'
    ).filter(itgc_category__slug=category_slug).order_by('sequence_order')

    return render(request, T["ITGC_ROWS"]["path"], {"controls": controls})

def control_detail(request, control_id):
    """Display detailed information for a single ITGC control."""
    try:
        control = ITGCControl.objects.select_related('itgc_category__itgc_layer').get(
            control_id=control_id
        )
    except ITGCControl.DoesNotExist:
        return render(request, T["ITGC_CONTROL_NOT_FOUND"]["path"], {"control_id": control_id})
    
    context = {
        "control": control,
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, T["ITGC_CONTROL_DETAIL"]["path"], context)

def itgc_narrative(request, slug):
    try:
        narrative = ItgcNarrative.objects.prefetch_related("categories__itgc_layer").get(
            slug=slug, is_published=True
        )
    except ItgcNarrative.DoesNotExist:
        return render(request, T["ITGC_NARRATIVE_NOT_FOUND"]["path"], {"slug": slug})

    controls = ITGCControl.objects.select_related("itgc_category__itgc_layer").filter(
        itgc_category__in=narrative.categories.all()
    ).order_by("itgc_category__itgc_layer__name", "sequence_order")

    return render(request, T["ITGC_NARRATIVE"]["path"], {
        "narrative": narrative,
        "controls": controls,
    })