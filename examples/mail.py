#!/usr/bin/env python
import sys
import smtplib
from optparse import OptionParser
from email.mime.text import MIMEText
import json
from datetime import datetime
try:
    from sensu import Handler
except ImportError:
    print('You must have the sensu Python module i.e.: pip install sensu')
    sys.exit(1)

class MailHandler(Handler):
    def handle(self):
	subj = self.settings.get('mail', {}).get('subject', 'Sensu Alert')
        to = self.settings.get('mail', {}).get('to', 'root@localhost')
        from_addr = self.settings.get('mail', {}).get('from', 'sensu@localhost')
        host = self.settings.get('mail', {}).get('host', 'localhost')
        port = self.settings.get('mail', {}).get('port', 25)
        user = self.settings.get('mail', {}).get('user', None)
        password = self.settings.get('mail', {}).get('password', None)
        self.send(subj, to, from_addr, host, port, user, password)

    def send(self, subj=None, to_addr=None, from_addr=None, host='localhost',
        port=25, user=None, password=None):
        # attempt to parse sensu message
        try:
            data = self.event
            host = data.get('client', {}).get('name')
            check_name = data.get('check', {}).get('name')
            check_action = data.get('action')
            timestamp = data.get('check', {}).get('issued')
            check_date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            parts = (
                'Date: {0}'.format(check_date),
                'Host: {0}'.format(host),
                'Address: {0}'.format(data.get('client', {}).get('address')),
                'Action: {0}'.format(check_action),
                'Name: {0}'.format(check_name),
                'Command: {0}'.format(data.get('check', {}).get('command')),
                'Output: {0}'.format(data.get('check', {}).get('output')),
            )
            text = '\n'.join(parts)
            subj = '{0} [{1}: {2} ({3})]'.format(subj, host, check_name, check_action)
        except Exception, e:
            text = str(e)
        msg = MIMEText(text)
        msg['Subject'] = subj
        msg['To'] = to_addr
        msg['From'] = from_addr
        s = smtplib.SMTP(host, int(port))
        if user:
            s.login(user, password)
        s.sendmail(from_addr, [to_addr], msg.as_string())
        s.quit()

if __name__=='__main__':
    m = MailHandler()
    sys.exit(0)

