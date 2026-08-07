SAP SOX Control Baselines

A curated baseline framework for SAP business process controls and IT General Controls (ITGCs). Built to help organizations design, assess, and test SOX programs in SAP environments.

Tech Stack
• Backend: Django 6.0.2, Python 3.12.1
• Database: PostgreSQL (Neon)
• Frontend: HTMX, JavaScript, CSS
• Visualization: Interactive SVG workflows
• Containerization: Docker & Docker Compose

Quick Start

Prerequisites:

• Docker & Docker Compose
• Neon PostgreSQL account (free tier available)

Clone and Configure

git clone <your-repo>
cd sox
cp env_example .env

Update .env with:
• DATABASE_URL=postgresql://...  # from Neon
• SECRET_KEY=<generate-new>
• DEBUG=False  # for production

Build and start containers
• docker compose up

Create superuser
docker compose exec app python manage.py createsuperuser

Run tests
docker compose exec app python manage.py test sox_controls itgc --keepdb


Project Structure
sox/
├── sox_controls/       # SAP Business Process Controls dashboard
├── itgc/               # IT General Controls dashboard
├── about/              # About page
├── blog/               # Blog (future expansion)
├── mysite/             # Django settings & constants
├── templates/          # HTML templates
├── static/             # CSS & JavaScript
└── requirements.txt    # Dependencies

Modules


SOX Controls (/sox_controls)

• Interactive dashboards organized by SAP business processes (Procure to Pay, Order to Cash, Record to Report, Acquire to Retire, Inventory)
• Click process tabs to load workflows
• Click subprocess nodes to filter controls
• Multi-column filtering (Control ID, Process, Sub-Process, Risk, Description)
• Bulk CSV import for controls
• Real-time HTMX-powered updates

ITGC (/itgc)

• IT General Controls framework organized by Layer → Category
• Access Management, Change Control, Batch Processing, and Backup Management
• Interactive workflow visualizations
• Dynamic filtering and search

About (/about)
• Expertise and credential overview

Key Features
• Interactive SVG Workflows: Click-driven process flows for exploring controls
• Real-Time Filtering: HTMX-powered table updates without page reloads
• Centralized Template Management: Refactor-safe template registry in mysite/constants.py
• CSV Bulk Import: Mass-load controls via Django admin
• Automated Testing: 19-test suite for regression detection

Development
Model changes
• docker compose exec app python manage.py makemigrations sox_controls
• docker compose exec app python manage.py makemigrations itgc
• docker compose exec app python manage.py migrate

Template Registry System
• All template paths and view mappings are managed in mysite/constants.py under the TEMPLATE_REGISTRY dictionary. This prevents hardcoded paths and keeps the codebase refactor-proof.
• docker compose exec app python manage.py verify_templates


