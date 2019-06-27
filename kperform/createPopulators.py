#!/usr/bin/env python
#createPopulators.py
import os
import csv
import json
import logging
import random
import requests
import click
from time import sleep

kpcl = logging.getLogger('createPopulators')
kpl = logging.getLogger('create')


def main(KENTIK_API_TOKEN,KENTIK_API_EMAIL):
    # Implement quick exit function for standalone invocation. if token=empty, go to login.
    print ("Trying to run standalone. Why not try 'kperform create populators --help'")
    print ("Token: {}\nEmail: {}".format(KENTIK_API_TOKEN,KENTIK_API_EMAIL))
    ##### FUTURE WORK: Implement user prompts to enable standalone execution and call to createPopulators(args)

def validate(cd_id):
    """validate if provided custom dimension id exists. 
    Also checks if credentials are correct.
    Add duplicate IP validation as future-scope.
    """
    try:
        if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
            print("[WARN]: Not logged in. Try 'kkonsole login --help'")
            raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
        headers = {
        "Content-Type": "application/json",
        "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
        "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
        r = requests.get('https://api.kentik.com/api/v5/customdimensions',headers=headers, stream=True)    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
        if err.response.status_code == 401: print('[ERROR]: Invalid Credentials. Please login again.'); print((err.response.text));kpcl.critical('[Fugazy:%s] Invalid Credentials. Please login again.',fugazy)
        elif err.response.status_code == 403: print('[ERROR]: IP Unauthorized.'); print(err.response.text); kpcl.critical('[Fugazy:%s] IP Unauthorized.',fugazy)     #; print(err.response.raw._connection.sock.getpeername())
        else: print(err); kpcl.debug('[Fugazy:%s] Error Text: %s',fugazy,str(err))
    except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
        print(err)
    except requests.exceptions.RequestException as err:         # Bail
        print (err)
    #kpcl.info('[Fugazy:%s] Site Built %s',fugazy,str(r.status_code))
    #print ('[NOTICE]: Check /var/log/kperform_create.log for more details')
    #kpcl.info('[Fugazy:%s] %s',fugazy,str(r.text))
    #print ((json.dumps(r.json(), indent=4)))
    current_cdlist = r.json()['customDimensions']
    kpcl.info ('{} Custom Dimension(s) Found'.format(str(len(current_cdlist))))
    for cd in current_cdlist:
        if cd_id == cd['id']:
            print ("[INFO]: Valid entry.\tID:{}\t\tDisplay Name:{}".format(cd['id'],cd['display_name']))
            return cd
        else:
            print ("[WARN]: Provided Custom Dimension ID [{}] could not be found".format(cd_id))
            print ("[WARN]: Please check if the ID is correct and/or it exists. \n[WARN]: Else create manually (future scope to auto-add on confirm)")
            return None


def createPopulators(file,cd_id,direction):
    """prepare populators for POST"""
    kpcl.info("Inside createPopulators.py")
    fugazy = str(random.randint(100,900)*5)        #logger only takes strings. 
    kpl.info ('[Fugazy:{}] Initiating Create Populators'.format(fugazy))
    kpcl.debug ("[Fugazy:{}] File: {} Custom Dimension ID: {}".format(fugazy,file,cd_id))
    kpcl.info ('[Fugazy:{}] Validating if provided Custom Dimension ID [{}] exists'.format(fugazy, cd_id))
    print ('Validating if provided Custom Dimension ID [{}] exists (lookup fugazyID:{} in logs)'.format(cd_id,fugazy))
    cd=validate(cd_id)
    if cd is None:
        kpcl.warning ('[Fugazy:{}] Provided Custom Dimension ID [{}] could NOT be found"'.format(fugazy,cd_id))
        kpcl.warning ('[Fugazy:{}] Please confirm the ID or add manually. System Abort."'.format(fugazy,cd_id))
        raise SystemExit(0)
    
    kpcl.info('[Fugazy:{}] Valid entry found for ID:{} as {} with {} current populator(s)'.format(fugazy,cd['id'],cd['display_name'],len(cd['populators'])))
    print('[INFO]: Valid entry found for ID:{} as {} with {} current populator(s) (use Fugazy:{} for log grep)'.format(cd['id'],cd['display_name'],len(cd['populators']),fugazy))

    kpcl.debug ('[Fugazy:{}] Current State of the Dimension: {}'.format(fugazy,json.dumps(cd)))

    with open(file,newline='',encoding="utf-8-sig") as f:
        reader = csv.DictReader(f,dialect='excel')
        populators_2add = list()

        for row in reader:
            #print (row)
            #print ('')
            d=dict()
            for item in row.items():
                if item[0]=='value' or 'name':d[item[0]]=item[1]
                if item[0]=='addr' or 'ip' or 'ipaddr' or 'ip address':d[item[0]]=item[1]
                if item[0]=='device_name':d[item[0]]=item[1]
                if item[0]=='device_type':d[item[0]]=item[1]
                if item[0]=='site':d[item[0]]=item[1]
                if item[0]=='interface_name':d[item[0]]=item[1]
                if item[0]=='port':d[item[0]]=item[1]
                if item[0]=='tcp_flags':d[item[0]]=item[1]
                if item[0]=='protocol':d[item[0]]=item[1]
                if item[0]=='asn':d[item[0]]=item[1]
                if item[0]=='lasthop_as_name':d[item[0]]=item[1]
                if item[0]=='nexthop_asn':d[item[0]]=item[1]
                if item[0]=='nexthop_as_name':d[item[0]]=item[1]
                if item[0]=='nexthop':d[item[0]]=item[1]
                if item[0]=='bgp_aspath':d[item[0]]=item[1]
                if item[0]=='bgp_community':d[item[0]]=item[1]
                if item[0]=='mac':d[item[0]]=item[1]
                if item[0]=='country':d[item[0]]=item[1]
                if item[0]=='vlans':d[item[0]]=item[1]
            d['direction']=direction
            populators_2add.append(d)
        kpcl.info('[Fugazy:{}] {} Populators detected. Proceeding to POST'.format(fugazy,len(populators_2add)))
        print('[Fugazy:{}] {} Populators detected. Proceeding to POST'.format(fugazy,len(populators_2add)))
        post_populators(fugazy,populators_2add,cd_id)

##########################

def post_populators(fugazy,populators_2add,cd_id):
    """post prepared populators via kentik API with rate-limiter"""
    url="https://api.kentik.com/api/v5/customdimension/{}/populator/".format(cd_id)
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
    "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
    i=0;failed=[]

    with click.progressbar(populators_2add,label='Adding Populators') as bar:
        for populator in bar:
            p = dict()
            p['populator']=populator
            #print (json.dumps(p,indent=4))
            i+=1
            kpcl.info('[Fugazy:{}_{}] Adding Populator as {}'.format(fugazy,i,p))

            try:
                if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
                    print("[WARN]: Not logged in. Try 'kkonsole login --help'")
                    raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
                r = requests.post(url,headers=headers, data=json.dumps(p))    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
                r.raise_for_status()
                if r.status_code!=201:
                    r['status_code']=r.status_code
                    failed.append(r)
                    kpcl.warning('[Fugazy:{}_{}]\tStatus Code {}\t\tNot able to POST {}'.format(fugazy,i,r.status_code,r.text))

                kpcl.info('[Fugazy:{}_{}] Status Code {}'.format(fugazy,i,str(r.status_code)))
                kpcl.info('[Fugazy:%s_%s] %s',fugazy,i,str(r.text))

            except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
                if err.response.status_code == 401: print('[ERROR]: Invalid Credentials. Please login again.'); print((err.response.text));kpcl.critical('[Fugazy:%s] Invalid Credentials. Please login again.',fugazy)
                elif err.response.status_code == 403: print('[ERROR]: IP Unauthorized.'); print(err.response.text); kpcl.critical('[Fugazy:%s] IP Unauthorized.',fugazy)     #; print(err.response.raw._connection.sock.getpeername())
                else: print(err); kpcl.debug('[Fugazy:%s] Error Text: %s',fugazy,str(err))
            except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
                print(err)
            except requests.exceptions.RequestException as err:         # Bail
                print (err)
            finally:
                sleep(float(os.environ.get('API_RATE_LIMITER',0.1)))

    if failed:
        print ('[Fugazy:{}] Encountered {}/{} failures. Check Logs.'.format(fugazy,len(failed),len(populators_2add)))
        kpcl.warning ('[Fugazy:{}] Encountered {}/{} failures. Check Logs.'.format(fugazy,len(failed),len(populators_2add)))
        #kpcl.warning ('[Fugazy:{}] Encountered {} failures. Check Logs.'.format(fugazy,(failed)))
        print (failed)
    else:
        kpcl.info('[Fugazy:{}] All Added. Check Logs.'.format(fugazy))
        print('[Fugazy:{}] All Added. Check Logs.'.format(fugazy))


if __name__=="__main__": main(os.getenv('KENTIK_API_TOKEN',''),os.getenv('KENTIK_API_EMAIL',''))