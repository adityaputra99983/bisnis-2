from django.db import migrations


CURRENCIES = [
    {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'rate_to_idr': '0.000230'},
    {'code': 'AFN', 'name': 'Afghan Afghani', 'symbol': '؋', 'rate_to_idr': '0.005400'},
    {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'rate_to_idr': '0.000096'},
    {'code': 'BDT', 'name': 'Bangladeshi Taka', 'symbol': '৳', 'rate_to_idr': '0.006800'},
    {'code': 'BGN', 'name': 'Bulgarian Lev', 'symbol': 'лв', 'rate_to_idr': '0.000110'},
    {'code': 'BHD', 'name': 'Bahraini Dinar', 'symbol': '.د.ب', 'rate_to_idr': '0.000024'},
    {'code': 'BND', 'name': 'Brunei Dollar', 'symbol': 'B$', 'rate_to_idr': '0.000085'},
    {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$', 'rate_to_idr': '0.000310'},
    {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'rate_to_idr': '0.000086'},
    {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF', 'rate_to_idr': '0.000057'},
    {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'rate_to_idr': '0.000460'},
    {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč', 'rate_to_idr': '0.001400'},
    {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr', 'rate_to_idr': '0.000430'},
    {'code': 'EGP', 'name': 'Egyptian Pound', 'symbol': '£', 'rate_to_idr': '0.003100'},
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'rate_to_idr': '0.000058'},
    {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'rate_to_idr': '0.000050'},
    {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'rate_to_idr': '0.000490'},
    {'code': 'HUF', 'name': 'Hungarian Forint', 'symbol': 'Ft', 'rate_to_idr': '0.022000'},
    {'code': 'IDR', 'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'rate_to_idr': '1.000000'},
    {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'rate_to_idr': '0.005300'},
    {'code': 'ISK', 'name': 'Icelandic Króna', 'symbol': 'kr', 'rate_to_idr': '0.008700'},
    {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'rate_to_idr': '0.009600'},
    {'code': 'KES', 'name': 'Kenyan Shilling', 'symbol': 'KSh', 'rate_to_idr': '0.000810'},
    {'code': 'KHR', 'name': 'Cambodian Riel', 'symbol': '៛', 'rate_to_idr': '0.000250'},
    {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩', 'rate_to_idr': '0.083000'},
    {'code': 'KWD', 'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'rate_to_idr': '0.000019'},
    {'code': 'KZT', 'name': 'Kazakhstani Tenge', 'symbol': '₸', 'rate_to_idr': '0.000300'},
    {'code': 'LAK', 'name': 'Lao Kip', 'symbol': '₭', 'rate_to_idr': '1.340000'},
    {'code': 'LKR', 'name': 'Sri Lankan Rupee', 'symbol': 'Rs', 'rate_to_idr': '0.019000'},
    {'code': 'MMK', 'name': 'Myanmar Kyat', 'symbol': 'K', 'rate_to_idr': '0.000130'},
    {'code': 'MNT', 'name': 'Mongolian Tögrög', 'symbol': '₮', 'rate_to_idr': '0.220000'},
    {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': 'Mex$', 'rate_to_idr': '0.001100'},
    {'code': 'MYR', 'name': 'Malaysian Ringgit', 'symbol': 'RM', 'rate_to_idr': '0.000290'},
    {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦', 'rate_to_idr': '0.000100'},
    {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr', 'rate_to_idr': '0.000670'},
    {'code': 'NZD', 'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'rate_to_idr': '0.000100'},
    {'code': 'OMR', 'name': 'Omani Rial', 'symbol': 'ر.ع.', 'rate_to_idr': '0.000024'},
    {'code': 'PHP', 'name': 'Philippine Peso', 'symbol': '₱', 'rate_to_idr': '0.003500'},
    {'code': 'PKR', 'name': 'Pakistani Rupee', 'symbol': '₨', 'rate_to_idr': '0.017000'},
    {'code': 'PLN', 'name': 'Polish Zloty', 'symbol': 'zł', 'rate_to_idr': '0.000250'},
    {'code': 'QAR', 'name': 'Qatari Riyal', 'symbol': 'ر.ق', 'rate_to_idr': '0.000230'},
    {'code': 'RON', 'name': 'Romanian Leu', 'symbol': 'lei', 'rate_to_idr': '0.000290'},
    {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽', 'rate_to_idr': '0.005800'},
    {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': '﷼', 'rate_to_idr': '0.000240'},
    {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr', 'rate_to_idr': '0.000660'},
    {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$', 'rate_to_idr': '0.000085'},
    {'code': 'THB', 'name': 'Thai Baht', 'symbol': '฿', 'rate_to_idr': '0.002200'},
    {'code': 'TRY', 'name': 'Turkish Lira', 'symbol': '₺', 'rate_to_idr': '0.002100'},
    {'code': 'TWD', 'name': 'New Taiwan Dollar', 'symbol': 'NT$', 'rate_to_idr': '0.002000'},
    {'code': 'UAH', 'name': 'Ukrainian Hryvnia', 'symbol': '₴', 'rate_to_idr': '0.002600'},
    {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'rate_to_idr': '0.000063'},
    {'code': 'VND', 'name': 'Vietnamese Dong', 'symbol': '₫', 'rate_to_idr': '1.560000'},
    {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'rate_to_idr': '0.001200'},
]


def seed_currencies(apps, schema_editor):
    Currency = apps.get_model('payments', 'Currency')
    for data in CURRENCIES:
        Currency.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'symbol': data['symbol'],
                'rate_to_idr': data['rate_to_idr'],
                'is_active': True,
            }
        )


def reverse_seed(apps, schema_editor):
    Currency = apps.get_model('payments', 'Currency')
    Currency.objects.filter(code__in=[c['code'] for c in CURRENCIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_alter_payment_payment_code'),
    ]

    operations = [
        migrations.RunPython(seed_currencies, reverse_seed),
    ]
