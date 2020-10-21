#!/usr/local/bin/python3

import argparse
import sys
import os
import logging

def run(command):
    os.system(command)

def extract_and_copy(container):
    run("docker exec {container} bash -c 'source setup/activate.sh; ./e-mission-py.bash bin/debug/extract_timeline_for_day_range_and_user.py -a 2020-01-01 2022-01-01 /tmp/emission_ind'".format(container=container))
    run("docker exec {container} bash -c 'tar -czvf /tmp/emission.tar.gz /tmp/emission_ind*'".format(container=container))

def extract_and_copy_channel(container, channel):
    run("docker exec {container} bash -c 'source setup/activate.sh; ./e-mission-py.bash bin/debug/get_users_for_channel.py {channel} -o /tmp/{channel}.users'".format(container=container, channel=channel))
    run("docker exec {container} bash -c 'source setup/activate.sh; ./e-mission-py.bash bin/debug/extract_timeline_for_day_range_and_user.py -f /tmp/{channel}.users 2020-01-01 2022-01-01 /tmp/{channel}_ind'".format(container=container, channel=channel))
    run("docker exec {container} bash -c 'tar -czvf /tmp/{channel}.tar.gz /tmp/{channel}_ind*'".format(container=container, channel=channel))
    run("docker cp {container}:/tmp/{channel}.tar.gz /tmp/".format(container=container, channel=channel))

def encrypt(gpg_key, file_name):
    run("gpg --encrypt -r {recipient} {file_name}".format(recipient=gpg_key, file_name=file_name))

def publish(file_name, out_dir):
    run("cp {file_name}.gpg {out_dir}".format(file_name=file_name, out_dir=out_dir))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="extract.py")

    parser.add_argument("container", help="the container running the analysis pipeline")
    parser.add_argument("--channel", help="the channel whose data should be extracted")
    parser.add_argument("gpg_key", help="the gpg key to encrypt the file with")
    parser.add_argument("outdir", help="directory on the web server to publish to")

    args = parser.parse_args()

    if args.channel:
        extract_and_copy_channel(args.container, args.channel)
        file_name = "/tmp/{channel}.tar.gz".format(channel=args.channel)
    else:
        extract_and_copy(args.container)
        file_name = "/tmp/emission.tar.gz"
    encrypt(args.gpg_key, file_name)
    publish(file_name, args.outdir)
