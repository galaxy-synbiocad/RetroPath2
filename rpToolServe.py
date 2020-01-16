#!/usr/bin/env python3

import argparse
import os
import glob
import shutil
import tempfile
import logging
import csv

import rpTool

KPATH = '/usr/local/knime/knime'
RP_WORK_PATH = '/home/src/RetroPath2.0.knwf'


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
def main(source, sink, rules, dmin, dmax, maxSteps, scopeCSV, topx, mwmax_source, mwmax_cof, timeout):
    tmpOutputFolder = tempfile.mkdtemp()
    rules_path = '/home/src/rules_rall_rp2_retro.csv'
    if not os.path.isfile(rules_path):
        eprint('ERROR: Cannot find rules file')
    #test to see if there are more than one line (as it stands we only support one source at a time)
    cp_source, fname_source = readCopyFile(source, tmpOutputFolder)
    cp_sink, fname_sink = readCopyFile(sink, tmpOutputFolder)
    if (rules==rules_path) or (rules==None) or (rules=='None'):
        exit_code = rpTool.run_rp2(dmin, dmax, maxSteps, cp_source, cp_sink, rules_path, topx, mwmax_source, mwmax_cof, tmpOutputFolder, float(timeout)*60.0) # input is in minutes and we convert to seconds
    else:
        cp_rules, fname_rules = readCopyFile(rules, tmpOutputFolder)
        exit_code = rpTool.run_rp2(dmin, dmax, maxSteps, cp_source, cp_sink, cp_rules, topx, mwmax_source, mwmax_cof, tmpOutputFolder, float(timeout)*60.0) # input is in minutes and we convert to seconds
    count = 0
    if not exit_code:
        logging.error('rpTool returned an error')
        Gashutil.rmtree(tmpOutputFolder)
        return False
    try:
        with open(tmpOutputFolder+'/source-in-sink.csv') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for i in reader:
                count += 1
        if count>1:
            logging.error('Source has been found in the sink')
            shutil.rmtree(tmpOutputFolder)
            return False
    except FileNotFoundError:
        logging.error('Cannot find source-in-sink.csv file')
        shutil.rmtree(tmpOutputFolder)
        return False
    #TODO: have another error if there are no results in the scope file
    csvScope = glob.glob(tmpOutputFolder+'/*_scope.csv')
    try:
        shutil.copy2(csvScope[0], scopeCSV)
    except IndexError:
        logging.error('RetroPath2.0 has not found any results')
        shutil.rmtree(tmpOutputFolder)
        return False
    shutil.rmtree(tmpOutputFolder)
    return exit_code
