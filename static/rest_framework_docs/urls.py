from django.conf.urls import url
from rest_framework_docs.views import DRFDocsView
from django.conf.urls.static import static

urlpatterns = patterns("",
    # Your stuff goes here


urlpatterns = [
    # Url to view the API Docs
    url(r'^$', DRFDocsView.as_view(), name='drfdocs') + static('/', document_root='static/'),
]
