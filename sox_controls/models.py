from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class BusinessProcess(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    code = models.CharField(
        max_length=10, 
        unique=True,
        help_text="Short code used as the prefix for Control IDs (e.g. 'P2P', 'OTC'). "
                  "Cannot be changed once controls have been created."
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Business Process"
        verbose_name_plural = "Business Processes"

    def __str__(self):
        return self.name


class SubProcess(models.Model):
    business_process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name="sub_processes",
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
                  "Uncheck for standalone blocks like 'Vendor Rebates' or 'Intercompany'."
    )

    class Meta:
        verbose_name = "Sub Process"
        verbose_name_plural = "Sub Processes"
        ordering = ["sequence_order"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def reorder_for_business_process(business_process):
        """Reorder all subprocesses for a business process using a two-pass approach."""
        from django.db import transaction
        
        subprocesses = SubProcess.objects.filter(
            business_process=business_process
        ).order_by('sequence_order', 'id')
        
        with transaction.atomic():
            # First pass: assign temporary IDs (high values to avoid conflicts)
            for index, sp in enumerate(subprocesses, start=1):
                sp.sequence_order = 10000 + index  # Large positive temp values
                sp.save(update_fields=['sequence_order'])
            
            # Second pass: assign final sequence orders (10, 20, 30, ...)
            for index, sp in enumerate(subprocesses, start=1):
                sp.sequence_order = index * 10
                sp.save(update_fields=['sequence_order'])
        
        return len(subprocesses)

    def __str__(self):
        return f"{self.business_process.name} › {self.name}"


class SoxControl(models.Model):
    control_id = models.CharField(max_length=50, unique=True, blank=True)
    sub_process = models.ForeignKey(SubProcess, on_delete=models.PROTECT, related_name="controls")
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
            help_text="How the control is implemented in the system/process"
        )
    test_procedures = models.TextField(
        blank=True,
        help_text="How to test that the control is working effectively"
    )
    effective_date = models.DateField()
    sequence_order = models.PositiveIntegerField(
        default=10,
        help_text="Order for renumbering (drag to reorder). Use multiples of 10 to allow insertions."
    )        

    def save(self, *args, **kwargs):
        if not self.control_id:
            prefix = self.sub_process.business_process.code.upper()
            existing_controls = SoxControl.objects.filter(
                sub_process__business_process=self.sub_process.business_process,
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
        """Renumber selected controls sequentially by business process."""
        from django.db import transaction
        from itertools import groupby
        
        queryset = queryset.order_by('sub_process__business_process__code', 'sequence_order', 'id')
        
        with transaction.atomic():
            # First pass: assign temporary IDs
            for index, control in enumerate(queryset, start=1):
                control.control_id = f"__TEMP_{control.pk}__"
                control.save(update_fields=['control_id'])
            
            # Second pass: assign final IDs, reset counter per business process
            for bp_code, group in groupby(queryset, key=lambda c: c.sub_process.business_process.code.upper()):
                for index, control in enumerate(group, start=1):
                    control.control_id = f"{bp_code}-{str(index).zfill(2)}"
                    control.save(update_fields=['control_id'])
        
        return len(queryset)


    class Meta:
        verbose_name = "SOX Control"
        verbose_name_plural = "SOX Controls"
        ordering = ['sequence_order']

    def __str__(self):
        return f"{self.control_id} – {self.sub_process.name}"