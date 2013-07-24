#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models

DATE_FMT = u'%A %d %B %Y %Hh:%Mmn'


class IncomingSMS(models.Model):

    STATUS_NOTSENT = 'not_sent'
    STATUS_SENTOK = 'sent_ok'
    STATUS_ERROR = 'error'

    STATUSES = {
        STATUS_NOTSENT: "Not Sent",
        STATUS_SENTOK: "Sent OK.",
        STATUS_ERROR: "Error"
    }

    PENDING_STATUSES = (STATUS_NOTSENT, STATUS_ERROR)

    identity = models.CharField(max_length=30)
    received_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUSES.items(),
                              default=STATUS_NOTSENT)
    text = models.TextField(blank=True, null=True)
    destination = models.CharField(max_length=30)

    def __unicode__(self):
        return self.text

    def to_dict(self):
        return {'identity': self.identity, 'text': self.text,
                'status': self.status,
                'received_on': self.received_on.strftime(DATE_FMT)}
