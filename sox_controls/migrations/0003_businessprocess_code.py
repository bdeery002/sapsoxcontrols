from django.db import migrations, models

def set_default_codes(apps, schema_editor):
    BusinessProcess = apps.get_model('sox_controls', 'BusinessProcess')
    codes = {
        'procure-to-pay': 'P2P',
        'order-to-cash': 'OTC',
    }
    for bp in BusinessProcess.objects.all():
        bp.code = codes.get(bp.slug, bp.slug.upper()[:10])
        bp.save()

class Migration(migrations.Migration):
    dependencies = [
        ('sox_controls', '0002_alter_soxcontrol_control_id'),
    ]
    operations = [
        migrations.AddField(
            model_name='businessprocess',
            name='code',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.RunPython(set_default_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='businessprocess',
            name='code',
            field=models.CharField(
                max_length=10,
                unique=True,
                help_text="Short code used as the prefix for Control IDs (e.g. 'P2P', 'OTC'). Cannot be changed once controls have been created."
            ),
        ),
    ]
