"""
Daily demo shop data refresh.
HARDCODED shop ID — will NEVER touch any other shop.
Deletes all demo data, then re-seeds with fresh realistic data.
"""
import requests
import json
import time
from datetime import datetime, timedelta, timezone

SUPABASE_URL = "https://hglbhncsdchfevxdbcoa.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnbGJobmNzZGNoZmV2eGRiY29hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDY1MjYzMCwiZXhwIjoyMDkwMjI4NjMwfQ.lgb_PQYZRnKJpbH8YRFu4xG6aqWsWYDiDDpjCRwRLmM"

# ⚠️ HARDCODED — this is the ONLY shop this script touches
DEMO_SHOP_ID = "75acac8a-adb6-493b-b310-ebc4c84d4aed"
DEMO_EMAIL = "try@automotai.com"
DEMO_PASSWORD = "DemoShop1!"

headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def rest(path, method="GET", body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if method == "GET":
        r = requests.get(url, headers=headers)
    elif method == "POST":
        r = requests.post(url, headers=headers, json=body)
    elif method == "PATCH":
        r = requests.patch(url, headers=headers, json=body)
    elif method == "DELETE":
        r = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unknown method: {method}")
    if r.status_code not in (200, 201, 204):
        print(f"  FAIL [{r.status_code}] {method} {path}: {r.text[:200]}")
        return None
    return r.json() if r.text else None

def first(result):
    if result and isinstance(result, list) and len(result) > 0:
        return result[0]
    return result

# ═══════════════════════════════════════════════════════════
# PHASE 1: NUKE all demo shop data
# ═══════════════════════════════════════════════════════════
print("🧹 Nuking demo shop data...")

# Order matters — delete children before parents (FK constraints)
tables = [
    "dvi_checkpoints",       # depends on dvi_templates
    "dvi_findings",          # depends on dvi_inspections
    "dvi_photos",            # depends on dvi_findings
    "dvi_inspections",       # depends on jobs, vehicles
    "dvi_templates",         # no FK deps
    "payment_invoices",      # depends on payments, invoices
    "payments",              # depends on invoices
    "line_items",            # depends on estimates, jobs
    "job_groups",            # depends on jobs
    "time_entries",          # depends on jobs, employees
    "appointments",          # depends on customers, vehicles
    "invoices",              # depends on estimates, customers
    "estimates",             # depends on customers, vehicles
    "jobs",                  # depends on customers, vehicles
    "vehicles",              # depends on customers
    "customers",             # no FK deps to shop data
    "service_templates",     # no FK deps
    "knowledge_base",        # no FK deps
    "usage_allowances",      # no FK deps
]

for table in tables:
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{table}?shop_id=eq.{DEMO_SHOP_ID}",
        headers=headers,
    )
    if r.status_code in (200, 201, 204):
        print(f"  ✓ {table}")
    else:
        # Table might not exist or might not have shop_id column
        print(f"  - {table} (skipped: {r.status_code})")

# Also clean up employees that aren't the owner
r = requests.delete(
    f"{SUPABASE_URL}/rest/v1/employees?shop_id=eq.{DEMO_SHOP_ID}&user_id=is.null",
    headers=headers,
)
if r.status_code in (200, 201, 204):
    print(f"  ✓ employees (non-owner)")

# Ensure shop is complimentary
r = requests.patch(
    f"{SUPABASE_URL}/rest/v1/shops?id=eq.{DEMO_SHOP_ID}",
    headers=headers,
    json={"complimentary": True, "onboarding_complete": True},
)
if r.status_code in (200, 201, 204):
    print(f"  ✓ shop (complimentary + onboarding)")

print("✅ Nuke complete")

# ═══════════════════════════════════════════════════════════
# PHASE 2: RE-SEED
# ═══════════════════════════════════════════════════════════
print("\n🌱 Re-seeding demo data...")
now = datetime.now(timezone.utc)

# ── Service templates ──
print("  Service templates...")
services = [
    {"name": "Oil Change - Synthetic", "description": "Full synthetic oil change with filter replacement. Includes multi-point inspection.", "category": "Maintenance"},
    {"name": "Brake Pad Replacement - Front", "description": "Front brake pad replacement. Includes rotor inspection and brake fluid check.", "category": "Brakes"},
    {"name": "Brake Pad Replacement - Rear", "description": "Rear brake pad replacement. Includes rotor inspection and brake fluid check.", "category": "Brakes"},
    {"name": "Brake Pad Replacement - All Four", "description": "Complete brake pad replacement front and rear. Includes rotor inspection and brake fluid check.", "category": "Brakes"},
    {"name": "Tire Rotation & Balance", "description": "Rotate all four tires and computer balance. Includes tread depth measurement.", "category": "Tires"},
    {"name": "Wheel Alignment", "description": "Four-wheel computer alignment. Ensures proper handling and even tire wear.", "category": "Tires"},
    {"name": "A/C Diagnostic", "description": "Full A/C system diagnostic including pressure test, leak detection, and performance evaluation.", "category": "HVAC"},
    {"name": "A/C Recharge", "description": "Evacuate and recharge A/C system with proper refrigerant. Includes leak check.", "category": "HVAC"},
    {"name": "Transmission Fluid Service", "description": "Drain and fill transmission fluid, replace filter. Not a flush — safe for high-mileage vehicles.", "category": "Transmission"},
    {"name": "Check Engine Light Diagnostic", "description": "OBD-II scan, code interpretation, and visual inspection. Does not include repair.", "category": "Diagnostic"},
    {"name": "Pre-Purchase Inspection", "description": "Comprehensive 150-point inspection for used vehicle purchases. Includes test drive, compression test, and detailed report.", "category": "Diagnostic"},
    {"name": "Timing Belt Replacement", "description": "Timing belt replacement with water pump, tensioners, and coolant flush. Price varies by vehicle.", "category": "Engine"},
    {"name": "Spark Plug Replacement", "description": "Replace all spark plugs. Includes ignition coil inspection.", "category": "Engine"},
    {"name": "Battery Replacement", "description": "Battery testing and replacement. Includes terminal cleaning and charging system check.", "category": "Electrical"},
    {"name": "Alternator Replacement", "description": "Alternator replacement with belt inspection. Includes charging system verification.", "category": "Electrical"},
    {"name": "Suspension Inspection", "description": "Full suspension inspection including shocks, struts, ball joints, tie rods, and bushings.", "category": "Suspension"},
    {"name": "Coolant Flush", "description": "Complete cooling system flush and fill with proper coolant. Includes thermostat check.", "category": "Engine"},
    {"name": "State Inspection", "description": "Texas state vehicle safety inspection.", "category": "Other"},
]
for s in services:
    rest("service_templates", "POST", {**s, "shop_id": DEMO_SHOP_ID})
print(f"    {len(services)} created")

# ── Customers ──
print("  Customers...")
customers_data = [
    {"name": "David Thompson", "email": "david.t@email.com", "phone": "(512) 555-0101", "notes": "Prefers synthetic oil. Has a fleet of 3 work trucks for his landscaping business. Always pays on time."},
    {"name": "Lisa Martinez", "email": "lisa.m@email.com", "phone": "(512) 555-0102", "notes": "Single mom, drives a lot for work. Very price-conscious but values quality. Prefers text updates."},
    {"name": "Robert Chen", "email": "robert.c@email.com", "phone": "(512) 555-0103", "notes": "Tech professional, works from home. Very particular about his BMW. Wants OEM parts only."},
    {"name": "Maria Garcia", "email": "maria.g@email.com", "phone": "(512) 555-0104", "notes": "Retired teacher. Has been coming to the shop for 5+ years. Drives carefully, mostly local trips."},
    {"name": "James Wilson", "email": "james.w@email.com", "phone": "(512) 555-0105", "notes": "Construction contractor. Hard on his trucks. Needs vehicles back fast — downtime costs him money."},
    {"name": "Emily Park", "email": "emily.p@email.com", "phone": "(512) 555-0106", "notes": "College student. Parents pay for maintenance. Usually needs basic services — oil changes, tire rotations."},
]
customer_ids = []
for c in customers_data:
    r = first(rest("customers", "POST", {**c, "shop_id": DEMO_SHOP_ID}))
    if r:
        customer_ids.append(r["id"])
print(f"    {len(customer_ids)} created")

# ── Vehicles ──
print("  Vehicles...")
vehicles_data = [
    {"customer_idx": 0, "make": "Ford", "model": "F-150", "year": 2020, "vin": "1FTEW1E56LFA12345", "license_plate": "TX-8ABC12", "mileage": 85000, "color": "Oxford White", "notes": "3.5L EcoBoost V6"},
    {"customer_idx": 0, "make": "Ford", "model": "F-250 Super Duty", "year": 2022, "vin": "1FT7W2BT5NEA67890", "license_plate": "TX-7DEF34", "mileage": 45000, "color": "Agate Black", "notes": "6.7L Power Stroke V8"},
    {"customer_idx": 0, "make": "Chevrolet", "model": "Silverado 1500", "year": 2019, "vin": "3GCUYDED1KG12345", "license_plate": "TX-5GHI56", "mileage": 112000, "color": "Summit White", "notes": "5.3L EcoTec3 V8"},
    {"customer_idx": 1, "make": "Toyota", "model": "Camry", "year": 2021, "vin": "4T1B11HK0MU12345", "license_plate": "TX-3JKL78", "mileage": 62000, "color": "Celestial Silver", "notes": "2.5L I4"},
    {"customer_idx": 2, "make": "BMW", "model": "530i", "year": 2023, "vin": "WBA53BH03PW12345", "license_plate": "TX-1MNO90", "mileage": 18000, "color": "Alpine White", "notes": "2.0L TwinPower Turbo I4"},
    {"customer_idx": 3, "make": "Honda", "model": "CR-V", "year": 2018, "vin": "5J6RW2H58JL12345", "license_plate": "TX-9PQR12", "mileage": 95000, "color": "Modern Steel Metallic", "notes": "1.5L Turbo I4"},
    {"customer_idx": 4, "make": "Ram", "model": "2500", "year": 2021, "vin": "3C6UR5FL2MG12345", "license_plate": "TX-2STU34", "mileage": 72000, "color": "Bright White", "notes": "6.7L Cummins Turbo Diesel I6"},
    {"customer_idx": 5, "make": "Hyundai", "model": "Elantra", "year": 2022, "vin": "KMHLM4AG5NU12345", "license_plate": "TX-4VWX56", "mileage": 28000, "color": "Fluid Metal", "notes": "2.0L I4"},
]
vehicle_ids = []
for v in vehicles_data:
    r = first(rest("vehicles", "POST", {
        "shop_id": DEMO_SHOP_ID,
        "customer_id": customer_ids[v["customer_idx"]],
        "make": v["make"], "model": v["model"], "year": v["year"],
        "vin": v["vin"], "license_plate": v["license_plate"],
        "mileage": v["mileage"], "color": v["color"], "notes": v.get("notes", ""),
    }))
    if r:
        vehicle_ids.append(r["id"])
print(f"    {len(vehicle_ids)} created")

# ── Estimates ──
print("  Estimates...")
est_data = [
    {"estimate_number": "EST-2026-0042", "customer_id": customer_ids[0], "vehicle_id": vehicle_ids[0],
     "status": "approved", "subtotal": 449.99, "tax_rate": 8.25, "tax_amount": 37.12, "total": 487.11,
     "notes": "Front and rear brake pads are at 3mm. Rotors look good. Recommend pad replacement all around.",
     "created_at": (now - timedelta(days=5)).isoformat(), "updated_at": (now - timedelta(days=3)).isoformat()},
    {"estimate_number": "EST-2026-0043", "customer_id": customer_ids[1], "vehicle_id": vehicle_ids[3],
     "status": "awaiting_approval", "subtotal": 129.98, "tax_rate": 8.25, "tax_amount": 10.72, "total": 140.70,
     "notes": "Routine maintenance — oil change and tire rotation. Tires at 6/32\" tread remaining.",
     "created_at": (now - timedelta(days=2)).isoformat(), "updated_at": (now - timedelta(days=2)).isoformat()},
    {"estimate_number": "EST-2026-0044", "customer_id": customer_ids[2], "vehicle_id": vehicle_ids[4],
     "status": "draft", "subtotal": 89.99, "tax_rate": 8.25, "tax_amount": 7.42, "total": 97.41,
     "notes": "Customer reports A/C blowing warm on driver side only. Suspect blend door actuator issue.",
     "created_at": (now - timedelta(hours=4)).isoformat(), "updated_at": (now - timedelta(hours=4)).isoformat()},
    {"estimate_number": "EST-2026-0045", "customer_id": customer_ids[4], "vehicle_id": vehicle_ids[6],
     "status": "awaiting_approval", "subtotal": 799.99, "tax_rate": 8.25, "tax_amount": 66.00, "total": 865.99,
     "notes": "Timing belt is due at 75K miles per Cummins maintenance schedule. Currently at 72K — recommend doing it now to avoid downtime later.",
     "created_at": (now - timedelta(days=1)).isoformat(), "updated_at": (now - timedelta(days=1)).isoformat()},
]
estimate_ids = []
for e in est_data:
    r = first(rest("estimates", "POST", {**e, "shop_id": DEMO_SHOP_ID}))
    if r:
        estimate_ids.append(r["id"])
print(f"    {len(estimate_ids)} created")

# ── Job groups + line items ──
print("  Job groups & line items...")
# Get owner employee for submitted_by
emp = first(rest(f"employees?shop_id=eq.{DEMO_SHOP_ID}&user_id=not.is.null&select=id"))
emp_id = emp["id"] if emp else None

estimate_items = {
    "EST-2026-0042": {
        "groups": [
            {"name": "Brake Service - Front", "status": "approved", "sort_order": 0},
            {"name": "Brake Service - Rear", "status": "approved", "sort_order": 1},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "Front brake pad replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 0},
            {"group_idx": 0, "type": "parts", "description": "Front brake pad set (ceramic)", "quantity": 1, "unit_price": 90.00, "total": 90.00, "part_number": "FD-1414C", "sort_order": 1},
            {"group_idx": 1, "type": "labor", "description": "Rear brake pad replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 0},
            {"group_idx": 1, "type": "parts", "description": "Rear brake pad set (ceramic)", "quantity": 1, "unit_price": 74.99, "total": 74.99, "part_number": "FD-1415C", "sort_order": 1},
        ],
    },
    "EST-2026-0043": {
        "groups": [
            {"name": "Routine Maintenance", "status": "submitted", "sort_order": 0},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "Oil change - synthetic (labor)", "quantity": 0.5, "unit_price": 95.00, "total": 47.50, "sort_order": 0},
            {"group_idx": 0, "type": "parts", "description": "Full synthetic oil 5W-30 (6 qts)", "quantity": 6, "unit_price": 5.83, "total": 34.98, "part_number": "MOB1-5W30", "sort_order": 1},
            {"group_idx": 0, "type": "parts", "description": "Oil filter", "quantity": 1, "unit_price": 7.50, "total": 7.50, "part_number": "TOY-04152", "sort_order": 2},
            {"group_idx": 0, "type": "labor", "description": "Tire rotation & balance (labor)", "quantity": 0.5, "unit_price": 80.00, "total": 40.00, "sort_order": 3},
        ],
    },
    "EST-2026-0044": {
        "groups": [
            {"name": "A/C System Diagnostic", "status": "draft", "sort_order": 0},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "A/C system diagnostic - full inspection", "quantity": 1.0, "unit_price": 89.99, "total": 89.99, "sort_order": 0},
        ],
    },
    "EST-2026-0045": {
        "groups": [
            {"name": "Timing Belt Service", "status": "submitted", "sort_order": 0},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "Timing belt replacement - labor (Cummins 6.7L)", "quantity": 5.0, "unit_price": 95.00, "total": 475.00, "sort_order": 0},
            {"group_idx": 0, "type": "parts", "description": "Timing belt kit (belt, tensioner, idler)", "quantity": 1, "unit_price": 189.99, "total": 189.99, "part_number": "GAT-TCK329", "sort_order": 1},
            {"group_idx": 0, "type": "parts", "description": "Water pump", "quantity": 1, "unit_price": 90.00, "total": 90.00, "part_number": "GAT-43134", "sort_order": 2},
            {"group_idx": 0, "type": "parts", "description": "Coolant (concentrate, 1 gal)", "quantity": 2, "unit_price": 22.50, "total": 45.00, "part_number": "ZER-G05", "sort_order": 3},
        ],
    },
}

for i, est_id in enumerate(estimate_ids):
    en = est_data[i]["estimate_number"]
    if en not in estimate_items:
        continue
    data = estimate_items[en]
    group_ids = []
    for g in data["groups"]:
        r = first(rest("job_groups", "POST", {
            "estimate_id": est_id, "shop_id": DEMO_SHOP_ID,
            "name": g["name"], "status": g["status"], "sort_order": g["sort_order"],
            "submitted_by": emp_id if g["status"] in ("submitted", "approved") else None,
        }))
        if r:
            group_ids.append(r["id"])
    for item in data["items"]:
        rest("estimate_line_items", "POST", {
            "estimate_id": est_id, "shop_id": DEMO_SHOP_ID,
            "job_group_id": group_ids[item["group_idx"]],
            "type": item["type"], "description": item["description"],
            "quantity": item["quantity"], "unit_price": item["unit_price"],
            "total": item["total"], "part_number": item.get("part_number"),
            "sort_order": item["sort_order"],
        })
print(f"    {sum(len(v['items']) for v in estimate_items.values())} line items across {sum(len(v['groups']) for v in estimate_items.values())} groups")

# ── Invoices ──
print("  Invoices...")
inv_data = [
    {"invoice_number": "INV-2026-0042", "customer_id": customer_ids[0], "vehicle_id": vehicle_ids[0],
     "estimate_id": estimate_ids[0], "status": "paid",
     "subtotal": 449.99, "tax_rate": 8.25, "tax_amount": 37.12, "total": 487.11,
     "paid_at": (now - timedelta(days=2)).isoformat(), "created_at": (now - timedelta(days=3)).isoformat(),
     "due_date": (now + timedelta(days=27)).isoformat()},
    {"invoice_number": "INV-2026-0043", "customer_id": customer_ids[3], "vehicle_id": vehicle_ids[5],
     "status": "sent", "subtotal": 199.98, "tax_rate": 8.25, "tax_amount": 16.50, "total": 216.48,
     "created_at": (now - timedelta(days=1)).isoformat(), "due_date": (now + timedelta(days=29)).isoformat()},
]
invoice_ids = []
for inv in inv_data:
    r = first(rest("invoices", "POST", {**inv, "shop_id": DEMO_SHOP_ID}))
    if r:
        invoice_ids.append(r["id"])
print(f"    {len(invoice_ids)} created")

# ── Invoice line items ──
print("  Invoice line items...")
invoice_items = {
    "INV-2026-0042": [
        {"type": "labor", "description": "Front brake pad replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 0},
        {"type": "part", "description": "Front brake pad set (ceramic)", "quantity": 1, "unit_price": 90.00, "total": 90.00, "sort_order": 1},
        {"type": "labor", "description": "Rear brake pad replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 2},
        {"type": "part", "description": "Rear brake pad set (ceramic)", "quantity": 1, "unit_price": 74.99, "total": 74.99, "sort_order": 3},
    ],
    "INV-2026-0043": [
        {"type": "labor", "description": "Spark plug replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 0},
        {"type": "part", "description": "Spark plug (NGK Laser Iridium)", "quantity": 4, "unit_price": 14.37, "total": 57.48, "sort_order": 1},
    ],
}
for i, inv_id in enumerate(invoice_ids):
    inn = inv_data[i]["invoice_number"]
    if inn in invoice_items:
        for item in invoice_items[inn]:
            rest("invoice_line_items", "POST", {
                "invoice_id": inv_id,
                "type": item["type"], "description": item["description"],
                "quantity": item["quantity"], "unit_price": item["unit_price"],
                "total": item["total"], "sort_order": item["sort_order"],
            })
print(f"    {sum(len(v) for v in invoice_items.values())} line items")

# ── Appointments ──
print("  Appointments...")
appointments = [
    {"customer_id": customer_ids[1], "vehicle_id": vehicle_ids[3], "scheduled_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"), "scheduled_time": "09:00", "duration_minutes": 60, "status": "confirmed", "service_notes": "Oil change + tire rotation"},
    {"customer_id": customer_ids[2], "vehicle_id": vehicle_ids[4], "scheduled_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"), "scheduled_time": "11:00", "duration_minutes": 60, "status": "confirmed", "service_notes": "A/C diagnostic — driver side blowing warm"},
    {"customer_id": customer_ids[4], "vehicle_id": vehicle_ids[6], "scheduled_date": (now + timedelta(days=2)).strftime("%Y-%m-%d"), "scheduled_time": "08:00", "duration_minutes": 300, "status": "scheduled", "service_notes": "Timing belt replacement — full day job"},
    {"customer_id": customer_ids[5], "vehicle_id": vehicle_ids[7], "scheduled_date": (now + timedelta(days=3)).strftime("%Y-%m-%d"), "scheduled_time": "10:00", "duration_minutes": 30, "status": "scheduled", "service_notes": "Oil change — synthetic"},
]
for a in appointments:
    rest("appointments", "POST", {**a, "shop_id": DEMO_SHOP_ID})
print(f"    {len(appointments)} created")

# ── DVI templates ──
print("  DVI templates...")
dvi_full = first(rest("dvi_templates", "POST", {
    "shop_id": DEMO_SHOP_ID, "name": "Full Vehicle Inspection",
    "description": "Complete 50-point vehicle inspection covering all major systems.", "is_default": True,
}))
if dvi_full:
    checkpoints_full = [
        ("Tires", "Tire tread depth - Front Left", "Measure tread depth in 32nds", "poor"),
        ("Tires", "Tire tread depth - Front Right", "Measure tread depth in 32nds", "poor"),
        ("Tires", "Tire tread depth - Rear Left", "Measure tread depth in 32nds", "poor"),
        ("Tires", "Tire tread depth - Rear Right", "Measure tread depth in 32nds", "poor"),
        ("Tires", "Tire pressure check", "Check and adjust all tire pressures", "fair"),
        ("Brakes", "Front brake pad thickness", "Measure pad thickness in mm", "poor"),
        ("Brakes", "Rear brake pad thickness", "Measure pad thickness in mm", "poor"),
        ("Brakes", "Brake rotor condition", "Check for scoring, warping, rust", "fair"),
        ("Brakes", "Brake fluid condition", "Test fluid for moisture content", "fair"),
        ("Suspension", "Shocks/struts - Front", "Check for leaks, bounce test", "fair"),
        ("Suspension", "Shocks/struts - Rear", "Check for leaks, bounce test", "fair"),
        ("Suspension", "Ball joints", "Check for play and boot condition", "poor"),
        ("Suspension", "Tie rod ends", "Check for play and boot condition", "poor"),
        ("Engine", "Oil level and condition", "Check dipstick, note color/level", "poor"),
        ("Engine", "Coolant level and condition", "Check reservoir, test concentration", "fair"),
        ("Engine", "Drive belt condition", "Check for cracks, glazing, wear", "fair"),
        ("Engine", "Air filter condition", "Check for dirt/debris", "fair"),
        ("Engine", "Battery test", "Load test battery, check terminals", "fair"),
        ("Electrical", "Headlights", "Check high/low beams", "fair"),
        ("Electrical", "Taillights and brake lights", "Check all rear lights", "fair"),
        ("Electrical", "Turn signals", "Check front and rear", "fair"),
        ("Electrical", "Windshield wipers", "Check blade condition and operation", "fair"),
        ("HVAC", "A/C performance", "Check vent temperature", "fair"),
        ("HVAC", "Heater performance", "Check heat output", "fair"),
        ("HVAC", "Cabin air filter", "Check for debris", "fair"),
        ("Safety", "Seat belts", "Check all belts latch and retract", "good"),
        ("Safety", "Horn", "Test operation", "good"),
        ("Safety", "Windshield condition", "Check for cracks/chips", "fair"),
        ("Underbody", "Exhaust system", "Check for leaks, rust, damage", "fair"),
        ("Underbody", "Fluid leaks", "Check for any visible leaks", "poor"),
    ]
    for i, (cat, name, desc, threshold) in enumerate(checkpoints_full):
        rest("dvi_checkpoints", "POST", {
            "template_id": dvi_full["id"], "name": name, "description": desc,
            "severity_threshold": threshold, "category": cat, "sort_order": i,
        })
    print(f"    Full Vehicle Inspection ({len(checkpoints_full)} checkpoints)")

dvi_brakes = first(rest("dvi_templates", "POST", {
    "shop_id": DEMO_SHOP_ID, "name": "Brake Inspection",
    "description": "Focused brake system inspection with pad measurements and rotor evaluation.", "is_default": True,
}))
if dvi_brakes:
    checkpoints_brakes = [
        ("Brakes", "Front left pad thickness", "Measure in mm", "poor"),
        ("Brakes", "Front right pad thickness", "Measure in mm", "poor"),
        ("Brakes", "Rear left pad thickness", "Measure in mm", "poor"),
        ("Brakes", "Rear right pad thickness", "Measure in mm", "poor"),
        ("Brakes", "Front rotor condition", "Check for scoring, lip, heat spots", "fair"),
        ("Brakes", "Rear rotor condition", "Check for scoring, lip, heat spots", "fair"),
        ("Brakes", "Brake fluid moisture", "Test with electronic tester", "fair"),
        ("Brakes", "Brake lines", "Check for cracks, leaks, corrosion", "poor"),
        ("Brakes", "Parking brake", "Test engagement and holding", "fair"),
    ]
    for i, (cat, name, desc, threshold) in enumerate(checkpoints_brakes):
        rest("dvi_checkpoints", "POST", {
            "template_id": dvi_brakes["id"], "name": name, "description": desc,
            "severity_threshold": threshold, "category": cat, "sort_order": i,
        })
    print(f"    Brake Inspection ({len(checkpoints_brakes)} checkpoints)")

# ── Knowledge base ──
print("  Knowledge base...")
kb_entries = [
    {"title": "Shop Warranty Policy", "content": "All repairs come with a 12-month/12,000-mile warranty on parts and labor. OEM parts carry the manufacturer's warranty. Customer-supplied parts are not covered under our warranty. If something isn't right, bring it back — we'll make it right.", "category": "general"},
    {"title": "After-Hours Drop-Off", "content": "Customers can drop off vehicles after hours using the key drop box located to the left of the main entrance. Place keys in an envelope with your name and phone number. We'll call you by 9 AM the next business day with an update.", "category": "general"},
    {"title": "Loaner Vehicle Policy", "content": "We have two loaner vehicles available for jobs expected to take more than 4 hours. Reserve at least 24 hours in advance. Must have valid driver's license and proof of insurance. No charge for loaners on jobs over $500.", "category": "general"},
    {"title": "Payment Methods", "content": "We accept cash, all major credit cards, debit cards, and checks (with valid ID). Financing available through Synchrony for repairs over $500. Payment is due upon completion unless prior arrangements have been made.", "category": "general"},
    {"title": "Texas State Inspection Info", "content": "Texas state inspections cost $25.50 for most passenger vehicles. We perform inspections Monday-Friday 8 AM - 4 PM, Saturday 9 AM - 1 PM. No appointment needed for inspections, but wait times are shorter before 10 AM.", "category": "procedure"},
    {"title": "Diesel Service Capabilities", "content": "We service all light-duty diesel trucks including Ford Power Stroke, Ram Cummins, and GM Duramax. We handle routine maintenance, fuel system service, emissions systems, and performance upgrades. We do NOT perform internal engine rebuilds on diesels — we refer those to Texas Diesel Specialists on Burnet Rd.", "category": "general"},
    {"title": "Common BMW Issues", "content": "For BMW vehicles, common issues we see: oil filter housing gasket leaks (N20/N55 engines), valve cover gasket leaks, electric water pump failures (usually 60-80K miles), and VANOS solenoid issues. We recommend OEM parts for all BMW repairs — aftermarket parts often cause problems on these vehicles.", "category": "diagnostic"},
    {"title": "Ford EcoBoost Maintenance", "content": "Ford EcoBoost engines (3.5L, 2.7L, 1.6L) require more frequent oil changes than the manual suggests — we recommend every 5,000 miles with full synthetic. Carbon buildup on intake valves is a known issue; we offer walnut blasting service. Always use Motorcraft or NGK spark plugs — aftermarket plugs cause misfire issues on these engines.", "category": "tip"},
]
for kb in kb_entries:
    rest("knowledge_base", "POST", {**kb, "shop_id": DEMO_SHOP_ID})
print(f"    {len(kb_entries)} created")

# ── Usage allowance ──
print("  Usage allowance...")
period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
if now.month == 12:
    period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
else:
    period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
rest("usage_allowances", "POST", {
    "shop_id": DEMO_SHOP_ID,
    "billing_period_start": period_start.isoformat(),
    "billing_period_end": period_end.isoformat(),
    "included_input_tokens": 100000, "included_output_tokens": 50000,
    "used_input_tokens": 0, "used_output_tokens": 0,
    "overage_input_tokens": 0, "overage_output_tokens": 0,
    "overage_input_rate_cents": 0, "overage_output_rate_cents": 0,
    "is_complimentary": True,
})

print(f"\n✅ Refresh complete!")
print(f"   Shop: Metro Auto Care ({DEMO_SHOP_ID})")
print(f"   Login: https://app.automotai.com/login")
print(f"   Email: {DEMO_EMAIL}")
print(f"   Password: {DEMO_PASSWORD}")
