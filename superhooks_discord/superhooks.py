#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

# A event listener meant to be subscribed to PROCESS_STATE_CHANGE
# events.  It will send web hook messages when processes that are children of
# supervisord transition unexpectedly to the EXITED state.

# A supervisor config snippet that tells supervisor to use this script
# as a listener is below.
"""
Usage: superhooks [-u url] [-e events]

Options:
  -h, --help            show this help message and exit
  -f file, --url=URL
                        file which contains discord webhook

  -e EVENTS, --events=EVENTS
                        Supervisor process state event(s)
"""

import copy
import os
import time
import sys
import json

import requests
from superlance.process_state_monitor import ProcessStateMonitor
from supervisor import childutils


class SuperHooksDiscord(ProcessStateMonitor):
    SUPERVISOR_EVENTS = (
        'STARTING',
        'RUNNING',
        'BACKOFF',
        'STOPPING',
        'FATAL',
        'EXITED',
        'STOPPED',
        'UNKNOWN',
    )

    @classmethod
    def _get_opt_parser(cls):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option("-f",
                          "--file",
                          help="File which contains discord web hook.")
        parser.add_option(
            "-e",
            "--events",
            help=
            "Supervisor event(s). Can be any, some or all of {} as comma separated values"
            .format(cls.SUPERVISOR_EVENTS))

        return parser

    @classmethod
    def parse_cmd_line_options(cls):
        parser = cls._get_opt_parser()
        (options, args) = parser.parse_args()
        return options

    @classmethod
    def validate_cmd_line_options(cls, options):
        parser = cls._get_opt_parser()
        if not options.file:
            parser.print_help()
            sys.exit(1)
        if not options.events:
            parser.print_help()
            sys.exit(1)

        validated = copy.copy(options)
        return validated

    @classmethod
    def get_cmd_line_options(cls):
        return cls.validate_cmd_line_options(cls.parse_cmd_line_options())

    @classmethod
    def create_from_cmd_line(cls):
        options = cls.get_cmd_line_options()

        if 'SUPERVISOR_SERVER_URL' not in os.environ:
            sys.stderr.write('Must run as a supervisor event listener\n')
            sys.exit(1)

        if not os.path.exists(options.file):
            sys.stderr.write(
                'Discord webhooks file at {} does not exist'.format(
                    options.file))
            sys.exit(1)

        return cls(**options.__dict__)

    def __init__(self, **kwargs):
        ProcessStateMonitor.__init__(self, **kwargs)
        with open(kwargs['file'], 'r') as discord_webhook_file:
            self.discord_webhook = discord_webhook_file.read().strip()
        events = kwargs.get('events', None)
        self.process_state_events = [
            'PROCESS_STATE_{}'.format(e.strip().upper())
            for e in events.split(",") if e in self.SUPERVISOR_EVENTS
        ]

    def get_process_state_change_msg(self, headers, payload):
        pheaders, pdata = childutils.eventdata(payload + '\n')
        pheaders_all = ""
        for k, v in pheaders.items():
            pheaders_all = pheaders_all + k + ":" + v + " "
        return "{groupname}:{processname};{from_state};{event};{pheaders_all}".format(
            event=headers['eventname'], pheaders_all=pheaders_all, **pheaders)

    def send_batch_notification(self):
        for msg in self.batchmsgs:
            processname, from_state, eventname, pheaders_all = msg.rsplit(';')
            params = {
                'process_name': processname,
                'from_state': from_state,
                'event_name': eventname,
                'pheaders_all': pheaders_all
            }

            embed_data = {
                "embeds": [{
                    "title":
                    processname,
                    "description":
                    "Event Type: {}\nFrom: {}".format(eventname, from_state)
                }]
            }
            result = requests.post(
                self.discord_webhook,
                data=json.dumps(embed_data),
                headers={"Content-Type": "application/json"})
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                sys.stderr.write('[{}] Could not deliver webhook: {}'.format(time.ctime(), err))
            else:
                sys.stderr.write("[{}] Posted to discord webhook successfully".format(time.ctime()))


def main():
    superhooks = SuperHooksDiscord.create_from_cmd_line()
    superhooks.run()


if __name__ == '__main__':
    main()
