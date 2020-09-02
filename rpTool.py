#!/usr/bin/env python3
"""
Created on January 16 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""


import subprocess
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
def run_rp2(source_bytes, sink_bytes, rules_bytes, max_steps, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, partial_retro=False):
    is_timeout = False
    is_results_empty = True
    ### run the KNIME RETROPATH2.0 workflow
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        sink_path = tmpOutputFolder+'/tmp_sink.csv'
        with open(sink_path, 'wb') as outfi:
            outfi.write(sink_bytes)
        source_path = tmpOutputFolder+'/tmp_source.csv'
        with open(source_path, 'wb') as outfi:
            outfi.write(source_bytes)
        #rulesfile, fname_rules = readCopyFile(rulesfile, tmpOutputFolder)
        rules_path = tmpOutputFolder+'/tmp_rules.csv'
        with open(rules_path, 'wb') as outfi:
            outfi.write(rules_bytes)
        ### run the KNIME RETROPATH2.0 workflow
        try:
            knime_command = KPATH+' -nosplash -nosave -reset --launcher.suppressErrors -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile='+RP_WORK_PATH+' -workflow.variable=input.dmin,"'+str(dmin)+'",int -workflow.variable=input.dmax,"'+str(dmax)+'",int -workflow.variable=input.max-steps,"'+str(max_steps)+'",int -workflow.variable=input.sourcefile,"'+str(source_path)+'",String -workflow.variable=input.sinkfile,"'+str(sink_path)+'",String -workflow.variable=input.rulesfile,"'+str(rules_path)+'",String -workflow.variable=input.topx,"'+str(topx)+'",int -workflow.variable=input.mwmax-source,"'+str(mwmax_source)+'",int -workflow.variable=input.mwmax-cof,"'+str(mwmax_cof)+'",int -workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String -workflow.variable=output.solutionfile,"results.csv",String -workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String'
            commandObj = subprocess.Popen(knime_command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)
            result = ''
            error = ''
            try:
                #commandObj.wait(timeout=timeout) #subprocess timeout is in seconds while we input minutes
                result, error = commandObj.communicate(timeout=timeout*60.0) #subprocess timeout is in seconds while we input minutes
                result = result.decode('utf-8')
                error = error.decode('utf-8')
            except subprocess.TimeoutExpired as e:
                commandObj.kill()
                is_timeout = True
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
                #is_results_empty is already set to True
                pass
            ########################################################################
            ##################### HANDLE all the different cases ###################
            ########################################################################
            ### if source is in sink. Note making sure that it contains more than the default first line
            try:
                count = 0
                with open(tmpOutputFolder+'/source-in-sink.csv') as f:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                    for i in reader:
                        count += 1
                if count>1:
                    return b'', b'sourceinsinkerror', str('Command: '+str(knime_command)+'\n Error: Source found in sink\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            except FileNotFoundError as e:
                return b'', b'sourceinsinknotfounderror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ### handle timeout
            if is_timeout:
                if not is_results_empty and partial_retro:
                    with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                        results_csv = op.read()
                    return results_csv, b'timeoutwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    return b'', b'timeouterror', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ### if java has an memory issue
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                if not is_results_empty and partial_retro:
                    with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                        results_csv = op.read()
                    return results_csv, b'memwarning', str('Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    return b'', b'memerror', str('Command: '+str(knime_command)+'\n Error: Memory error \n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            ############## IF ALL IS GOOD ##############
            ### csv scope copy to the .dat location
            try:
                csv_scope = glob.glob(tmpOutputFolder+'/*_scope.csv')
                with open(csv_scope[0], 'rb') as op:
                    scope_csv = op.read()
                return scope_csv, b'noerror', str('').encode('utf-8')
            except IndexError as e:
                if not is_results_empty and partial_retro:
                    with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                        results_csv = op.read()
                    return results_csv, b'noresultwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
                else:
                    return b'', b'noresulterror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
        except OSError as e:
            if not is_results_empty and partial_retro:
                with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                    results_csv = op.read()
                return results_csv, b'oswarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            else:
                return b'', b'oserror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
        except ValueError as e:
            if not is_results_empty and partial_retro:
                with open(tmpOutputFolder+'/results.csv', 'rb') as op:
                    results_csv = op.read()
                return results_csv, b'ramwarning', str('Command: '+str(knime_command)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
            else:
                return b'', b'ramerror', str('Command: '+str(knime_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*'))).encode('utf-8')
