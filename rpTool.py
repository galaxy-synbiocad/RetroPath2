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
