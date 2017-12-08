#!/usr/bin/env python3
"""Export some metrics for LIFX bulbs"""

import argparse
import sys
import asyncio as aio
from functools import partial

from prometheus_client import start_http_server, Gauge
import aiolifx as alix

UDP_BROADCAST_PORT = 56700

standard_labels = ['name', 'location', 'group', 'type']

bulb_power = Gauge('lifx_bulb_on', 'Power state of light bulb', standard_labels)
bulb_hue = Gauge('lifx_bulb_hue', 'Hue of light bulb', standard_labels)
bulb_saturation = Gauge('lifx_bulb_saturation', 'Saturation of light bulb', standard_labels)
bulb_brightness = Gauge('lifx_bulb_brightness', 'Brightness of light bulb', standard_labels)
bulb_kelvin = Gauge('lifx_bulb_kelvin', 'Colour temperature of light bulb', standard_labels)


class Bulbs():
    """A structure containing bulbs."""
    def __init__(self):
        self.bulbs = []

    def register(self, bulb):
        """Register a light bulb"""
        bulb.get_label()
        bulb.get_location()
        bulb.get_version()
        bulb.get_group()
        bulb.get_wififirmware()
        bulb.get_hostfirmware()
        self.bulbs.append(bulb)
        self.bulbs.sort(key=lambda x: x.label or x.mac_addr)

    def unregister(self, bulb):
        """Unregister a light bulb"""
        idx = 0
        for x in list([y.mac_addr for y in self.bulbs]):
            if x == bulb.mac_addr:
                del self.bulbs[idx]
                break
            idx += 1


@aio.coroutine
def update_bulbs(my_bulbs):
    """Update the status of our bulbs"""
    while True:
        for bulb in my_bulbs.bulbs:
            colour_callback = partial(update_metrics)
            bulb.get_color(callb=colour_callback)
        yield from aio.sleep(5)


def update_metrics(bulb, resp):
    """Given a callback from a colour request, update some metrics"""

    # Because I only own one kind of bulb, sorry
    if bulb.product == 27:
        product = 'LIFX A19'
    else:
        product = bulb.product

    label_values = [bulb.label, bulb.location, bulb.group, product]

    # If we haven't got anything, set the values to -1 to make this obvious
    if not resp:
        bulb_power.labels(*label_values).set(-1)
        bulb_hue.labels(*label_values).set(-1)
        bulb_saturation.labels(*label_values).set(-1)
        bulb_brightness.labels(*label_values).set(-1)
        bulb_kelvin.labels(*label_values).set(-1)
        return

    bulb_power.labels(*label_values).set(min(resp.power_level, 1))
    bulb_hue.labels(*label_values).set(resp.color[0])
    bulb_saturation.labels(*label_values).set(resp.color[1])
    bulb_brightness.labels(*label_values).set(resp.color[2])
    bulb_kelvin.labels(*label_values).set(resp.color[3])


def main():
    """Do stuff with things."""
    parser = argparse.ArgumentParser(description='Expose LIFX bulb metrics')
    parser.add_argument('--port', type=int, nargs='?', help='Port to listen on',
                        default=8564)
    args = parser.parse_args()

    start_http_server(args.port)

    my_bulbs = Bulbs()
    loop = aio.get_event_loop()
    coro = loop.create_datagram_endpoint(
        partial(alix.LifxDiscovery, loop, my_bulbs),
        local_addr=('0.0.0.0', UDP_BROADCAST_PORT))

    loop.create_task(coro)
    aio.Task(update_bulbs(my_bulbs))

    loop.run_forever()


if __name__ == '__main__':
    main()
