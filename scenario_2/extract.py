#!/usr/local/bin/python3

import argparse
import sys
import os
import logging
import json

def run(command):
    os.system(command)

def extract_uuids(container, channel):
    run("docker exec {container} bash -c 'source setup/activate.sh; ./e-mission-py.bash bin/debug/get_users_for_channel.py {channel} -o /tmp/{channel}.users'".format(container=container, channel=channel))
    run("docker cp {container}:/tmp/{channel}.users".format(container=container, channel=channel))
    uuid_list = open("/tmp/{channel}.users".format(channel=channel)).readlines()
    uuid_query = {"user_id": {"$in": [{"$uuid": u.strip()} for u in uuid_list]}}
    queryFile = "/tmp/{channel}.queryfile".format(channel = channel)
    uuid_query_file = json.dump(open(queryFile, "w"))

def dump_and_copy_channel_and_collection(container, channel, collection, out_file_name):
    mongodump_cmd = ""
    if collection is not None:
        mongodump_cmd = mongodump_cmd + "--collection"+collection
    if channel is not None:
        queryFile = "/tmp/{channel}.queryfile".format(channel = channel)
        run("docker cp /tmp/{channel}.queryfile {container}:/tmp".format(channel=channel, container))
        mongodump_cmd = mongodump_cmd + "--queryFile "+queryFile
    print("About to run command "+mongodump_cmd)
    run("docker exec {container} cd /tmp && bash -c '{cmd}'".format(cmd=mongodump_cmd))
    run("docker exec {container} cd /tmp && bash -c 'tar -czvf /tmp/{file_name}.tar.gz /tmp/mongodump".format(
        container=container, file_name = file_name)
    run("docker cp {container}:/tmp/{file_name}.tar.gz /tmp/".format(container=container, file_name=file_name))

def encrypt(gpg_key, file_name):
    run("gpg --encrypt -r {recipient} {file_name}".format(recipient=gpg_key, file_name=file_name))

def publish(file_name, out_dir):
    run("cp {file_name}.gpg {out_dir}".format(file_name=file_name, out_dir=out_dir))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="extract.py")

    parser.add_argument("analysis_container", help="the container running the analysis pipeline")
    parser.add_argument("mongod_container", help="the container running mongod")
    parser.add_argument("--collection", help="the collection whose data should be extracted")
    parser.add_argument("--channel", help="the channel whose data should be extracted")
    parser.add_argument("gpg_key", help="the gpg key to encrypt the file with")
    parser.add_argument("outdir", help="directory on the web server to publish to")

    args = parser.parse_args()

    if args.channel:
        out_file_name = "/tmp/mongodump_{channel}.tar.gz".format(channel=args.channel)
        extract_uuids(args.analysis_container, args.channel)
        dump_and_copy_channel_and_collection(args.mongod_container, args.channel, args.collection, out_file_name)
    else:
        out_file_name = "/tmp/emission.tar.gz"
        dump_and_copy_channel(args.mongod_container, None, args.collection, out_file_name)
    encrypt(args.gpg_key, file_name)
    publish(file_name, args.outdir)
