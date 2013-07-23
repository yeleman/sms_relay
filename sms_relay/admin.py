#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin

from sms_relay.models import IncomingSMS


class CustomIncomingSMS(admin.ModelAdmin):
    list_display = ("received_on", "identity", "text", "status")
    list_filter = ("received_on", "status")

admin.site.register(IncomingSMS, CustomIncomingSMS)