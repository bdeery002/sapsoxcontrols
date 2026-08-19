import re

from django.core.management.base import BaseCommand
from django.db import transaction

from itgc.models import ITGCCategory, ItgcNarrative


NARRATIVES = [
    {
        "title": "IT General Controls — Access Management",
        "slug": "itgc-access-management",
        "summary": (
            "How access to SAP systems, databases, and infrastructure is requested, "
            "approved, reviewed, and removed in a typical SAP-centric environment."
        ),
        "category_keywords": ["access"],
        "content": """## Overview

Access management controls govern how users obtain, change, and lose access to SAP systems, and how their activity is monitored. Effective access management applies across the entire technology stack: the application layer, the database layer, the operating system layer, and the network/identity layer.

## Typical process

1. **Identity origination.** Worker status changes — such as hiring, transfer, or termination — are captured in the authoritative HR or identity system. This system acts as the trigger for access provisioning and de-provisioning.
2. **Access request and approval.** A user or manager requests access through a documented workflow. The request is routed to role owners, line managers, and security or control reviewers for approval before roles are assigned.
3. **Role assignment and SoD review.** SAP roles and authorizations are assigned based on least privilege and job responsibilities. Segregation-of-duties (SoD) conflicts are identified and either resolved or covered by a mitigating control.
4. **Privileged and emergency access.** Elevated access is granted only when needed, for a limited time, and with documented justification. Emergency access (for example, SAP GRC Firefighter IDs) is logged and reviewed after use.
5. **Periodic access reviews.** Management reviews user access at regular intervals to confirm that privileges remain appropriate and that terminated or transferred users have been removed.
6. **De-provisioning.** When a user terminates or changes roles, access is disabled or removed within a defined timeframe, and any shared or privileged credentials are rotated if necessary.

## What could go wrong

- Unauthorized users obtain access to SAP systems or sensitive transactions.
- Users retain excessive privileges that enable fraud, error, or circumvention of business-process controls.
- SoD conflicts are not detected or mitigated.
- Privileged or emergency access is granted without approval or review.
- Terminated users retain access because de-provisioning is delayed or incomplete.
- Password policies are weak or inconsistent across layers.

## Typical control points

- Approved access requests with role-owner and security sign-off.
- Automated or manual SoD analysis before role assignment.
- Periodic user access reviews by process owners and IT security.
- Privileged access reviews and firefighter log reviews.
- Password and authentication parameters aligned with corporate policy.
- Timely de-provisioning and account lockdown procedures.
- Audit logging of administrative and sensitive user activity (for example, SAP HANA audit policies, SAP Security Audit Log, table logging, and OS audit logs).
""",
    },
    {
        "title": "IT General Controls — Change Management",
        "slug": "itgc-change-management",
        "summary": (
            "How configuration, code, and infrastructure changes are authorized, tested, "
            "and promoted through an SAP landscape in a controlled manner."
        ),
        "category_keywords": ["change"],
        "content": """## Overview

Change management controls ensure that changes to SAP configuration, code, and infrastructure are authorized, tested, and implemented in a controlled manner. In SAP environments, changes are typically moved through a multi-tier landscape (development, quality assurance, and production) using the SAP transport system, while non-transportable changes follow a separate emergency procedure.

## Typical process

1. **Change request and classification.** A change is logged in the change management system, classified by risk and urgency (planned, emergency, or standard), and linked to a business justification.
2. **Development and testing.** Developers create the change in the development environment and unit-test it. Business or IT analysts perform functional testing in a quality assurance environment.
3. **Approval.** The change is reviewed and approved by a change control board or authorized approver before it is moved to production.
4. **Transport and promotion.** Approved changes are imported into production by authorized personnel only. Transport routes are configured so that changes cannot bypass the QA environment.
5. **Production client protection.** The production client is locked for direct changes. When a non-transportable change must be made directly, a controlled exception process is followed (opening production temporarily, making the change, then immediately closing it), and all activity is logged.
6. **Segregation of duties.** Individuals who develop or configure changes are generally not the same individuals who approve or import them into production.
7. **Post-implementation review.** Standard or emergency changes may be reviewed after implementation to confirm they were appropriate and properly documented.

## What could go wrong

- Changes are moved to production without approval or testing.
- Developers can directly modify production, bypassing the transport workflow.
- Emergency changes are not documented or reviewed.
- Segregation between development and deployment is weak.
- Non-transportable changes are made without a controlled exception process.
- Transport logs and approvals are not retained.

## Typical control points

- Change request tickets with evidence of testing and approval.
- Change control board minutes or electronic approval records.
- Transport route configuration and import logs (for example, SAP TMS history).
- Production client lock settings and change logs (for example, SCC4 change logs).
- Firefighter or emergency access logs for non-transportable changes.
- Segregation of duties between development, testing, and deployment roles.
- Periodic review of changes for appropriateness.
""",
    },
    {
        "title": "IT General Controls — Computer Operations",
        "slug": "itgc-computer-operations",
        "summary": (
            "How SAP batch processing, backup and recovery, system monitoring, and "
            "log retention are typically managed to support reliable operations."
        ),
        "category_keywords": ["operation", "operations"],
        "content": """## Overview

Computer operations controls ensure that SAP systems operate reliably, that data is backed up and recoverable, and that operational issues are detected and resolved in a timely manner. These controls cover batch processing, backup and recovery, system monitoring, and log retention.

## Typical process

1. **Batch job management.** Critical recurring jobs (for example, period-end close, payment file generation, exchange rate updates, and user lock synchronization) are scheduled, documented, and assigned priorities. Job failures generate alerts or tickets for investigation.
2. **Monitoring.** Operational dashboards or system monitoring tools track job completion, system availability, and error conditions. Alerts are routed to the responsible team.
3. **Incident and remediation.** Failed jobs or system events are investigated, documented, and resolved. Root causes and resolutions are recorded for high-priority failures.
4. **Backup and recovery.** Backups are scheduled and retained according to policy. Recovery procedures are documented and tested periodically to verify that critical data can be restored.
5. **Log retention.** System, security, and batch logs are retained for a period sufficient to support audit and investigation requirements.

## What could go wrong

- Critical batch jobs fail without detection or timely remediation.
- Backups are incomplete or untested, leading to inability to restore data.
- System outages or errors are not monitored or escalated.
- Logs are retained for too short a period to support audits or forensic reviews.
- Security events (for example, unauthorized access attempts) are not logged or reviewed.

## Typical control points

- Batch job scheduling and monitoring (for example, SAP Solution Manager or native SAP job management).
- Job failure alerts and service desk tickets with documented root cause.
- Backup schedules and restore-test results.
- System and security log retention (for example, SAP Security Audit Log, SAP HANA audit logs, OS logs).
- Periodic review of backup and recovery plans.
""",
    },
]


class Command(BaseCommand):
    help = "Load or update the baseline ITGC narrative content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the plan without creating or updating records.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing narrative content and category links.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        for spec in NARRATIVES:
            categories = self._find_categories(spec["category_keywords"])

            if not categories:
                self.stdout.write(
                    self.style.WARNING(
                        f"No categories matched for '{spec['title']}' — narrative will have no linked controls."
                    )
                )

            if dry_run:
                self.stdout.write(
                    f"Would create/update '{spec['title']}' "
                    f"with {len(categories)} matched categorie(s)."
                )
                for cat in categories:
                    self.stdout.write(f"  - {cat}")
                continue

            narrative, created = ItgcNarrative.objects.get_or_create(
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "content": spec["content"],
                    "is_published": True,
                },
            )

            if created or force:
                narrative.title = spec["title"]
                narrative.summary = spec["summary"]
                narrative.content = spec["content"]
                narrative.is_published = True
                narrative.save()
                narrative.categories.set(categories)
                action = "created" if created else "updated"
            else:
                action = "skipped"

            self.stdout.write(
                self.style.SUCCESS(
                    f"{action}: {narrative.title} ({narrative.categories.count()} categories)"
                )
            )

    def _find_categories(self, keywords):
        """Return categories whose names match any of the provided keywords (case-insensitive)."""
        categories = ITGCCategory.objects.all()
        matched = set()
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            for cat in categories:
                if pattern.search(cat.name) and cat not in matched:
                    matched.add(cat)
        return sorted(matched, key=lambda c: (c.itgc_layer.name, c.name))
