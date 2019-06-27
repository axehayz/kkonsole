#!/usr/bin/env python
import os
import csv
import json
import logging
import random
import requests

# logging.basicConfig(filename='/var/log/kperform_create_devices.log',datefmt='%Y/%m/%d %H:%M:%S',level=logging.DEBUG)  #Not necessary, as this is always called by kperform.py
# :this same log file or logname, will append to log

kpcl = logging.getLogger('createDevices')
kpl = logging.getLogger('create')

def main(KENTIK_API_TOKEN,KENTIK_API_EMAIL):
    # Implement quick exit function for standalone invocation. if token=empty, go to login.
    print ("Trying to run standalone. Why not try 'kperform create devices --help'")
    print ("Token: {}\nEmail: {}".format(KENTIK_API_TOKEN,KENTIK_API_EMAIL))
    ##### FUTURE WORK: Implement user prompts to enable standalone execution and call to createDevices(args)

def createDevices(file,v3,bgp,plan_id):
    kpcl.info("Inside create_devices.py")
    fugazy = str(random.randint(200,1000)*5)        #logger only takes strings. 
    kpl.info ('[Fugazy:{}] Initiating Create Sites'.format(fugazy))
    kpcl.debug ("[Fugazy:{}] File: {}\tSNMP v3: {}\tBGP: {}\tPlan-ID: {}".format(fugazy,file,v3,bgp,plan_id))
    with open(file,newline='',encoding="utf-8-sig") as f:
        kpcl.debug("[Fugazy:%s] Expecting CSV file (utf-8-sig encoded) (Typically save excel file as .csv)",format(fugazy))
        reader = csv.DictReader(f,dialect='excel')
        #kpcl.info("[Fugazy:%s] %s devices found",fugazy,str(len(list(reader))))     # CAUTION: !!! do not read the 'reader' else the obj pointer will be lost and the below for loop wont execute.
        #print (type(next(reader)))
        #print (type(reader))                    # csv.DictReader object, with each row being each device in OrderedDict
        devices = list()
        i=0
        for row in reader:                       # Every row is an orderedDict.
            d = dict()
            #print (type(str(row)))
            i+=1
            kpcl.debug("[Fugazy:%s_%s] Compiling Device_%s with %s",fugazy,str(i),str(i),str(row.items()))
            #print ((row.items()))
            for item in row.items():            # Every tuple in a row
                if item[0]=='device_name': d[item[0]]=item[1]
                if item[0]=='device_description': d[item[0]]=item[1]
                if item[0]=='sending_ips': d[item[0]]=item[1].split(",")       #CAUTION: CHANGE CSV IPS TO LIST
                if item[0]=='device_sample_rate': d[item[0]]=int(item[1])
                if item[0]=='plan_id': d[item[0]]=int(item[1])
                if item[0]=='device_snmp_ip': d[item[0]]=item[1]
                if item[0]=='device_snmp_community': d[item[0]]=item[1]
                
                #d['site_id']=3915      # Implement for adding sites automatically.
                if v3:
                    device_snmp_v3_conf = dict()
                    if item[0]=='v3_UserName': device_snmp_v3_conf[item[0]]=item[1]
                    if item[0]=='v3_AuthenticationProtocol': device_snmp_v3_conf[item[0]]=item[1]
                    if item[0]=='AuthenticationPassphrase': device_snmp_v3_conf[item[0]]=item[1]
                    if item[0]=='PrivacyProtocol': device_snmp_v3_conf[item[0]]=item[1]
                    if item[0]=='PrivacyPassphrase': device_snmp_v3_conf[item[0]]=item[1]
                    d['device_snmp_v3_conf']=device_snmp_v3_conf
                if bgp:
                    if item[0]=='': d[item[0]]='device'
                    if item[0]=='device_bgp_neighbor_ip': d[item[0]]=item[1]
                    if item[0]=='device_bgp_neighbor_ip6': d[item[0]]=item[1]
                    if item[0]=='device_bgp_neighbor_asn': d[item[0]]=item[1]
                    if item[0]=='device_bgp_password': d[item[0]]=item[1]
                #print (type(item))
            d['minimize_snmp']=False        # Hardcoded defaults -- should always be after 'for'
            d['device_bgp_type']="none"     # Hardcoded defaults -- should always be after 'for'
            d['device_type']='router'       # Hardcoded defaults -- should always be after 'for'
            if plan_id: d['plan_id'] = int(plan_id) # want to prefer CLI value. So using after for loop. 
            #print (d)
            devices.append(d)       # DO NOT TAKE THIS AWAY.
            #print (len(devices))
            #print (type(row))
        #print (reader.fieldnames)                
        #print (type(reader.fieldnames))         # List of all the fields. Use this to map the fields. 
        """for row in reader:
            #print (len(row))
            print (((json.dumps(row,indent=4))))"""
        """for row in reader:
            logging.debug(row)
            print (row)"""
    """for field in ((csv.DictReader(open(file,newline='',encoding="utf-8-sig"),dialect='excel')).fieldnames):
        print (field)"""
    print("Number of devices found: ",format(str(len(devices))))
    kpcl.debug("[Fugazy:%s] List of %s Device(s) compiled and ready to go",fugazy,str(len(devices)))
    post_devices(devices,fugazy)


##########################

def post_devices(devices,fugazy):
    url="https://api.kentik.com/api/v5/device"
    headers = {
    "Content-Type": "application/json",
    "X-CH-Auth-API-Token": os.environ.get('KENTIK_API_TOKEN',''),
    "X-CH-Auth-Email": os.environ.get('KENTIK_API_EMAIL','')}
    for device in devices:
        d = dict()
        d['device']=device
        print (json.dumps(d,indent=4))
        #print (json.dumps(device,indent=4))

        try:
            if os.environ.get('KENTIK_API_EMAIL','')=="" or os.environ.get('KENTIK_API_TOKEN','')=="":
                print("[WARN]: Not logged in. Try 'kkonsole login --help'")
                raise SystemExit(0)             # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
            r = requests.post(url,headers=headers, data=json.dumps(d), stream=True)    #stream=True is [optionally] used for accessing raw._connection further below to get remote/local IPs.
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:                # catch from r.raise_for_status call above.
            if err.response.status_code == 401: print('[ERROR]: Invalid Credentials. Please login again.'); print((err.response.text));kpcl.critical('[Fugazy:%s] Invalid Credentials. Please login again.',fugazy)
            elif err.response.status_code == 403: print('[ERROR]: IP Unauthorized.'); print(err.response.text); kpcl.critical('[Fugazy:%s] IP Unauthorized.',fugazy)     #; print(err.response.raw._connection.sock.getpeername())
            else: print(err); kpcl.debug('[Fugazy:%s] Error Text: %s',fugazy,str(err))
        except requests.exceptions.ConnectionError as err:          # Catch DNS failures, refused connections. 
            print(err)
        except requests.exceptions.RequestException as err:         # Bail
            print (err)
        
        print ('[NOTICE]: Check /var/log/kperform_create.log for more details')

        kpcl.info('[Fugazy:%s] Status Code %s',fugazy,str(r.status_code))
        kpcl.info('[Fugazy:%s] %s',fugazy,str(r.text))


if __name__=="__main__": main(os.getenv('KENTIK_API_TOKEN',''),os.getenv('KENTIK_API_EMAIL',''))