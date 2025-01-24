# Centipede-Ublox

Python script providing Centipede NTRIP data directly to the u-blox chip. The correction will be done in the chip, so there's no need for *librtk* to do the correction.

This script is partly based on the excellent [pygnssutils](https://github.com/semuconsulting/pygnssutils) library.

## Configuration

The script can be configured using the provided `centipede.ini` file.

| Parameter | Value(s) | Description |
|-----------|----------|-------------|
| **u-blox**                         |
| port      | /dev/ttyACM0 | Path to the USB port of the GPS |
| baudrate  | 115200   | Communication speed |
| **Caster**                         |
| server | caster.centipede.fr | server address of the caster |
| port   | 2101 | caster server port |
| mountpoint | autodetect | mountpoint to use. If empty or `autodetect`, the script will detect the closest base station automatically |
| **Output**                         |
| type | none | Optional output of the coordinates  Possible values are: `logfile` `tcpserver`or `none` |
| filename |  | filename |
| port | 1234 | output port for position |
| trigger | all | when to write |

