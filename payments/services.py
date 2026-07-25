from decimal import Decimal
from django.core.cache import cache
from .models import Currency

EXCHANGE_RATES_CACHE_KEY = 'exchange_rates_all'
EXCHANGE_RATES_CACHE_TIMEOUT = 600

EXCHANGE_RATES_FALLBACK = {
    'IDR': 1.0,
    'USD': 0.000063,
    'EUR': 0.000058,
    'GBP': 0.000050,
    'CNY': 0.00046,
    'JPY': 0.0096,
    'SGD': 0.000085,
    'MYR': 0.00029,
    'AUD': 0.000096,
    'CAD': 0.000086,
    'CHF': 0.000057,
    'KRW': 0.083,
    'THB': 0.0022,
    'PHP': 0.0035,
    'VND': 1.56,
    'INR': 0.0053,
    'RUB': 0.0058,
    'SAR': 0.00024,
    'AED': 0.00023,
    'QAR': 0.00023,
    'BHD': 0.000024,
    'KWD': 0.000019,
    'OMR': 0.000024,
    'PKR': 0.017,
    'BDT': 0.0068,
    'NZD': 0.00010,
    'HKD': 0.00049,
    'TWD': 0.0020,
    'TRY': 0.0021,
    'ZAR': 0.0012,
    'BRL': 0.00031,
    'MXN': 0.0011,
    'EGP': 0.0031,
    'NGN': 0.00010,
    'KES': 0.00081,
    'GHS': 0.0010,
    'UGX': 0.00024,
    'TZS': 0.00016,
    'ETB': 0.00035,
    'CZK': 0.0014,
    'PLN': 0.00025,
    'HUF': 0.022,
    'SEK': 0.00066,
    'NOK': 0.00067,
    'DKK': 0.00043,
    'ISK': 0.0087,
    'BGN': 0.00011,
    'RON': 0.00029,
    'HRK': 0.00043,
    'RSD': 0.0065,
    'UAH': 0.0026,
    'BYN': 0.00020,
    'KZT': 0.00030,
    'UZS': 0.000078,
    'AFN': 0.0054,
    'LKR': 0.019,
    'MMK': 0.00013,
    'KHR': 0.00025,
    'LAK': 1.34,
    'MNT': 0.22,
    'BND': 0.000085,
    'FJD': 0.00014,
    'PGK': 0.00025,
    'WST': 0.00017,
    'TOP': 0.00015,
    'VUV': 0.00076,
    'SBD': 0.00052,
    'IDR': 1.0,
}

CURRENCY_NAMES = {
    'IDR': 'Indonesian Rupiah',
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound Sterling',
    'CNY': 'Chinese Yuan',
    'JPY': 'Japanese Yen',
    'SGD': 'Singapore Dollar',
    'MYR': 'Malaysian Ringgit',
    'AUD': 'Australian Dollar',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'KRW': 'South Korean Won',
    'THB': 'Thai Baht',
    'PHP': 'Philippine Peso',
    'VND': 'Vietnamese Dong',
    'INR': 'Indian Rupee',
    'RUB': 'Russian Ruble',
    'SAR': 'Saudi Riyal',
    'AED': 'UAE Dirham',
    'QAR': 'Qatari Riyal',
    'BHD': 'Bahraini Dinar',
    'KWD': 'Kuwaiti Dinar',
    'OMR': 'Omani Rial',
    'PKR': 'Pakistani Rupee',
    'BDT': 'Bangladeshi Taka',
    'NZD': 'New Zealand Dollar',
    'HKD': 'Hong Kong Dollar',
    'TWD': 'New Taiwan Dollar',
    'TRY': 'Turkish Lira',
    'ZAR': 'South African Rand',
    'BRL': 'Brazilian Real',
    'MXN': 'Mexican Peso',
    'EGP': 'Egyptian Pound',
    'NGN': 'Nigerian Naira',
    'KES': 'Kenyan Shilling',
    'GHS': 'Ghanaian Cedi',
    'UGX': 'Ugandan Shilling',
    'TZS': 'Tanzanian Shilling',
    'ETB': 'Ethiopian Birr',
    'CZK': 'Czech Koruna',
    'PLN': 'Polish Zloty',
    'HUF': 'Hungarian Forint',
    'SEK': 'Swedish Krona',
    'NOK': 'Norwegian Krone',
    'DKK': 'Danish Krone',
    'ISK': 'Icelandic Krona',
    'BGN': 'Bulgarian Lev',
    'RON': 'Romanian Leu',
    'HRK': 'Croatian Kuna',
    'RSD': 'Serbian Dinar',
    'UAH': 'Ukrainian Hryvnia',
    'BYN': 'Belarusian Ruble',
    'KZT': 'Kazakhstani Tenge',
    'UZS': 'Uzbekistani Som',
    'AFN': 'Afghan Afghani',
    'LKR': 'Sri Lankan Rupee',
    'MMK': 'Myanmar Kyat',
    'KHR': 'Cambodian Riel',
    'LAK': 'Lao Kip',
    'MNT': 'Mongolian Tugrik',
    'BND': 'Brunei Dollar',
    'FJD': 'Fijian Dollar',
    'PGK': 'Papua New Guinean Kina',
    'WST': 'Samoan Tala',
    'TOP': 'Tongan Pa\u02BBanga',
    'VUV': 'Vanuatu Vatu',
    'SBD': 'Solomon Islands Dollar',
}

CURRENCY_SYMBOLS = {
    'IDR': 'Rp',
    'USD': '$',
    'EUR': '\u20ac',
    'GBP': '\u00a3',
    'CNY': '\u00a5',
    'JPY': '\u00a5',
    'SGD': 'S$',
    'MYR': 'RM',
    'AUD': 'A$',
    'CAD': 'C$',
    'CHF': 'CHF',
    'KRW': '\u20a9',
    'THB': '\u0e3f',
    'PHP': '\u20b1',
    'VND': '\u20ab',
    'INR': '\u20b9',
    'RUB': '\u20bd',
    'SAR': '\ufdfc',
    'AED': 'AED',
    'QAR': 'QAR',
    'BHD': 'BHD',
    'KWD': 'KWD',
    'OMR': 'OMR',
    'PKR': '\u20a8',
    'BDT': '\u09f3',
    'NZD': 'NZ$',
    'HKD': 'HK$',
    'TWD': 'NT$',
    'TRY': '\u20ba',
    'ZAR': 'R',
    'BRL': 'R$',
    'MXN': 'MX$',
    'EGP': 'E\u00a3',
    'NGN': '\u20a6',
    'KES': 'KSh',
    'GHS': 'GH\u20b5',
    'UGX': 'USh',
    'TZS': 'TSh',
    'ETB': 'Br',
    'CZK': 'K\u010d',
    'PLN': 'z\u0142',
    'HUF': 'Ft',
    'SEK': 'kr',
    'NOK': 'kr',
    'DKK': 'kr',
    'ISK': 'kr',
    'BGN': '\u043b\u0432',
    'RON': 'lei',
    'HRK': 'kn',
    'RSD': 'din',
    'UAH': '\u20b4',
    'BYN': 'Br',
    'KZT': '\u20b8',
    'UZS': 'so\u02bcm',
    'AFN': '\u060b',
    'LKR': 'Rs',
    'MMK': 'K',
    'KHR': '\u17db',
    'LAK': '\u20ad',
    'MNT': '\u20ae',
    'BND': 'B$',
    'FJD': 'FJ$',
    'PGK': 'K',
    'WST': 'WS$',
    'TOP': 'T$',
    'VUV': 'VT',
    'SBD': 'SI$',
}


def get_exchange_rates():
    cached = cache.get(EXCHANGE_RATES_CACHE_KEY)
    if cached:
        return cached
    rates = {}
    try:
        for currency in Currency.objects.filter(is_active=True):
            rates[currency.code] = float(currency.rate_to_idr)
    except Exception:
        pass
    if not rates:
        rates = EXCHANGE_RATES_FALLBACK.copy()
    cache.set(EXCHANGE_RATES_CACHE_KEY, rates, EXCHANGE_RATES_CACHE_TIMEOUT)
    return rates


def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return Decimal(str(amount))

    rates = get_exchange_rates()

    from_rate = rates.get(from_currency, 1.0)
    to_rate = rates.get(to_currency, 1.0)

    # Convert source currency to IDR first
    if from_currency == 'IDR':
        amount_idr = Decimal(str(float(amount)))
    else:
        amount_idr = Decimal(str(float(amount))) / Decimal(str(from_rate))

    # Convert IDR to target currency
    if to_currency == 'IDR':
        result = amount_idr
    else:
        result = amount_idr * Decimal(str(to_rate))

    return result.quantize(Decimal('0.01'))


def format_currency(amount, currency_code):
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
    formatted = f'{float(amount):,.2f}'
    if currency_code in ('IDR',):
        formatted = f'{symbol}{formatted}'
    elif currency_code in ('USD', 'EUR', 'GBP', 'SGD', 'AUD', 'CAD', 'NZD', 'HKD', 'TWD', 'BND', 'FJD'):
        formatted = f'{symbol}{formatted}'
    else:
        formatted = f'{symbol} {formatted}'
    return formatted


def get_all_currencies():
    rates = get_exchange_rates()
    currencies = []
    for code, rate in sorted(rates.items()):
        currencies.append({
            'code': code,
            'name': CURRENCY_NAMES.get(code, code),
            'symbol': CURRENCY_SYMBOLS.get(code, code),
            'rate_to_idr': rate,
        })
    return currencies
