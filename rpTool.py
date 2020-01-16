#!/usr/bin/env python3

import subprocess
import logging

import sys
sys.path.insert(0, '/home/src/')

KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'

'''
#Debug function
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
'''

##
#
#
def run_rp2(dmin, dmax, maxSteps, sourcefile, sinkfile, rulesfile, topx, mwmax_source, mwmax_cof, outDir, timeout):
    try:
        knime_command = [KPATH,
                '-nosplash',
                '-nosave',
                '-reset',
                '--launcher.suppressErrors',
                '-application',
                'org.knime.product.KNIME_BATCH_APPLICATION',
                '-workflowFile='+RP_WORK_PATH,
                '-workflow.variable=input.dmin,"'+str(dmin)+'",int',
                '-workflow.variable=input.dmax,"'+str(dmax)+'",int',
                '-workflow.variable=input.max-steps,"'+str(maxSteps)+'",int',
                '-workflow.variable=input.sourcefile,"'+str(sourcefile)+'",String',
                '-workflow.variable=input.sinkfile,"'+str(sinkfile)+'",String',
                '-workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String',
                '-workflow.variable=output.topx,"'+str(topx)+'",int',
                '-workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int',
                '-workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int',
                '-workflow.variable=output.dir,"'+str(outDir)+'/",String',
                '-workflow.variable=output.solutionfile,"results.csv",String',
                '-workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String']
        exit_code = subprocess.call(knime_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=timeout)
    except OSError as e:
        #eprint('Error: Running the RetroPath2.0 Knime program produced an OSError')
        logging.error('Running the RetroPath2.0 Knime program produced an OSError')
        #eprint(e)
        return False
    except subprocess.TimeoutExpired as e:
        #eprint('Error: TimeOut')
        logging.error('TimeOut')
        #eprint(e)
        return False
    return True


KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'
MAX_VIRTUAL_MEMORY = 30000*1024*1024 # 30 GB -- define what is the best
RULES_FILE = '/home/src/retrorules_rr02_rp2_flat_retro.csv'


###
#
# function that takes the .dat input of a file, opens to be read by python and then writes it to a file to be csv
#
def readCopyFile(inputFile, tmpOutputFolder):
    outputFile = tmpOutputFolder+'/'+inputFile.split('/')[-1].replace('.dat', '')+'.csv'
    with open(outputFile, 'w') as outF:
        outCSV = csv.writer(outF, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        with open(inputFile, 'r') as inF:
            inCSV = csv.reader(inF, delimiter=',', quotechar='"')
            for row in inCSV:
                outCSV.writerow(row)
    return outputFile, inputFile.split('/')[-1].replace('.dat', '')+'.csv'

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))

##
#
#
def run_rp2(sinkfile, sourcefile, maxSteps, rulesfile, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30):
    with tempfile.TemporaryDirectory() as tmpfolder:
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
