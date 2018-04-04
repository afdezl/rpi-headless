#!/usr/bin/env python

import argparse
import logging
import os
import sys
import stat


log = logging.getLogger(__name__)
log_hdlr = logging.StreamHandler(sys.stdout)
log_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
log.addHandler(log_hdlr)
log.setLevel(logging.INFO)

OS_USER = os.getlogin()
MEDIA_DIR = os.path.join('/media', OS_USER)
BOOT_DIR = os.path.join(MEDIA_DIR, 'boot')
FS_DIR = os.path.join(MEDIA_DIR, 'rootfs')
SSH_BOOT_FILE = os.path.join(BOOT_DIR, 'ssh')
WPA_SUPPLICANT_DIR = os.path.join(FS_DIR, 'etc', 'wpa_supplicant')
WPA_SUPPLICANT_FILE = os.path.join(WPA_SUPPLICANT_DIR, 'wpa_supplicant.conf')
NETWORK_INTERFACES_DIR = os.path.join(FS_DIR, 'etc', 'network')
NETWORK_INTERFACES_FILE = os.path.join(NETWORK_INTERFACES_DIR, 'interfaces')
PI_USER_UID = 1000
PI_USER_GID = 1000

WPA_SUPPLICANT_CONF = u"""
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""

INTERFACES_CONF = u"""
auto lo
iface lo inet loopback

auto eth0
allow-hotplug eth0
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
"""


def touch_ssh_file():
    """Touches an empty file called ssh in the boot directory to enable SSH on boot."""
    if not os.path.isfile(SSH_BOOT_FILE):
        open(SSH_BOOT_FILE, 'a').close()
        log.info('Touched {}'.format(SSH_BOOT_FILE))
    else:
        log.info('File already present "{}", skipping'.format(SSH_BOOT_FILE))


def write_network_interfaces():
    try:
        log.debug('Backing up existing interfaces config to {}'.format(NETWORK_INTERFACES_FILE + '.old'))
        os.rename(NETWORK_INTERFACES_FILE, NETWORK_INTERFACES_FILE + '.old')
        open(NETWORK_INTERFACES_FILE, 'a').close()
        with open(NETWORK_INTERFACES_FILE, 'w') as f:
            f.write(INTERFACES_CONF)
        log.info('Edited "{}"'.format(NETWORK_INTERFACES_FILE))
    except IOError as e:
        log.exception(e)
        exit(1)


def write_wpa_supplicant(ssid=None, password=None):
    """Writes a new wpa_suplicant.conf file with the required  network SSID and password."""
    try:
        if not os.path.isfile(WPA_SUPPLICANT_FILE):
            open(WPA_SUPPLICANT_FILE, 'a').close()
        with open(WPA_SUPPLICANT_FILE, 'w') as f:
            f.write(WPA_SUPPLICANT_CONF.format(ssid=ssid, password=password))
        log.info('Edited "{}"'.format(WPA_SUPPLICANT_FILE))
    except IOError as e:
        log.exception(e)
        exit(1)


def copy_auth_key(src=None, dest=None):
    """Copies the content of src and appends it to dest.
    If the destination path does not exist, it is created with +rwx for directories
    and +rw for files.
    """
    src = os.path.expanduser(src)
    dest = (os.path.join(FS_DIR, dest)
            if not os.path.isabs(dest)
            else (dest
                    if dest.startswith(FS_DIR)
                    else FS_DIR + dest))
    dest_dir = os.path.dirname(dest)
    try:
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
            log.debug('Created {}'.format(dest_dir))
            os.chown(dest_dir, PI_USER_UID, PI_USER_GID)
            log.debug('Setting ownership on {}'.format(dest_dir))
            os.chmod(dest_dir, stat.S_IRWXU)
            log.debug('Setting permissions on {}'.format(dest_dir))
        with open(src, 'r') as f:
            src_f = f.read()
        with open(dest, 'a') as f:
            f.write(src_f)
        os.chown(dest, PI_USER_UID, PI_USER_GID)
        log.debug('Setting ownership on {}'.format(dest))
        os.chmod(dest, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        log.debug('Setting permissions on {}'.format(dest))
        log.info('Copied contents of "{}" to "{}"'.format(src, dest))
    except IOError as e:
        log.exception('You must be sudo when running this script!')
        exit(1)


def main(args):
    if args.verbose:
        log.setLevel(logging.DEBUG)
    log.info('Starting new headless configuration')
    if args.os == 'raspbian':
        touch_ssh_file()
    if args.os == 'armbian':
        write_network_interfaces()
    write_wpa_supplicant(ssid=args.ssid, password=args.password)
    if args.auth_key:
        copy_auth_key(src=args.auth_key[0], dest=args.auth_key[1])
    log.info('Completed headless configuration')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssid', required= True, help="Network SSID")
    parser.add_argument('--password', required=True, help='Network password')
    parser.add_argument('--auth-key', required=False, nargs=2, help='Authorized hosts SSH key, paths must be absolute')
    parser.add_argument('--os', required=False, nargs=1, default='raspbian', choices=['raspbian', 'armbian'])
    parser.add_argument('-v', '--verbose', action='store_true', required=False, help='Enable verbose mode')
    args = parser.parse_args()

    main(args)
