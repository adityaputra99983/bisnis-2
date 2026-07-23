from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from healers.models import HealerCategory, Healer, HealerSchedule, Location, HealingCenter, Speciality, Testimonial
from payments.models import Currency, PaymentMethod
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@balibalihealer.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser: admin / admin123'))

        cats = [
            ('Reiki Healing', 'Japanese energy healing technique for stress reduction and relaxation', 'hand-sparkles'),
            ('Chakra Healing', 'Balancing and aligning the seven energy centers of the body', 'circle-nodes'),
            ('Energy Healing', 'Channeling healing energy to clear blockages and restore balance', 'bolt'),
            ('Sound Healing', 'Using therapeutic sound frequencies from singing bowls and gongs', 'music'),
            ('Spiritual Guidance', 'Intuitive guidance and spiritual counseling for life path', 'eye'),
            ('Meditation', 'Guided meditation practices for inner peace and clarity', 'brain'),
            ('Balinese Healing', 'Traditional Balinese healing practices using ancient rituals', 'spa'),
            ('Aura Reading', 'Reading and interpreting the energy field surrounding the body', 'star'),
        ]
        for name, desc, icon in cats:
            HealerCategory.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
        self.stdout.write(self.style.SUCCESS(f'Categories: {HealerCategory.objects.count()}'))

        healers_data = [
            {'name': 'Wayan Surya Dharma', 'slug': 'wayan-surya', 'category': 'Reiki Healing',
             'bio': 'With over 25 years of experience, Wayan is one of Bali\'s most respected Reiki masters. His sessions combine traditional Balinese healing with Japanese energy techniques.',
             'experience_years': 25, 'phone': '+62 361 234 567', 'email': 'wayan@balibalihealer.com',
             'address': 'Ubud, Gianyar, Bali', 'price_idr': 650000, 'rating': 4.9,
             'specializations': 'Reiki Healing Chakra Balancing Energy Cleansing'},
            {'name': 'Anjali Patel', 'slug': 'anjali-patel', 'category': 'Chakra Healing',
             'bio': 'Anjali brings a unique blend of Indian and Balinese healing traditions. Specializing in chakra alignment and emotional healing.',
             'experience_years': 15, 'phone': '+62 361 345 678', 'email': 'anjali@balibalihealer.com',
             'address': 'Canggu, Badung, Bali', 'price_idr': 500000, 'rating': 4.8,
             'specializations': 'Chakra Balancing Sound Healing Meditation'},
            {'name': 'Kadek Widiarti', 'slug': 'kadek-widiarti', 'category': 'Sound Healing',
             'bio': 'Kadek is a master sound healer who uses traditional Balinese gamelan instruments and crystal singing bowls for deep therapeutic sessions.',
             'experience_years': 12, 'phone': '+62 361 456 789', 'email': 'kadek@balibalihealer.com',
             'address': 'Sanur, Denpasar, Bali', 'price_idr': 600000, 'rating': 5.0,
             'specializations': 'Sound Healing Singing Bowls Gamelan Therapy'},
            {'name': 'Made Suarjana', 'slug': 'made-suarjana', 'category': 'Balinese Healing',
             'bio': 'A traditional Balinese healer (Balian) continuing centuries-old healing traditions passed down through generations.',
             'experience_years': 30, 'phone': '+62 361 567 890', 'email': 'made@balibalihealer.com',
             'address': 'Ubud, Gianyar, Bali', 'price_idr': 700000, 'rating': 4.9,
             'specializations': 'Traditional Healing Ritual Cleansing Spiritual Guidance'},
            {'name': 'Putu Eka Pratama', 'slug': 'putu-eka', 'category': 'Energy Healing',
             'bio': 'Putu combines modern energy healing techniques with ancient Balinese wisdom for powerful transformation.',
             'experience_years': 18, 'phone': '+62 361 678 901', 'email': 'putu@balibalihealer.com',
             'address': 'Canggu, Badung, Bali', 'price_idr': 550000, 'rating': 4.8,
             'specializations': 'Energy Healing Aura Cleansing Crystal Healing'},
            {'name': 'Sri Rahayu', 'slug': 'sri-rahayu', 'category': 'Meditation',
             'bio': 'Sri is a meditation guide and spiritual counselor who helps seekers find inner peace through guided meditation and mindfulness.',
             'experience_years': 20, 'phone': '+62 361 789 012', 'email': 'sri@balibalihealer.com',
             'address': 'Sanur, Denpasar, Bali', 'price_idr': 450000, 'rating': 5.0,
             'specializations': 'Meditation Spiritual Guidance Mindfulness'},
        ]
        for h in healers_data:
            cat = HealerCategory.objects.filter(name=h['category']).first()
            healer, created = Healer.objects.get_or_create(slug=h['slug'], defaults={**h, 'category': cat})
            if created:
                for day in range(6):
                    HealerSchedule.objects.get_or_create(healer=healer, day_of_week=day,
                        defaults={'start_time': '09:00', 'end_time': '17:00'})
        self.stdout.write(self.style.SUCCESS(f'Healers: {Healer.objects.count()}'))

        locs = [
            ('Abiansemal', 'Sacred Waters & Ancient Healing', '064e3b,047857', 6, 1),
            ('Ubud', 'The Spiritual Heart of Bali', '78350f,b45309', 3, 2),
            ('Canggu', 'Where Ancient Meets Modern Wellness', '164e63,0891b2', 2, 1),
            ('Sanur', 'Peaceful Healing by the Sea', '0c4a6e,1d4ed8', 1, 1),
            ('Seminyak', 'Luxury Meets Spirituality', '581c87,9333ea', 1, 1),
        ]
        for name, desc, grad, hc, cc in locs:
            Location.objects.get_or_create(name=name, defaults={
                'description': desc, 'gradient': grad, 'healer_count': hc, 'center_count': cc})
        self.stdout.write(self.style.SUCCESS(f'Locations: {Location.objects.count()}'))

        loc_ubud = Location.objects.filter(name='Ubud').first()
        loc_canggu = Location.objects.filter(name='Canggu').first()
        loc_sanur = Location.objects.filter(name='Sanur').first()

        centers_data = [
            ('Beji Healing', 'Abiansemal, Bali', 'A sacred healing center near ancient water temples.', '155e75,0e7490', 4.8, 12, 'Energy Cleansing,Ritual Healing,Water Therapy', 'Rp 300.000 - Rp 1.200.000', True, loc_ubud),
            ('Ubud Sacred Healing Sanctuary', 'Ubud, Bali', 'Nestled in the heart of Ubud\'s rice terraces.', '312e81,4338ca', 4.9, 8, 'Meditation,Reiki,Sound Healing', 'Rp 400.000 - Rp 1.500.000', True, loc_ubud),
            ('Canggu Wellness Collective', 'Canggu, Bali', 'Modern wellness meets traditional healing.', '065f46,047857', 4.7, 15, 'Holistic Healing,Yoga,Chakra Balancing', 'Rp 350.000 - Rp 1.000.000', True, loc_canggu),
        ]
        for name, addr, desc, grad, rat, rc, specs, pr, gb, loc in centers_data:
            HealingCenter.objects.get_or_create(name=name, defaults={
                'address': addr, 'description': desc, 'gradient': grad,
                'rating': rat, 'review_count': rc, 'specializations': specs,
                'price_range': pr, 'has_google_badge': gb, 'location': loc})
        self.stdout.write(self.style.SUCCESS(f'Centers: {HealingCenter.objects.count()}'))

        specs_data = [
            ('Reiki Healing', '🔮', 'Japanese energy healing technique for stress reduction and spiritual growth.'),
            ('Chakra Healing', '⚡', 'Balancing and aligning the seven energy centers of the body.'),
            ('Energy Healing', '✨', 'Channeling healing energy to clear blockages and restore balance.'),
            ('Sound Healing', '🎵', 'Using therapeutic sound frequencies from singing bowls and gongs.'),
            ('Spiritual Guidance', '👁️', 'Intuitive guidance and spiritual counseling for your life path.'),
            ('Meditation', '🧠', 'Guided meditation practices for inner peace and clarity.'),
            ('Balinese Healing', '🌿', 'Traditional Balinese healing practices using ancient rituals.'),
            ('Aura Reading', '⭐', 'Reading and interpreting the energy field surrounding your body.'),
        ]
        for i, (name, emoji, desc) in enumerate(specs_data):
            Speciality.objects.get_or_create(name=name, defaults={'emoji': emoji, 'description': desc, 'order': i})
        self.stdout.write(self.style.SUCCESS(f'Specialities: {Speciality.objects.count()}'))

        testimonials = [
            ('Sarah M.', 5, 'Wayan\'s healing session was truly transformative. I felt a deep sense of peace and renewal that I hadn\'t experienced in years.'),
            ('James K.', 5, 'Anjali has an incredible gift. Her Reiki session helped me release years of stored emotional tension.'),
            ('Elena P.', 5, 'The sound bath with Kadek was beyond words. The vibrations of the singing bowls took me to a state of deep relaxation.'),
            ('Michael T.', 5, 'The healing center in Ubud was breathtaking. The combination of traditional and modern approaches was exactly what I needed.'),
            ('Lisa R.', 5, 'I was skeptical at first, but the chakra balancing session completely changed my energy. I feel more centered than ever.'),
            ('David W.', 5, 'A truly authentic Balinese healing experience. Made\'s traditional knowledge is priceless.'),
        ]
        for name, rating, comment in testimonials:
            Testimonial.objects.get_or_create(customer_name=name, defaults={'rating': rating, 'comment': comment})
        self.stdout.write(self.style.SUCCESS(f'Testimonials: {Testimonial.objects.count()}'))

        currencies_data = [
            ('IDR', 'Indonesian Rupiah', 'Rp', 1.0), ('USD', 'US Dollar', '$', 0.000063),
            ('EUR', 'Euro', '\u20ac', 0.000058), ('GBP', 'British Pound', '\u00a3', 0.000050),
            ('CNY', 'Chinese Yuan', '\u00a5', 0.00046), ('JPY', 'Japanese Yen', '\u00a5', 0.0096),
            ('SGD', 'Singapore Dollar', 'S$', 0.000085), ('AUD', 'Australian Dollar', 'A$', 0.000096),
            ('RUB', 'Russian Ruble', '\u20bd', 0.0058), ('KRW', 'South Korean Won', '\u20a9', 0.083),
            ('THB', 'Thai Baht', '\u0e3f', 0.0022), ('MYR', 'Malaysian Ringgit', 'RM', 0.00029),
            ('INR', 'Indian Rupee', '\u20b9', 0.0053), ('PHP', 'Philippine Peso', '\u20b1', 0.0035),
        ]
        for code, name, symbol, rate in currencies_data:
            Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'rate_to_idr': Decimal(str(rate))})
        self.stdout.write(self.style.SUCCESS(f'Currencies: {Currency.objects.count()}'))

        methods = [
            ('Transfer Bank (BCA)', 'Transfer via BCA Virtual Account', 'university'),
            ('Transfer Bank (Mandiri)', 'Transfer via Mandiri Virtual Account', 'university'),
            ('GoPay', 'Payment via GoPay', 'mobile-alt'),
            ('OVO', 'Payment via OVO', 'mobile-alt'),
            ('DANA', 'Payment via DANA', 'wallet'),
            ('Kartu Kredit', 'Visa, Mastercard, JCB', 'credit-card'),
            ('PayPal', 'International payment via PayPal', 'globe'),
            ('Crypto (USDT/BTC)', 'Cryptocurrency payment', 'bitcoin'),
        ]
        for name, desc, icon in methods:
            PaymentMethod.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
        self.stdout.write(self.style.SUCCESS(f'Payment Methods: {PaymentMethod.objects.count()}'))

        self.stdout.write(self.style.SUCCESS('\nDone! Login: admin / admin123'))
