#!/usr/local/bin/python3

import argparse
import sys
import os
import logging
import json
import base64
import uuid

def run(command):
    os.system(command)

def to_binary(uuidbson):
    base64uuid = base64.b64encode(uuid.UUID(uuidbson["$uuid"]).bytes).decode("ASCII")
    return {"$binary": base64uuid, "$type": "03"}

def extract_uuids(container, channel):
    run("docker exec {container} bash -c 'source setup/activate.sh; ./e-mission-py.bash bin/debug/get_users_for_channel.py {channel} -o /tmp/{channel}.users'".format(container=container, channel=channel))
    run("docker cp {container}:/tmp/{channel}.users /tmp".format(container=container, channel=channel))
    uuid_list = json.load(open("/tmp/{channel}.users".format(channel=channel)))

    uuid_query = {"user_id": {"$in": [to_binary(u["uuid"]) for u in uuid_list]}}
    queryFile = "/tmp/{channel}.queryfile".format(channel = channel)
    uuid_query_file = json.dump(uuid_query, open(queryFile, "w"))

# Workaround until we get the confirmed_trips objects in the analysis database
def dump_manual_inputs(container, channel):
    mongodump_cmd = "mongodump --db Stage_database"
    mongodump_cmd = mongodump_cmd + " --collection Stage_timeseries"
    if channel is not None:
        uuidqueryFile = "/tmp/{channel}.queryfile".format(channel = channel)
        combo_query = json.load(open(queryFile))
        combo_query["metadata.key"] = {"$regex": "/manual"}
        print("combined query = "+combined_query)
        comboQueryFile = "/tmp/{channel}.comboqueryfile".format(channel = channel)
        json.dump(combo_query, open(comboQueryFile, "w"))
        run("docker cp /tmp/{channel}.comboqueryfile {container}:/tmp".format(channel=channel, container=container))
        mongodump_cmd = mongodump_cmd + " --queryFile "+comboQueryFile
    print("About to run command "+mongodump_cmd)
    run("docker exec {container} bash -c 'cd /tmp && {cmd}'".format(container=container, cmd=mongodump_cmd))

def dump_and_copy_channel_and_collection(container, channel, collection, out_file_name):
    mongodump_cmd = "mongodump --db Stage_database"
    if collection is not None:
        mongodump_cmd = mongodump_cmd + " --collection "+collection
    if channel is not None:
        queryFile = "/tmp/{channel}.queryfile".format(channel = channel)
        run("docker cp /tmp/{channel}.queryfile {container}:/tmp".format(channel=channel, container=container))
        mongodump_cmd = mongodump_cmd + " --queryFile "+queryFile
    print("About to run command "+mongodump_cmd)
    run("docker exec {container} bash -c 'cd /tmp && {cmd}'".format(container=container, cmd=mongodump_cmd))
    run("docker exec {container} bash -c 'tar -czvf {file_name} /tmp/dump'".format(
        container=container, file_name = out_file_name))
    run("docker cp {container}:{file_name} /tmp/".format(container=container, file_name=out_file_name))

def encrypt(gpg_key, file_name):
    run("gpg --encrypt --trust-model always -r {recipient} {file_name}".format(recipient=gpg_key, file_name=file_name))

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
        dump_manual_inputs(args.mongod_container):
        dump_and_copy_channel_and_collection(args.mongod_container, args.channel, args.collection, out_file_name)
    else:
        out_file_name = "/tmp/emission.tar.gz"
        dump_and_copy_channel(args.mongod_container, None, args.collection, out_file_name)
    encrypt(args.gpg_key, out_file_name)
    publish(out_file_name, args.outdir)
