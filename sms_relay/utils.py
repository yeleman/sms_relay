#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import urllib2
import datetime
import requests
from django.conf import settings

from sms_relay.models import TextSMS

NB_CHARS_VALID_NUMBER = 8


def unquote_url(url):
    return urllib2.unquote(url).replace("+", " ")


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
              "sc": cl(sms.sim_number),
              "msg": sms.text,
              "from": cl(sms.identity)}
    req = requests.get(url, params=params)

    try:
        req.raise_for_status()
        sms.status = sms.STATUS_SENTOK
    except requests.exceptions.HTTPError:
        sms.status = sms.STATSUS_ERROR
    sms.save()

    # add reply to outgoing list
    if req.text:
        TextSMS.objects.create(direction=TextSMS.OUTGOING,
                               identity=sms.identity,
                               event_on=datetime.datetime.now(),
                               text=unquote_url(req.text),
                               sim_number=settings.SIM_NUMBER)

    return sms.status == sms.STATUS_SENTOK


def is_connection_ok():
    try:
        req = requests.get(settings.SOUKTEL_TEST_URL)
        req.raise_for_status()
        return True  # we are using /sms/ as test URL which is blank
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError):
        return False

    return bool(req.text)


def clear_pending_messages():
    from sms_relay.tasks import queue_sms_forward

    if not is_connection_ok():
        return False

    for sms in TextSMS.incoming.filter(status__in=TextSMS.PENDING_STATUSES):
        queue_sms_forward.apply_async([sms])

    return True


def datetime_range(start, stop=None, days=1):
    ''' return a list of dates incremented by 'days'

        start/stop = date or datetime
        days = increment number of days '''

    # stop at 00h00 today so we don't have an extra
    # point for today if the last period ends today.
    stop = stop or datetime.datetime(*datetime.date.today().timetuple()[:-4])

    while(start < stop):
        yield start
        start += datetime.timedelta(days)

    yield stop
