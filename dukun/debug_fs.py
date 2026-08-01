import os

from django.conf import settings
from django.http import HttpResponse


def debug_fs(request):
    base = str(settings.BASE_DIR)
    lines = []
    lines.append("BASE_DIR = %s" % base)
    lines.append("DEBUG = %s" % settings.DEBUG)
    lines.append("STATIC_ROOT = %s" % settings.STATIC_ROOT)
    lines.append("exists STATIC_ROOT = %s" % os.path.exists(settings.STATIC_ROOT))
    if os.path.exists(settings.STATIC_ROOT):
        try:
            lines.append("STATIC_ROOT count = %d" % len(os.listdir(settings.STATIC_ROOT)))
        except OSError as exc:
            lines.append("STATIC_ROOT listdir error: %r" % exc)
        admin_css = os.path.join(settings.STATIC_ROOT, 'admin', 'css', 'base.css')
        lines.append("admin css exists = %s" % os.path.exists(admin_css))
        style_css = os.path.join(settings.STATIC_ROOT, 'css', 'style.css')
        lines.append("style.css exists = %s" % os.path.exists(style_css))
    if os.path.isdir(base):
        try:
            lines.append("BASE_DIR entries = %s" % ", ".join(sorted(os.listdir(base))))
        except OSError as exc:
            lines.append("BASE_DIR listdir error: %r" % exc)
    try:
        cwd = os.getcwd()
        lines.append("CWD = %s" % cwd)
        lines.append("CWD entries = %s" % ", ".join(sorted(os.listdir(cwd))))
    except OSError as exc:
        lines.append("CWD error: %r" % exc)
    return HttpResponse("\n".join(lines), content_type="text/plain")
