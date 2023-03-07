# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import getopt
import signal


class CloudflareDDNS:
    def __init__(self, host_name, domain_name, token, check_period, address='ip.cn'):
        self._host_name = host_name
        self._domain_name = domain_name
        self._token = token
        self._check_period = check_period
        self._address = address
        self._types = 'A'
        self._running = True

    def _get_ip_address(self):
        get_ip_method = os.popen('curl -s ' + self._address)
        get_ip_responses = get_ip_method.readlines()[0]
        ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = ip_pattern.findall(get_ip_responses)[0]
        return ip

    def _get_ip_record(self):
        pass

    def _update_ip_record(self, new_ip):
        pass

    def run(self):
        ip_record = self._get_ip_record()
        while self._running:
            public_ip = self._get_ip_address()
            if ip_record != public_ip:
                self._update_ip_record(public_ip)
                ip_record = public_ip
            time.sleep(self._check_period)

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
    elif info[0] == 3 and not info[1] >= 3:
        print('Python 3.3+ required.')
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

    # Instanlise the DDNS service
    service = CloudflareDDNS()

    # Run the DDNS service
    service.run()


if __name__ == '__main__':
    main()
