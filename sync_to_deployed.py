# -*- coding: utf-8 -*-
"""
Sinkronkan data konten lokal (db.sqlite3) ke database produksi (Supabase/PostgreSQL)
secara MERGE: menambah/memperbarui data demo tapi TIDAK menghapus data user asli
(user, booking, payment) yang ada di produksi. Aman dijalankan ulang (upsert).

Cara pakai:
    set DATABASE_URL=postgresql://... 
    python sync_to_deployed.py [path_ke_db.sqlite3]

WAJIB: jangan hardcode password di file ini. Selalu lewat environment variable.
"""
import os
import sqlite3
import sys
from collections import defaultdict

import psycopg2

PG = os.environ.get('DATABASE_URL')
if not PG:
    sys.exit("ERROR: set environment variable DATABASE_URL terlebih dahulu (postgresql://...)")

LOCAL = sys.argv[1] if len(sys.argv) > 1 else 'db.sqlite3'

lc = sqlite3.connect(LOCAL)
lc.row_factory = sqlite3.Row
lcur = lc.cursor()

pc = psycopg2.connect(PG)
pc.autocommit = False
pcur = pc.cursor()

cat_map = {}
loc_map = {}
healer_map = {}
summary = defaultdict(int)
BOOL_TABLES = {}


def qq(name):
    return '"%s"' % name


def bool_cols(table):
    if table not in BOOL_TABLES:
        pcur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name=%s AND data_type='boolean'""", (table,))
        BOOL_TABLES[table] = {r[0] for r in pcur.fetchall()}
    return BOOL_TABLES[table]


def cast_row(table, data):
    for c in data:
        v = data[c]
        if c in bool_cols(table) and v is not None:
            data[c] = bool(v)
    return data


def upsert_by_match(table, match_col, cols, row):
    pcur.execute("SELECT id FROM %s WHERE %s=%%s" % (table, qq(match_col)), (row[match_col],))
    found = pcur.fetchone()
    data = {c: (row[c] if c in row.keys() else None) for c in cols}
    cast_row(table, data)
    if found:
        sets = ','.join('%s=%%s' % qq(c) for c in cols)
        pcur.execute("UPDATE %s SET %s WHERE id=%%s" % (table, sets),
                     list(data.values()) + [found[0]])
        return found[0]
    icols = [qq(c) for c in data.keys()]
    placeholders = ','.join(['%s'] * len(icols))
    pcur.execute("INSERT INTO %s (%s) VALUES (%s) RETURNING id"
                 % (table, ','.join(icols), placeholders), list(data.values()))
    return pcur.fetchone()[0]


# 1. HealerCategory
lcur.execute("SELECT * FROM healers_healercategory")
for row in lcur.fetchall():
    cat_map[row['id']] = upsert_by_match('healers_healercategory', 'name',
                                         ['name', 'description', 'icon'], row)
summary['categories'] = len(cat_map)

# 2. Location
lcur.execute("SELECT * FROM healers_location")
for row in lcur.fetchall():
    loc_map[row['id']] = upsert_by_match(
        'healers_location', 'name',
        ['name', 'slug', 'description', 'gradient', 'healer_count', 'center_count'], row)
summary['locations'] = len(loc_map)

# 3. Speciality
lcur.execute("SELECT * FROM healers_speciality")
for row in lcur.fetchall():
    upsert_by_match('healers_speciality', 'name',
                    ['name', 'slug', 'emoji', 'description', 'order'], row)
summary['specialities'] = 8

# 4. Testimonial
lcur.execute("SELECT * FROM healers_testimonial")
n = 0
for row in lcur.fetchall():
    upsert_by_match('healers_testimonial', 'customer_name',
                    ['customer_name', 'rating', 'comment', 'date', 'is_featured'], row)
    n += 1
summary['testimonials'] = n

# 5. Payment method (dedupe + merge)
pcur.execute("SELECT id, name FROM payments_paymentmethod ORDER BY id")
by_name = defaultdict(list)
for pid, name in pcur.fetchall():
    by_name[name].append(pid)
for name, ids in by_name.items():
    if len(ids) > 1:
        keep = ids[0]
        for dup in ids[1:]:
            pcur.execute("UPDATE payments_payment SET payment_method_id=%s WHERE payment_method_id=%s",
                         (keep, dup))
            pcur.execute("DELETE FROM payments_paymentmethod WHERE id=%s", (dup,))
            summary['payment_method_dups_removed'] += 1
lcur.execute("SELECT * FROM payments_paymentmethod")
for row in lcur.fetchall():
    upsert_by_match('payments_paymentmethod', 'name',
                    ['name', 'description', 'icon', 'is_active', 'instructions'], row)
summary['payment_methods'] = 25

# 6. Healer
lcur.execute("SELECT * FROM healers_healer")
base_cols = ['name', 'slug', 'category_id', 'bio', 'experience_years', 'photo', 'phone',
             'email', 'address', 'price_idr', 'rating', 'is_available',
             'specializations', 'created_at', 'updated_at']
for row in lcur.fetchall():
    cat_id = cat_map.get(row['category_id'])
    pcur.execute("SELECT id FROM healers_healer WHERE slug=%s", (row['slug'],))
    found = pcur.fetchone()
    data = {c: (row[c] if c in row.keys() else None) for c in base_cols}
    data['category_id'] = cat_id
    data['photo'] = data['photo'] or ''
    cast_row('healers_healer', data)
    if found:
        sets = ','.join('%s=%%s' % qq(c) for c in base_cols)
        pcur.execute("UPDATE healers_healer SET %s WHERE id=%%s" % sets,
                     list(data.values()) + [found[0]])
        healer_map[row['id']] = found[0]
    else:
        icols = [qq(c) for c in (['user_id'] + base_cols)]
        placeholders = ','.join(['%s'] * len(data.values()))
        pcur.execute("INSERT INTO healers_healer (%s) VALUES (NULL,%s) RETURNING id"
                     % (','.join(icols), placeholders), list(data.values()))
        healer_map[row['id']] = pcur.fetchone()[0]
summary['healers'] = len(healer_map)

# 7. HealerSchedule
lcur.execute("SELECT * FROM healers_healerschedule")
n = 0
for row in lcur.fetchall():
    new_hid = healer_map.get(row['healer_id'])
    if new_hid is None:
        continue
    pcur.execute("""
        INSERT INTO healers_healerschedule (healer_id, day_of_week, start_time, end_time, is_active)
        VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (healer_id, day_of_week) DO UPDATE SET
            start_time=EXCLUDED.start_time, end_time=EXCLUDED.end_time, is_active=EXCLUDED.is_active
    """, (new_hid, row['day_of_week'], row['start_time'], row['end_time'], bool(row['is_active'])))
    n += 1
summary['schedules'] = n

# 8. HealingCenter
lcur.execute("SELECT * FROM healers_healingcenter")
base_cols = ['name', 'location_id', 'address', 'description', 'phone', 'email', 'photo',
             'rating', 'review_count', 'specializations', 'price_range',
             'min_price_idr', 'max_price_idr', 'has_google_badge', 'is_active', 'gradient']
for row in lcur.fetchall():
    loc_id = loc_map.get(row['location_id'])
    pcur.execute("SELECT id FROM healers_healingcenter WHERE slug=%s", (row['slug'],))
    found = pcur.fetchone()
    data = {c: (row[c] if c in row.keys() else None) for c in base_cols}
    data['location_id'] = loc_id
    data['photo'] = data['photo'] or ''
    cast_row('healers_healingcenter', data)
    if found:
        sets = ','.join('%s=%%s' % qq(c) for c in base_cols)
        pcur.execute("UPDATE healers_healingcenter SET %s WHERE id=%%s" % sets,
                     list(data.values()) + [found[0]])
    else:
        icols = [qq(c) for c in (base_cols + ['slug', 'created_at'])]
        placeholders = ','.join(['%s'] * len(icols))
        pcur.execute("INSERT INTO healers_healingcenter (%s) VALUES (%s)"
                     % (','.join(icols), placeholders),
                     list(data.values()) + [row['slug'], row['created_at']])
summary['centers'] = 3

# 9. HealerService (upsert by healer_id+name agar tidak dobel saat dijalankan ulang)
lcur.execute("SELECT * FROM healers_healerservice")
n = 0
for row in lcur.fetchall():
    new_hid = healer_map.get(row['healer_id'])
    if new_hid is None:
        continue
    pcur.execute("SELECT id FROM healers_healerservice WHERE healer_id=%s AND name=%s",
                 (new_hid, row['name']))
    found = pcur.fetchone()
    if found:
        pcur.execute("""
            UPDATE healers_healerservice SET description=%s, price_idr=%s,
                duration_minutes=%s, is_active=%s WHERE id=%s
        """, (row['description'], row['price_idr'], row['duration_minutes'],
              bool(row['is_active']), found[0]))
    else:
        pcur.execute("""
            INSERT INTO healers_healerservice
                (healer_id, name, description, price_idr, duration_minutes, is_active, "order", created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (new_hid, row['name'], row['description'], row['price_idr'],
              row['duration_minutes'], bool(row['is_active']), row['order'], row['created_at']))
    n += 1
summary['services'] = n

# 10. HealerPaymentSetting
lcur.execute("SELECT * FROM healers_healerpaymentsetting")
n = 0
for row in lcur.fetchall():
    new_hid = healer_map.get(row['healer_id'])
    if new_hid is None:
        continue
    pcur.execute("SELECT id FROM healers_healerpaymentsetting WHERE healer_id=%s", (new_hid,))
    if pcur.fetchone():
        continue
    pcur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='healers_healerpaymentsetting' ORDER BY ordinal_position""")
    cols = [r[0] for r in pcur.fetchall()]
    data = {c: (row[c] if c in row.keys() else None) for c in cols}
    data['healer_id'] = new_hid
    data.pop('id', None)
    cast_row('healers_healerpaymentsetting', data)
    icols = [qq(c) for c in data.keys()]
    placeholders = ','.join(['%s'] * len(icols))
    pcur.execute("INSERT INTO healers_healerpaymentsetting (%s) VALUES (%s)"
                 % (','.join(icols), placeholders), list(data.values()))
    n += 1
summary['healer_pay_settings'] = n

# 11. BankTransactionSetting
lcur.execute("SELECT * FROM healers_banktransactionsetting")
n = 0
for row in lcur.fetchall():
    new_hid = healer_map.get(row['healer_id'])
    if new_hid is None:
        continue
    pcur.execute("SELECT id FROM healers_banktransactionsetting WHERE healer_id=%s AND bank_code=%s",
                 (new_hid, row['bank_code']))
    if pcur.fetchone():
        continue
    pcur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='healers_banktransactionsetting' ORDER BY ordinal_position""")
    cols = [r[0] for r in pcur.fetchall()]
    data = {c: (row[c] if c in row.keys() else None) for c in cols}
    data['healer_id'] = new_hid
    data.pop('id', None)
    cast_row('healers_banktransactionsetting', data)
    icols = [qq(c) for c in data.keys()]
    placeholders = ','.join(['%s'] * len(icols))
    pcur.execute("INSERT INTO healers_banktransactionsetting (%s) VALUES (%s)"
                 % (','.join(icols), placeholders), list(data.values()))
    n += 1
summary['bank_txn_settings'] = n

pc.commit()
print("SYNC OK:")
for k, v in sorted(summary.items()):
    print("  %s: %s" % (k, v))

lc.close()
pc.close()
