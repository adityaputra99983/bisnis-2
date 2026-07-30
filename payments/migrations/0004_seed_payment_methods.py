from django.db import migrations


def seed_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model('payments', 'PaymentMethod')
    methods = [
        {'name': 'Transfer Bank (BCA)', 'description': 'Transfer via BCA Virtual Account', 'icon': 'university', 'is_active': True, 'instructions': 'Transfer ke rekening BCA Virtual Account yang tertera. Pembayaran akan dikonfirmasi otomatis.'},
        {'name': 'Transfer Bank (Mandiri)', 'description': 'Transfer via Mandiri Virtual Account', 'icon': 'university', 'is_active': True, 'instructions': 'Transfer ke rekening Mandiri Virtual Account yang tertera.'},
        {'name': 'GoPay', 'description': 'Pembayaran melalui GoPay', 'icon': 'mobile-alt', 'is_active': True, 'instructions': 'Bayar menggunakan GoPay dengan memasukkan kode pembayaran.'},
        {'name': 'OVO', 'description': 'Pembayaran melalui OVO', 'icon': 'mobile-alt', 'is_active': True, 'instructions': 'Bayar menggunakan OVO dengan memasukkan kode pembayaran.'},
        {'name': 'DANA', 'description': 'Pembayaran melalui DANA', 'icon': 'wallet', 'is_active': True, 'instructions': 'Bayar menggunakan DANA dengan memasukkan kode pembayaran.'},
        {'name': 'Kartu Kredit', 'description': 'Visa, Mastercard, JCB', 'icon': 'credit-card', 'is_active': True, 'instructions': 'Masukkan detail kartu kredit Anda untuk menyelesaikan pembayaran.'},
        {'name': 'PayPal', 'description': 'Pembayaran internasional via PayPal', 'icon': 'globe', 'is_active': True, 'instructions': 'Anda akan diarahkan ke halaman PayPal untuk menyelesaikan pembayaran.'},
        {'name': 'Crypto (USDT/BTC)', 'description': 'Pembayaran dengan cryptocurrency', 'icon': 'bitcoin', 'is_active': True, 'instructions': 'Transfer crypto ke alamat yang tertera.'},
        {'name': 'Transfer Bank (BRI)', 'description': 'Transfer via BRI', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (BNI)', 'description': 'Transfer via BNI', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (BSI)', 'description': 'Transfer via BSI', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (CIMB)', 'description': 'Transfer via CIMB Niaga', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Danamon)', 'description': 'Transfer via Danamon', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Permata)', 'description': 'Transfer via Permata', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (OCBC)', 'description': 'Transfer via OCBC NISP', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Maybank)', 'description': 'Transfer via Maybank', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Mega)', 'description': 'Transfer via Bank Mega', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Panin)', 'description': 'Transfer via Bank Panin', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (BTN)', 'description': 'Transfer via Bank BTN', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'Transfer Bank (Muamalat)', 'description': 'Transfer via Bank Muamalat', 'icon': 'university', 'is_active': True, 'instructions': ''},
        {'name': 'ShopeePay', 'description': 'Payment via ShopeePay', 'icon': 'shopping-bag', 'is_active': True, 'instructions': ''},
        {'name': 'LinkAja', 'description': 'Payment via LinkAja', 'icon': 'link', 'is_active': True, 'instructions': ''},
        {'name': 'iSaku', 'description': 'Payment via iSaku', 'icon': 'piggy-bank', 'is_active': True, 'instructions': ''},
        {'name': 'QRIS', 'description': 'Pembayaran via QRIS (semua e-wallet & mobile banking)', 'icon': 'qrcode', 'is_active': True, 'instructions': ''},
        {'name': 'Cash', 'description': 'Pembayaran Tunai', 'icon': 'money-bill', 'is_active': True, 'instructions': 'Bayar tunai langsung di lokasi sesi.'},
    ]
    for data in methods:
        PaymentMethod.objects.get_or_create(name=data['name'], defaults=data)


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_alter_payment_status_alter_transactionlog_log_type'),
    ]

    operations = [
        migrations.RunPython(seed_payment_methods),
    ]
