from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time
from decimal import Decimal
from healers.models import HealerCategory, Healer
from bookings.models import Booking
from payments.models import Payment, PaymentMethod


class CreatePaymentDuplicateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.cat = HealerCategory.objects.create(name='Test')
        self.healer = Healer.objects.create(
            name='Test Healer', category=self.cat, bio='x', phone='1', address='a',
        )
        self.method = PaymentMethod.objects.create(name='Cash', is_active=True)
        self.booking = Booking.objects.create(
            healer=self.healer,
            customer_name='Purnama',
            customer_email='p@test.com',
            customer_phone='0812',
            service_type='Test',
            booking_date=date.today(),
            booking_time=time(12, 0),
            total_price_idr=Decimal('100000'),
            status='pending_payment',
        )

    def _post_create(self):
        return self.client.post(
            reverse('create_payment', args=[self.booking.booking_code]),
            {'payment_method': self.method.id, 'currency': 'IDR'},
        )

    def test_first_create_succeeds(self):
        resp = self._post_create()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)

    def test_duplicate_create_returns_existing(self):
        self._post_create()
        resp = self._post_create()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)

    def test_duplicate_create_processing_returns_existing(self):
        self._post_create()
        p = Payment.objects.get(booking=self.booking)
        p.status = 'processing'
        p.save()
        resp = self._post_create()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)

    def test_failed_payment_gets_reset(self):
        self._post_create()
        p = Payment.objects.get(booking=self.booking)
        p.status = 'failed'
        p.save()
        resp = self._post_create()
        self.assertEqual(resp.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.status, 'pending')
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)

    def test_payment_process_active_payment_redirects(self):
        self._post_create()
        p = Payment.objects.get(booking=self.booking)
        p.status = 'processing'
        p.save()
        resp = self.client.get(
            reverse('payment_process', args=[self.booking.booking_code]),
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(p.payment_code, resp.url)

    def test_payment_process_failed_shows_form(self):
        self._post_create()
        p = Payment.objects.get(booking=self.booking)
        p.status = 'failed'
        p.save()
        resp = self.client.get(
            reverse('payment_process', args=[self.booking.booking_code]),
        )
        self.assertEqual(resp.status_code, 200)
