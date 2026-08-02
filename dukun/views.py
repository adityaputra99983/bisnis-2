from django.http import HttpResponse
from datetime import datetime

def robots_txt(request):
    host = request.get_host()
    scheme = "https" if request.is_secure() else "https"
    base = f"{scheme}://{host}"
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /payments/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "",
        f"Sitemap: {base}/sitemap.xml",
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

def sitemap_xml(request):
    host = request.get_host()
    scheme = "https" if request.is_secure() else "https"
    base = f"{scheme}://{host}"
    today = datetime.now().strftime("%Y-%m-%d")
    pages = [
        ("", "1.0", "daily"),
        ("login/", "0.8", "monthly"),
        ("register/", "0.8", "monthly"),
        ("register/healer/", "0.8", "monthly"),
        ("healers/", "0.9", "weekly"),
        ("centers/", "0.7", "monthly"),
        ("about/", "0.5", "monthly"),
    ]
    urls = []
    for lang in ("id", "en"):
        for path, priority, freq in pages:
            full = f"{base}/{lang}/{path}"
            urls.append(f"""  <url>
    <loc>{full}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>"""
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")
