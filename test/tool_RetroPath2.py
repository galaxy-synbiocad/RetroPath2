#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import sys
sys.path.insert(0, '/home/src/')
import argparse

import rpTool


if __name__ == "__main__":
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-maxSteps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-topx', type=int)
    parser.add_argument('-dmin', type=int)
    parser.add_argument('-dmax', type=int)
    parser.add_argument('-mwmax_source', type=int)
    parser.add_argument('-mwmax_cof', type=int)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-timeout', type=int)
    params = parser.parse_args()
    rpTool.main(params.sinkfile,
                params.sourcefile,
                params.maxSteps,
                params.rulesfile,
                params.scope_csv,
                params.topx,
                params.dmin,
                params.dmax,
                params.mwmax_source,
                params.mwmax_cof,
                params.timeout)
