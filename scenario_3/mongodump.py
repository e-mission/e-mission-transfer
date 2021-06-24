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

def extract_and_copy(program, container):
    dumpname = program + "_"+ dt.date.today().isoformat()
    run(f"docker exec {container} bash -c 'cd /tmp; mongodump'")
    run(f"docker exec {container} bash -c 'cd /tmp; tar czvf {dumpname}.tar.gz dump'")
    run(f"docker cp {container}:/tmp/{dumpname}.tar.gz /tmp/")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="mongodump.py")

    parser.add_argument("program", help="the program to download data for")
    parser.add_argument("--container", help="specify the container instead of inferring from the program")
    
    args = parser.parse_args()

    if not args.container:
        args.container = f"{args.program}-stack_{args.program}-db_1"
        print(f"auto-detecting container as {args.container}")
    extract_and_copy(args.program, args.container)
