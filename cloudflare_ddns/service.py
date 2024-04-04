# -*- coding: utf-8 -*-

import re
import sys
import time
import json
import getopt
import logging
import signal
import urllib.error
from urllib.request import Request, urlopen
from typing import Dict, Any, Optional


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(filename)s: %(lineno)d] - %(message)s')


def parameter_join(*parameters: str) -> str:
    return '?' + '&'.join(parameters)


def url_path_join(url: str, *paths: str) -> str:
    paths = tuple(path.removeprefix('/').removesuffix('/') for path in paths)
    return '/'.join([url.removesuffix('/'), *paths])


def record_join(host_name: Optional[str], domain_name: str) -> str:
    if host_name is None or host_name.isspace():
        return domain_name
    else:
        return host_name + '.' + domain_name


class CloudflareDDNS:

    api = 'https://api.cloudflare.com/client/v4/zones'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'

    def __init__(self, host_name: Optional[str], domain_name: str, token: str, type_: str, check_period: int = 300, get_ip_url: Optional[str] = None):
        assert type_ in ('A', 'AAAA')
        self.host_name = host_name
        self.domain_name = domain_name
        self.token = token
        self.type_ = type_
        self.check_period = check_period
        if get_ip_url is None:
            if type_ == 'A':
                self.get_ip_url = 'https://myip4.ipip.net'
            else:
                self.get_ip_url = 'https://myip6.ipip.net'
        else:
            self.get_ip_url = get_ip_url
        self.zone_identifier = self.get_zone_identifier()
        self._running = False
        logging.info('The DDNS service has initialized, configuration:\n{}'.format(json.dumps({
            'name': record_join(self.host_name, self.domain_name),
            'type': self.type_,
            'check_period': self.check_period,
            'get_ip_url': self.get_ip_url
        }, sort_keys=False, indent=4)))

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
            logging.error("Get ip address failed: " + str(e.code))
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
            logging.error("Get ip address failed: no IP in response.")
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
                logging.error("Wrong API token.")
                sys.exit(2)
            else:
                raise
        result = json.loads(response.read())['result']
        if not result:
            logging.error("Wrong domain name.")
            sys.exit(2)
        else:
            return result[0]['id']

    def _get_dns_info(self) -> Dict[str, Any]:
        name = "name=" + record_join(self.host_name, self.domain_name)
        type_ = "type=" + self.type_
        parameters = parameter_join(name, type_)
        url = url_path_join(self.api, self.zone_identifier, 'dns_records') + parameters
        request = Request(url, headers=self._header, method="GET")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                logging.error("Wrong API token.")
                sys.exit(2)
            else:
                raise
        result = json.loads(response.read())['result']
        if not result:
            logging.error("Wrong host name or record type.")
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
            "name": dns_info["name"],
            "type": dns_info["type"],
            "proxied": dns_info["proxied"],
            "ttl": dns_info["ttl"],
            "comment": dns_info["comment"]
        }
        request = Request(url, data=bytes(json.dumps(data), encoding="utf-8"), headers=self._header, method="PUT")
        try:
            response = urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                logging.error("Wrong API token.")
                sys.exit(2)
            else:
                raise
        if not json.loads(response.read())['success']:
            logging.error("Update IP record failed.")
            sys.exit(2)

    def run(self) -> None:
        logging.info('The DDNS service has started.')
        self._running = True
        ip_record = self.get_ip_record()
        while self._running:
            logging.info('Checking ip change ...')
            public_ip = self.get_ip_address()
            logging.info('Current ip record: {}'.format(ip_record))
            logging.info('Current ip address: {}'.format(public_ip))
            if ip_record != public_ip:
                logging.info('Updating ip record {} -> {}'.format(ip_record, public_ip))
                self.update_ip_record(public_ip)
                logging.info('Update ip record success.')
                ip_record = public_ip
            time.sleep(self.check_period)

    def stop(self) -> None:
        logging.info('The DDNS service has stopped.')
        self._running = False


def print_help_information() -> None:
    print('''A DDNS service using cloudflare api.

Usage: cloudflare-ddns [options...]

Options:
    -n, --name <host_name>              Your host name, "" for no host name. e.g. "www"
    -d, --domain <domain_name>          Your domain name. e.g. "example.com"
    -k, --token <token>                 Your cloudflare api token.
    -t, --type <record_type>            The record type, supports "A" and "AAAA".
    -p, --check-period <check_period>   The period for checking ip address change. Default: 300s
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


def parse_input() -> Dict[str, Any]:
    shortopts = 'hk:n:d:t:p:'
    longopts = ['help', 'version', 'token=', 'name=', 'domain=', 'type=', 'check-period=', 'ip-url=']

    try:
        if sys.argv[0] in ("python", "python3"):
            argv = sys.argv[2:]
        else:
            argv = sys.argv[1:]
        optdict, _ = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError as e:
        logging.error(e)
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
            config['token'] = str(value)
        elif key in ('-n', '--name'):
            config['host_name'] = str(value) if value else None
        elif key in ('-d', '--domain'):
            config['domain_name'] = str(value)
        elif key in ('-t', '--type'):
            config['type_'] = str(value)
        elif key in ('-p', '--check-period'):
            config['check_period'] = int(value)
        elif key == '--ip-url':
            config['get_ip_url'] = str(value)
        else:
            logging.error("Unknown argument: {}".format(key))
            sys.exit(2)

    config['host_name'] = config.get('host_name', None)

    check_config(config)

    return config


def check_python() -> None:
    info = sys.version_info
    if info[0] == 3 and not info[1] >= 9:
        logging.error('Python 3.9+ required.')
        sys.exit(1)
    elif info[0] != 3:
        logging.error('Python version not supported.')
        sys.exit(1)


def check_config(config: Dict[str, Any]) -> None:
    if 'domain_name' not in config:
        logging.error('Domain name is not specified.')
        print_help_information()
        sys.exit(2)

    if 'type_' not in config:
        logging.error('Record type is not specified.')
        print_help_information()
        sys.exit(2)

    if 'token' not in config:
        logging.error('Token is not specified.')
        print_help_information()
        sys.exit(2)

    if config['type_'] not in ('A', 'AAAA'):
        logging.error('The record type must be "A" or "AAAA".')
        sys.exit(2)


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
