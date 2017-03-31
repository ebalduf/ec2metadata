# Copyright (c) 2013 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of ec2metadata.
#
# ec2metadata is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
import time
import requests

METAOPTS = ['ami-id', 'ami-launch-index', 'ami-manifest-path',
            'ancestor-ami-id', 'availability-zone', 'block-device-mapping',
            'instance-id', 'instance-type', 'local-hostname', 'local-ipv4',
            'kernel-id', 'product-codes', 'public-hostname', 'public-ipv4',
            'public-keys', 'ramdisk-id', 'reservation-id', 'security-groups',
            'user-data']

class Error(Exception):
    pass

class EC2Metadata:
    """Class for querying metadata from EC2"""

    def __init__(self, addr='169.254.169.254', api='2008-02-01'):
        self.addr = addr
        self.api = api

        if not self._test_connectivity(self.addr, 80):
            raise Error("could not establish connection to: %s" % self.addr)

    @staticmethod
    def _test_connectivity(addr, port):
        try:
          r = requests.get(('http://%s:%s/' % (addr, port)), timeout=6)
          r.raise_for_status()
        except Exception as e:
          return False

        return True

    def _get(self, uri):
        url = 'http://%s/%s/%s' % (self.addr, self.api, uri)
        try:
          r = requests.get(url, timeout=6)
          r.raise_for_status()
        except:
            return None

        return r.text

    def get(self, metaopt):
        """return value of metaopt"""

        if metaopt not in METAOPTS:
            raise Error('unknown metaopt', metaopt, METAOPTS)

        if metaopt == 'availability-zone':
            return self._get('meta-data/placement/availability-zone')

        if metaopt == 'public-keys':
            public_keys = []
            data = self._get('meta-data/public-keys')
            if not data:
                return public_keys

            keyids = [ line.split('=')[0] for line in data.splitlines() ]
            for keyid in keyids:
                uri = 'meta-data/public-keys/%d/openssh-key' % int(keyid)
                public_keys.append(self._get(uri).rstrip())

            return public_keys

        if metaopt == 'user-data':
            return self._get('user-data')

        return self._get('meta-data/' + metaopt)

def get(metaopt):
    """primitive: return value of metaopt"""

    m = EC2Metadata()
    return m.get(metaopt)

def display(metaopts, prefix=False):
    """primitive: display metaopts (list) values with optional prefix"""

    m = EC2Metadata()
    for metaopt in metaopts:
        value = m.get(metaopt)
        if not value:
            value = "unavailable"

        if prefix:
            print "%s: %s" % (metaopt, value)
        else:
            print value

