from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

admin.site.site_header = 'Email Bot Admin'
admin.site.site_title = 'emailbot'
admin.site.index_title = 'Панель администратора'
