#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import subprocess
import logging
import csv
import glob
import resource
import tempfile

KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/RetroPath2.0.knwf'

#MAX_VIRTUAL_MEMORY = 20000*1024*1024 # 20 GB -- define what is the best
MAX_VIRTUAL_MEMORY = 30000*1024*1024 # 30 GB -- define what is the best

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))


##
#
#
def run_rp2(source_path, sink_path, rules_path, max_steps, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, partial_retro=False, logger=None):
    if logger==None:
        logger = logging.getLogger(__name__)
    logger.info('Rules file: '+str(rules_path))
    logger.info('Timeout: '+str(timeout*60.0)+' seconds')
    is_timeout = False
    is_results_empty = True
    ### run the KNIME RETROPATH2.0 workflow
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        try:
            knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(max_steps)+'",int -workflow.variable=input.sourcefile,"'+str(source_path)+'",String -workflow.variable=input.sinkfile,"'+str(sink_path)+'",String -workflow.variable=input.rulesfile,"'+str(rules_path)+'",String -workflow.variable=input.topx,"'+str(topx)+'",int -workflow.variable=input.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=input.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
            logger.info('KNIME command: '+str(knime_command))
            commandObj = subprocess.Popen(knime_command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)
            result = b''
            error = b''
            try:
                #commandObj.wait(timeout=timeout) #subprocess timeout is in seconds while we input minutes
                result, error = commandObj.communicate(timeout=timeout*60.0) #subprocess timeout is in seconds while we input minutes
            except subprocess.TimeoutExpired as e:
                logging.warning('RetroPath2.0 has reached its execution timeout limit')
                commandObj.kill()
                is_timeout = True
            #(result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            logger.info('RetroPath2.0 results message: '+str(result))
            logger.info('RetroPath2.0 error message: '+str(error))
            logger.info('Output folder: '+str(glob.glob(tmpOutputFolder+'/*')))
            #check to see if the results.csv is empty
            try:
                count = 0
                with open(tmpOutputFolder+'/results.csv') as f:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                    for i in reader:
                        count += 1
                if count>1:
                    is_results_empty = False
            except (IndexError, FileNotFoundError) as e:
                logger.warning('No results.csv file')
            ### handle timeout
            if is_timeout:
                if not is_results_empty and partial_retro:
                    logger.warning('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
                    return b'', b'timeoutwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    logger.error('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
                    return b'', b'timeouterror', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ### if source is in sink. Note making sure that it contains more than the default first line
            try:
                count = 0
                with open(tmpOutputFolder+'/source-in-sink.csv') as f:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                    for i in reader:
                        count += 1
                if count>1:
                    logger.error('Source has been found in the sink')
                    return b'', b'sourceinsinkerror', str('Command: '+str(knime_command)+'\n Error: Source found in sink\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            except FileNotFoundError as e:
                logger.error('Cannot find source-in-sink.csv file')
                logger.error(e)
                return b'', b'sourceinsinknotfounderror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ### if java has an memory issue
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                if not is_results_empty and partial_retro:
                    logger.warning('RetroPath2.0 does not have sufficient memory to continue')
                    with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                        results_csv = op.read()
                    logger.warnning('Passing the results file instead')
                    return results_csv, b'memwarning', str('Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    logger.error('RetroPath2.0 does not have sufficient memory to continue')
                    return b'', b'memerror', str('Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ### csv scope copy to the .dat location
            try:
                csv_scope = glob.glob(tmpOutputFolder+'/*_scope.csv')
                with open(csv_scope[0], 'rb') as op:
                    scope_csv = op.read()
                return scope_csv, b'noerror', str('').encode('utf-8')
            except IndexError as e:
                if not is_results_empty and partial_retro:
                    logger.warning('No scope file generated')
                    with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                        results_csv = op.read()
                    logger.warnning('Passing the results file instead')
                    return results_csv, b'noresultwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    logger.error('RetroPath2.0 has not found any results')
                    return b'', b'noresulterror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
        except OSError as e:
            if not is_results_empty and partial_retro:
                logger.warning('Running the RetroPath2.0 Knime program produced an OSError')
                logger.warning(e) 
                with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                    results_csv = op.read()
                logger.warnning('Passing the results file instead')
                return results_csv, b'oswarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            else:
                logger.error('Running the RetroPath2.0 Knime program produced an OSError')
                logger.error(e)
                return b'', b'oserror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
        except ValueError as e:
            if not is_results_empty and partial_retro:
                logger.warning('Cannot set the RAM usage limit')
                logger.warning(e)
                with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                    results_csv = op.read()
                logger.warnning('Passing the results file instead')
                return results_csv, b'ramwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            else:
                logger.error('Cannot set the RAM usage limit')
                logger.error(e)
                return b'', b'ramerror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
