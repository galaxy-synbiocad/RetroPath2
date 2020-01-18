#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import requests
import argparse
import json
import os
import logging

##
#
#
def retropathUpload(sinkfile,
                    sourcefile,
                    maxSteps,
                    rulesfile,
                    topx,
                    dmin,
                    dmax,
                    mwmax_source,
                    mwmax_cof,
                    server_url,
                    scope_csv,
                    timeout):
    # Post request
    data = {'maxSteps': maxSteps,
            'topx': topx,
            'dmin': dmin,
            'dmax': dmax,
            'mwmax_source': mwmax_source,
            'mwmax_cof': mwmax_cof,
            'timeout': timeout}
    if rulesfile==None or rulesfile=='' or rulesfile==b'' or rulesfile=='None':
        rulesfile = os.getcwd()+'/empty_file.csv'
        with open(rulesfile, 'wb') as ef:
            ef.write(b'')
    files = {'sinkfile': open(sinkfile, 'rb'),
            'sourcefile': open(sourcefile, 'rb'),
            'rulesfile': open(rulesfile, 'rb'),
            'data': ('data.json', json.dumps(data))}
    try:
        r = requests.post(server_url+'/Query', files=files)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        logging.error(r.text)
        return False
    return_content = r.content
    with open(scope_csv, 'wb') as ot:
        ot.write(return_content)


##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-maxSteps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-topx', type=int)
    parser.add_argument('-dmin', type=int)
    parser.add_argument('-dmax', type=int)
    parser.add_argument('-mwmax_source', type=int)
    parser.add_argument('-mwmax_cof', type=int)
    parser.add_argument('-server_url', type=str)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-timeout', type=int)
    params = parser.parse_args()
    retropathUpload(params.sinkfile,
                    params.sourcefile,
                    params.maxSteps,
                    params.rulesfile,
                    params.topx,
                    params.dmin,
                    params.dmax,
                    params.mwmax_source,
                    params.mwmax_cof,
                    params.server_url,
                    params.scope_csv,
                    params.timeout)

