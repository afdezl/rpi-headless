#!/usr/bin/env python

import argparse
import logging
import os
import sys


log = logging.getLogger(__name__)
log_hdlr = logging.StreamHandler(sys.stdout)
log_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
log.addHandler(log_hdlr)
log.setLevel(logging.DEBUG)

OS_USER = os.getlogin()
MEDIA_DIR = os.path.join('/media', OS_USER)
BOOT_DIR = os.path.join(MEDIA_DIR, 'boot')
FS_DIR = os.path.join(MEDIA_DIR, 'rootfs')
SSH_BOOT_FILE = os.path.join(BOOT_DIR, 'ssh')
WPA_SUPPLICANT_DIR = os.path.join(FS_DIR, 'etc', 'wpa_supplicant')
WPA_SUPPLICANT_FILE = os.path.join(WPA_SUPPLICANT_DIR, 'wpa_supplicant.conf')

WPA_SUPPLICANT_CONF = u"""
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""


def touch_ssh_file():
    """Touches an empty file called ssh in the boot directory to enable SSH on boot."""
    if not os.path.isfile(SSH_BOOT_FILE):
        open(SSH_BOOT_FILE, 'a').close()
        log.info('Touched {}'.format(SSH_BOOT_FILE))
    else:
        log.info('File already present "{}", skipping'.format(SSH_BOOT_FILE))


def write_wpa_supplicant(ssid=None, password=None):
    """Writes a new wpa_suplicant.conf file with the required  network SSID and password."""
    try:
        with open(WPA_SUPPLICANT_FILE, 'w') as f:
            f.write(WPA_SUPPLICANT_CONF.format(ssid=ssid, password=password))
        log.info('Edited "{}"'.format(WPA_SUPPLICANT_FILE))
    except IOError as e:
        log.exception(e)
        exit(1)


def copy_auth_key(src=None, dest=None):
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
            os.chown(dest_dir, os.getuid(), -1)
            log.debug('Setting permissions on {}'.format(dest_dir))
        with open(src, 'r') as f:
            src_f = f.read()
        with open(dest, 'a') as f:
            dest_f = f.write(src_f)
        os.chown(dest, os.getuid(), -1)
        log.info('Copied contents of "{}" to "{}"'.format(src, dest))
    except IOError as e:
        log.exception('You must be sudo when running this script!')


def main(args):
    log.info('Starting new headless configuration')
    touch_ssh_file()
    write_wpa_supplicant(ssid=args.ssid, password=args.password)
    if args.auth_key:
        copy_auth_key(src=args.auth_key[0], dest=args.auth_key[1])
    log.info('Completed headless configuration')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssid', required= True, help="Network SSID")
    parser.add_argument('--password', required=True, help='Network password')
    parser.add_argument('--auth-key', required=False, nargs=2, help='Authorized hosts SSH key, paths must be absolute')
    args = parser.parse_args()
    
    main(args)
