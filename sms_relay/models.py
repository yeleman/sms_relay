#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models

DATE_FMT = u'%A %d %B %Y %Hh:%Mmn'


class IncomingManager(models.Manager):

    def get_query_set(self):
        return super(IncomingManager, self).get_query_set().filter(direction=TextSMS.INCOMING)


class OutgoingManager(models.Manager):

    def get_query_set(self):
        return super(OutgoingManager, self).get_query_set().filter(direction=TextSMS.OUTGOING)


class TextSMS(models.Model):

    STATUS_NOTSENT = 'not_sent'
    STATUS_SENTOK = 'sent_ok'
    STATUS_ERROR = 'error'

    STATUSES = {
        STATUS_NOTSENT: "Not Sent",
        STATUS_SENTOK: "Sent OK.",
        STATUS_ERROR: "Error"
    }

    INCOMING = 'incoming'
    OUTGOING = 'outgoing'

    DIRECTIONS = {
        INCOMING: "Incoming",
        OUTGOING: "Outgoing"
    }

    PENDING_STATUSES = (STATUS_NOTSENT, STATUS_ERROR)

    direction = models.CharField(max_length=30, choices=DIRECTIONS.items())

    identity = models.CharField(max_length=30)
    event_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUSES.items(),
                              default=STATUS_NOTSENT)
    text = models.TextField(blank=True, null=True)
    sim_number = models.CharField(max_length=30)

    objects = models.Manager()
    incoming = IncomingManager()
    outgoing = OutgoingManager()

    def __unicode__(self):
        return self.text

    def to_dict(self):
        return {'identity': self.identity, 'text': self.text,
                'status': self.status,
                'event_on': self.event_on.strftime(DATE_FMT)}
