from django import template
from django.utils.safestring import mark_safe

register = template.Library()

LANGUAGE_CURRENCY_MAP = {
    'id': {'code': 'IDR', 'symbol': 'Rp', 'name': 'Indonesian Rupiah'},
    'en': {'code': 'USD', 'symbol': '$', 'name': 'US Dollar'},
    'zh-hans': {'code': 'CNY', 'symbol': '¥', 'name': 'Chinese Yuan'},
    'zh-hant': {'code': 'TWD', 'symbol': 'NT$', 'name': 'New Taiwan Dollar'},
    'ja': {'code': 'JPY', 'symbol': '¥', 'name': 'Japanese Yen'},
    'ko': {'code': 'KRW', 'symbol': '₩', 'name': 'South Korean Won'},
    'ru': {'code': 'RUB', 'symbol': '₽', 'name': 'Russian Ruble'},
    'ar': {'code': 'SAR', 'symbol': '﷼', 'name': 'Saudi Riyal'},
    'es': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'fr': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'de': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'pt': {'code': 'BRL', 'symbol': 'R$', 'name': 'Brazilian Real'},
    'it': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'nl': {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    'th': {'code': 'THB', 'symbol': '฿', 'name': 'Thai Baht'},
    'vi': {'code': 'VND', 'symbol': '₫', 'name': 'Vietnamese Dong'},
    'tr': {'code': 'TRY', 'symbol': '₺', 'name': 'Turkish Lira'},
    'pl': {'code': 'PLN', 'symbol': 'zł', 'name': 'Polish Zloty'},
    'hi': {'code': 'INR', 'symbol': '₹', 'name': 'Indian Rupee'},
}

CURRENCY_FORMATTING = {
    'IDR': {'decimals': 0, 'thousands': '.', 'prefix': True},
    'USD': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'EUR': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'GBP': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'CNY': {'decimals': 0, 'thousands': ',', 'prefix': True},
    'JPY': {'decimals': 0, 'thousands': ',', 'prefix': True},
    'KRW': {'decimals': 0, 'thousands': ',', 'prefix': True},
    'TWD': {'decimals': 0, 'thousands': ',', 'prefix': True},
    'THB': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'VND': {'decimals': 0, 'thousands': '.', 'prefix': True},
    'INR': {'decimals': 0, 'thousands': ',', 'prefix': True},
    'RUB': {'decimals': 0, 'thousands': ' ', 'prefix': True},
    'SAR': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'TRY': {'decimals': 0, 'thousands': '.', 'prefix': True},
    'PLN': {'decimals': 2, 'thousands': ' ', 'prefix': True},
    'BRL': {'decimals': 2, 'thousands': '.', 'prefix': True},
    'PHP': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'MYR': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'SGD': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'AUD': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'CAD': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'CHF': {'decimals': 2, 'thousands': "'", 'prefix': True},
    'HKD': {'decimals': 2, 'thousands': ',', 'prefix': True},
    'NZD': {'decimals': 2, 'thousands': ',', 'prefix': True},
}


def _format_price(amount, currency_code):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return '0'

    fmt = CURRENCY_FORMATTING.get(currency_code, {'decimals': 2, 'thousands': ',', 'prefix': True})

    SYMBOLS = {
        'IDR': 'Rp', 'USD': '$', 'EUR': '\u20ac', 'GBP': '\u00a3', 'CNY': '\u00a5', 'JPY': '\u00a5',
        'KRW': '\u20a9', 'TWD': 'NT$', 'THB': '\u0e3f', 'VND': '\u20ab', 'INR': '\u20b9', 'RUB': '\u20bd',
        'SAR': '\ufdfc', 'TRY': '\u20ba', 'PLN': 'z\u0142', 'BRL': 'R$', 'PHP': '\u20b1', 'MYR': 'RM',
        'SGD': 'S$', 'AUD': 'A$', 'CAD': 'C$', 'CHF': 'CHF', 'HKD': 'HK$', 'NZD': 'NZ$',
    }
    symbol = SYMBOLS.get(currency_code, currency_code)

    if fmt['decimals'] == 0:
        amount = round(amount)
        formatted = f"{amount:,.0f}"
    else:
        decimals = fmt['decimals']
        formatted = f"{amount:,.{decimals}f}"

    # Add space between symbol and amount for readability
    return f"{symbol} {formatted}"


def _get_currency_for_language(language_code):
    return LANGUAGE_CURRENCY_MAP.get(language_code, LANGUAGE_CURRENCY_MAP['id'])


@register.filter(name='convert_price')
def convert_price(price_idr, language_code):
    from payments.services import convert_currency
    if not price_idr:
        return 'Rp 0'

    currency_info = _get_currency_for_language(language_code)
    currency_code = currency_info['code']

    converted = convert_currency(price_idr, 'IDR', currency_code)
    return _format_price(converted, currency_code)


@register.filter(name='get_currency_symbol')
def get_currency_symbol(language_code):
    currency_info = _get_currency_for_language(language_code)
    return currency_info['symbol']


@register.filter(name='get_currency_code')
def get_currency_code(language_code):
    currency_info = _get_currency_for_language(language_code)
    return currency_info['code']


@register.filter(name='price_with_original')
def price_with_original(price_idr, language_code):
    from payments.services import convert_currency
    if not price_idr:
        return mark_safe('<span>Rp 0</span>')

    currency_info = _get_currency_for_language(language_code)
    currency_code = currency_info['code']

    if currency_code == 'IDR':
        return mark_safe(f'<span>Rp {float(price_idr):,.0f}</span>')

    converted = convert_currency(price_idr, 'IDR', currency_code)
    formatted = _format_price(converted, currency_code)

    return mark_safe(
        f'<span>{formatted}</span>'
        f'<span style="font-size:0.75em;opacity:0.6;margin-left:4px">(Rp {float(price_idr):,.0f})</span>'
    )
