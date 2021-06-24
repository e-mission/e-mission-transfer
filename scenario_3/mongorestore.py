#!/usr/local/bin/python3

import argparse
import sys
import os
import logging
# using datetime instead of arrow to reduce dependencies on external libraries
# we want to make it easy to run this from the default system python
# instead of setting up a conda environment
import datetime as dt

def run(command):
    print(f"Running {command}")
    os.system(command)

def extract_and_copy(container):
    dumpname = container + "_upload"
    run(f"docker cp /tmp/{dumpname}.tar.gz {container}:/tmp/{dumpname}.tar.gz")
    run(f"docker exec {container} bash -c 'cd /tmp; tar xzvf {dumpname}.tar.gz; mongorestore")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="mongorestore.py")

    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("--program", help="the program to upload data into")
    parser.add_argument("--container", help="specify the container instead of inferring from the program")
    
    args = parser.parse_args()

    if not args.container:
        args.container = f"{args.program}-stack_{args.program}-db_1"
        print(f"auto-detecting container as {args.container}")
    extract_and_copy(args.container)
