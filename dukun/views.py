from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /payments/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "",
        "Crawl-delay: 5",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")

def security_txt(request):
    host = request.get_host()
    scheme = "https" if request.is_secure() else "https"
    base = f"{scheme}://{host}"
    lines = [
        "Contact: mailto:admin@balibalihealer.com",
        f"Contact: {base}/",
        "Expires: 2027-08-02T00:00:00.000Z",
        "Preferred-Languages: id, en",
        "Policy: https://www.google.com/about/appsecurity/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
