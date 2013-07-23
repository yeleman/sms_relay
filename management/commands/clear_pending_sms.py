#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django.core.management.base import BaseCommand

from sms_relay.utils import clear_pending_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('clear_sms_mgmt')


class Command(BaseCommand):
    help = "Clear all not sent and errored SMS (send to Souktel)"

    def handle(self, *args, **options):
        logger.info("Starting to clear messages…")
        status = clear_pending_messages()
        logger.info("Clearing process done: {}".format(status))
