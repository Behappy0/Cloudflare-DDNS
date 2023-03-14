# -*- coding: utf-8 -*-

import re
import sys
import time
import json
import getopt
import signal
import urllib.error
from urllib.request import Request, urlopen


def parameter_join(*parameters: str) -> str:
    return '?' + '&'.join(parameters)


def url_path_join(url: str, *paths: str) -> str:
    paths = [path.removeprefix('/').removesuffix('/') for path in paths]
    return '/'.join([url.removesuffix('/'), *paths])


def record_join(host_name: str, domain_name: str) -> str:
    return domain_name if host_name is None or host_name.isspace() \
        else host_name + '.' + domain_name


class CloudflareDDNS:

    api = 'https://api.cloudflare.com/client/v4/zones'

    def __init__(self, host_name: str or None, domain_name: str, token: str, types: str = 'A', check_period: int = 60, get_ip_url: str = 'http://www.net.cn/static/customercare/yourip.asp'):
        self.host_name = host_name
        self.domain_name = domain_name
        self.token = token
        self.check_period = check_period
        self.get_ip_url = get_ip_url
        self.types = types
        self._zone_identifier = self._get_zone_identifier()
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def _header(self) -> dict[str, str]:
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

    def get_ip_address(self) -> str:
        try:
            get_ip_response = urlopen(self.get_ip_url)
        except urllib.error.HTTPError as e:
            print("Get ip address failed: " + str(e.code), file=sys.stderr)
            sys.exit(2)
        content_type = get_ip_response.headers["Content-Type"]
        if content_type is None:
            encoding_charset = "utf-8"
        else:
            content_type = list(filter(lambda item: item.startswith("charset="),
                                       content_type.split(';')))
            if not content_type:
                encoding_charset = "utf-8"
            else:
                encoding_charset = content_type[0].split('=')[1].lower()
        get_ip_content = get_ip_response.read().decode(encoding=encoding_charset)
        ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = ip_pattern.findall(get_ip_content)
        if not ip:
            print("Get ip address failed: no ip in response", file=sys.stderr)
            sys.exit(2)
        else:
            return ip[0]

    def _get_zone_identifier(self) -> str:
        name = "name=" + self.domain_name
        parameters = parameter_join(name)
        url = self.api + parameters
        request = Request(url, headers=self._header, method="GET")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("Wrong API Token", file=sys.stderr)
                sys.exit(2)
            else:
                raise
        result = json.loads(response.read())['result']
        if not result:
            print("Wrong Domain Name", file=sys.stderr)
            sys.exit(2)
        else:
            return result[0]['id']

    def get_ip_record(self) -> str:
        name = "name=" + record_join(self.host_name, self.domain_name)
        types = "type=" + self.types
        parameters = parameter_join(name, types)
        url = url_path_join(self.api, self._zone_identifier,
                            'dns_records') + parameters
        request = Request(url, headers=self._header, method="GET")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("Wrong API Token", file=sys.stderr)
                sys.exit(2)
            else:
                raise

    def update_ip_record(self, new_ip: str) -> bool:
        pass

    def run(self) -> None:
        self._is_running = True
        ip_record = self.get_ip_record()
        while self._is_running:
            public_ip = self.get_ip_address()
            if ip_record != public_ip:
                self.update_ip_record(public_ip)
                ip_record = public_ip
            time.sleep(self.check_period)

    def stop(self) -> None:
        self._is_running = False


def print_help_information() -> None:
    pass


def parse_input() -> dict[str, any]:
    shortopts = 'hp:'
    longopts = ['help', 'check-period=']

    try:
        optdict, _ = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print_help_information()
        sys.exit(2)

    config = dict()
    for key, value in optdict:
        if key in ('-h', '--help'):
            print_help_information()
            sys.exit(0)

    return config


def check_python() -> None:
    info = sys.version_info
    if info[0] == 3 and not info[1] >= 9:
        print('Python 3.9+ required.')
        sys.exit(1)
    elif info[0] != 3:
        print('Python version not supported.')
        sys.exit(1)


def check_config(config: dict[str, any]) -> None:
    pass


def main() -> None:
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
