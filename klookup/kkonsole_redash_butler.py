#!/usr/bin/env python

"""
    File name: kkonsole_redash_butler.py
    Author: Akshay Dhawale
    Email: akshay@kentik.com
    Date created: 12/22/2018
    Date last modified: 12/30/2018
    Python Version: 2.7+

This script is modified. Original from Redash API Documentation
https://redash.io/help/user-guide/integrations-and-api/api Github/arikfr

    Usage: This is NOT installed locally. Confirm it exists on jmp01 at $HOME/kkonsole_redash_butler.py
"""
import sys
import requests
import json
import time
#import os # Imported for os.environ push and getenv approach. No longer used.

this_param_name=None
this_param_key=None
this_param=None
this_query_id=None
redash_user_api_key=None
# Set to null to avoid accidental / malicious direct local run of the script

def poll_job(s, redash_url, job):
    # TODO: add timeout
    while job['status'] not in (3,4):
        response = s.get('{}/api/jobs/{}'.format(redash_url, job['id']))
        job = response.json()['job']
        time.sleep(1)

    if job['status'] == 3:
        return job['query_result_id']

    return None

def get_fresh_query_result(redash_url, query_id, api_key, params):
    s = requests.Session()
    s.headers.update({'Authorization': 'Key {}'.format(api_key)})

    response = s.post('{}/api/queries/{}/refresh'.format(redash_url, query_id), params=params)

    if response.status_code != 200:
        raise Exception('Initial post failed. \nPossible the Redash URL and/or API is incorrect or formatting error on sys.argv')

    result_id = poll_job(s, redash_url, response.json()['job'])

    if result_id:
        #print ("Poll job sucessfull. Returned some results. Proceeding to call 'get' response")
        response = s.get('{}/api/queries/{}/results/{}.json'.format(redash_url, query_id, result_id))
        if response.status_code != 200:
            raise Exception('Failed getting response.')
    else:
        raise Exception('Query execution failed.')

    return response.json()['query_result']['data']['rows']

"""def parameter_reconstruct():
    this_param_name=sys.argv[1]
    this_param_key=sys.argv[2]
    this_param={'p_COMPANY_ID': 38021}
    print 'the param is {}'.format(this_param)
    this_query_id=sys.argv[3]
    print "the query id is {}".format(this_query_id)
    redash_user_api_key=sys.argv[4]
    print redash_user_api_key"""

def main(query_id, api_key, params):
    response = get_fresh_query_result('https://redash.iad1.kentik.com/', query_id, api_key, params)

    # Do NOT remove the below print. This is used to collect from stdout on local machine.
    print response

    # OK to not return
    #return response
    # Need to use a *user API key* here (and not a query API key).

""" Butler project. Hosted this template / framework file on @kentik.com
    to avoid using ssh libraries in python. Dont handle yubikey well and complex to setup.
"""

""" Take the command line received args from parent calling local script under main for a remote `this` script.
"""
    # parameter_reconstruct()
""" parameter_reconstruct() doesn't work. this_* variables are not exported back.
    Quit writing `return`. Work in main().
"""

""" query_id=os.getenv['query_id']
    print (query_id)
    Can we pass invoking environment's envvar to called script. Tried and failed.
"""

""" This was an attempt to pass args using JSON.
    Convert data to strings and then use json.loads() on remote end.
    Reason to do this is because sys.argv[:] can only be strings.
    Failed to work. Ceased pursuing.

    params = {'p_COMPANY_ID': 38021}
    print query_id
    query_id = 27
    data = json.loads(sys.argv[1:])
    print json.loads(data)
    q1=sys.argv[2]
    print q1
    api_key = 'yea--seriously.'
    pprint(get_fresh_query_result('https://redash.iad1.kentik.com/', query_id, api_key, params))
    print (get_fresh_query_result('https://redash.iad1.kentik.com/', this_query_id, redash_user_api_key, this_params))
"""

if __name__ == '__main__':
    """
    After several attempts at keeping this script on local machine
    And failing to run a local script with variables on remote server (it should NOT be easy)
    This script modifies init call to take values from system variables.
    """
    print ("\nI am here...")
    #this_param={'p_COMPANY_ID': 38021}

    this_param_name=sys.argv[1]
    this_param_key=sys.argv[2]
    this_query_id=sys.argv[3]
    redash_user_api_key=sys.argv[4]

    this_param={this_param_name:this_param_key}

    #print ('Looking up Redash against {} on Query ID {}'.format(this_param,this_query_id))
    main(this_query_id, redash_user_api_key, this_param)