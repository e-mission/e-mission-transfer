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

def extract_and_copy(filename, basename, container):
    dumpname = container + "_upload"
    run(f"docker cp {filename} {container}:/tmp/{basename}")
    run(f"docker exec {container} bash -c 'cd /tmp; tar xzvf {basename}; mongorestore'")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="mongorestore.py")

    parser.add_argument("mongodump_file", help="the mongodump to upload")
    parser.add_argument("--container", help="specify the container instead of inferring from the program")

    args = parser.parse_args()
    # if mongodump_file is /home/ubuntu/program_upload.tar.gz, basename is program_upload.tar.gz
    args.basename = os.path.basename(args.mongodump_file)
    args.program = args.basename.split("_")[0]

    if not args.container:
        args.container = f"{args.program}-stack_{args.program}-db_1"
        print(f"auto-detecting container as {args.container}")
    extract_and_copy(args.mongodump_file, args.basename, args.container)
