#!/usr/bin/python

import sys
sys.path += ['/esp/']

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'esp.settings'

import manage
from esp.dbmail.cronmail import send_miniblog_messages, process_messages, send_email_requests
#send_event_notices_for_day('tomorrow')
#send_miniblog_messages()
process_messages()
send_email_requests()
