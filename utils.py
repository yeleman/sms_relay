#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import requests
from django.conf import settings

from sms_relay.models import IncomingSMS

NB_CHARS_VALID_NUMBER = 8


def is_valid_number(number):
    ''' checks if number is valid for HOTLINE_NUMBERS

        We want to get rid of operator spam '''
    if number is None:
        return False
    return len(number) >= NB_CHARS_VALID_NUMBER


def forward_sms(sms):
    cl = lambda x: x.replace('+', '')

    if sms.status == sms.STATUS_SENTOK:
        return False

    url = settings.SOUKTEL_URL
    params = {"api_id": settings.SOUKTEL_API_ID,
              "key": settings.SOUKTEL_KEY,
              "sc": cl(sms.destination),
              "msg": sms.text,
              "from": cl(sms.identity)}
    req = requests.get(url, params=params)

    try:
        req.raise_for_status()
        sms.status = sms.STATUS_SENTOK
    except requests.exceptions.HTTPError:
        sms.status = sms.STATSUS_ERROR
    sms.save()

    return sms.status == sms.STATUS_SENTOK


def is_connection_ok():
    try:
        req = requests.get(settings.SOUKTEL_URL)
        req.raise_for_status()
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError):
        return False

    return req.text == "1"


def clear_pending_messages():
    from sms_relay.tasks import queue_sms_forward

    if not is_connection_ok():
        return False

    for sms in IncomingSMS.objects.filter(status__in=IncomingSMS.PENDING_STATUSES):
        queue_sms_forward.apply_async([sms])

    return True
