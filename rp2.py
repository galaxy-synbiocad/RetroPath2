"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
import subprocess
import logging
import resource
import os
import tempfile
import glob

#DOCKER
#KPATH = '/home/src/knime'
KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 15000*1024*1024 # 15 GB -- define what is the best
RULES_FILE = '/home/src/retrorules_rr02_rp2_flat_retro.csv'

"""
#test server
KPATH = '/home/mdulac/src/knime_3.6.2/knime'
RP_WORK_PATH = '/home/mdulac/src/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 15000*1024*1024 # 15 GB -- define what is the best
RULES_FILE = '/home/mdulac/src/retrorules_rr02_rp2_flat_retro.csv'
"""

#workstation
"""
KPATH = '/home/mdulac/knime_3.6.1/knime'
RP_WORK_PATH = '/home/mdulac/Downloads/RetroPath2.0/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 15000*1024*1024 # 15 GB -- define what is the best
RULES_FILE = '/home/mdulac/Downloads/retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_retro.csv'
"""

def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))

def run(sinkfile_bytes, sourcefile_bytes, maxSteps, rulesfile_bytes, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30):
    with tempfile.TemporaryDirectory() as tmpfolder:
        #write the input to file
        sourcefile = tmpfolder+'/source.csv'
        with open(sourcefile, 'wb') as sourcefi:
            sourcefi.write(sourcefile_bytes)
        sinkfile = tmpfolder+'/sink.csv'
        with open(sinkfile, 'wb') as sinkfi:
            sinkfi.write(sinkfile_bytes)
        if rulesfile_bytes==b'':
            rulesfile = RULES_FILE
        else:
            rulesfile = tmpfolder+'/rules.csv'
            with open(rulesfile, 'wb') as rulesfi:
                rulesfi.write(rulesfile_bytes)
        try:
            knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(maxSteps)+'",int -workflow.variable=input.sourcefile,"'+str(sourcefile)+'",String -workflow.variable=input.sinkfile,"'+str(sinkfile)+'",String -workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String -workflow.variable=output.topx,"'+str(topx)+'",int -workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpfolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
            commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)
            try:
                commandObj.wait(timeout=timeout*60.0)
            except subprocess.TimeoutExpired as e:
                logging.error('ERROR: Timeout from retropath2.0 ('+str(timeout)+' minutes)')
                commandObj.kill()
                return b'timeout', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*'))
            (result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                logging.error('RetroPath2.0 does not have sufficient memory to continue')
                return b'memerror', 'Command: '+str(knime_command)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*'))
            else:
                try:
                    csvScope = glob.glob(tmpfolder+'/*_scope.csv')
                    with open(csvScope[0], mode='rb') as scopeFile:
                        rp2_pathways = scopeFile.read()
                    return rp2_pathways, 'Command: '+str(knime_command)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*'))
                except IndexError as e:
                    logging.error('ERROR: RetroPath2.0 has not found any results')
                    return b'noresulterror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*'))
        except OSError as e:
            logging.error('ERROR: Running the RetroPath2.0 Knime program produced an OSError')
            logging.error(e)
            return b'oserror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*')) 
        except ValueError as e:
            logging.error('ERROR: Cannot set the RAM usage limit')
            logging.error(e)
            return b'ramerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*'))
    return rp2_pathways, ''
