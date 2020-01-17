#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import subprocess
import logging
import shutil
import csv
import glob
import resource
import tempfile

KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 30000*1024*1024 # 30 GB -- define what is the best
RULES_PATH = '/home/src/rules_rall_rp2_retro.csv'

###
#
# function that takes the .dat input of a file, opens to be read by python and then writes it to a file to be csv
#
def readCopyFile(inputFile, tmpOutputFolder):
    outputFile = tmpOutputFolder+'/'+inputFile.split('/')[-1].replace('.dat', '').replace('.csv', '')+'.csv'
    with open(outputFile, 'w') as outF:
        outCSV = csv.writer(outF, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        with open(inputFile, 'r') as inF:
            inCSV = csv.reader(inF, delimiter=',', quotechar='"')
            for row in inCSV:
                outCSV.writerow(row)
    return outputFile, inputFile.split('/')[-1].replace('.dat', '').replace('.csv', '')+'.csv'

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))


##
#
#
def run_rp2(sinkfile, sourcefile, maxSteps, rulesfile, scopeCSV, tmpOutputFolder, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30):
    ### run the KNIME RETROPATH2.0 workflow
    try:
        knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(maxSteps)+'",int -workflow.variable=input.sourcefile,"'+str(sourcefile)+'",String -workflow.variable=input.sinkfile,"'+str(sinkfile)+'",String -workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String -workflow.variable=output.topx,"'+str(topx)+'",int -workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
        commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)
        try:
            commandObj.wait(timeout=timeout*60.0)
        except subprocess.TimeoutExpired as e:
            logging.error('Timeout from retropath2.0 ('+str(timeout)+' minutes)')
            commandObj.kill()
            return b'timeout', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        (result, error) = commandObj.communicate()
        result = result.decode('utf-8')
        error = error.decode('utf-8')
        #logging.warning(result)
        #logging.warning(error)
        ### if java has an memory issue
        if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
            logging.error('RetroPath2.0 does not have sufficient memory to continue')
            return b'memerror', 'Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        ### if source is in sink
        try:
            count = 0
            with open(tmpOutputFolder+'/source-in-sink.csv') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"')
                for i in reader:
                    count += 1
            if count>1:
                logging.error('Source has been found in the sink')
                return b'sourceinsinkerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
        except FileNotFoundError as e:
            logging.error('Cannot find source-in-sink.csv file')
            logging.error(e)
            return b'sourceinsinknotfounderror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')) 
        ### csv scope copy to the .dat location
        try:
            csvScope = glob.glob(tmpOutputFolder+'/*_scope.csv')
            shutil.copy2(csvScope[0], scopeCSV)
            return b'noerror', ''
        except IndexError as e:
            logging.error('RetroPath2.0 has not found any results')
            logging.error(e)
            return b'noresulterror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
    except OSError as e:
        logging.error('Running the RetroPath2.0 Knime program produced an OSError')
        logging.error(e)
        return b'oserror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))
    except ValueError as e:
        logging.error('Cannot set the RAM usage limit')
        logging.error(e)
        return b'ramerror', 'Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))

##
#
#
def main(sinkfile, sourcefile, maxSteps, rulesfile, scopeCSV, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30):
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        ### copy the .dat files to .csv and the rules file if need be
        sourcefile, fname_source = readCopyFile(sourcefile, tmpOutputFolder)
        sinkfile, fname_sink = readCopyFile(sinkfile, tmpOutputFolder)
        if (rulesfile==None) or (rulesfile=='None') or (rulesfile==''):
            rulesfile = RULES_PATH
        else:
            rulesfile, fname_rules = readCopyFile(rulesfile, tmpOutputFolder)
        ### run RetroPath2.0
        status, errorstring = run_rp2(sinkfile, sourcefile, maxSteps, rulesfile, scopeCSV, tmpOutputFolder, topx, dmin, dmax, mwmax_source, mwmax_cof, timeout)
        #if the errors are not detected by Galaxy catch them here
        #logging.error(errorstring)
