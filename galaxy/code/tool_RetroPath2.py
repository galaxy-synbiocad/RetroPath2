#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import requests
import sys
import argparse
import json
import os
import logging
import tempfile
import tarfile
import glob

##
#
#
def retropathUpload(sinkfile,
                    sourcefile,
                    max_steps,
                    rulesfile,
                    rulesfile_format,
                    topx,
                    dmin,
                    dmax,
                    mwmax_source,
                    mwmax_cof,
                    server_url,
                    scope_csv,
                    timeout,
                    partial_retro):
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        if rulesfile_format=='tar':
            with tarfile.open(rulesfile) as rf:
                rf.extractall(tmpInputFolder)
            out_file = glob.glob(tmpInputFolder+'/*.csv')
            if len(out_file)>1:
                logging.error('Cannot detect file: '+str(glob.glob(tmpInputFolder+'/*.csv')))
                return False
            rulesfile = out_file[0]
        elif rulesfile_format=='csv':
            pass
        else:
            logging.error('Cannot detect the rules_format: '+str(rulesfile_format))
        # Post request
        data = {'max_steps': max_steps,
                'topx': topx,
                'dmin': dmin,
                'dmax': dmax,
                'mwmax_source': mwmax_source,
                'mwmax_cof': mwmax_cof,
                'timeout': timeout,
                'partial_retro': partial_retro}
        #logging.debug(data)
        files = {'sinkfile': open(sinkfile, 'rb'),
                'sourcefile': open(sourcefile, 'rb'),
                'rulesfile': open(rulesfile, 'rb'),
                'data': ('data.json', json.dumps(data))}
        try:
            r = requests.post(server_url+'/Query', files=files)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            #logging.error(err)
            logging.error(r.text)
            return False
        status = r.headers['status_message']
        status = status.replace('--', '\n')
        logging.info(status)
        #not sure why Galaxy does not detect the logging results, need to print the status message to handle WARNINGS
        print(status)
        return_content = r.content
        logging.info(status)
        with open(scope_csv, 'wb') as ot:
            ot.write(return_content)


##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-max_steps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-rulesfile_format', type=str)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-topx', type=int, default=100)
    parser.add_argument('-dmin', type=int, default=0)
    parser.add_argument('-dmax', type=int, default=100)
    parser.add_argument('-mwmax_source', type=int, default=1000)
    parser.add_argument('-mwmax_cof', type=int, default=1000)
    parser.add_argument('-server_url', type=str, default='http://0.0.0.0:8888/REST')
    parser.add_argument('-timeout', type=int, default=30)
    parser.add_argument('-partial_retro', type=str, default='False')
    params = parser.parse_args()
    if params.max_steps<=0:
        logging.error('Maximal number of steps cannot be less or equal to 0')
        exit(1)
    if params.topx<0:
        logging.error('Cannot have a topx value that is <0: '+str(params.topx))
        exit(1)
    if params.dmin<0:
        logging.error('Cannot have a dmin value that is <0: '+str(params.dmin))
        exit(1)
    if params.dmax<0:
        logging.error('Cannot have a dmax value that is <0: '+str(params.dmax))
        exit(1)
    if params.dmax>1000:
        logging.error('Cannot have a dmax valie that is >1000: '+str(params.dmax))
        exit(1)
    if params.dmax<params.dmin:
        logging.error('Cannot have dmin>dmax : dmin: '+str(params.dmin)+', dmax: '+str(params.dmax))
        exit(1)
    if params.partial_retro=='False' or params.partial_retro=='false' or params.partial_retro=='F':
        partial_retro = False
    elif params.partial_retro=='True' or params.partial_retro=='true' or params.partial_retro=='T':
        partial_retro = True
    else:
        logging.error('Cannot interpret partial_retro: '+str(params.partial_retro))
        exit(1)
    retropathUpload(params.sinkfile,
                    params.sourcefile,
                    params.max_steps,
                    params.rulesfile,
                    params.rulesfile_format,
                    params.topx,
                    params.dmin,
                    params.dmax,
                    params.mwmax_source,
                    params.mwmax_cof,
                    params.server_url,
                    params.scope_csv,
                    params.timeout,
                    partial_retro)
