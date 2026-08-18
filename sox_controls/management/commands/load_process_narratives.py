from django.core.management.base import BaseCommand
from sox_controls.models import BusinessProcess, ProcessNarrative


DISCLAIMER = (
    "**Disclaimer:** This process narrative is provided as a generic reference describing a "
    "typical SAP S/4HANA process flow. Actual business processes, transaction codes, Fiori apps, "
    "and control configurations may differ based on your organization's specific SAP implementation, "
    "release, cloud/on-premise deployment, and industry configuration. Please validate against your "
    "own SAP system and control documentation."
)

NARRATIVES = [
    {
        "process_name": "Procure to Pay",
        "title": "Procure to Pay (P2P) Process Narrative",
        "slug": "procure-to-pay",
        "summary": (
            "A generic SAP S/4HANA Procure-to-Pay narrative covering requisitioning, purchasing, "
            "goods receipt, invoice verification, payment, and period-end GR/IR clearing."
        ),
        "content": """## Overview

The Procure-to-Pay process covers the full lifecycle of acquiring goods and services, from identifying a need through to paying the supplier. In a typical SAP S/4HANA environment, the process flows through **Materials Management (MM)** for procurement and **Financial Accounting (FI)** for liability and cash settlement.

## Typical Process Flow

1. **Requirement and Purchase Requisition**  
   A user identifies a need and creates a **Purchase Requisition (PR)**. In SAP S/4HANA this can be done via the **Create Requisition** Fiori app or classic transaction `ME51N`. PRs may route through a release strategy based on value, account assignment, or material group.

2. **Sourcing and Purchase Order**  
   Procurement converts the PR into a **Purchase Order (PO)** using `ME21N` or the **Create Purchase Order** Fiori app. The PO captures the supplier, material, quantity, price, delivery date, and account assignment. POs are typically subject to release/approval via `ME29N`. For services, the PO may reference a **Service Entry Sheet**.

3. **Goods Receipt / Service Confirmation**  
   When goods arrive, the warehouse posts a **Goods Receipt (GR)** via `MIGO`. This creates a material document and an accounting entry, typically debiting inventory or expense and crediting the **GR/IR clearing account**. Services are confirmed via a service entry sheet rather than a physical GR.

4. **Invoice Verification**  
   Accounts Payable posts the supplier invoice using `MIRO` (Logistics Invoice Verification) or the **Create Supplier Invoice** Fiori app. SAP performs a **three-way match** against the PO, GR, and invoice. If variances exceed tolerance, the invoice is blocked for payment until resolved.

5. **Payment**  
   Approved invoices are paid via the automatic payment run `F110` or manually via `F-53`. Payments clear the vendor liability and the bank account.

6. **Period-End Clearing**  
   At month-end, the **GR/IR clearing account** is reconciled (`F.19` or `MR11`) to clear differences between goods received and invoices received.

## Key S/4HANA Notes

- **Business Partner is mandatory** for supplier master data in S/4HANA; classic vendor transactions (`XK01`, `MK01`, `FK01`) redirect to transaction `BP` or the **Manage Business Partner Master Data** Fiori app.
- **Goods movements are consolidated into `MIGO`**; many legacy MB transactions are obsolete in S/4HANA.
- **Central Invoice Management** may be used in S/4HANA Cloud or newer deployments to streamline invoice receipt and matching.

## Typical Controls

- Segregation of duties between requisitioner, buyer, receiver, and AP poster
- PR/PO release strategies
- GR-based invoice verification
- Three-way match and tolerance configuration
- Vendor master change controls
- Duplicate invoice check
- Payment run proposal review
""",
    },
    {
        "process_name": "Order to Cash",
        "title": "Order to Cash (O2C) Process Narrative",
        "slug": "order-to-cash",
        "summary": (
            "A generic SAP S/4HANA Order-to-Cash narrative covering customer master, credit, sales order, "
            "delivery, billing, accounts receivable, and collections."
        ),
        "content": """## Overview

Order-to-Cash is the mirror process of P2P: it covers selling goods or services to a customer and collecting cash. In SAP S/4HANA, this spans **Sales and Distribution (SD)**, **Logistics Execution**, and **Financial Accounting (FI)**.

## Typical Process Flow

1. **Customer Master and Credit Setup**  
   In S/4HANA, the customer is managed as a **Business Partner** with FI and SD roles. Credit limits are set in SAP Credit Management (FSCM), often via the **Manage Customer Credit** Fiori app or `UKM_BP`, rather than the classic `FD32` approach.

2. **Pre-Sales (Optional)**  
   Inquiries and quotations may be created via `VA11` and `VA21` or equivalent Fiori apps.

3. **Sales Order Creation**  
   The customer order is captured in a **Sales Order** (`VA01` or the **Create Sales Orders** Fiori app). The system performs pricing, tax determination, availability checking (ATP), and credit checking.

4. **Availability and Scheduling**  
   SAP checks stock availability using ATP logic and schedules delivery dates. In S/4HANA, **Advanced ATP (aATP)** supports more sophisticated allocation and backorder handling.

5. **Outbound Delivery**  
   A delivery is created via `VL01N` or the **Create Outbound Deliveries** Fiori app. The warehouse picks, packs, and stages goods for shipment.

6. **Post Goods Issue (PGI)**  
   PGI records the physical shipment. It reduces inventory and posts the cost of goods sold (COGS) entry.

7. **Billing**  
   A billing document is created via `VF01` or the **Create Billing Documents** Fiori app. The invoice posts revenue and accounts receivable to the customer account.

8. **Cash Receipt and Clearing**  
   Customer payments are posted via `F-28`, lockbox processing, or electronic bank statement. Open AR items are cleared via `F-32` or `FB05`.

## Key S/4HANA Notes

- **Business Partner replaces the classic customer master**.
- **SAP Credit Management (FSCM)** is the strategic credit platform in S/4HANA.
- **Universal Journal** posts revenue and AR in real time.
- **Pricing data** is stored in compatibility views and new tables such as `PRCD_ELEMENTS`.

## Typical Controls

- Credit limit checks and blocked order release
- Incompletion procedures to enforce mandatory fields
- Pricing condition record governance
- Delivery/billing block reasons
- Segregation of duties between sales, shipping, billing, and AR
- Dunning and collections management
- Revenue recognition cut-off at PGI
""",
    },
    {
        "process_name": "Record to Report",
        "title": "Record to Report (R2R) Process Narrative",
        "slug": "record-to-report",
        "summary": (
            "A generic SAP S/4HANA Record-to-Report narrative built around the Universal Journal, "
            "covering recording, reconciliation, close, consolidation, and reporting."
        ),
        "content": """## Overview

Record-to-Report covers the capture, processing, and reporting of all financial transactions. In SAP S/4HANA, this is built around the **Universal Journal (ACDOCA)**, which acts as a single source of truth for financial and management accounting.

## Typical Process Flow

1. **Record**  
   Daily transactions are recorded in the General Ledger, either automatically from logistics (e.g., P2P, O2C, P2M) or manually via journal entries. Classic manual journal transactions include `FB50`/`F-02`, while S/4HANA offers the **Post General Journal** Fiori app.

2. **Sub-Ledger Reconciliation**  
   Sub-ledgers (AP, AR, Fixed Assets, Inventory, Bank) are reconciled to the GL. In S/4HANA, the Universal Journal allows sub-ledger detail to be reported directly from GL views.

3. **Entity Close**  
   At period-end, posting periods are managed via `OB52`, `MMPV`, or the **Manage Posting Periods** Fiori app. Adjusting entries, accruals, provisions, and reclassifications are posted.

4. **Consolidation and Corporate Close**  
   Intercompany transactions are matched and eliminated. In S/4HANA, **Group Reporting** and **Intercompany Matching and Reconciliation (ICMR)** support consolidation. The **Financial Closing Cockpit** helps orchestrate close tasks.

5. **Reporting**  
   Financial statements, trial balances, and management reports are generated. S/4HANA embedded analytics and Fiori apps provide real-time dashboards.

6. **Regulatory Submissions**  
   Statutory reports and tax filings are produced from the General Ledger.

## Key S/4HANA Notes

- The **Universal Journal** eliminates the traditional FI/CO reconciliation.
- **Posting periods** can be managed by business transaction type and closing step via Fiori apps.
- **Real-time depreciation** is calculated on individual asset transactions, reducing period-end close time.

## Typical Controls

- Posting period open/close procedures
- Journal entry approval workflows (park/post)
- Segregation of duties for journal creation, review, and posting
- Balance sheet account reconciliation
- Intercompany reconciliation and elimination
- Balance carryforward and period lock
- Financial Closing Cockpit task tracking
""",
    },
    {
        "process_name": "Acquire to Retire",
        "title": "Acquire to Retire (A2R) / Fixed Assets Process Narrative",
        "slug": "acquire-to-retire",
        "summary": (
            "A generic SAP S/4HANA Acquire-to-Retire narrative covering asset creation, capital projects, "
            "acquisition, depreciation, transfers, and retirement."
        ),
        "content": """## Overview

The Acquire-to-Retire process covers the lifecycle of fixed assets, from capital expenditure planning and acquisition through depreciation, maintenance, and eventual disposal or retirement.

## Typical Process Flow

1. **Asset Master Creation**  
   Assets are created in the asset master using `AS01` or the **Manage Fixed Assets** Fiori app. The asset master links to the asset class, depreciation key, and GL reconciliation account.

2. **Capital Projects and Assets Under Construction (AUC)**  
   For larger capital projects, costs are collected on **Internal Orders** or **Work Breakdown Structure (WBS)** elements. Costs from MM, FI, and CO are settled to the asset under construction, then transferred to a completed fixed asset.

3. **Acquisition**  
   Assets may be acquired through:
   - A purchase order with account assignment to an asset (`MIGO`/`F-90`)
   - Direct acquisition via `F-90`
   - Transfer from another asset or company code (`ABUMN`)
   - Asset acquisition without a vendor (`ABNAN`)

4. **Depreciation**  
   Planned depreciation is calculated and posted periodically via `AFAB` or `AFBP`. In S/4HANA’s new Asset Accounting, depreciation is calculated in real time on individual asset transactions.

5. **Asset Transfers and Adjustments**  
   Assets may be transferred between cost centers, profit centers, or company codes (`ABUMN`). Post-capitalization and revaluation may be posted where permitted.

6. **Retirement and Disposal**  
   Assets are retired or scrapped using `ABAON` (retirement with revenue), `ABAVN` (scrapping without revenue), or `ABUMN` (intercompany transfer). Gain or loss on disposal is calculated.

7. **Period-End and Year-End**  
   Depreciation runs are posted, asset balances are reconciled to the GL, and year-end balance carryforward is performed. In S/4HANA, no separate asset balance carryforward is needed because the new Asset Accounting is integrated with the GL balance carryforward.

## Key S/4HANA Notes

- **New Asset Accounting** is mandatory in S/4HANA and integrates directly with the Universal Journal.
- **Asset Accounting** supports parallel accounting and real-time depreciation.
- **Business Partner** is used for vendor/customer interactions in asset acquisitions/disposals.

## Typical Controls

- Asset class and depreciation key configuration
- Capital expenditure approval and AUC settlement
- Segregation of duties between asset creation, acquisition posting, and depreciation posting
- Physical asset verification against asset register
- Depreciation run review and approval
- Authorization controls for asset disposals
""",
    },
    {
        "process_name": "Produce to Make",
        "title": "Produce to Make (P2M) Process Narrative",
        "slug": "produce-to-make",
        "summary": (
            "A generic SAP S/4HANA Produce-to-Make narrative covering planning, cost estimating, "
            "production order execution, WIP, variance, settlement, and actual costing."
        ),
        "content": """## Overview

Produce-to-Make covers the planning, execution, and accounting of manufacturing operations. In SAP S/4HANA, this integrates **Production Planning (PP)**, **Materials Management (MM)**, **Controlling (CO)**, and **Financial Accounting (FI)**.

## Typical Process Flow

1. **Demand Planning and MRP**  
   Production requirements are derived from sales demand, forecasts, and stock levels. MRP runs (`MD01`/`MD02` or Fiori **Schedule MRP Runs**) generate planned orders or purchase requisitions.

2. **Product Cost Planning**  
   A **standard cost estimate** is created using `CK11N` and marked/released with `CK24`. This establishes the planned cost of the product based on BOM, routing, and overhead rates.

3. **Production Order Creation and Release**  
   A **Production Order** is created (`CO01` or **Manage Production Orders** Fiori app), referencing the material, BOM, and routing. The order is released (`CO02`) to authorize shop floor activity.

4. **Material Issue to Production**  
   Components are issued to the production order via `MIGO` (goods issue), typically with movement type `261`.

5. **Production Confirmation**  
   Labor and machine operations are confirmed via `CO11N`/`CO15` or the **Confirm Production Operation** Fiori app. This records actual activity quantities consumed.

6. **Goods Receipt from Production**  
   Finished goods are received into inventory via `MIGO` (movement type `101`), posting inventory and crediting the production order.

7. **Work in Process (WIP) and Variance Calculation**  
   WIP is calculated for unfinished orders. For completed orders, variance calculation compares actual costs to the standard cost estimate.

8. **Order Settlement**  
   The production order is settled (`KO88`/`CO88`), transferring costs to finished goods inventory, cost of goods sold, or CO-PA. The order is then closed.

9. **Actual Costing (Optional)**  
   Where **Material Ledger** is active, actual costs are calculated at period-end to revalue inventory and capture price differences.

## Key S/4HANA Notes

- **Material Ledger** is recommended in S/4HANA for actual costing and parallel valuation.
- **Fiori apps** such as **Manage Production Orders**, **Confirm Production Operation**, and **Production Order Confirmation** are commonly used.
- **S/4HANA PP/DS** (Production Planning and Detailed Scheduling) offers advanced planning capabilities.

## Typical Controls

- BOM and routing accuracy
- Standard cost estimate approval and release
- Production order release authorization
- Material issue and goods receipt matching
- Confirmation accuracy and backflush controls
- WIP and variance analysis
- Order settlement review and period-end close
""",
    },
    {
        "process_name": "Inventory",
        "title": "Inventory Management Process Narrative",
        "slug": "inventory-management",
        "summary": (
            "A generic SAP S/4HANA Inventory Management narrative covering movements, physical inventory, "
            "valuation, reserves, and reporting."
        ),
        "content": """## Overview

Inventory Management covers the movement, valuation, and physical control of materials. In SAP S/4HANA, inventory processes are tightly integrated with procurement, production, sales, and finance.

## Typical Process Flow

1. **Inventory Movements**  
   Goods are received against purchase orders or production orders, issued to production or sales, and transferred between storage locations or plants. In S/4HANA, these movements are typically posted via `MIGO`. Movement types (e.g., `101`, `261`, `301`, `311`) determine the accounting and stock impact.

2. **Stock Transport Orders**  
   Inter-plant transfers may use stock transport orders rather than direct transfer postings, providing visibility and control over the in-transit stock.

3. **Physical Inventory / Cycle Counting**  
   Physical inventory is performed through:
   - **Physical Inventory Documents** (`MI01`, `MI20`, `MI31`)
   - **Cycle Counting** based on ABC classification
   - **Inventory Differences** posted via `MI20` or the relevant Fiori app
   
   Counts are entered, variances analyzed, and adjustment postings are made.

4. **Inventory Valuation**  
   Inventory is valued at standard price, moving average price, or actual cost (Material Ledger). Price differences from procurement or production are posted to price variance accounts.

5. **Reserves and Valuation Adjustments**  
   At period-end, inventory may be evaluated for lower of cost or market, obsolescence, or other reserves. Adjustments are posted via manual journals or valuation programs.

6. **Inventory Reporting**  
   Stock levels, movements, and valuation are reported via `MB52`, `MMBE`, `MC.9`, and Fiori apps such as **Stock - Multiple Materials** and **Material Movements**.

## Key S/4HANA Notes

- **MIGO is the central transaction** for goods movements; legacy MB transactions are obsolete.
- **Material Ledger** provides actual costing and parallel valuation.
- **Warehouse Management (WM)** or **Extended Warehouse Management (EWM)** may be used for advanced warehouse operations.
- **Inventory Management** is integrated with the Universal Journal for real-time valuation postings.

## Typical Controls

- Movement type authorization
- Goods receipt/quality inspection holds
- Cycle count frequency and tolerance
- Segregation of duties for count entry, approval, and adjustment posting
- Inventory valuation review and reserve analysis
- Negative stock and tolerance settings
- Slow-moving/obsolete inventory reporting
""",
    },
]


class Command(BaseCommand):
    help = "Load generic SAP S/4HANA process narratives into the database."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in NARRATIVES:
            bp = BusinessProcess.objects.filter(name=item["process_name"]).first()
            if not bp:
                self.stdout.write(
                    self.style.WARNING(f"BusinessProcess not found: {item['process_name']}")
                )
                continue

            narrative, created = ProcessNarrative.objects.update_or_create(
                business_process=bp,
                defaults={
                    "title": item["title"],
                    "slug": item["slug"],
                    "summary": item["summary"],
                    "content": item["content"],
                    "disclaimer": DISCLAIMER,
                    "is_published": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {item['title']}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated: {item['title']}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {created_count} created, {updated_count} updated."
            )
        )