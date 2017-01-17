# autopulse

Script for dynamically changing your default PulseAudio sink on hotplug events for USB peripherals, etc.

## Hotplug Configuration

`autopulse` uses only one configuration file called `autopulse.yml`, located either in `$HOME/.config/autopulse.yml` or
`/etc/autopulse.yml`. This file's format is as follows:

```
---
default: "abcd:ef01"
hotplug:
  - "dead:beef"
  - "cafe:babe"
```

One default sink must be named, and as many hotplug sinks as desired can be listed. The script chooses the first present
hotplug sink found, otherwise falls back to the default sink.

Device identifiers can be listed as follows:

```
$ autopulse ls
  1002:aab0 Cape Verde/Pitcairn HDMI Audio [Radeon HD 7700/7800 Series] Digital Stereo (HDMI)
  8086:0d0c Built-in Audio Digital Stereo (HDMI)
  8086:8c20 Built-in Audio Analog Stereo
* 0d8c:1066 I'm Fulla Schiit Analog Stereo
```

The current sink is prefixed with a `*` character.

## System Configuration

The easiest way to get auto hotplugging working is via systemd and udev. Create a systemd unit at
`/etc/systemd/system/autopulse@.service`:

```
[Unit]
Description=PulseAudio Hotplug Service

[Service]
Type=oneshot
Environment=DISPLAY=:0
User=%i
ExecStart=/usr/local/bin/autopulse switch
```

Next, we'll create a udev rule which calls this unit:

```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0d8c", ATTRS{idProduct}=="1066", ENV{SYSTEMD_WANTS}="autopulse@naftuli.service"
```

Whenever a USB device with the given product and vendor ids is attached, detached, or changed, the systemd unit will
be called, running as user `naftuli`.

> **NOTE:** It's still unfortunately necessary to set `DISPLAY` so that the script can find the PulseAudio daemon. If
> anyone knows a better solution for this, please send it my way.
