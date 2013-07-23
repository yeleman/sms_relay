#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from sms_relay.models import IncomingSMS
from sms_relay.utils import is_valid_number
from sms_relay.tasks import queue_sms_forward


def home(request):
    return HttpResponse("OK")


@csrf_exempt
def smssync(request):

    def http_response(is_processed):
        response = {'payload': {'success': bool(is_processed)}}
        return HttpResponse(json.dumps(response), mimetype='application/json')

    if not request.method == 'POST':
        return http_response(True)

    processed = False

    sent_timestamp = request.POST.get('sent_timestamp')
    try:
        received_on = datetime.datetime.fromtimestamp(int(sent_timestamp) / 1000)
    except (TypeError, ValueError):
        received_on = None
    identity = request.POST.get('from')
    message = request.POST.get('message')

    print(identity)

    # skip SPAM
    if not is_valid_number(identity):
        return http_response(True)
    print(is_valid_number(identity))
    print("VALID")

    try:
        existing = IncomingSMS.objects.get(identity=identity,
                                           received_on=received_on)
    except IncomingSMS.DoesNotExist:
        existing = None

    if existing:
        return http_response(True)

    try:
        sms = IncomingSMS.objects.create(
            identity=identity,
            received_on=received_on,
            text=message,
            destination=settings.MALITEL_NUMBER)
        processed = True
    except:
        return http_response(False)

    queue_sms_forward.apply_async([sms])

    return http_response(processed)
