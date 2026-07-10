"""
Add job groups and line items to existing demo estimates.
"""
import requests
import json

SUPABASE_URL = "https://hglbhncsdchfevxdbcoa.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnbGJobmNzZGNoZmV2eGRiY29hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDY1MjYzMCwiZXhwIjoyMDkwMjI4NjMwfQ.lgb_PQYZRnKJpbH8YRFu4xG6aqWsWYDiDDpjCRwRLmM"
DEMO_SHOP_ID = "75acac8a-adb6-493b-b310-ebc4c84d4aed"

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

# Get existing estimates
estimates = rest(f"estimates?shop_id=eq.{DEMO_SHOP_ID}&order=estimate_number.asc&select=id,estimate_number,status,subtotal,total")
if not estimates:
    print("No estimates found!")
    exit(1)

print(f"Found {len(estimates)} estimates")

# Get employee ID for submitted_by
emp = first(rest(f"employees?shop_id=eq.{DEMO_SHOP_ID}&select=id,name,roles"))
emp_id = emp["id"] if emp else None
print(f"Using employee: {emp['name'] if emp else 'none'} ({emp_id})")

# Define line items for each estimate
# EST-2026-0042: David's F-150 brake job (approved, $487.11)
# EST-2026-0043: Lisa's Camry oil change + tire rotation (awaiting_approval, $140.70)
# EST-2026-0044: Robert's BMW A/C diagnostic (draft, $97.41)
# EST-2026-0045: James's Ram timing belt (awaiting_approval, $865.99)

estimate_items = {
    "EST-2026-0042": {
        "groups": [
            {"name": "Brake Service - Front", "status": "approved", "sort_order": 0},
            {"name": "Brake Service - Rear", "status": "approved", "sort_order": 1},
        ],
        "items": [
            # Group 0: Front brakes
            {"group_idx": 0, "type": "labor", "description": "Front brake pad replacement - labor", "quantity": 1.5, "unit_price": 95.00, "total": 142.50, "sort_order": 0},
            {"group_idx": 0, "type": "parts", "description": "Front brake pad set (ceramic)", "quantity": 1, "unit_price": 89.99, "total": 89.99, "part_number": "FD-1414C", "sort_order": 1},
            # Group 1: Rear brakes
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
            {"group_idx": 0, "type": "parts", "description": "Full synthetic oil 5W-30 (6 qts)", "quantity": 6, "unit_price": 5.50, "total": 33.00, "part_number": "MOB1-5W30", "sort_order": 1},
            {"group_idx": 0, "type": "parts", "description": "Oil filter", "quantity": 1, "unit_price": 8.99, "total": 8.99, "part_number": "TOY-04152", "sort_order": 2},
            {"group_idx": 0, "type": "labor", "description": "Tire rotation & balance (labor)", "quantity": 0.5, "unit_price": 80.00, "total": 40.00, "sort_order": 3},
        ],
    },
    "EST-2026-0044": {
        "groups": [
            {"name": "A/C System Diagnostic", "status": "draft", "sort_order": 0},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "A/C system diagnostic - full inspection", "quantity": 1.0, "unit_price": 95.00, "total": 95.00, "sort_order": 0},
        ],
    },
    "EST-2026-0045": {
        "groups": [
            {"name": "Timing Belt Service", "status": "submitted", "sort_order": 0},
        ],
        "items": [
            {"group_idx": 0, "type": "labor", "description": "Timing belt replacement - labor (Cummins 6.7L)", "quantity": 5.0, "unit_price": 95.00, "total": 475.00, "sort_order": 0},
            {"group_idx": 0, "type": "parts", "description": "Timing belt kit (belt, tensioner, idler)", "quantity": 1, "unit_price": 189.99, "total": 189.99, "part_number": "GAT-TCK329", "sort_order": 1},
            {"group_idx": 0, "type": "parts", "description": "Water pump", "quantity": 1, "unit_price": 89.99, "total": 89.99, "part_number": "GAT-43134", "sort_order": 2},
            {"group_idx": 0, "type": "parts", "description": "Coolant (concentrate, 1 gal)", "quantity": 2, "unit_price": 22.50, "total": 45.00, "part_number": "ZER-G05", "sort_order": 3},
        ],
    },
}

for est in estimates:
    en = est["estimate_number"]
    if en not in estimate_items:
        print(f"  Skipping {en} — no items defined")
        continue

    data = estimate_items[en]
    print(f"\n📋 {en} ({est['status']}) — ${est['total']:.2f}")

    # Check if groups already exist
    existing_groups = rest(f"job_groups?estimate_id=eq.{est['id']}&select=id")
    if existing_groups and len(existing_groups) > 0:
        print(f"  Already has {len(existing_groups)} groups — skipping")
        continue

    # Create groups
    group_ids = []
    for g in data["groups"]:
        r = first(rest("job_groups", "POST", {
            "estimate_id": est["id"],
            "shop_id": DEMO_SHOP_ID,
            "name": g["name"],
            "status": g["status"],
            "sort_order": g["sort_order"],
            "submitted_by": emp_id if g["status"] in ("submitted", "approved") else None,
        }))
        if r:
            group_ids.append(r["id"])
            print(f"  ✓ Group: {g['name']} ({g['status']})")

    # Create line items
    for item in data["items"]:
        gid = group_ids[item["group_idx"]]
        r = rest("estimate_line_items", "POST", {
            "estimate_id": est["id"],
            "shop_id": DEMO_SHOP_ID,
            "job_group_id": gid,
            "type": item["type"],
            "description": item["description"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total": item["total"],
            "part_number": item.get("part_number"),
            "sort_order": item["sort_order"],
        })
        if r:
            print(f"    + {item['description']} — ${item['total']:.2f}")

print("\n✅ Done!")
