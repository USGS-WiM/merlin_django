from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^merlinservices/', include('merlinservices.urls')),
    url(r'^merlinauth/', include('djoser.urls')),
    url(r'^merlinadmin/', admin.site.urls),
    url(r'^merlin/', include('merlin.urls')),
]
