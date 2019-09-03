#!/usr/bin/env python3

from __future__ import print_function
import subprocess
import argparse
import os
import sys
import csv
import glob
import shutil

# local paths
#KPATH = '/home/mdulac/knime_3.6.1/knime'
#RP_WORK_PATH = '/home/mdulac/Downloads/RetroPath2.0_docker_test/RetroPath2.0/RetroPath2.0.knwf'
#docker paths
KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'

#Debug function
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#def main(dmin, dmax, maxSteps, sourcefile, sinkfile, rulesfile, topx, mwmax_source, mwmax_cof, outDir, timeout):
def main(dmin, dmax, maxSteps, sourcefile, sinkfile, topx, mwmax_source, mwmax_cof, outDir, timeout):
    try:
        #construct the knime command
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
                #'-workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String', 
                '-workflow.variable=input.rulesfile,"/home/src/rules_rall_rp2.csv",String', 
                '-workflow.variable=output.topx,"'+str(topx)+'",int', 
                '-workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int', 
                '-workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int', 
                '-workflow.variable=output.dir,"'+str(outDir)+'/",String', 
                '-workflow.variable=output.solutionfile,"results.csv",String', 
                '-workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String']
        #we make the knime call and supress the output since its has warning and errors and Galaxy doesn't like that

        #FNULL = open(os.devnull, 'w')
        #exit_code = subprocess.call(knime_command, stdout=FNULL, stderr=subprocess.STDOUT)    

        exit_code = subprocess.call(knime_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=timeout)    
        #exit_code = subprocess.call(knime_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        #exit_code = subprocess.call(knime_command)
        #with open(outDir+'/stdout.txt','wb') as out, open(outDir+'/stderr.txt','wb') as err:
        #    exit_code = subprocess.call(knime_command, stdout=out, stderr=err)    
	#FNULL = open(os.devnull, 'w')
        #exit_code = subprocess.call(knime_command, stdout=sys.stderr, stderr=FNULL)
    except OSError as e:
        eprint('Error: Running the RetroPath2.0 Knime program produced an OSError')
        eprint(e)
        return 2
    except subprocess.TimeoutExpired as e:
        eprint('Error: TimeOut')
        eprint(e)
        return 2
    #in the docker it returns 4 but everything is well generated
    #if exit_code==4:
    #    return 0
    return exit_code


#function that takes the .dat input of a file, opens to be read by python and then writes it to a file to be csv
def readCopyFile(inputFile, outDir):
    outputFile = outDir+'/'+inputFile.split('/')[-1].replace('.dat', '')+'.csv'
    #outputFile = inputFile.split('/')[-1].replace('.dat', '')+'.csv' 
    with open(outputFile, 'w') as outF:
        outCSV = csv.writer(outF, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        with open(inputFile, 'r') as inF:
            inCSV = csv.reader(inF, delimiter=',', quotechar='"')
            for row in inCSV:
                outCSV.writerow(row)
    return outputFile, inputFile.split('/')[-1].replace('.dat', '')+'.csv'


if __name__ == "__main__":
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow')
    parser.add_argument('-source', type=str)
    parser.add_argument('-sink', type=str)
    #parser.add_argument('-rules', type=str)
    parser.add_argument('-dmin', type=int)
    parser.add_argument('-dmax', type=int)
    parser.add_argument('-maxSteps', type=int)
    #parser.add_argument('-results', type=str)
    #parser.add_argument('-sourceinsink', type=str)
    parser.add_argument('-scopeCSV', type=str)
    parser.add_argument('-topx', type=int)
    parser.add_argument('-mwmax_source', type=int)
    parser.add_argument('-mwmax_cof', type=int)
    parser.add_argument('-timeout', type=int)
    #parser.add_argument('-outDir', type=str)
    params = parser.parse_args()
    #### Create symlink with the input files that are .dat to the KNIME accepted .csv format
    # Does not work with DOCKER
    # Trying to read and copy the input file to the docker since we cannot add a symlink to it
    outDir = '/home/src/data'
    #test to see if there are more than one line (as it stands we only support one source at a time)

    cp_source, fname_source = readCopyFile(params.source, outDir) 
    cp_sink, fname_sink = readCopyFile(params.sink, outDir)
    #cp_rules, fname_rules = readCopyFile(params.rules, outDir)
    #exit_code = main(params.dmin, params.dmax, params.maxSteps, cp_source, cp_sink, cp_rules, params.topx, params.mwmax_source, params.mwmax_cof, outDir, float(params.timeout)*60.0) # input is in minutes and we convert to seconds
    exit_code = main(params.dmin, params.dmax, params.maxSteps, cp_source, cp_sink, params.topx, params.mwmax_source, params.mwmax_cof, outDir, float(params.timeout)*60.0) # input is in minutes and we convert to seconds
    ###### parse the source-in-sink and return an error if its full
    #shutil.copy2(outDir+'/source-in-sink.csv', params.sourceinsink)
    count = 0
    try:
        with open(outDir+'/source-in-sink.csv') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for i in reader:
                count += 1
        if count>1:
            eprint('ERROR: Source has been found in the sink')
            exit(1)
    except FileNotFoundError:
        eprint('ERROR: Cannot find source-in-sink.csv file')
        exit(1)
    #TODO: have another error if there are no results in the scope file
    csvScope = glob.glob(outDir+'/*_scope.csv')
    try:
        shutil.copy2(csvScope[0], params.scopeCSV)
    except IndexError:
        eprint('ERROR: RetroPath2.0 has not found any results')
        exit(1)
    #shutil.copy2(outDir+'/results.csv', params.results)
    #shutil.copy2(outDir+'/source-in-sink.csv', params.sourceinsink)
    exit(exit_code)
