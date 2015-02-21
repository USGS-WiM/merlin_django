from django.conf.urls import patterns, url, include
from mercurybatchupload import views
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

urlpatterns = patterns('',
                       
                        url(r'^save', views.BatchUploadSave.as_view()),
                       )
