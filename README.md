# lifx_exporter
Expose metrics about your light bulbs because why not. Largely written A)
because metrics, B) because I wanted to get to know the aiolifx library. As
such, don't expect perfect code quality.

Bulbs should be discovered by this exporter within a couple of minutes of them
appearing on the network.

## Requirements

`python` >= 3.4, `[aiolifx](https://github.com/frawau/aiolifx)`,
`[prometheus client_python](https://github.com/prometheus/client_python)`,
some LIFX bulbs that are discoverable.

This has only been tested on Linux, but I don't see why it wouldn't work
elsewhere.

## Usage

Run the script, optionally with a --port option (default is 8564). A unit file
is provided for your convenience if you use systemd.

## Metrics
All metrics have the following labels:
- **name**: The label (LIFX terminology) applied to the bulb
- **location**: The overall location a bulb is in (i.e. "My Home" by default)
- **group**: The group a bulb has been assigned to
- **type**: What type of bulb it is, with the caveat that this is a useless
  number unless you have the same bulbs as me (A19)

The following metrics are exposed:
- `lifx_bulb_on`: Self explanatory, 1 = on, 0 = off
- `lifx_bulb_hue`: 16-bit integer representing the hue
- `lifx_bulb_saturation`: Unsigned 16-bit integer representing the saturation
- `lifx_bulb_brightness`: Unsigned 16-bit integer representing the brightness
- `lifx_bulb_kelvin`: Unsigned 16-bit integer representing the colour
  temperature in Kelvin, valid values are from 2500-9000.

Metric values will all be set to -1 if requests time out. This may or may not
be desirable.
