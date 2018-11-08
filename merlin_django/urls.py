from django.conf.urls import include, url

app_name = 'merlin_django'

urlpatterns = [
    url(r'^merlinservices/', include('merlinservices.urls', 'merlin_django')),
    url(r'^merlinauth/', include(('djoser.urls', 'merlin_django'), namespace="merlinauth")),
    url(r'^merlin/', include(('merlin.urls', 'merlin_django'), namespace="merlin")),
]
