#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from autopulse.data import PulseSink
from autopulse.exceptions import PulseSinkParseException

from pathlib import Path
from pulsectl import Pulse

import argparse
import sys
import yaml

CONFIG_FILE_SOURCES = (Path.home().joinpath('.config/autopulse.yml'), Path('/etc/autopulse.yml'))


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(prog="autopulse")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    # auto switch
    auto_parser = subparsers.add_parser('switch', help="Switch to the first available hotplug sink or the default.")
    auto_parser.set_defaults(callback=auto_switch)

    # list command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help="List available outputs and identifiers.")
    list_parser.set_defaults(callback=list_outputs)

    # set output command
    set_parser = subparsers.add_parser('set-output', aliases=['set'], help="Switch the output to a given device.")
    set_parser.set_defaults(callback=set_output)
    set_parser.add_argument('id', help="Device identifier to switch to. See output of the list command.")

    args = parser.parse_args()
    args.callback(args)


def list_outputs(args):
    """List available outputs and their unique vendor/product ids."""

    pulse = Pulse('autopulse')
    default_sink = pulse.server_info().default_sink_name

    for sink in pulse.sink_list():
        is_default = "*" if sink.name == default_sink else " "
        vendor = sink.proplist.get('device.vendor.id')
        product = sink.proplist.get('device.product.id')
        desc = sink.proplist.get('device.description')
        print(" {default} {vendor}:{product} {desc}".format(vendor=vendor, product=product, desc=desc,
            default=is_default))


def auto_switch(args):
    """Automatically switch to the first available hotplug output."""
    valid_configs = list(filter(lambda p: p.is_file(), CONFIG_FILE_SOURCES))

    if len(valid_configs) == 0:
        error("ERROR: Unable to load a configuration file from any of the following paths: \n{}".format(
            "\n".join(map(lambda p: " - {}".format(str(p)), CONFIG_FILE_SOURCES))
        ))

    # we have an extant configuration file
    config_file = valid_configs[0]

    # try to parse the configuration file
    with config_file.open('rb') as f:
        try:
            config = yaml.load(f.read())
        except Exception as e:
            error("ERROR: Unable to parse {}: {}".format(str(config_file), str(e)))

    # make sure that it's a dictionary
    if not type(config) is dict:
        error("ERROR: failed to parse dictionary from config.")

    # make sure that the default sink is defined
    try:
        default_ps = PulseSink.from_string(config.get('default', ''))
    except PulseSinkParseException as e:
        error("ERROR: Unable to load default sink from config - {}".format(e))

    # setup pulse
    pulse = Pulse('autopulse')

    # fetch the default sink
    default_sinks = list(filter(lambda s: s == default_ps, pulse.sink_list()))

    if len(default_sinks) == 0:
        error("ERROR: Unable to find default sink: {}".format(str(default_ps)))

    default_sink = default_sinks[0]

    # try to extract a list of hotplug sinks
    try:
        hotplug_sink_ids = list(map(lambda s: PulseSink.from_string(s), config.get('hotplug', [])))
    except PulseSinkParseException as e:
        error("ERROR: Unable to parse hotplug sink id: {}".format(str(e)))

    # get the actual extant hotplug sinks
    hotplug_sinks = list(filter(lambda s: s in hotplug_sink_ids, pulse.sink_list()))

    if len(hotplug_sinks) > 0:
        print("Switching to Hotplug Sink: \"{}\"".format(hotplug_sinks[0].proplist.get('device.description')))
        switch_to_sink(pulse, hotplug_sinks[0])
    else:
        print("Switching to Default Sink, No Hotplug Sinks Found: {}".format(default_sink.proplist.get('device.description')))
        switch_to_sink(pulse, default_sink)


def set_output(args):
    """Set the default sink to the given vendor/product id combination."""
    try:
        # try to parse the sink from user input
        ps = PulseSink.from_string(args.id)
    except PulseSinkParseException as e:
        error("ERROR: {}".format(str(e)))

    pulse = Pulse('autopulse')
    default_sink_name = pulse.server_info().default_sink_name

    new_sinks = list(filter(lambda s: ps == s, pulse.sink_list()))

    if len(new_sinks) == 0:
        error("ERROR: Unable to find device: {}".format(ps))

    switch_to_sink(pulse, new_sinks[0])


def switch_to_sink(pulse, sink):
    """Switch output to the given sink."""

    # set the default sink
    pulse.default_set(sink)

    # move existing streams over to the sink
    for sink_input in pulse.sink_input_list():
        pulse.sink_input_move(sink_input.index, sink.index)


def error(message, rc=1):
    """Print an error and exit."""
    sys.stderr.write(message + "\n")
    sys.stderr.flush()
    sys.exit(rc)
