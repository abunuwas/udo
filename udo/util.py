# Handy common utilities for udo modules

import boto3
import getpass
import json
import os
import socket
import sys
import urllib2

from pprint import pprint
from time import sleep

import config

# don't use for tests

def debug(msg):
    # to use:
    # export DEBUG='True'
    if os.environ.get('DEBUG') == 'True':
        pprint(msg)
    
def default_config():
    return config.Config()

def region():
    region = default_config().get('region')
    return region

# returns dict of arguments common to any boto connection we establish
def connection_args():
    debug("in util.py connection_args")
    _region = region()
    if not _region:
        # use the default region, I guess?
        print "Warning: default region is not configured"
        return "us-east-1"

    args = {
        'region_name': _region
    }
    return args

# AutoScaling connection
def as_conn():
    debug("in util.py as_conn")
    args = connection_args()
    return boto3.client('autoscaling', **args)

# EC2 connection
def ec2_conn():
    debug("in util.py ec2_conn")
    args = connection_args()
    return boto3.client('ec2', **args)

# CodeDeploy connection
def deploy_conn():
    debug("in util.py deploy_conn")
    args = connection_args()
    return boto3.client('codedeploy', **args)

# ask a yes/no question
# returns true/false
def confirm(msg):
    debug("in util.py confirm")
    yn = raw_input(msg + " (y/n) ")
    if yn.lower() == 'y':
        return True
    print "Aborted"
    return False

# keep trying proc until timeout or no exception is thrown
# use this when you're waiting for a change to take effect
# FIXME: actually respect timeout
# FIXME: this depends on boto . does not work with boto3 yet
# There's some polling stuff in boto3 that should help replace this
# There's probably something in botocore that will replace this
#
#def retry(proc, timeout):
#    debug("in util.py retry")
#    success = False
#    ret = None
#    while success == False:
#        try:
#            ret = proc()     
#            success = True
#        except boto.exception.BotoServerError as e:
#            if default_config().get('debug'):
#                # dump response
#                print "Error: {}, retrying...".format(e)
#            else:
#                print('.'),
#            sys.stdout.flush()
#            sleep(5)
#    print "\n"
#    return ret

def user_and_host():
    debug("in util.py user_and_host")
    username = getpass.getuser()
    hostname = socket.gethostname()
    return "{}@{}".format(username, hostname)

# also prints out msg
def message_integrations(msg):
    debug("in util.py message_integrations")
    message_slack("[{}]  {}".format(user_and_host(), msg))
    print msg

def message_slack(msg):
    debug("in util.py message_slack")
    slack_cfg = default_config().new_root('slack')
    if not slack_cfg:
        # not configured
        return

    slack_url      = slack_cfg.get('url')
    slack_username = slack_cfg.get('username')
    slack_channel  = slack_cfg.get('channel')

    payload = {
        'username': slack_username,
        'text': msg,
        'channel': slack_channel,
    }

    data = json.dumps(payload)
    headers = {'Content-Type': 'application/json'}
    request = urllib2.Request(slack_url, data, headers=headers)
    return urllib2.urlopen(request).read()
