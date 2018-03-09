## Headless RPi configuration

Headless setup for a RaspberryPi 3 to connect to a WiFi network and allow SSH.

### Prerequisites

The following has only been attempted on a Debian machine.

Download and burn the [raspbian-stretch-lite](https://downloads.raspberrypi.org/raspbian_lite_latest) image into an SD card.

Assert that the SD card is available under `/media/$USER`. Follow the next steps to configure the RPi for headless setup.

### Usage

**NOTE: Run the `rpi_headless.py` script as sudo.**

```bash
$ sudo ./rpi_headless.py --ssid <WiFI_name> --password <WiFi_password>
```

The card can now be unmounted and extracted. Boot the RaspberryPi and you should be able to SSH into it. If you have trouble finding the RaspberryPi IP, `nmap` can come in handy issuing a command like so:

```bash
nmap -sn 192.168.1.0/24
```

### Optional

Set up a static IP address.
