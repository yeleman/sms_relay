#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from celery import task

from sms_relay.utils import forward_sms


@task(name='queue_sms_forward')
def queue_sms_forward(sms):
    forward_sms(sms)
