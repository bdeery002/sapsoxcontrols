from django.core.management.base import BaseCommand
from django.template.loader import get_template, TemplateDoesNotExist
from mysite.constants import TEMPLATE_REGISTRY

class Command(BaseCommand):
    help = 'Verifies templates and shows their full metadata mapping'

    def handle(self, *args, **kwargs):
            # 1. Define the header FIRST
            header = f"{'STATUS':<8} | {'TEMPLATE FILE':<45} | {'ROLE':<10} | {'VIEW':<30} | {'MODELS':<25} | {'HTMX TARGET'}"
            
            # 2. Now you can use the length of the header
            sep = "=" * len(header)
            
            self.stdout.write(sep)
            self.stdout.write(header)
            self.stdout.write(sep)

            passed = 0
            failed = 0

            for name, info in TEMPLATE_REGISTRY.items():
                path = info.get("path")
                role = info.get("role", "N/A")
                view = info.get("view", "N/A")
                models = info.get("models", "N/A")
                htmx_target = info.get("htmx_target", "N/A")
                
                try:
                    get_template(path)
                    # 3. Ensure the spacing in the f-string matches the header widths EXACTLY
                    self.stdout.write(self.style.SUCCESS(
                        f"{'✅ PASS':<8} | {path:<45} | {role:<10} | {view:<30} | {models:<25} | {htmx_target}"
                    ))
                    passed += 1
                except TemplateDoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"{'❌ FAIL':<8} | {path:<45} | {role:<10} |  {view:<30} | {models:<25} | {htmx_target} (NOT FOUND)"
                    ))
                    failed += 1

            self.stdout.write(sep)
            self.stdout.write(f"SUMMARY: {passed} passed, {failed} failed")
            self.stdout.write(sep)