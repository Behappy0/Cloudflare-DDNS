# -*- coding: utf-8 -*-

import re
import sys
import time
import json
import getopt
import logging
import signal
import inspect
import urllib.error
from urllib.request import Request, urlopen
from typing import Dict, Any, Optional


def parameter_join(*parameters: str) -> str:
    return '?' + '&'.join(parameters)


def url_path_join(url: str, *paths: str) -> str:
    paths = tuple(path.removeprefix('/').removesuffix('/') for path in paths)
    return '/'.join([url.removesuffix('/'), *paths])


def record_join(host_name: Optional[str], domain_name: str) -> str:
    return domain_name if host_name is None or host_name.isspace() \
        else host_name + '.' + domain_name


class CloudflareDDNS:

    api = 'https://api.cloudflare.com/client/v4/zones'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'

    def __init__(self, host_name: Optional[str], domain_name: str, token: str, type_: str = 'A', check_period: int = 300, get_ip_url: Optional[str] = None):
        assert type_ in ('A', 'AAAA')
        self.host_name = host_name
        self.domain_name = domain_name
        self.token = token
        self.check_period = check_period
        if get_ip_url is None:
            if type_ == 'A':
                self.get_ip_url = 'https://whatismyipaddress.com/'
            else:
                self.get_ip_url = 'https://whatismyipaddress.com/'
        else:
            self.get_ip_url = get_ip_url
        self.type_ = type_
        self.zone_identifier = self.get_zone_identifier()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def _header(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

    def get_ip_address(self) -> str:
        request = Request(self.get_ip_url, headers={'User-Agent': self.user_agent}, method="GET")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            print("Get ip address failed: " + str(e.code), file=sys.stderr)
            sys.exit(2)
        content_type = response.headers["Content-Type"]
        if content_type is None:
            encoding_charset = "utf-8"
        else:
            content_type = list(filter(lambda item: item.startswith("charset="), content_type.split(';')))
            if not content_type:
                encoding_charset = "utf-8"
            else:
                encoding_charset = content_type[0].split('=')[1].lower()
        content = response.read().decode(encoding=encoding_charset)
        if self.type_ == 'A':
            ip_pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
        else:
            ip_pattern = re.compile(r'(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){6}:[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){5}(:[0-9a-fA-F]{1,4}){1,2})|(([0-9a-fA-F]{1,4}:){4}(:[0-9a-fA-F]{1,4}){1,3})|(([0-9a-fA-F]{1,4}:){3}(:[0-9a-fA-F]{1,4}){1,4})|(([0-9a-fA-F]{1,4}:){2}(:[0-9a-fA-F]{1,4}){1,5})|([0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6}))|(:((:[0-9a-fA-F]{1,4}){1,7}))')
        ip = ip_pattern.search(content)
        if not ip:
            print("Get ip address failed: no ip in response", file=sys.stderr)
            sys.exit(2)
        else:
            return ip.group(0)

    def get_zone_identifier(self) -> str:
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

    def _get_dns_info(self) -> Dict[str, Any]:
        name = "name=" + record_join(self.host_name, self.domain_name)
        types = "type=" + self.type_
        parameters = parameter_join(name, types)
        url = url_path_join(self.api, self.zone_identifier, 'dns_records') + parameters
        request = Request(url, headers=self._header, method="GET")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("Wrong API Token", file=sys.stderr)
                sys.exit(2)
            else:
                raise
        result = json.loads(response.read())['result']
        if not result:
            print("Wrong Domain Name or Host Name", file=sys.stderr)
            sys.exit(2)
        else:
            return result[0]

    def get_ip_record(self) -> str:
        return self._get_dns_info()['content']

    def update_ip_record(self, new_ip: str) -> None:
        dns_info = self._get_dns_info()
        identifier = dns_info['id']
        url = url_path_join(self.api, self.zone_identifier, 'dns_records', identifier)
        data = {
            "content": new_ip,
            "name": record_join(self.host_name, self.domain_name),
            "type": self.type_
        }
        request = Request(url, data=bytes(json.dumps(data), encoding="utf-8"), headers=self._header, method="PUT")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("Wrong API Token", file=sys.stderr)
                sys.exit(2)
            else:
                raise
        if not json.loads(response.read())['success']:
            print("Update IP Record Failed", file=sys.stderr)
            sys.exit(2)

    def run(self) -> None:
        self._running = True
        ip_record = self.get_ip_record()
        while self._running:
            public_ip = self.get_ip_address()
            if ip_record != public_ip:
                self.update_ip_record(public_ip)
                ip_record = public_ip
            time.sleep(self.check_period)

    def stop(self) -> None:
        self._running = False


def print_help_information() -> None:
    print('''A DDNS service using cloudflare api.

Usage: cloudflare-ddns [options...]

Options:
    -n, --name <host_name>              Your host name, "" for no host name. e.g. "www"
    -d, --domain <domain_name>          Your domain name. e.g. "example.com"
    -k, --token <token>                 Your cloudflare api token.
    -t, --type <record_type>            The record type, support "A" and "AAAA".
    -p, --check-period  <check_period>  The period for checking ip address change. Default: 300s
    --ip-url <get_ip_url>               The url to get your ip address. Note: the cloudflare-ddns will open this url and find ip address in response using regular expression.

Gereral options:
    -h, --help                          Print the help information.
    --version                           Print the version of cloudflare-ddns.

Online page: <https://github.com/Behappy0/Cloudflare-DDNS>''')


def print_version() -> None:
    version = ''
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('cloudflare-ddns').version
    except Exception:
        pass
    print('cloudflare-ddns {}'.format(version))


def to_str(s):
    if bytes != str:
        if type(s) == bytes:
            return s.decode('utf-8')
    return str(s)


def parse_input() -> Dict[str, Any]:
    shortopts = 'hk:n:d:t:p:'
    longopts = ['help', 'version', 'token=', 'name=', 'domain=', 'type=', 'check-period=', 'ip-url=']

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
        elif key == '--version':
            print_version()
            sys.exit(0)
        elif key in ('-k', '--token'):
            config['token'] = to_str(value)
        elif key in ('-n', '--name'):
            config['host_name'] = to_str(value) if value else None
        elif key in ('-d', '--domain'):
            config['domain_name'] = to_str(value)
        elif key in ('-t', '--type'):
            config['type_'] = to_str(value)
        elif key in ('-p', '--check-period'):
            config['check_period'] = int(value)
        elif key == '--ip-url':
            config['get_ip_url'] = to_str(value)
        else:
            print("Unknown argument: {}".format(key), file=sys.stderr)
            sys.exit(2)

    sig = inspect.signature(CloudflareDDNS)

    config['host_name'] = config.get('host_name', None)
    config['check_period'] = config.get('check_period', sig.parameters['check_period'].default)
    config['get_ip_url'] = config.get('get_ip_url', sig.parameters['get_ip_url'].default)

    check_config(config)

    return config


def check_python() -> None:
    info = sys.version_info
    if info[0] == 3 and not info[1] >= 9:
        print('Python 3.9+ required.')
        sys.exit(1)
    elif info[0] != 3:
        print('Python version not supported.')
        sys.exit(1)


def check_config(config: Dict[str, Any]) -> None:
    pass


def main() -> None:
    # check python version
    check_python()

    # Set stop signal
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(1))

    # Parse command line inputs
    config = parse_input()

    # Instanlise the DDNS service
    service = CloudflareDDNS(**config)

    # Run the DDNS service
    service.run()


if __name__ == '__main__':
    main()
