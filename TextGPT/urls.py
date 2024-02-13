from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='questions')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('questions.urls')),
    path('api-docs/', schema_view),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
