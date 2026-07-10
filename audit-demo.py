#!/usr/bin/env python3
"""Audit demo shop data for correctness."""
import json, subprocess, sys

KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnbGJobmNzZGNoZmV2eGRiY29hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDY1MjYzMCwiZXhwIjoyMDkwMjI4NjMwfQ.lgb_PQYZRnKJpbH8YRFu4xG6aqWsWYDiDDpjCRwRLmM"
URL = "https://hglbhncsdchfevxdbcoa.supabase.co/rest/v1"
SHOP = "75acac8a-adb6-493b-b310-ebc4c84d4aed"
H = f"apikey: {KEY}\nAuthorization: Bearer {KEY}"

def get(path):
    r = subprocess.run(["curl", "-s", f"{URL}/{path}", "-H", H], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout)
    except:
        return []

issues = []

# ── Shop ──
shop = get(f"shops?id=eq.{SHOP}&select=name,slug,phone,address,city,state,zip,labor_rate,tax_rate,tax_labor,onboarding_complete,complimentary")
s = shop[0] if shop else {}
print("=== SHOP ===")
print(f"  {s.get('name')} | {s.get('address')}, {s.get('city')}, {s.get('state')} {s.get('zip')}")
print(f"  Labor: ${s.get('labor_rate')}/hr | Tax: {s.get('tax_rate')}% | Tax labor: {s.get('tax_labor')}")
print(f"  Onboarding: {s.get('onboarding_complete')} | Complimentary: {s.get('complimentary')}")
if not s.get('onboarding_complete'):
    issues.append("Shop onboarding NOT complete — user will hit wizard on login")
if not s.get('complimentary'):
    issues.append("Shop NOT complimentary — demo users will hit billing wall")

# ── Employees ──
emps = get(f"employees?shop_id=eq.{SHOP}&select=name,email,roles,is_active,user_id")
print(f"\n=== EMPLOYEES ({len(emps)}) ===")
has_owner = False
for e in emps:
    print(f"  {e['name']} — {e['email']} — roles={e['roles']} — active={e['is_active']} — has_user={bool(e.get('user_id'))}")
    if 'owner' in e.get('roles', []):
        has_owner = True
if not has_owner:
    issues.append("No owner employee — permissions may be broken")

# ── Customers ──
custs = get(f"customers?shop_id=eq.{SHOP}&select=id,name,email,phone,notes")
print(f"\n=== CUSTOMERS ({len(custs)}) ===")
for c in custs:
    print(f"  {c['name']} — {c['email']} — {c['phone']}")
if len(custs) < 3:
    issues.append(f"Only {len(custs)} customers — looks sparse")

# ── Vehicles ──
vehs = get(f"vehicles?shop_id=eq.{SHOP}&select=id,make,model,year,vin,license_plate,mileage,color,customer_id")
print(f"\n=== VEHICLES ({len(vehs)}) ===")
for v in vehs:
    cust = next((c for c in custs if c['id'] == v['customer_id']), None)
    print(f"  {v['year']} {v['make']} {v['model']} — {v['license_plate']} — {v['mileage']:,}mi — {cust['name'] if cust else 'ORPHAN'}")
    if not cust:
        issues.append(f"Vehicle {v['year']} {v['make']} {v['model']} has no customer match")

# ── Estimates ──
ests = get(f"estimates?shop_id=eq.{SHOP}&order=estimate_number.asc&select=id,estimate_number,status,subtotal,tax_rate,tax_amount,total,customer_id,vehicle_id,notes")
print(f"\n=== ESTIMATES ({len(ests)}) ===")
for e in ests:
    cust = next((c for c in custs if c['id'] == e['customer_id']), None)
    veh = next((v for v in vehs if v['id'] == e['vehicle_id']), None)
    items = get(f"estimate_line_items?estimate_id=eq.{e['id']}&select=type,description,quantity,unit_price,total")
    groups = get(f"job_groups?estimate_id=eq.{e['id']}&select=name,status")
    item_sum = sum(i['total'] for i in items)
    expected_tax = round(e['subtotal'] * 0.0825, 2)
    expected_total = round(e['subtotal'] + e['tax_amount'], 2)
    
    print(f"\n  {e['estimate_number']} ({e['status']}) — {cust['name'] if cust else '?'} / {veh['year']} {veh['make']} {veh['model']} — ${e['subtotal']:.2f} + ${e['tax_amount']:.2f} = ${e['total']:.2f}")
    
    tax_ok = abs(e['tax_amount'] - expected_tax) < 0.02
    total_ok = abs(e['total'] - expected_total) < 0.02
    line_ok = abs(item_sum - e['subtotal']) < 0.02
    
    if not tax_ok:
        issues.append(f"{e['estimate_number']}: tax ${e['tax_amount']} != expected ${expected_tax}")
    if not total_ok:
        issues.append(f"{e['estimate_number']}: total ${e['total']} != expected ${expected_total}")
    if not line_ok:
        issues.append(f"{e['estimate_number']}: line sum ${item_sum:.2f} != subtotal ${e['subtotal']:.2f}")
    if not items:
        issues.append(f"{e['estimate_number']}: NO LINE ITEMS")
    if not groups:
        issues.append(f"{e['estimate_number']}: NO JOB GROUPS")
    
    print(f"    Tax: {'✓' if tax_ok else '✗'} | Total: {'✓' if total_ok else '✗'} | Lines: ${item_sum:.2f} {'✓' if line_ok else '✗'} | Groups: {len(groups)} | Items: {len(items)}")
    for g in groups:
        print(f"    └ {g['name']} ({g['status']})")
    for i in items:
        print(f"       {i['type']:6} {i['description']:50} x{i['quantity']} @ ${i['unit_price']:.2f} = ${i['total']:.2f}")

# ── Invoices ──
invs = get(f"invoices?shop_id=eq.{SHOP}&order=invoice_number.asc&select=id,invoice_number,status,subtotal,tax_rate,tax_amount,total,customer_id,vehicle_id,estimate_id,paid_at,due_date")
print(f"\n=== INVOICES ({len(invs)}) ===")
for inv in invs:
    cust = next((c for c in custs if c['id'] == inv['customer_id']), None)
    veh = next((v for v in vehs if v['id'] == inv['vehicle_id']), None)
    items = get(f"invoice_line_items?invoice_id=eq.{inv['id']}&select=type,description,quantity,unit_price,total")
    item_sum = sum(i['total'] for i in items)
    expected_tax = round(inv['subtotal'] * 0.0825, 2)
    expected_total = round(inv['subtotal'] + inv['tax_amount'], 2)
    
    print(f"\n  {inv['invoice_number']} ({inv['status']}) — {cust['name'] if cust else '?'} / {veh['year']} {veh['make']} {veh['model']} — ${inv['subtotal']:.2f} + ${inv['tax_amount']:.2f} = ${inv['total']:.2f}")
    
    tax_ok = abs(inv['tax_amount'] - expected_tax) < 0.02
    total_ok = abs(inv['total'] - expected_total) < 0.02
    line_ok = abs(item_sum - inv['subtotal']) < 0.02
    
    if not tax_ok:
        issues.append(f"{inv['invoice_number']}: tax ${inv['tax_amount']} != expected ${expected_tax}")
    if not total_ok:
        issues.append(f"{inv['invoice_number']}: total ${inv['total']} != expected ${expected_total}")
    if not line_ok:
        issues.append(f"{inv['invoice_number']}: line sum ${item_sum:.2f} != subtotal ${inv['subtotal']:.2f}")
    if not items:
        issues.append(f"{inv['invoice_number']}: NO LINE ITEMS")
    
    print(f"    Tax: {'✓' if tax_ok else '✗'} | Total: {'✓' if total_ok else '✗'} | Lines: ${item_sum:.2f} {'✓' if line_ok else '✗'} | Items: {len(items)}")
    for i in items:
        print(f"       {i['type']:6} {i['description']:50} x{i['quantity']} @ ${i['unit_price']:.2f} = ${i['total']:.2f}")
    if inv.get('paid_at'):
        print(f"    Paid: {inv['paid_at']}")
    if inv.get('due_date'):
        print(f"    Due: {inv['due_date']}")

# ── Appointments ──
appts = get(f"appointments?shop_id=eq.{SHOP}&order=scheduled_date.asc,scheduled_time.asc&select=scheduled_date,scheduled_time,duration_minutes,status,service_notes,customer_id,vehicle_id")
print(f"\n=== APPOINTMENTS ({len(appts)}) ===")
for a in appts:
    cust = next((c for c in custs if c['id'] == a['customer_id']), None)
    veh = next((v for v in vehs if v['id'] == a['vehicle_id']), None)
    print(f"  {a['scheduled_date']} {a['scheduled_time']} ({a['duration_minutes']}min) — {a['status']:12} — {cust['name'] if cust else '?'} / {veh['year']} {veh['make']} {veh['model']} — {a['service_notes']}")

# ── Service templates ──
svcs = get(f"service_templates?shop_id=eq.{SHOP}&select=name,category")
print(f"\n=== SERVICE TEMPLATES ({len(svcs)}) ===")
for s in svcs:
    print(f"  [{s['category']:15}] {s['name']}")

# ── DVI ──
dvis = get(f"dvi_templates?shop_id=eq.{SHOP}&select=id,name")
print(f"\n=== DVI TEMPLATES ({len(dvis)}) ===")
for d in dvis:
    cps = get(f"dvi_checkpoints?template_id=eq.{d['id']}&select=name,category")
    print(f"  {d['name']} ({len(cps)} checkpoints)")

# ── KB ──
kbs = get(f"knowledge_base?shop_id=eq.{SHOP}&select=title,category")
print(f"\n=== KNOWLEDGE BASE ({len(kbs)}) ===")
for k in kbs:
    print(f"  [{k['category']:12}] {k['title']}")

# ── Usage ──
ua = get(f"usage_allowances?shop_id=eq.{SHOP}&select=included_input_tokens,included_output_tokens,is_complimentary")
print(f"\n=== USAGE ({len(ua)}) ===")
for u in ua:
    print(f"  Complimentary: {u['is_complimentary']} | Input: {u['included_input_tokens']:,} | Output: {u['included_output_tokens']:,}")

# ── Summary ──
print(f"\n{'='*60}")
if issues:
    print(f"❌ {len(issues)} ISSUES FOUND:")
    for i in issues:
        print(f"  • {i}")
else:
    print("✅ NO ISSUES FOUND")
