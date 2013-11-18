#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from batbelt import to_timestamp

from sms_relay.models import TextSMS
from sms_relay.utils import is_valid_number, datetime_range
from sms_relay.tasks import queue_sms_forward


def home(request):
    return HttpResponse("OK")


@csrf_exempt
def smssync(request):

    def http_response(is_processed, with_outgoing=False):
        response = {'payload': {'success': bool(is_processed)}}

        if TextSMS.tosend.count() and with_outgoing:
            response['payload'].update({'task': 'send',
                                        'secret': settings.USHAHIDI_SECRET,
                                        'messages': []})
            for outgoing_msg in TextSMS.tosend.order_by('event_on')[:settings.MAX_OUTOING_MESSAGES]:
                response['payload']['messages'].append({'to': outgoing_msg.identity, 'message': outgoing_msg.text})
                outgoing_msg.status = outgoing_msg.STATUS_SENTOK
                outgoing_msg.save()

        return HttpResponse(json.dumps(response), mimetype='application/json')

    if request.method == 'GET' and request.GET.get('task') == 'send':
        return http_response(True, with_outgoing=True)

    if not request.method == 'POST':
        return http_response(True)

    processed = False

    sent_timestamp = request.POST.get('sent_timestamp')
    try:
        event_on = datetime.datetime.fromtimestamp(int(sent_timestamp) / 1000)
    except (TypeError, ValueError):
        event_on = None
    identity = request.POST.get('from')
    message = request.POST.get('message')

    # skip SPAM
    if not is_valid_number(identity):
        return http_response(True)

    try:
        existing = TextSMS.incoming.get(identity=identity,
                                        event_on=event_on)
    except TextSMS.DoesNotExist:
        existing = None

    if existing:
        return http_response(True, with_outgoing=True)

    try:
        sms = TextSMS.objects.create(
            identity=identity,
            event_on=event_on,
            text=message,
            direction=TextSMS.INCOMING,
            sim_number=settings.SIM_NUMBER)
        processed = True
    except:
        return http_response(False)

    queue_sms_forward.apply_async([sms])

    return http_response(processed, with_outgoing=True)


def dashboard(request):
    context = {'page': 'dashboard'}

    nb_inc_notsent = TextSMS.incoming.filter(status=TextSMS.STATUS_NOTSENT).count()
    nb_inc_sentok = TextSMS.incoming.filter(status=TextSMS.STATUS_SENTOK).count()
    nb_inc_senterr = TextSMS.incoming.filter(status=TextSMS.STATUS_ERROR).count()

    nb_out_notsent = TextSMS.outgoing.filter(status=TextSMS.STATUS_NOTSENT).count()
    nb_out_sentok = TextSMS.outgoing.filter(status=TextSMS.STATUS_SENTOK).count()
    nb_out_senterr = TextSMS.outgoing.filter(status=TextSMS.STATUS_ERROR).count()

    context.update({"nb_inc_notsent": nb_inc_notsent,
                    "nb_inc_sentok": nb_inc_sentok,
                    "nb_inc_senterr": nb_inc_senterr,
                    "nb_out_notsent": nb_out_notsent,
                    "nb_out_sentok": nb_out_sentok,
                    "nb_out_senterr": nb_out_senterr
                    })
    return render(request, "dashboard.html", context)


def list_incomingsms(request, number=None):

    data_sms = {'incomingsms': [sms.to_dict()
                        for sms in TextSMS.incoming.order_by('-event_on').all()[:number]],
                'outgoingsms': [sms.to_dict()
                        for sms in TextSMS.outgoing.order_by('-event_on').all()[:number]],
                }

    return HttpResponse(json.dumps(data_sms), mimetype='application/json')


def get_graph_context():
    date_start_end = lambda d, s=True: \
        datetime.datetime(int(d.year), int(d.month), int(d.day),
                          0 if s else 23, 0 if s else 59, 0 if s else 59)

    try:
        start = TextSMS.incoming.order_by('event_on')[0].event_on
    except IndexError:
        start = datetime.datetime.today()

    nb_incomingsms = []
    nb_outgoingsms = []
    for date in datetime_range(start):
        ts = int(to_timestamp(date)) * 1000
        sms_in_count = TextSMS.incoming.filter(event_on__gte=date_start_end(date),
                                           event_on__lt=date_start_end(date, False)).count()
        nb_incomingsms.append((ts, sms_in_count))
        sms_out_count = TextSMS.outgoing.filter(event_on__gte=date_start_end(date),
                                           event_on__lt=date_start_end(date, False)).count()
        nb_outgoingsms.append((ts, sms_out_count))
    data_event = {'nb_incomingsms': nb_incomingsms, 'nb_outgoingsms': nb_outgoingsms}
    return data_event


def graph_data(request):
    ''' Return graph data in json '''

    return HttpResponse(json.dumps(get_graph_context()), mimetype='application/json')
