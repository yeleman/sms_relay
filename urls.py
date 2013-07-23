from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'sms_relay.views.home', name='home'),
    url(r'^smssync$', 'sms_relay.views.smssync', name='smssync'),
    url(r'^admin/', include(admin.site.urls)),
)
