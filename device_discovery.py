#!/usr/bin/python
### device_discovery.py ###
# Zabbix UserParameter Script

# discover block devices for Zabbix Low Level Discovery
###

import os, sys, glob, json
import logging
import argparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def find_blkdevs():
    """find block devices
    
    Returns:
        [list]: block devices list
    """
    return glob.glob('/sys/block/*')

def is_real_blkdev(name):
    """checking that name is real block device or not
    
    Args:
        name (str): device file name
    """
    path = "/sys/block/{0}/device".format(name)
    if os.path.exists(path) and os.path.islink(path):
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action="store_true", help="enable debug mode")
    args = parser.parse_args()
    opt_dbg = args.debug
    if opt_dbg:
        logger.removeHandler(ch)
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    result = {"data":[]}

    devs = find_blkdevs()
    logger.debug("discovered block devices: {0}".format(devs))
    for dev in devs:
        dev_name = os.path.basename(dev)
        dev_size = 0
        if not os.path.islink(dev):
            sys.stderr.write("Invalaid block device {0}\n".format(dev))
            continue
        if not is_real_blkdev(dev_name):
            continue

        dev_size_file = '{0}/size'.format(dev)
        if not os.path.exists(dev_size_file):
            sys.stderr.write("Not found {0}\n".format(dev_size_file))
            continue

        with open(dev_size_file) as f:
            dev_size = f.readline()
        if dev_size == 0:
            sys.stderr.write("Ignoring block device {0}, so its size equals to 0\n"
                .format(dev)
            )
            continue

        blkdev = {}
        blkdev["{#BLOCKDEVICE}"] = dev_name
        result["data"].append(blkdev)
        logger.debug("now result set: {0}".format(result))
    print(json.dumps(result, sort_keys=True, indent=4))
