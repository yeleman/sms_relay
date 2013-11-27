#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import random
import json

from django.conf import settings
from django.http import HttpResponse
from fondasms.utils import datetime_from_timestamp

from sms_relay.utils import (normalized_phonenumber,
                             is_valid_number,
                             operator_from_malinumber)
from sms_relay.models import TextSMS
from sms_relay.tasks import queue_sms_forward, pop_pending_replies


class UnableToCreateHotlineRequest(Exception):
    pass

# place holder for incoming phone numbers (phone device)
# with operator
INCOMING_NUMBERS_BY_OPERATOR = {}
INCOMING_NUMBERS_WITH_OPERATOR = {}


def automatic_reply_handler(payload):
    # called by automatic reply logic
    # if settings.FONDA_SEND_AUTOMATIC_REPLY_VIA_HANDLER
    # Can be used to fetch or forge reply when we need more than
    # the static FONDA_AUTOMATIC_REPLY_TEXT
    return None


def handle_incoming_sms(payload):
    print("handle_incoming_sms")
    # on SMS received
    return handle_sms_call(payload)


def handle_incoming_call(payload):
    print("handle_incoming_call")
    # on call received
    return handle_sms_call(payload, event_type='call')


def handle_outgoing_request(payload):
    return pop_pending_replies()


def handle_sms_call(payload, event_type=None):

    phone_number = normalized_phonenumber(payload.get('from').strip())
    if not is_valid_number(phone_number):
        return

    message = payload.get('message').strip()
    if not len(message):
        message = None

    if message is None and event_type == 'call':
        message = "ring ring"

    # phone_number = payload.get('phone_number')
    timestamp = payload.get('timestamp')
    received_on = datetime_from_timestamp(timestamp)

    try:
        existing = TextSMS.incoming.get(identity=phone_number,
                                        event_on=received_on)
    except TextSMS.DoesNotExist:
        existing = None

    if existing:
        return

    try:
        sms = TextSMS.objects.create(
            identity=phone_number,
            event_on=received_on,
            text=message,
            direction=TextSMS.INCOMING,
            sim_number=settings.SIM_NUMBER)
    except:
        return

    queue_sms_forward.apply_async([sms])

    return pop_pending_replies()


def build_response_with(events=[], phone_number=None):
    response = {'events': [],
                'phone_number': phone_number}
    if len(events):
        if not len(response['events']):
            response['events'].append({'event': 'send', 'messages': []})
        response['events'][0]['messages'] += events
    return HttpResponse(json.dumps(response),
                        mimetype='application/json')


def handle_outgoing_status_change(payload):
    # we don't store outgoing messages for now
    return


def handle_device_status_change(payload):
    # we don't track device changes for now
    return


def check_meta_data(payload):
    # we don't track device changes for now
    return


def reply_with_phone_number(payload):
    end_user_phone = payload.get('from')
    if end_user_phone is not None:
        return get_phone_number_for(operator_from_malinumber(end_user_phone))
    return None


def get_phone_number_for(operator):
    return random.choice(INCOMING_NUMBERS_BY_OPERATOR.get(operator, [None])) or None

for number in settings.FONDA_INCOMING_NUMBERS:
    operator = operator_from_malinumber(number)
    if not operator in INCOMING_NUMBERS_BY_OPERATOR.keys():
        INCOMING_NUMBERS_BY_OPERATOR.update({operator: []})
    INCOMING_NUMBERS_BY_OPERATOR[operator].append(number)
    INCOMING_NUMBERS_WITH_OPERATOR.update({number: operator})
