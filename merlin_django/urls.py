from django.conf.urls import include, url


urlpatterns = [
    url(r'^merlinservices/', include('merlinservices.urls')),
    url(r'^merlinauth/', include('djoser.urls')),
    url(r'^merlin/', include('merlin.urls')),
]
