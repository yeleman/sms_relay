from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'sms_relay.views.dashboard', name='dashboard'),
    url(r'^smssync$', 'sms_relay.views.smssync', name='smssync'),

    url(r'^graph_data/$', 'sms_relay.views.graph_data', name='graph_data'),
    url(r'^in_out_sms/(?P<number>\d+)/$', 'sms_relay.views.list_incomingsms', name='incomingsms'),
    url(r'^admin/', include(admin.site.urls)),
)
