from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Prefetch
from django.http import JsonResponse
from .models import Healer, HealerCategory, HealerReview, HealerSchedule, Location, HealingCenter, Speciality, Testimonial
from payments.services import convert_currency, format_currency, get_all_currencies


def home(request):
    featured_healers = Healer.objects.filter(is_available=True).select_related(
        'category'
    ).prefetch_related(
        'reviews',
        Prefetch('schedules', queryset=HealerSchedule.objects.filter(is_active=True)),
    ).order_by('-rating')[:6]
    categories = HealerCategory.objects.all()
    centers = HealingCenter.objects.filter(is_active=True).select_related('location')[:3]
    locations = Location.objects.all()[:5]
    specialities = Speciality.objects.all()[:8]
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    return render(request, 'home.html', {
        'healers': featured_healers,
        'categories': categories,
        'centers': centers,
        'locations': locations,
        'specialities': specialities,
        'testimonials': testimonials,
    })


def healer_list(request):
    healers = Healer.objects.filter(is_available=True).select_related('category').prefetch_related('reviews')
    categories = HealerCategory.objects.all()
    locations = Location.objects.all()
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    location_id = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if query:
        healers = healers.filter(
            Q(name__icontains=query) |
            Q(specializations__icontains=query) |
            Q(bio__icontains=query) |
            Q(address__icontains=query)
        )
    if category_id:
        healers = healers.filter(category_id=category_id)
    if location_id:
        loc = Location.objects.filter(id=location_id).first()
        if loc:
            healers = healers.filter(address__icontains=loc.name)
    if min_price:
        healers = healers.filter(price_idr__gte=min_price)
    if max_price:
        healers = healers.filter(price_idr__lte=max_price)

    return render(request, 'healer_list.html', {
        'healers': healers,
        'categories': categories,
        'locations': locations,
        'query': query or '',
        'selected_category': category_id or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
    })


def healer_detail(request, slug):
    healer = get_object_or_404(
        Healer.objects.select_related('category').prefetch_related(
            'reviews',
            'services',
            Prefetch('schedules', queryset=HealerSchedule.objects.filter(is_active=True)),
        ),
        slug=slug
    )
    reviews = healer.reviews.all().order_by('-created_at')[:10]
    schedules = healer.schedules.all()
    services = healer.services.all()
    avg_rating = healer.reviews.aggregate(avg=Avg('rating'))['avg'] or healer.rating
    currencies = get_all_currencies()

    converted_prices = {}
    for curr in currencies:
        converted_prices[curr['code']] = {
            'amount': convert_currency(healer.price_idr, 'IDR', curr['code']),
            'symbol': curr['symbol'],
        }

    return render(request, 'healer_detail.html', {
        'healer': healer,
        'reviews': reviews,
        'schedules': schedules,
        'services': services,
        'avg_rating': avg_rating,
        'currencies': currencies,
        'converted_prices': converted_prices,
    })


def center_list(request):
    centers = HealingCenter.objects.filter(is_active=True).select_related('location')
    return render(request, 'center_list.html', {'centers': centers})


def center_detail(request, slug):
    center = get_object_or_404(HealingCenter, slug=slug)
    return render(request, 'center_detail.html', {'center': center})


def speciality_list(request):
    specialities = Speciality.objects.all()
    return render(request, 'speciality_list.html', {'specialities': specialities})


def location_list(request):
    locations = Location.objects.all()
    return render(request, 'location_list.html', {'locations': locations})


def healer_schedule_api(request, healer_id):
    healer = get_object_or_404(Healer, id=healer_id)
    schedules = list(healer.schedules.filter(is_active=True).values(
        'day_of_week', 'start_time', 'end_time'
    ))
    return JsonResponse({'schedules': schedules})
