from django.conf.urls import patterns, include
from django.contrib import admin

urlpatterns = patterns('',
    (r'^forum/', include('djangobb_forum.urls', namespace='djangobb')),
    (r'^admin/', include(admin.site.urls)),
)
