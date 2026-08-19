import sys
from django.core.management.base import BaseCommand
from itgc.models import ITGCLayer, ITGCCategory, ItgcNarrative


NARRATIVES = [
    {
        "title": "Application — Access to Programs and Data",
        "slug": "itgc-application-access-to-programs-and-data",
        "layer": "Application",
        "category": "access-to-programs-and-data",
        "content": """## Application — Access to Programs and Data

### Purpose
This narrative describes the generic controls that govern how users access SAP application functions and the financial data they process. It covers the full user lifecycle — from initial provisioning through periodic review and termination — and the hardening settings that protect the application layer.

### How application access works
Users are authenticated before they can access the SAP application layer. In most environments, Single Sign-On (SSO) is the primary mechanism, binding SAP user accounts to the corporate identity provider or directory service. Fallback password authentication is retained for a small number of exceptions, such as emergency accounts, technical users, and administrators who cannot use SSO.

Access is granted through a role-based security model. Business functions are mapped to authorization roles in the SAP system, and users receive only the roles required for their job responsibilities. Privileged roles are tightly controlled.

### Authentication
- SSO is configured as the default path for standard business users.
- Local password authentication is limited to administrators, emergency users, and technical interfaces.
- Password parameters are enforced at the application layer, including minimum length, complexity, history, expiration, account lockout, and idle timeout.
- Standard default accounts are locked in production, and their initial passwords are changed.

### Provisioning
- Access requests are initiated through a formal workflow, typically a governance tool such as SAP Access Control or an approved IT service-management ticket.
- Requests are evaluated for Segregation of Duties (SoD) conflicts before provisioning.
- Management or role owners approve the specific access before it is granted.
- Emergency access is granted through a controlled break-glass process with documented justification and logging.

### Periodic reviews
- Management performs periodic reviews of sensitive or privileged access.
- Reviews focus on high-risk capabilities rather than raw technical role names, so reviewers can certify whether access is appropriate for each user’s job function.
- Inappropriate, excessive, or dormant access is removed and the remediation is documented.

### Termination and de-provisioning
- The HR system of record drives user termination.
- When the primary identity account is disabled, downstream SAP access is automatically locked or expired through interfaces or batch processes.
- Any residual access is manually remediated within a defined service-level window.

### Application hardening
- The production client is locked to prevent direct configuration changes.
- Repository and global settings are configured as not modifiable in production.
- Powerful baseline profiles are not assigned to standard business users.
- All transactions enforce authorization checks.

### Why this matters
Weaknesses at the application access layer can allow unauthorized transactions, SoD violations, data leakage, or fraud. These controls provide the foundation on which business-process controls rely.
""",
    },
    {
        "title": "Application — Change Management",
        "slug": "itgc-application-change-management",
        "layer": "Application",
        "category": "change-management",
        "content": """## Application — Change Management

### Purpose
This narrative describes the generic change-management process for the SAP application layer. It explains how program and configuration changes are requested, tested, approved, and moved into production while maintaining Segregation of Duties and preserving audit evidence.

### Change landscape
SAP changes typically move through a multi-tier landscape: Development, Quality Assurance, and Production. Transport routes are configured so that changes must pass through QA before they can reach Production; direct promotion to Production is blocked.

### Change request and traceability
- A change request is created in the enterprise change-management tool or SAP Change Request Management.
- The request documents the change description, business justification, risk assessment, and related transport identifiers.
- SAP transport requests are cross-referenced to the change ticket so that every production import can be traced back to an approved request.

### Testing
- Changes are tested in a non-production environment before they are approved for production.
- Functional and user-acceptance testing evidence is attached to the change record.
- Unsuccessful test results are resolved before the change is approved.

### Approval and deployment
- Production imports require formal management approval, typically through a Change Control Board or delegated approver.
- Approval is documented before the transport is imported.
- Production imports are executed by authorized personnel who are separate from the developers who created the change.

### Production lockdown
- The production client is set to prevent direct changes to client-specific objects.
- Global system change options are set to not modifiable.
- Any temporary opening of the production client is logged, approved, and immediately restored.

### Emergency changes
- True emergencies follow a shortened but documented path.
- Changes are still tested in a non-production environment when possible.
- Emergency access is obtained through a controlled privileged-account workflow.
- All activity is logged and reviewed after the fact.

### Segregation of Duties
- Developers and functional analysts do not have the ability to import their own transports into production.
- Transport administration and change execution are performed by separate teams.

### Documentation and logs
- Transport history, import logs, and approval metadata are retained.
- The complete population of production imports can be extracted from the transport management system.

### Why this matters
Uncontrolled changes can introduce errors, bypass application controls, or corrupt financial data. A disciplined change process ensures that the SAP system remains in a known, approved state throughout the audit period.
""",
    },
    {
        "title": "Application — Computer Operations",
        "slug": "itgc-application-computer-operations",
        "layer": "Application",
        "category": "computer-operations",
        "content": """## Application — Computer Operations

### Purpose
This narrative describes the generic controls over SAP computer operations, including backup and recovery, batch job monitoring, and interface management. These controls help ensure that financial data is available, complete, and accurate.

### Backup and recovery
- Data backups are performed on a recurring basis for all systems that support financial reporting.
- Backup strategies typically include periodic full backups, incremental backups, and continuous log backups that enable point-in-time recovery.
- Backups are written to secure, isolated storage with defined retention periods.
- Backup success and failure are monitored.

### Backup restoration testing
- The organization tests its ability to restore backups at least annually.
- Restores are performed into a non-production or isolated environment.
- Data integrity and transaction audit logs are validated.
- Results are reviewed and approved by IT management.

### Batch job monitoring
- Critical batch jobs are identified in a risk-based register.
- Jobs that directly affect financial reporting, period-end close, or key ITGC automation are monitored.
- Monitoring tools generate alerts when a job aborts, fails, or exceeds expected run times.
- Failures are investigated and remediated within a defined operational timeframe.
- Root cause and resolution are documented.

### Log retention
- Job logs and application logs for critical processes are retained long enough to support audit and forensic review.
- Premature purging of critical logs is prevented.

### Interface management
- Interfaces feeding into or out of SAP are monitored for completeness and accuracy.
- Staged files are protected from unauthorized modification.
- Re-processing procedures ensure that data is not duplicated.

### Why this matters
Computer operations underpin the availability and integrity of financial data. Untimely backup failures, unremediated batch job errors, or incomplete interfaces can directly lead to inaccurate financial reporting.
""",
    },
    {
        "title": "Database — Access to Programs and Data",
        "slug": "itgc-database-access-to-programs-and-data",
        "layer": "Database",
        "category": "access-to-programs-and-data",
        "content": """## Database — Access to Programs and Data

### Purpose
This narrative describes the generic controls over access to the SAP database layer, using SAP HANA as the reference platform. Database access controls complement application-layer security by protecting the underlying data from unauthorized direct access, modification, or elevation of privilege.

### Database authentication
- Primary administrative access to the database uses enterprise authentication, such as SAML or Kerberos, integrated with the corporate identity provider.
- Fallback database user names and passwords are configured for technical users, emergency accounts, and clients that cannot use SSO.
- Password policies are defined at the database level, covering minimum length, complexity, history, expiration, and lockout thresholds.

### User and privilege management
- Database users are assigned the minimum privileges required for their role.
- System privileges (e.g., user administration, backup, audit, database administration) are granted through roles rather than directly to individuals.
- Privileged access is limited to database administrators and required service accounts.
- High-risk privilege combinations are avoided.

### SYSTEM account control
- The built-in database superuser (SYSTEM) is deactivated in production.
- If emergency use is required, it is activated through a formal break-glass procedure with advance approval and documented justification.
- Activation, usage, and deactivation are captured in audit logs.
- The account is locked immediately after the approved maintenance activity.

### Database audit logging
- Database auditing is enabled.
- Audit policies target high-risk events such as user creation and deletion, privilege and role changes, schema and table modifications, and security-configuration changes.
- High-volume technical application users are excluded from routine data-manipulation auditing to avoid log bloat.
- Audit logs are retained in accordance with corporate policy and reviewed periodically.

### Periodic access review
- Management reviews database user access on a recurring basis.
- The review focuses on active human users and service accounts that hold administrative or high-risk privileges.
- Excessive, dormant, or inappropriate access is removed.
- Findings and remediation are documented.

### Encryption and storage security
- Data-at-rest encryption is enabled for data volumes and redo logs where supported.
- Encryption keys are backed up and stored securely.
- Backups are stored in protected, access-controlled repositories.

### Why this matters
Database-layer controls prevent users from bypassing application controls and changing financial data directly. Strong authentication, least-privilege access, audit logging, and periodic reviews are essential for SOX-relevant systems.
""",
    },
    {
        "title": "Operating System — Access to Programs and Data",
        "slug": "itgc-operating-system-access-to-programs-and-data",
        "layer": "Operating System",
        "category": "access-to-programs-and-data",
        "content": """## Operating System — Access to Programs and Data

### Purpose
This narrative describes the generic controls over access to the operating systems that host SAP application and database instances. OS access controls protect the infrastructure layer from unauthorized logon, privilege escalation, and unmonitored administrative activity.

### Authentication and identity
- Server access is integrated with a central directory service (e.g., Active Directory or LDAP) where possible.
- Interactive logon using local accounts is minimized or disabled.
- Password quality rules are enforced through the OS authentication framework, including minimum length, complexity, history, and expiration.
- Account lockout protects against brute-force attacks.
- Root or administrator logon is restricted; direct remote root or administrator logon is typically disabled.

### Privilege management
- Privileged access is granted through controlled groups and sudoers or equivalent privilege-elevation mechanisms.
- Only authorized administrators and required service accounts receive elevated rights.
- Privileged access follows the principle of least privilege.

### OS hardening
- Servers are built to a defined hardening baseline.
- Unnecessary services, ports, and protocols are disabled.
- Security patches and updates are applied in a controlled manner.
- Host-based firewall and anti-malware controls are configured where applicable.

### Periodic access review
- Management reviews OS user accounts, group memberships, and privilege-escalation rights on a recurring basis.
- The review reconciles active accounts against HR or asset records to identify terminated employees or contractors.
- Inappropriate or excessive access is remediated and documented.

### Logging and monitoring
- OS authentication, privilege escalation, and administrative commands are logged.
- Logs are forwarded to a centralized monitoring or SIEM solution.
- Alerts are generated for suspicious activity and investigated.

### Emergency access
- Emergency root or administrator access requires documented justification and approval.
- Activity is logged and reviewed.
- The elevated session is terminated as soon as the emergency work is completed.

### Why this matters
Weak OS controls can undermine the entire SAP stack. An attacker or insider with unrestricted OS access can bypass application and database controls, access financial data, or disrupt operations. These controls are therefore a foundational part of the ITGC framework.
""",
    },
]


class Command(BaseCommand):
    help = "Load per-layer ITGC narratives linked to the correct ITGCCategory records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing ItgcNarrative records before loading.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            count, _ = ItgcNarrative.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deleted {count} existing ItgcNarrative record(s).")
            )

        for item in NARRATIVES:
            try:
                layer = ITGCLayer.objects.get(name__iexact=item["layer"])
                category = ITGCCategory.objects.get(
                    itgc_layer=layer, slug=item["category"]
                )
            except ITGCLayer.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Layer not found: {item['layer']}")
                )
                sys.exit(1)
            except ITGCCategory.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Category not found: {item['category']} under layer {item['layer']}"
                    )
                )
                sys.exit(1)

            narrative, created = ItgcNarrative.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "content": item["content"],
                    "is_published": True,
                },
            )

            narrative.categories.set([category])

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} narrative '{narrative.title}' -> {layer.name} / {category.name}"
                )
            )

        self.stdout.write(self.style.SUCCESS("ITGC narrative loading complete."))