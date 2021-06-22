#!/usr/local/bin/python3

import argparse
import sys
import os
import logging

def run(command):
    print(f"Running {command}")
    os.system(command)

def extract_and_copy(user_email, container):
    run(f"docker exec {container} bash -c 'cd e-mission-server; source setup/activate.sh; ./e-mission-py.bash bin/debug/extract_timeline_for_day_range_and_user.py -e {user_email} -- 2020-01-01 2025-01-01 /tmp/emission_ind'")
    run(f"docker exec {container} bash -c 'tar -czvf /tmp/{user_email}.tar.gz /tmp/emission_ind*'")
    run(f"docker cp {container}:/tmp/{user_email}.tar.gz /tmp/")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="extract.py")

    parser.add_argument("user_email", help="the user email or token")
    parser.add_argument("--container", help="specify the container instead of inferring from user email")
    
    args = parser.parse_args()

    if not args.container:
        program = args.user_email.split("_")[0]
        args.container = f"{program}-stack_{program}-analysis-server_1"
        print(f"auto-detecting container as {args.container}")
    extract_and_copy(args.user_email, args.container)
