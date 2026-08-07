from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class ITGCLayer(models.Model):
    """IT General Controls Layer (Application, Database, OS, Network, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    code = models.CharField(
        max_length=10, 
        unique=True,
        help_text="Short code for Control IDs (e.g. 'APP', 'DB', 'OS'). "
                  "Cannot be changed once controls have been created."
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "ITGC Layer"
        verbose_name_plural = "ITGC Layers"

    def __str__(self):
        return self.name


class ITGCCategory(models.Model):
    """Categories within an ITGC Layer (Access, Change Management, Operations, etc.)"""
    itgc_layer = models.ForeignKey(
        ITGCLayer,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    sequence_order = models.PositiveIntegerField(
        default=10,
        help_text="Controls position in workflow. Use multiples of 10 (10, 20, 30) to leave room for future insertions."
    )
    is_primary_flow = models.BooleanField(
        default=True,
        help_text="Primary flow nodes appear in the connected linear workflow. "
                  "Uncheck for standalone blocks."
    )

    class Meta:
        verbose_name = "ITGC Category"
        verbose_name_plural = "ITGC Categories"
        ordering = ["sequence_order"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def reorder_for_layer(itgc_layer):
        """Reorder all categories for an ITGC layer using a two-pass approach."""
        from django.db import transaction
        
        categories = ITGCCategory.objects.filter(
            itgc_layer=itgc_layer
        ).order_by('sequence_order', 'id')
        
        with transaction.atomic():
            # First pass: assign temporary IDs (high values to avoid conflicts)
            for index, cat in enumerate(categories, start=1):
                cat.sequence_order = 10000 + index
                cat.save(update_fields=['sequence_order'])
            
            # Second pass: assign final sequence orders (10, 20, 30, ...)
            for index, cat in enumerate(categories, start=1):
                cat.sequence_order = index * 10
                cat.save(update_fields=['sequence_order'])
        
        return len(categories)

    def __str__(self):
        return f"{self.itgc_layer.name} › {self.name}"


class ITGCControl(models.Model):
    """Individual ITGC control"""
    control_id = models.CharField(max_length=50, unique=True, blank=True)
    itgc_category = models.ForeignKey(ITGCCategory, on_delete=models.PROTECT, related_name="controls")
    control_description = models.TextField()
    risk = models.TextField(help_text="Describe what could go wrong if this control fails.")
    
    CONTROL_TYPE_CHOICES = (
        ('preventative', 'Preventative'),
        ('detective', 'Detective'),
    )
    EXECUTION_TYPE_CHOICES = (
        ('automated', 'Automated'),
        ('manual', 'Manual'),
    )

    control_type = models.CharField(
        max_length=20,
        choices=CONTROL_TYPE_CHOICES,
        default='preventative',
        help_text="Preventative (prevents errors) or Detective (detects errors)"
    )
    execution_type = models.CharField(
        max_length=20,
        choices=EXECUTION_TYPE_CHOICES,
        default='automated',
        help_text="Automated (performed by system) or Manual (performed by person)"
    )
    implementation_details = models.TextField(
        blank=True,
        help_text="How the control is implemented"
    )
    test_procedures = models.TextField(
        blank=True,
        help_text="How to test that the control is working effectively"
    )
    effective_date = models.DateField()
    sequence_order = models.PositiveIntegerField(
        default=10,
        help_text="Order for renumbering. Use multiples of 10 to allow insertions."
    )

    def save(self, *args, **kwargs):
        if not self.control_id:
            prefix = self.itgc_category.itgc_layer.code.upper()
            existing_controls = ITGCControl.objects.filter(
                itgc_category__itgc_layer=self.itgc_category.itgc_layer,
                control_id__startswith=f"{prefix}-"
            ).values_list('control_id', flat=True)
            
            if existing_controls:
                numbers = []
                for control_id in existing_controls:
                    try:
                        num = int(control_id.split('-')[1])
                        numbers.append(num)
                    except (ValueError, IndexError):
                        pass
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
            
            self.control_id = f"{prefix}-{str(next_num).zfill(2)}"
        
        super().save(*args, **kwargs)

    @staticmethod
    def renumber_controls_for_queryset(queryset):
        """Renumber selected controls sequentially by ITGC layer."""
        from django.db import transaction
        from itertools import groupby
        
        queryset = queryset.order_by('itgc_category__itgc_layer__code', 'sequence_order', 'id')
        
        with transaction.atomic():
            # First pass: assign temporary IDs
            for index, control in enumerate(queryset, start=1):
                control.control_id = f"__TEMP_{control.pk}__"
                control.save(update_fields=['control_id'])
            
            # Second pass: assign final IDs, reset counter per layer
            for layer_code, group in groupby(queryset, key=lambda c: c.itgc_category.itgc_layer.code.upper()):
                for index, control in enumerate(group, start=1):
                    control.control_id = f"{layer_code}-{str(index).zfill(2)}"
                    control.save(update_fields=['control_id'])
        
        return len(queryset)

    class Meta:
        verbose_name = "ITGC Control"
        verbose_name_plural = "ITGC Controls"
        ordering = ['sequence_order']

    def __str__(self):
        return f"{self.control_id} – {self.itgc_category.name}"
