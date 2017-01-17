#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from autopulse.exceptions import PulseSinkParseException

import pulsectl
import re

SINK_ID_RX = re.compile(r'(?P<vendor>[a-f0-9]{4}):(?P<product>[a-f0-9]{4})', re.I)


class PulseSink(object):

    @classmethod
    def from_string(cls, value):
        if value is None or not SINK_ID_RX.match(value):
            raise PulseSinkParseException("Unable to parse sink identifier from: {value}".format(value=value))

        m = SINK_ID_RX.match(value)

        return PulseSink(vendor_id=m.group('vendor'), product_id=m.group('product'))

    def __init__(self, vendor_id, product_id):
        """Create a new PulseSink object with the given vendor and product id."""
        self.vendor_id = vendor_id
        self.product_id = product_id

    def __str__(self):
        """Render as a readable string."""
        return "{vendor_id}:{product_id}".format(vendor_id=self.vendor_id, product_id=self.product_id)

    def __eq__(self, other):
        """Test equality."""
        if type(other) is PulseSink:
            return self.vendor_id == other.vendor_id and self.product_id == other.vendor_id
        elif type(other) is pulsectl.PulseSinkInfo:
            return self.vendor_id == other.proplist.get('device.vendor.id', '') and \
                self.product_id == other.proplist.get('device.product.id', '')
        else:
            return False
