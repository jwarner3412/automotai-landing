"""
Fix demo estimate line items (correct math) and add invoice line items.
"""
import requests

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

# Get estimates and invoices
estimates = rest(f"estimates?shop_id=eq.{DEMO_SHOP_ID}&order=estimate_number.asc&select=id,estimate_number,status,subtotal,total")
invoices = rest(f"invoices?shop_id=eq.{DEMO_SHOP_ID}&order=invoice_number.asc&select=id,invoice_number,status,subtotal,total,estimate_id")

print(f"Estimates: {[(e['estimate_number'], e['status']) for e in (estimates or [])]}")
print(f"Invoices: {[(i['invoice_number'], i['status']) for i in (invoices or [])]}")

# Get employee for submitted_by
emp = first(rest(f"employees?shop_id=eq.{DEMO_SHOP_ID}&user_id=not.is.null&select=id"))
emp_id = emp["id"] if emp else None

# ── Nuke existing groups + line items ──
print("\n🧹 Nuking existing groups and line items...")
for est in (estimates or []):
    # Delete line items
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/estimate_line_items?estimate_id=eq.{est['id']}", headers=headers)
    print(f"  Deleted line items for {est['estimate_number']}: {r.status_code}")
    # Delete groups
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/job_groups?estimate_id=eq.{est['id']}", headers=headers)
    print(f"  Deleted groups for {est['estimate_number']}: {r.status_code}")

for inv in (invoices or []):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/invoice_line_items?invoice_id=eq.{inv['id']}", headers=headers)
    print(f"  Deleted line items for {inv['invoice_number']}: {r.status_code}")

# ── Re-create with correct math ──
# EST-2026-0042: $449.99 subtotal
#   Front: labor $142.50 + parts $90.00 = $232.50
#   Rear:  labor $142.50 + parts $74.99 = $217.49
#   Total: $449.99 ✓

# EST-2026-0043: $129.98 subtotal
#   Oil labor $47.50 + oil $34.98 + filter $7.50 + rotation $40.00 = $129.98 ✓

# EST-2026-0044: $89.99 subtotal
#   A/C diagnostic $89.99 ✓

# EST-2026-0045: $799.99 subtotal
#   Labor $475.00 + belt kit $189.99 + water pump $90.00 + coolant $45.00 = $799.99 ✓

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

# Invoice line items
# INV-2026-0042: from EST-2026-0042 (paid, $487.11)
# INV-2026-0043: spark plug job for Maria's CR-V (sent, $216.49)
#   Labor $142.50 + plugs $57.49 = $199.99 ✓

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

# Fix INV-2026-0043 subtotal to match line items (199.98, not 199.99)
for inv in (invoices or []):
    if inv["invoice_number"] == "INV-2026-0043":
        new_subtotal = 199.98
        new_tax = round(new_subtotal * 0.0825, 2)  # 16.50
        new_total = new_subtotal + new_tax  # 216.48
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/invoices?id=eq.{inv['id']}",
            headers=headers,
            json={"subtotal": new_subtotal, "tax_amount": new_tax, "total": new_total},
        )
        print(f"  Fixed INV-2026-0043: subtotal={new_subtotal}, tax={new_tax}, total={new_total} ({r.status_code})")
        inv["subtotal"] = new_subtotal
        inv["total"] = new_total

# ── Create estimate groups + line items ──
print("\n📋 Estimates:")
for est in (estimates or []):
    en = est["estimate_number"]
    if en not in estimate_items:
        continue
    data = estimate_items[en]
    print(f"  {en} ({est['status']}) — ${est['subtotal']:.2f}")

    # Create groups
    group_ids = []
    for g in data["groups"]:
        r = first(rest("job_groups", "POST", {
            "estimate_id": est["id"], "shop_id": DEMO_SHOP_ID,
            "name": g["name"], "status": g["status"], "sort_order": g["sort_order"],
            "submitted_by": emp_id if g["status"] in ("submitted", "approved") else None,
        }))
        if r:
            group_ids.append(r["id"])

    # Create line items
    item_sum = 0
    for item in data["items"]:
        r = rest("estimate_line_items", "POST", {
            "estimate_id": est["id"], "shop_id": DEMO_SHOP_ID,
            "job_group_id": group_ids[item["group_idx"]],
            "type": item["type"], "description": item["description"],
            "quantity": item["quantity"], "unit_price": item["unit_price"],
            "total": item["total"], "part_number": item.get("part_number"),
            "sort_order": item["sort_order"],
        })
        item_sum += item["total"]
    print(f"    Line item sum: ${item_sum:.2f} (subtotal: ${est['subtotal']:.2f}) {'✓' if abs(item_sum - float(est['subtotal'])) < 0.02 else '✗ MISMATCH!'}")

# ── Create invoice line items ──
print("\n🧾 Invoices:")
for inv in (invoices or []):
    inn = inv["invoice_number"]
    if inn not in invoice_items:
        continue
    data = invoice_items[inn]
    print(f"  {inn} ({inv['status']}) — ${inv['subtotal']:.2f}")

    item_sum = 0
    for item in data:
        r = rest("invoice_line_items", "POST", {
            "invoice_id": inv["id"],
            "type": item["type"], "description": item["description"],
            "quantity": item["quantity"], "unit_price": item["unit_price"],
            "total": item["total"], "sort_order": item["sort_order"],
        })
        item_sum += item["total"]
    print(f"    Line item sum: ${item_sum:.2f} (subtotal: ${inv['subtotal']:.2f}) {'✓' if abs(item_sum - float(inv['subtotal'])) < 0.02 else '✗ MISMATCH!'}")

print("\n✅ Done!")
