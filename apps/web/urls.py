from django.urls import path
from django.contrib.sitemaps.views import sitemap
from apps.web.utils.sitemaps import StaticSitemap
from apps.web import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "web"

sitemaps = {
    "static": StaticSitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", views.home_view, name="home"),
    path("api/ask/", views.ask_rag_api, name='ask_rag'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)