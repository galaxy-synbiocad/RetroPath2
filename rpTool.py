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
#KPATH = '/home/mdulac/knime_3.6.1/knime'
RP_WORK_PATH = '/home/RetroPath2.0.knwf'
#RP_WORK_PATH = '/home/mdulac/workspace/Galaxy-SynBioCAD/RetroPath2/RetroPath2_image/RetroPath2.0.knwf'
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
def run_rp2(source_path, sink_path, rules_path, max_steps, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, logger=None):
    if logger==None:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
    logging.info('Rules file: '+str(rules_path))
    ### run the KNIME RETROPATH2.0 workflow
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        try:
            knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(max_steps)+'",int -workflow.variable=input.sourcefile,"'+str(source_path)+'",String -workflow.variable=input.sinkfile,"'+str(sink_path)+'",String -workflow.variable=input.rulesfile,"'+str(rules_path)+'",String -workflow.variable=input.topx,"'+str(topx)+'",int -workflow.variable=input.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=input.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
            logger.info('KNIME command: '+str(knime_command))
            commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)
            try:
                commandObj.wait(timeout=timeout*60.0) #subprocess timeout is in seconds while we input minutes
            except subprocess.TimeoutExpired as e:
                logger.error('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
                commandObj.kill()
                return b'', b'timeout', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            (result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            logger.info('RetroPath2.0 results message: '+str(result))
            logger.info('RetroPath2.0 error message: '+str(error))
            logger.info('Output folder: '+str(glob.glob(tmpOutputFolder+'/*')))
            ### if java has an memory issue
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                logger.error('RetroPath2.0 does not have sufficient memory to continue')
                return b'', b'memerror', 'Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            ### if source is in sink
            try:
                count = 0
                with open(tmpOutputFolder+'/source-in-sink.csv') as f:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                    for i in reader:
                        count += 1
                if count>1:
                    logger.error('Source has been found in the sink')
                    return b'', b'sourceinsinkerror', 'Command: '+str(knime_command)+'\n Error: Source found in sink\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            except FileNotFoundError as e:
                logger.warning('Cannot find source-in-sink.csv file')
                logger.warning(e)
                pass
                #return b'', b'sourceinsinknotfounderror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
            ### csv scope copy to the .dat location
            try:
                csv_scope = glob.glob(tmpOutputFolder+'/*_scope.csv')
                with open(csv_scope[0], 'rb') as op:
                    scope_csv = op.read()
                return scope_csv, b'noerror', ''
            except IndexError as e:
                logger.warning('RetroPath2.0 did not generate a scope file but did generate a results file, passing that as the results')
                try:
                    csv_scope = glob.glob(tmpOutputFolder+'/results.csv')
                    count = 0
                    with open(tmpOutputFolder+'/results.csv') as f:
                        reader = csv.reader(f, delimiter=',', quotechar='"')
                        for i in reader:
                            count += 1
                    if not count>1:
                        logger.error('results.csv is empty')
                        raise IndexError
                    with open(csv_scope[0], 'rb') as op:
                        scope_csv = op.read()
                    return scope_csv, b'noerror', ''
                except IndexError as e:
                    logger.error('RetroPath2.0 has not found any results')
                    return b'', b'noresulterror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        except OSError as e:
            logger.error('Running the RetroPath2.0 Knime program produced an OSError')
            logger.error(e)
            return b'', b'oserror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        except ValueError as e:
            logger.error('Cannot set the RAM usage limit')
            logger.error(e)
            return b'', b'ramerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
