import csv
from io import TextIOWrapper

from django.db import models
from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from adminsortable2.admin import SortableAdminMixin

from .models import ITGCLayer, ITGCCategory, ITGCControl, ItgcNarrative


# ----
# CSV Upload Form
# ----
class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(help_text="Upload a CSV file using the template.")
    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Validate only (no database changes).",
    )


# ----
# CSV Mixin
# ----
class ModelCsvAdminMixin:
    upload_template_name = "admin/csv_upload.html"
    import_natural_key_fields = None

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta
        custom_urls = [
            path("upload-csv/", self.admin_site.admin_view(self.upload_csv),
                 name=f"{opts.app_label}_{opts.model_name}_upload_csv"),
            path("download-template/", self.admin_site.admin_view(self.download_template_view),
                 name=f"{opts.app_label}_{opts.model_name}_download_template"),
        ]
        return custom_urls + urls

    def csv_fields(self):
        return [f for f in self.model._meta.fields if not f.primary_key]

    def csv_headers(self):
        return [f.name for f in self.csv_fields()]

    def get_fk_lookup(self, field, raw_value):
        rel_model = field.remote_field.model
        raw = (raw_value or "").strip()
        if not raw:
            return None
        try:
            if hasattr(rel_model, 'code'):
                return rel_model.objects.get(code=raw.upper())
            elif hasattr(rel_model, 'name'):
                return rel_model.objects.get(name=raw)
            return rel_model.objects.get(pk=raw)
        except rel_model.DoesNotExist:
            raise ValueError(f"{rel_model.__name__} not found: '{raw}'")

    def build_instance_from_row(self, row):
        kwargs = {}
        for f in self.csv_fields():
            raw = (row.get(f.name) or "").strip()
            if f.is_relation and f.many_to_one:
                kwargs[f.name] = self.get_fk_lookup(f, raw)
            elif isinstance(f, (models.DateField, models.DateTimeField)):
                kwargs[f.name] = None if raw == "" else f.to_python(raw)
            elif isinstance(f, models.BooleanField):
                kwargs[f.name] = raw.lower() in ("true", "1", "yes", "y")
            else:
                kwargs[f.name] = None if raw == "" else f.to_python(raw)
        return self.model(**kwargs)

    def download_template_view(self, request):
        opts = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{opts.model_name}_template.csv"'
        writer = csv.writer(response)
        writer.writerow(self.csv_headers())
        return response

    def upload_csv(self, request):
        opts = self.model._meta
        if request.method == "POST":
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
                reader = csv.DictReader(csv_file)
                dry_run = form.cleaned_data["dry_run"]
                count = 0
                try:
                    with transaction.atomic():
                        for row in reader:
                            instance = self.build_instance_from_row(row)
                            instance.save()
                            count += 1
                        if dry_run:
                            transaction.set_rollback(True)
                    msg = f"Successfully {'validated' if dry_run else 'imported'} {count} rows."
                    self.message_user(request, msg, messages.SUCCESS)
                    return redirect(f"admin:{opts.app_label}_{opts.model_name}_changelist")
                except Exception as e:
                    self.message_user(request, f"Error: {e}", messages.ERROR)
        else:
            form = CsvUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "opts": opts,
            "title": f"Upload CSV for {opts.verbose_name}",
        }
        return render(request, self.upload_template_name, context)

    @admin.action(description="Export selected to CSV")
    def export_selected_as_csv(self, request, queryset):
        opts = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{opts.model_name}_export.csv"'
        writer = csv.writer(response)
        headers = self.csv_headers()
        writer.writerow(headers)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in headers])
        return response

    @admin.action(description="Download CSV Template")
    def download_csv_template(self, request, queryset):
        return self.download_template_view(request)

    @admin.action(description="Go to Upload CSV")
    def go_to_upload_csv(self, request, queryset):
        opts = self.model._meta
        return redirect(f"admin:{opts.app_label}_{opts.model_name}_upload_csv")


# ----
# Inline: ITGCCategory inside ITGCLayer
# ----
class ITGCCategoryInline(admin.TabularInline):
    model = ITGCCategory
    extra = 1
    fields = ("name", "slug", "sequence_order", "is_primary_flow")
    readonly_fields = ("slug",)
    ordering = ("sequence_order",)


# ----
# ITGCLayer Admin
# ----
@admin.register(ITGCLayer)
class ITGCLayerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug", "code")
    fields = ("name", "slug", "code", "description")
    inlines = [ITGCCategoryInline]


# ----
# ITGCCategory Admin with Drag-and-Drop
# ----
@admin.register(ITGCCategory)
class ITGCCategoryAdmin(SortableAdminMixin, ModelCsvAdminMixin, admin.ModelAdmin):
    list_display = ("name", "itgc_layer", "sequence_order", "is_primary_flow", "slug")
    list_filter = ("itgc_layer", "is_primary_flow")
    ordering = ("sequence_order",)
    readonly_fields = ("slug",)
    sortable_by = ["sequence_order"]
    actions = ["download_csv_template", "go_to_upload_csv", "export_selected_as_csv"]

    def get_queryset(self, request):
        """Display in descending order while keeping sortable2 working in background."""
        qs = super().get_queryset(request)
        return qs.order_by("-sequence_order")

    def get_fk_lookup(self, field, raw_value):
        if field.name == "itgc_layer":
            try:
                return ITGCLayer.objects.get(
                    models.Q(name__iexact=raw_value) | models.Q(slug__iexact=raw_value)
                )
            except ITGCLayer.DoesNotExist:
                raise ValueError(
                    f"ITGCLayer '{raw_value}' not found. Create it in Admin first."
                )
        return super().get_fk_lookup(field, raw_value)


# ----
# ITGCControl Admin with Drag-and-Drop
# ----
@admin.register(ITGCControl)
class ITGCControlAdmin(SortableAdminMixin, ModelCsvAdminMixin, admin.ModelAdmin):
    list_display = ("control_id", "get_layer", "itgc_category", "short_description", "control_description", "risk")
    search_fields = ("control_id", "itgc_category__name", "risk")
    list_filter = ("itgc_category__itgc_layer",)
    readonly_fields = ("control_id",)
    ordering = ("sequence_order",)
    sortable_by = ["sequence_order"]
    fieldsets = (
        ("Identification", {
            "fields": ("control_id", "itgc_category", "effective_date"),
            "description": "Core control identifiers"
        }),
        ("Control Description & Risk", {
            "fields": ("short_description", "control_description", "risk"),
        }),
        ("Control Classification", {
            "fields": ("control_type", "execution_type"),
            "description": "Is this preventative/detective and automated/manual?"
        }),
        ("Implementation & Testing", {
            "fields": ("implementation_details", "test_procedures"),
        }),
        ("Sequence & Ordering", {
            "fields": ("sequence_order",),
            "description": "Used for drag-and-drop reordering in the admin list view"
        }),
    )

    actions = ["renumber_controls", "download_csv_template", "go_to_upload_csv", "export_selected_as_csv"]

    def get_queryset(self, request):
        """Group by ITGC layer, then display in descending order."""
        qs = super().get_queryset(request)
        return qs.order_by('itgc_category__itgc_layer__name', '-sequence_order')

    def csv_fields(self):
        return [f for f in self.model._meta.fields 
                if not f.primary_key and f.name != "control_id" and f.name != "sequence_order"]

    @admin.display(description="ITGC Layer", ordering="itgc_category__itgc_layer")
    def get_layer(self, obj):
        return obj.itgc_category.itgc_layer.name

    def get_fk_lookup(self, field, raw_value):
        if field.name == "itgc_category":
            try:
                return ITGCCategory.objects.get(
                    models.Q(name__iexact=raw_value) | models.Q(slug__iexact=raw_value)
                )
            except ITGCCategory.DoesNotExist:
                raise ValueError(
                    f"ITGCCategory '{raw_value}' not found. Create it in Admin first."
                )
        return super().get_fk_lookup(field, raw_value)

    @admin.action(description="Renumber selected controls sequentially")
    def renumber_controls(self, request, queryset):
        if queryset.exists():
            count = ITGCControl.renumber_controls_for_queryset(queryset)
            self.message_user(
                request,
                f"✓ Renumbered {count} selected controls",
                messages.SUCCESS
            )
        else:
            self.message_user(request, "No controls selected.", messages.ERROR)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(ItgcNarrative)
class ItgcNarrativeAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_published", "updated_at"]
    list_filter = ["is_published", "categories__itgc_layer"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "summary", "content"]
    filter_horizontal = ["categories"]
    