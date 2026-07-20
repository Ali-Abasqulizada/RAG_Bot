from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), ),

    path('', include('apps.web.urls', namespace='web')),
    
    re_path(r'^documents/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)