#!/usr/bin/env python
import click
import os
import subprocess
import sys
import json
#import pexpect
#import paramiko

###### Logging ########
import logging; 
formatter = logging.Formatter('[%(levelname)s]\t%(name)s\t%(asctime)s\t%(message)s', datefmt="%Y-%m-%d %H:%M:%S")
klookup_handler = logging.FileHandler('/var/log/klookup.log')
klookup_handler.setFormatter(formatter)
kll = logging.getLogger('klookup')
kll.setLevel(logging.DEBUG)
kll.addHandler(klookup_handler)
## haven't used logging in this file yet. Future-scope.
###### Logging ########


def pass_to_butler(COMMAND):
    """this is a tiny module to ssh (non-persistant) to kentik jmp box.
    And run remote script to fetch redash results on pre-configured queries
    """
    HOST="jmp01.iad1.kentik.com"
    ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        print (sys.stderr, "ERROR: %s" % error)
    else:
        r = result[0].decode('utf-8','ignore')      #need to decode for the stdout is read into bytes
        #print (*result)
        r2 = eval(r.replace("'", '"').replace('u"', '"'))   #using replace to cleanup unicode abd be ready for json module. Using eval to evaluate string to list
        for d in r2: print (json.dumps(d,indent=2))    
        print ("\n\t[INFO] found a list of output with {} items\n".format(len(r2)))


@click.command()
@click.option('--cid',help="lookup by Company ID",default=None,type=int )       #Plan to pass in method, but not use it.
@click.option('--email',help="lookup by Email",default=None,type=str)
@click.option('--cname',help="lookup by Company Name",default=None,type=str)
def klookup(cid,email,cname):
    """Lookup accounts in usual ways. (Today) need to add ssh-keys manually. 
    Make sure kkonsole_redash_butler.py exists in your $HOME on jmp01 and has execution rights.
    """
    #args={'cid':cid,'email':email,'cname':cname}
    args=dict()
    if cid: args['cid']=cid
    if email: args['email']=email
    if cname: args['cname']=cname

    limitonly1 = 1
    if cid and limitonly1 ==1:
        query_id = 89
        param_name = "p_Company_ID"
        param_key = cid
        limitonly1 +=1
    if email and limitonly1==1:
        query_id = 92
        param_name = "p_User_email"
        param_key = email
        limitonly1 +=1   
    if cname and limitonly1==1:
        query_id = 91
        param_name = "p_Company_Name"
        param_key = cname
        limitonly1 +=1     

    REDASH_USER_API_TOKEN = os.getenv('REDASH_USER_API_TOKEN','') if os.getenv('REDASH_USER_API_TOKEN','') else click.prompt('Enter REDASH_USER_API_TOKEN')
    COMMAND = "./kkonsole_redash_butler.py {} {} {} {}".format(param_name,param_key,query_id,REDASH_USER_API_TOKEN)
    #COMMAND="./kkonsole_redash_butler.py p_User_email bhalerao 92 key"
    pass_to_butler(COMMAND)

@click.command()
@click.option('--cid',help="lookup company STATS for CID",required=True,prompt=True,type=int)
def stats(cid):
    """query essential stats against a company
    Make sure kkonsole_redash_butler.py exists in your $HOME on jmp01 and has execution rights.
    """
    query_id = 142
    param_name = "p_cid"
    param_key = cid
    REDASH_USER_API_TOKEN = os.getenv('REDASH_USER_API_TOKEN','') if os.getenv('REDASH_USER_API_TOKEN','') else click.prompt('Enter REDASH_USER_API_TOKEN')
    COMMAND = "./kkonsole_redash_butler.py {} {} {} {}".format(param_name,param_key,query_id,REDASH_USER_API_TOKEN)
    #COMMAND="./kkonsole_redash_butler.py p_User_email bhalerao 92 key"
    pass_to_butler(COMMAND)   