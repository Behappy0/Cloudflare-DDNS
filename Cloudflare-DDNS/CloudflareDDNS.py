#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import getopt
import signal


class CloudflareDDNS:
    def __init__(self, token, checkPeriod, address='ip.cn'):
        self._token = token
        self._checkPeriod = checkPeriod
        self._address = address
        self._running = True

    def _getIPAddress(self):
        getIPMethod = os.popen('curl -s ' + self._address)
        getIPResponses = getIPMethod.readlines()[0]
        ipPattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = ipPattern.findall(getIPResponses)[0]
        return ip

    def _getIPRecord(self):
        pass

    def _updateIPRecord(self, newIP):
        pass

    def Run(self):
        ipRecord = self._getIPRecord()
        while self._running:
            publicIP = self._getIPAddress()
            if ipRecord != publicIP:
                self._updateIPRecord(publicIP)
                ipRecord = publicIP
            time.sleep(self._checkPeriod)

    def Stop(self):
        self._running = False


def printHelpInformation():
    pass


def parseInput():
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
            printHelpInformation()
            sys.exit(0)

    return config


def main():
    # Set stop signal
    signal.signal(signal.SIGINT, lambda: sys.exit(1))

    # Parse command line inputs
    config = parseInput()

    # Instanlise the DDNS service
    service = CloudflareDDNS()

    # Run the DDNS service
    service.Run()


if __name__ == '__main__':
    main()
