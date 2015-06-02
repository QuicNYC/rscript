from django.conf.urls import patterns, include, url
from django.contrib import admin
import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
import settings
admin.autodiscover()

dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^graph/(.+)$',views.graph,name='graph'),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^doc/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes':True}),
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.IMAGE_ROOT,'show_indexes':True})
    )

urlpatterns += staticfiles_urlpatterns()