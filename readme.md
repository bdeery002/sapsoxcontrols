# SAP SOX Control Baselines

A curated, interactive baseline framework for designing, assessing, and testing SOX (Sarbanes-Oxley) programs and IT General Controls (ITGCs) in SAP environments. Built with a focus on usability, this application transforms control documentation from static lists into dynamic, discoverable interfaces powered by real-time process workflows and advanced admin functionality.

### Background: Why This Project Exists

In my role as an IT Internal Auditor at a large public company, I oversee compliance with the **Sarbanes-Oxley Act (SOX)**, a U.S. federal law requiring public companies to maintain rigorous internal controls over financial reporting. A core part of this responsibility is documenting and testing controls across business processes in **SAP, the enterprise resource planning (ERP) system** used by most Fortune 500 organizations. After years working with multiple companies and their SAP implementations, I realized that control documentation is typically scattered across spreadsheets and email threads—making it difficult for auditors and compliance teams to understand which controls exist and why they matter. This project is a solution to that real-world problem: a centralized interface for exploring and managing SOX controls in SAP environments.

---

## Distinctiveness and Complexity

### Why This Project Is Distinct

This project is fundamentally distinct from all other CS50W course projects. While Project 2 addresses e-commerce, Project 3 mail clients, and Project 4 social networks, this application is a **curated baseline framework and reference resource for compliance professionals**. Rather than building a tool to solve my own workflow problem, I've created a reusable, well-documented baseline that demonstrates best practices in how SOX controls should be organized, documented, and explored in SAP environments.

The purpose is to provide other internal auditors, compliance professionals, and SAP implementation teams with a reference model for structuring their own control frameworks. It embodies my professional perspective on what effective SOX control documentation looks like: controls organized by business process flows (not alphabetical lists), clearly mapped to SAP subprocesses, with consistent documentation of risk, control type, and test procedures.

The domain, data model, and user interactions are entirely different from existing course projects—this is not a social network, e-commerce platform, or generic tool, but a domain-specific **baseline and methodology** for control framework design.

### The Complexity: Process-Driven Control Architecture & Professional Documentation

The core sophistication lies in **how controls are conceptually organized and presented**, not just the technical implementation:

**Process-Driven Architecture**: Controls are intrinsically tied to SAP business processes (Procure-to-Pay, Order-to-Cash, Record-to-Report, etc.) and their constituent subprocesses. This reflects how professional auditors think about controls—not by alphabetical name, but by business flow. The interactive SVG workflow visualization lets users understand the process context before evaluating controls, mirroring real audit methodology.

**Interactive Process Workflows**: Rather than a static list, I built an **SVG-based process flow interface** where clicking a subprocess instantly shows relevant controls. This transforms how users discover controls—by navigating business processes instead of searching. For compliance professionals using this baseline, this model demonstrates that control frameworks should be *discoverable* and *contextual*, not overwhelming lists.

**Multi-Column Real-Time Filtering**: The interface supports simultaneous filtering by Control ID, Sub-Process, Risk, and Description using HTMX with optimized queries. This allows professionals to slice controls by multiple dimensions—showing how a well-designed framework needs flexibility.

**Content-Heavy Admin Interface**: With 50+ controls across 5 business processes and 20+ subprocesses, managing this baseline requires robust data infrastructure. I built a **custom CSV import/export system** with dry-run validation, intelligent foreign key resolution, and atomic transactions. This demonstrates to other organizations how they can efficiently maintain and adapt their own control baselines.

**Sophisticated Model Logic**: The auto-generated control ID scheme (e.g., "P2P-01", "OTC-02") uses business process code prefixes, making IDs meaningful and standardized. A two-pass transaction renumbering strategy safely maintains ID consistency when controls are reordered. This shows professionals how to design control naming conventions that scale across implementations.

**Docker Containerization**: The framework is containerized for platform independence, enabling other organizations to immediately deploy and adapt the baseline without infrastructure friction.

### Technical Challenges Solved

These aren't just engineering problems—they demonstrate methodological maturity:
- **Centralized template registry** prevents fragile hardcoded paths and enables maintainability
- **CSV import with smart foreign key resolution** shows how to handle bulk control data cleanly
- **Database query optimization** demonstrates professional-grade data management
- **Atomic transaction handling** ensures data integrity when organizations adapt and customize the baseline

### Why This Matters as a Baseline

Compliance professionals benefit from this resource because:
- **It demonstrates best practices** in control documentation and organization
- **It provides a starting point** that organizations can customize for their specific SAP environments
- **It models how controls should be structured**—by business process, with clear risk/type documentation
- **It shows how to make control frameworks discoverable** through thoughtful UI/UX
- **It proves that compliance tooling doesn't have to be ugly or hard to use**

This is a reference baseline grounded in professional audit expertise—fundamentally different from generic course projects, offering value to the wider compliance profession.

---

## Project Structure & Files

**sox_controls/** — Core application
- `models.py`: `BusinessProcess` (SAP processes), `SubProcess` (workflow steps), `SoxControl` (controls with auto-ID generation and renumbering logic)
- `views.py`: HTMX-aware views for dashboard, filtering, and workflow display
- `admin.py`: CSV import/export, drag-and-drop reordering, admin customization
- `urls.py`: Routing for filtering and control detail pages
- `templates/`: Dashboard, control detail, workflow SVG, partial HTML for HTMX

**itgc/** — IT General Controls (parallel structure for IT-focused controls)

**mysite/** — Project settings
- `settings.py`: Django 6.0.2, PostgreSQL via environment variables
- `constants.py`: Centralized `TEMPLATE_REGISTRY` to prevent hardcoded paths
- `urls.py`: Project-level routing

**static/css/styles.css** — Responsive flexbox layout, SVG interaction, mobile-friendly tables

**Docker** — `Dockerfile` and `docker-compose.yml` for reproducible deployment

**Tests** — 19 test cases covering model logic, view filtering, CSV validation, and HTMX rendering

---

## How to Run Your Application

### Quick Start with Docker (Recommended)

```bash
git clone <your-repo-url>
cd sox
cp env_example .env
# Update .env with DATABASE_URL, SECRET_KEY, DEBUG=False
docker compose up
docker compose exec app python manage.py createsuperuser
```

Access the app at http://localhost:8000/

### Local Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configure .env with PostgreSQL connection
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Populate Data

1. Log into http://localhost:8000/admin
2. Create `BusinessProcess` objects (P2P, OTC, R2R, A2R, Inventory)
3. Create `SubProcess` objects for each
4. Use **Upload CSV** admin action to bulk-import controls

### Run Tests

```bash
python manage.py test sox_controls itgc --keepdb
```
Expected: 19 tests pass.

---

## Technology Choices & Additional Information

**HTMX over JavaScript frameworks**: Minimizes client-side complexity while preserving real-time filtering. Server-side logic remains centralized, JavaScript payload stays small, and semantic HTML is maintained.

**SVG workflow visualization**: Maps to how auditors think—controls aligned with business processes, not alphabetical lists. Clicking a process node instantly shows relevant controls.

**Django admin enhancements**: The default admin lacks bulk data handling. I extended it with CSV import/export, drag-and-drop reordering, and custom validation—reducing friction for non-technical compliance teams.

**Docker for platform independence**: Eliminates environment differences (Python versions, database drivers, system libraries). The same container runs identically on Windows, Mac, Linux, or cloud platforms.

**PostgreSQL & Neon**: Production-ready with concurrent writes and advanced querying. Neon's free tier provides cloud-hosted PostgreSQL without infrastructure management.

### Dependencies (requirements.txt)

- `django`: Web framework
- `psycopg2`: PostgreSQL driver
- `dj-database-url`: Parse DATABASE_URL from environment
- `python-dotenv`: Load .env files
- `django-admin-sortable2`: Drag-and-drop reordering
- `django-allauth`: Authentication framework
- `django-ratelimit`: Rate-limiting

### Testing & Quality

The 19-test suite covers model auto-ID generation, sequence reordering atomicity, CSV import validation, view filtering accuracy, and HTMX partial rendering.

### Mobile Responsiveness

Flexbox layout adapts to viewport size. Table columns have fixed widths to prevent layout shift during HTMX updates. Sidebar adjusts on smaller screens.
---

## Why This Project Stands Out

1. **Professional baseline resource** (not a personal tool)—created to advance compliance profession practices
2. **User-centric design** solving real auditor pain points through thoughtful UX
3. **Production-ready architecture** (Docker, PostgreSQL, comprehensive testing)
4. **Sophisticated admin** with CSV validation and bulk operations
5. **Clean, maintainable code** with proper ORM optimization and centralized configuration

This is a purpose-built baseline framework grounded in professional audit expertise—fundamentally distinct from social networks or e-commerce platforms—offering methodological value to the wider compliance profession.
