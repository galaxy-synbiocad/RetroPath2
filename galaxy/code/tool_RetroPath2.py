#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import sys
import argparse
import logging
import tempfile
import tarfile
import glob
import shutil
import os

sys.path.insert(0, '/home/')
import rpTool

logging.basicConfig(
    #level=logging.WARNING,
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)


if __name__ == "__main__":
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow to run RetroPath2.0')
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
    parser.add_argument('-timeout', type=int, default=90)
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
    '''
    if not os.path.exists(params.scope_csv):
        logging.error('The scope file cannot be found: '+str(params.scope_csv))
        exit(1)
    '''
    if not os.path.exists(params.rulesfile):
        logging.error('The rules file cannot be found: '+str(params.rulesfile))
        exit(1)
    if not os.path.exists(params.sinkfile):
        logging.error('The sink file cannot be found: '+str(params.sinkfile))
        exit(1)
    ########## handle the call ###########
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        if params.rulesfile_format=='csv':
            logging.debug('Rules file: '+str(params.rulesfile))
            rulesfile = tmpInputFolder+'/rules.csv'
            shutil.copy(params.rulesfile, rulesfile)
            logging.debug('Rules file: '+str(rulesfile))
        elif params.rulesfile_format=='tar':
            with tarfile.open(params.rulesfile) as rf:
                rf.extractall(tmpInputFolder)
            out_file = glob.glob(tmpInputFolder+'/*.csv')
            if len(out_file)>1:
                logging.error('Cannot detect file: '+str(glob.glob(tmpInputFolder+'/*.csv')))
                exit(1)
            elif len(out_file)==0:
                logging.error('The rules tar input is empty')
                exit(1)
            rulesfile = out_file[0]
        else:
            logging.error('Cannot detect the rules_format: '+str(params.rulesfile_format))
            exit(1)
        sourcefile = tmpInputFolder+'/source.csv'
        shutil.copy(params.sourcefile, sourcefile)
        sinkfile = tmpInputFolder+'/sink.csv'
        shutil.copy(params.sinkfile, sinkfile)
        result = rpTool.run_rp2(sourcefile,
                                sinkfile,
                                rulesfile,
                                params.max_steps,
                                params.topx,
                                params.dmin,
                                params.dmax,
                                params.mwmax_source,
                                params.mwmax_cof,
                                params.timeout,
                                partial_retro)
        ###########################
        if result[1]==b'timeouterror' or result[1]==b'timeoutwarning':
            if not partial_retro:
                logging.error('Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool')
            else:
                if result[0]==b'':
                    logging.error('Timeout caused RetroPath2.0 to not find any solutions')
                    exit(1)
                else:
                    logging.warning('Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool')
                    logging.warning('Returning partial results')
                    with open(params.scope_csv, 'wb') as scope_csv:
                        scope_csv.write(result[0])
                    exit(0)
        elif result[1]==b'memwarning' or result[1]==b'memerror':
            if not partial_retro:
                logging.error('RetroPath2.0 has exceeded its memory limit')
                exit(0)
            else:
                if result[0]==b'':
                    logging.error('Memory limit reached by RetroPath2.0 caused it to not find any solutions')
                    exit[0]
                else:
                    logging.warning('RetroPath2.0 has exceeded its memory limit')
                    logging.warning('Returning partial results')
                    with open(params.scope_csv, 'wb') as scope_csv:
                        scope_csv.write(result[0])
                    exit(0)
        elif result[1]==b'sourceinsinkerror':
            logging.error('Source exists in the sink')
            exit(1)
        elif result[1]==b'sourceinsinknotfounderror':
            logging.error('Cannot find the sink-in-source file')
            exit(1)
        elif result[1]==b'ramerror' or result[1]==b'ramwarning':
            logging.error('Memory allocation error')
            exit(1)
        elif result[1]==b'oserror' or result[1]==b'oswarning':
            logging.error('RetroPath2.0 has generated an OS error')
            exit(1)
        elif result[1]==b'noresultwarning':
            if partial_retro:
                if result[0]==b'':
                    logging.error('No results warning caused it to return no results')
                    exit(1)
                else:
                    logging.warning('RetroPath2.0 did not complete successfully')
                    logging.warning('Returning partial results')
                    with open(params.scope_csv, 'wb') as scope_csv:
                        scope_csv.write(result[0])
            else:
                logging.error('RetroPath2.0 did not complete successfully')
                exit(1)
        elif result[1]==b'noresulterror':
            logging.error('Empty results')
            exit(1)
        elif result[1]==b'noerror':
            logging.info('Successfull execution')
            with open(params.scope_csv, 'wb') as scope_csv:
                scope_csv.write(result[0])
        else:
            logging.error('Could not recognise the status message returned: '+str(results[1]))
            exit(1)
