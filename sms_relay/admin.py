#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin

from sms_relay.models import TextSMS


class CustomTextSMS(admin.ModelAdmin):
    list_display = ("event_on", "incoming", "identity", "text", "status")
    list_filter = ("event_on", "status", "direction")

admin.site.register(TextSMS, CustomTextSMS)
