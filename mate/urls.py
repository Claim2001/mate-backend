from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
# import os
from mate import settings

schema_view = get_schema_view(
    openapi.Info(title="Mate API", default_version='v1', description="Mate API urls",
                 contact=openapi.Contact(email="info@mate-edu.io"), license=openapi.License(name="Mate License")),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path(os.getenv('SECRET_ADMIN_URL') + '/admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('', include(('courses.urls', 'courses'), namespace='course')),
    path('account/', include(('account.urls', 'account'), namespace='account')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
