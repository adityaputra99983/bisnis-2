import decimal
from django.core.management.base import BaseCommand
from django.db import connection


DECIMAL_TABLES = {
    'healers_healer': {'price_idr': (12, 2), 'rating': (3, 2)},
    'healers_healerservice': {'price_idr': (12, 2)},
    'bookings_booking': {'total_price_idr': (12, 2), 'total_price_converted': (12, 2)},
    'payments_payment': {'amount_idr': (12, 2), 'amount_converted': (12, 2), 'exchange_rate': (15, 6)},
    'payments_currency': {'rate_to_idr': (15, 6)},
}


class Command(BaseCommand):
    help = 'Scan DecimalField columns for values exceeding max_digits or non-numeric values, and delete corrupted rows'

    def handle(self, *args, **options):
        total_deleted = 0
        with connection.cursor() as cursor:
            for table, columns in DECIMAL_TABLES.items():
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [table])
                if not cursor.fetchone():
                    continue
                for col, (max_digits, decimal_places) in columns.items():
                    cursor.execute("SELECT id, [%s] FROM [%s] WHERE [%s] IS NOT NULL AND [%s] != ''" % (col, table, col, col))
                    rows = cursor.fetchall()
                    bad_ids = []
                    for row_id, value in rows:
                        if value is None or value == '':
                            bad_ids.append(row_id)
                            continue
                        try:
                            d = decimal.Decimal(str(value))
                        except (decimal.InvalidOperation, ValueError):
                            bad_ids.append(row_id)
                            continue
                        try:
                            max_whole = max_digits - decimal_places
                            max_val = decimal.Decimal(10) ** max_whole - decimal.Decimal(10) ** (-decimal_places)
                            min_val = -(decimal.Decimal(10) ** max_whole)
                            if d > max_val or d < min_val:
                                bad_ids.append(row_id)
                        except (decimal.InvalidOperation, ValueError):
                            bad_ids.append(row_id)
                    for bad_id in bad_ids:
                        cursor.execute("DELETE FROM [%s] WHERE id = %%s" % table, (bad_id,))
                        total_deleted += 1
                        self.stdout.write(self.style.WARNING(
                            f'Deleted corrupted row from {table}.{col}: id={bad_id}'
                        ))
                    if not bad_ids:
                        self.stdout.write(self.style.SUCCESS(f'OK: {table}.{col} - no corruption'))
        if total_deleted == 0:
            self.stdout.write(self.style.SUCCESS('No corrupted data found. Database is clean.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nTotal deleted: {total_deleted} corrupted row(s)'))
