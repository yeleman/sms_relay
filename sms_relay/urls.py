#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'sms_relay.views.dashboard', name='dashboard'),
    url(r'^smssync$', 'sms_relay.views.smssync', name='smssync'),

    # Android API
    url(r'^fondasms/?$', 'fondasms.views.fondasms_handler',
        {'handler_module': 'sms_relay.fondasms_handlers',
         'send_automatic_reply': False,
         'automatic_reply_via_handler': False,
         'automatic_reply_text': ("On a bien enregistré votre demande.")},
        name='fondasms'),

    url(r'^graph_data/$', 'sms_relay.views.graph_data', name='graph_data'),
    url(r'^in_out_sms/(?P<number>\d+)/$', 'sms_relay.views.list_incomingsms', name='incomingsms'),
    url(r'^admin/', include(admin.site.urls)),
)
