from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import re
import sys
import time
import json
import getopt
import signal
import urllib.error
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class CloudflareDDNS:

    api = 'https://api.cloudflare.com/client/v4/zones'

    def __init__(self, host_name, domain_name, token, types='A', check_period=60, address='http://www.net.cn/static/customercare/yourip.asp'):
        self.host_name = host_name
        self.domain_name = domain_name
        self.token = token
        self.check_period = check_period
        self.address = address
        self.types = types
        self._zone_identifier = self._get_zone_identifier()
        self._running = True

    @property
    def _header(self):
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

    def _get_ip_address(self):
        try:
            get_ip_url = urlopen(self.address)
        except urllib.error.HTTPError as e:
            print("Get ip address failed: " + e.code, file=sys.stderr)
            sys.exit(2)
        get_ip_response = get_ip_url.read()
        ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = ip_pattern.findall(get_ip_response)
        if not ip:
            print("Get ip address failed: no ip in response", file=sys.stderr)
            sys.exit(2)
        else:
            return ip[0]

    def _get_zone_identifier(self):
        name = "name=" + self.domain_name
        parameters = "?" + name
        url = self.api + parameters
        request = Request(url, headers=self._header, method="GET")
        try:
            response = urlopen(request).read()
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("Wrong API Token", file=sys.stderr)
                sys.exit(2)
            else:
                raise
        result = json.loads(response)['result']
        if not result:
            print("Wrong Domain Name", file=sys.stderr)
            sys.exit(2)
        else:
            return result[0]['id']

    def _get_ip_record(self):
        name = "name=" + self.domain_name
        types = "type=" + self.types
        parameters = "?" + name + types
        url = urljoin(self.api, self._zone_identifier, 'dns_records') + parameters
        request = Request(url, headers=self._header, method="GET")

    def _update_ip_record(self, new_ip):
        pass

    def run(self):
        self._running = True
        ip_record = self._get_ip_record()
        while self._running:
            public_ip = self._get_ip_address()
            if ip_record != public_ip:
                self._update_ip_record(public_ip)
                ip_record = public_ip
            time.sleep(self.check_period)

    def stop(self):
        self._running = False


def print_help_information():
    pass


def parse_input():
    shortopts = 'hp:'
    longopts = ['help', 'check-period=']

    try:
        optdict, _ = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    config = dict()
    for key, value in optdict:
        if key in ('-h', '--help'):
            print_help_information()
            sys.exit(0)

    return config


def check_python():
    info = sys.version_info
    if info[0] == 2 and not info[1] >= 6:
        print('Python 2.6+ required.')
        sys.exit(1)
    elif info[0] == 3 and not info[1] >= 6:
        print('Python 3.6+ required.')
        sys.exit(1)
    elif info[0] not in [2, 3]:
        print('Python version not supported.')
        sys.exit(1)


def check_config(config):
    pass


def main():
    # check python version
    check_python()

    # Set stop signal
    signal.signal(signal.SIGINT, lambda: sys.exit(1))

    # Parse command line inputs
    config = parse_input()

    # check config
    check_config(config)

    # Instanlise the DDNS service
    service = CloudflareDDNS()

    # Run the DDNS service
    service.run()


if __name__ == '__main__':
    main()