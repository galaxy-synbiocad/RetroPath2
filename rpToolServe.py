#!/usr/bin/env python3
"""
Created on 16 January 21 2020

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""

import tempfile
import csv
import logging

import sys
sys.path.insert(0, '/home/src/')
import rpTool

RULES_PATH = '/home/src/rules_rall_rp2_retro.csv'

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
        status, errorstring = rpTool.run_rp2(sinkfile, sourcefile, maxSteps, rulesfile, scopeCSV, tmpOutputFolder, topx, dmin, dmax, mwmax_source, mwmax_cof, timeout)
        #if the errors are not detected by Galaxy catch them here
        #logging.error(errorstring)
