#!/usr/bin/env python
import click
import os


###### Logging ########
import logging; 
#logging.basicConfig(filename='/var/log/kperform.log',datefmt='%Y/%m/%d %H:%M:%S',level=logging.DEBUG)  #simple logging. can be called in other modules, but cant create 2 loggers. 

formatter = logging.Formatter('[%(levelname)s]\t%(name)s\t%(asctime)s\t%(message)s', datefmt="%Y-%m-%d %H:%M:%S")
# Logging - set file handlers.
kperform_handler = logging.FileHandler('/var/log/kperform.log')
kperform_handler.setFormatter(formatter)
kperform_create_handler = logging.FileHandler('/var/log/kperform_create.log')
kperform_create_handler.setFormatter(formatter)
# Logging - define loggers.
kpl = logging.getLogger('kperform')     # Make KPL logger record the transaction ID with USER and CID. in future. 
kpl.setLevel(logging.DEBUG)
kpl.addHandler(kperform_handler)
kpcl = logging.getLogger('create')
kpcl.setLevel(logging.DEBUG)
kpcl.addHandler(kperform_create_handler)

## same for another_handler.
# Logging - now log.
# Logging -- use the same loggers in another module? Absolutely. Just call them in that module/file like below:
##Multiple calls to getLogger() with the *same name* will always return a reference to the same Logger object.
# in another file>> kperform_logger = logging.getLogger('kperform')


@click.group()
def kperform():
    """Use kperform to add/delete/update various kentik dimensions"""
    #logging.warning('I GET NOTICED EVERYTIME')
    pass

@kperform.group()
@click.option('--prod/--no-prod', '-p/ ',default=False,help="PROD credentials.")
def create(prod):
    """create group routines for POST API methods against kentik v5 api"""
    if prod:
        if (os.getenv('PROD_API_TOKEN','')=="" or os.getenv('PROD_API_EMAIL','')==""): 
            click.echo("[WARN]: PROD credentials not set in .*.env file.")    # If PROD environment is not set.
            raise SystemExit(0)                        # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
        if (os.getenv('PROD_API_TOKEN','')!="" or os.getenv('PROD_API_EMAIL','')!=""): 
            click.confirm("Confirm using PROD credentials? ",default=False, abort=True, show_default=True)
            api_token=os.getenv('PROD_API_TOKEN','')
            api_email=os.getenv('PROD_API_EMAIL','')    #If PROD is set in env, then use those creds.
    else:                                               # If --prod is not set. 
        if (os.getenv('KENTIK_API_TOKEN','')!="" or os.getenv('KENTIK_API_EMAIL','')!=""):
            api_token=os.getenv("KENTIK_API_TOKEN","")
            api_email=os.getenv("KENTIK_API_EMAIL","")
        else:
            click.echo("[WARN]: Incorrect / No Login. Please try to login again. Try 'kkonsole login --help'")
            raise SystemExit(0)                        # Necessary to avoid system execution of below. This is better exit handling than import sys; sys.exit(0)
    #click.echo(api_token)
    #click.echo(api_email)

@kperform.group()
def delete():
    """delete group routines (not implemented yet)"""
    pass

@kperform.group()
def update():
    """update group routines (not implemented yet)"""
    pass


@click.command()
@click.option('--file', '-f',help="specify /path/to/src/file", type=click.Path(exists=True,file_okay=True, dir_okay=False, writable=False, readable=True),required=True,prompt=True)
@click.option('--v3/--v2c', '-3/ ',help="snmpv3 flag value. v3 currently not supported",default=False,show_default="--v2c" )       #Plan to pass in method, but not use it.
@click.option('--bgp/--no-bgp','-b/ ',help="flag to configure device_bgp",default=False,show_default="--no-bgp")
#@click.option('--minimize-snmp/--no-minimize-snmp','-m/ ',help='minimize snmp polling',show_default="--minimize-snmp",default=False)
@click.option('--plan-id',help="enter valid plan ID",type=int,show_default="from .csv, else this id for all devices")
def devices(file,v3,bgp,plan_id):
    """create devices"""
    # Initiating a new logger with user=createDevices, under the same logfile. 
    cdl = logging.getLogger('createDevices')
    cdl.setLevel(logging.DEBUG)
    cdl.addHandler(kperform_create_handler)

    from kperform.createDevices import createDevices
    #click.echo("[INFO]: I am here to add devices.")
    click.echo("File: {}\nSNMP v3: {}\nBGP: {}\nPlan-ID: {}".format(file,v3,bgp,plan_id))
    createDevices(file,v3,bgp,plan_id)


@click.option('--file', '-f',help="specify /path/to/src/file", type=click.Path(exists=True,file_okay=True, dir_okay=False, writable=False, readable=True),required=True,prompt=True)
@click.command()
def sites(file):
    """create sites"""
    click.echo("[NOTICE]: I am here with to add sites for {}".format(os.getenv('KENTIK_API_EMAIL','')))
    # Initiating a new logger with user=createSites, under the same logfile. 
    csl = logging.getLogger('createSites')
    csl.setLevel(logging.DEBUG)
    csl.addHandler(kperform_create_handler)
    #csl.info('Proceeding to adding sites')
    from kperform.createSites import createSites
    createSites(file)


@click.command()
def users():
    """create users (not implemented)"""
    click.echo("I am here with to add sites {}".format(os.getenv('KENTIK_API_TOKEN')))
    click.echo("I am not implemented yet. You can help.")

@click.command()
def devices_sites():
    """create devices and sites recursively (not implemented)"""
    click.echo("I am here with to add sites {}".format(os.getenv('KENTIK_API_TOKEN')))
    click.echo("I am not implemented yet. You can help.")

@click.option('-d', '--dir', help="enter direction",type=click.Choice(['src', 'dst', 'either']), default='either', required=True,show_default=True)
@click.option('--cd-id',help="enter custom dimension ID",type=int,required=True,prompt='Enter Custom Dimension ID')
@click.option('--file', '-f',help="specify /path/to/src/file", type=click.Path(exists=True,file_okay=True, dir_okay=False, writable=False, readable=True),required=True,prompt=True)
@click.command()
def populators(file,cd_id,dir):
    """create populators"""
    click.echo("\nI am here with to add populators for {}".format(os.getenv('KENTIK_API_EMAIL')))
    cpl = logging.getLogger('createPopulators')
    cpl.setLevel(logging.DEBUG)
    cpl.addHandler(kperform_create_handler)

    from kperform.createPopulators import createPopulators    
    createPopulators(file,cd_id,dir)

create.add_command(devices)
create.add_command(sites)
create.add_command(users)
create.add_command(devices_sites)
create.add_command(populators)
"""
kperform = click.CommandCollection(sources=[add,delete])
"""
if __name__=="__main__": kperform()