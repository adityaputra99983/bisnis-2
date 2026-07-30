from django.db import migrations


def seed_reference_data(apps, schema_editor):
    HealerCategory = apps.get_model('healers', 'HealerCategory')
    Location = apps.get_model('healers', 'Location')
    Speciality = apps.get_model('healers', 'Speciality')
    Testimonial = apps.get_model('healers', 'Testimonial')

    categories = [
        {'name': 'Penyembuhan Spiritual', 'description': 'Penyembuhan menggunakan energi spiritual dan doa', 'icon': 'pray'},
        {'name': 'Pembersihan Aura', 'description': 'Membersihkan energi negatif dan memperkuat aura positif', 'icon': 'star'},
        {'name': 'Penyembuhan Emosional', 'description': 'Penyembuhan luka batin dan gangguan emosional', 'icon': 'heart'},
        {'name': 'Mediasi Spiritual', 'description': 'Koneksi dengan alam gaib untuk bimbingan hidup', 'icon': 'yin-yang'},
        {'name': 'Pengobatan Tradisional', 'description': 'Pengobatan tradisional Bali dengan ramuan herbal', 'icon': 'leaf'},
        {'name': 'Perlindungan Spiritual', 'description': 'Perlindungan dari energi negatif dan santet', 'icon': 'shield-alt'},
        {'name': 'Reiki Healing', 'description': 'Japanese energy healing technique for stress reduction and relaxation', 'icon': 'hand-sparkles'},
        {'name': 'Chakra Healing', 'description': 'Balancing and aligning the seven energy centers of the body', 'icon': 'circle-nodes'},
        {'name': 'Energy Healing', 'description': 'Channeling healing energy to clear blockages and restore balance', 'icon': 'bolt'},
        {'name': 'Sound Healing', 'description': 'Using therapeutic sound frequencies from singing bowls and gongs', 'icon': 'music'},
        {'name': 'Spiritual Guidance', 'description': 'Intuitive guidance and spiritual counseling for life path', 'icon': 'eye'},
        {'name': 'Meditation', 'description': 'Guided meditation practices for inner peace and clarity', 'icon': 'brain'},
        {'name': 'Balinese Healing', 'description': 'Traditional Balinese healing practices using ancient rituals', 'icon': 'spa'},
        {'name': 'Aura Reading', 'description': 'Reading and interpreting the energy field surrounding the body', 'icon': 'star'},
    ]
    for data in categories:
        HealerCategory.objects.get_or_create(name=data['name'], defaults=data)

    locations = [
        {'name': 'Abiansemal', 'description': 'Sacred Waters & Ancient Healing', 'gradient': '064e3b,047857'},
        {'name': 'Ubud', 'description': 'The Spiritual Heart of Bali', 'gradient': '78350f,b45309'},
        {'name': 'Canggu', 'description': 'Where Ancient Meets Modern Wellness', 'gradient': '164e63,0891b2'},
        {'name': 'Sanur', 'description': 'Peaceful Healing by the Sea', 'gradient': '0c4a6e,1d4ed8'},
        {'name': 'Seminyak', 'description': 'Luxury Meets Spirituality', 'gradient': '581c87,9333ea'},
    ]
    for data in locations:
        Location.objects.get_or_create(name=data['name'], defaults=data)

    specialities = [
        {'name': 'Reiki Healing', 'emoji': '🔮', 'description': 'Japanese energy healing', 'order': 1},
        {'name': 'Chakra Healing', 'emoji': '🔄', 'description': 'Energy center balancing', 'order': 2},
        {'name': 'Energy Healing', 'emoji': '⚡', 'description': 'Energy blockages clearing', 'order': 3},
        {'name': 'Sound Healing', 'emoji': '🎵', 'description': 'Therapeutic sound frequencies', 'order': 4},
        {'name': 'Spiritual Guidance', 'emoji': '👁️', 'description': 'Intuitive counseling', 'order': 5},
        {'name': 'Meditation', 'emoji': '🧘', 'description': 'Guided meditation practices', 'order': 6},
        {'name': 'Balinese Healing', 'emoji': '🌺', 'description': 'Traditional Balinese rituals', 'order': 7},
        {'name': 'Aura Reading', 'emoji': '🔮', 'description': 'Energy field reading', 'order': 8},
    ]
    for data in specialities:
        Speciality.objects.get_or_create(name=data['name'], defaults=data)

    testimonials = [
        {'customer_name': 'Sarah M.', 'rating': 5, 'comment': 'Pengalaman spiritual yang luar biasa. Saya merasa sangat tenang dan damai setelah sesi penyembuhan. Healer sangat profesional dan penuh kasih.', 'is_featured': True},
        {'customer_name': 'Michael T.', 'rating': 5, 'comment': 'Amazing experience! The energy healing session was transformative. I felt blocked energy releasing during the session.', 'is_featured': True},
        {'customer_name': 'Putu A.', 'rating': 5, 'comment': 'Saya sudah 3 kali datang ke Bali untuk penyembuhan tradisional. Hasilnya sungguh nyata, kesehatan saya membaik drastis.', 'is_featured': True},
        {'customer_name': 'Emma L.', 'rating': 5, 'comment': 'The chakra balancing session was incredible. I could feel the energy shifting in my body. Highly recommended!', 'is_featured': True},
        {'customer_name': 'David K.', 'rating': 5, 'comment': 'I was skeptical at first, but after my first Reiki session I felt an incredible sense of peace and clarity.', 'is_featured': True},
        {'customer_name': 'Ni Luh', 'rating': 5, 'comment': 'Terima kasih banyak untuk penyembuhannya. Masalah insomnia yang sudah bertahun-tahun sekarang membaik setelah terapi.', 'is_featured': True},
    ]
    for data in testimonials:
        Testimonial.objects.get_or_create(
            customer_name=data['customer_name'],
            defaults=data,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('healers', '0012_alter_banktransactionsetting_admin_fee_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_reference_data),
    ]
