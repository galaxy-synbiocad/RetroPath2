#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import sys
sys.path.insert(0, '/home/')
import argparse
import logging

import rpTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#def run_rp2(sinkfile_bytes, sourcefile_bytes, max_steps, rules_bytes=None, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, logger=None):


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
    parser.add_argument('-is_forward', type=bool)
    parser.add_argument('-timeout', type=int)
    params = parser.parse_args()
    with open(params.sinkfile, 'rb') as sinkfile_bytes:
        with open(params.sourcefile, 'rb') as sourcefile_bytes:
            if (params.rulesfile==None) or (params.rulesfile==b'None') or (params.rulesfile=='None') or (params.rulesfile=='') or (params.rulesfile==b''):
                result = rpTool.run_rp2(sinkfile_bytes.read(),
                                        sourcefile_bytes.read(),
                                        params.maxSteps,
                                        b'None',
                                        params.topx,
                                        params.dmin,
                                        params.dmax,
                                        params.mwmax_source,
                                        params.mwmax_cof,
                                        params.timeout,
                                        params.is_forward,
                                        logger)
            else:
                with open(params.rulesfile, 'rb') as rulesfile_bytes:
                    result = rpTool.run_rp2(sinkfile_bytes.read(),
                                            sourcefile_bytes.read(),
                                            params.maxSteps,
                                            rulesfile_bytes.read(),
                                            params.topx,
                                            params.dmin,
                                            params.dmax,
                                            params.mwmax_source,
                                            params.mwmax_cof,
                                            params.timeout,
                                            params.is_forward,
                                            logger)
            with open(params.scope_csv, 'wb') as s_c:
                s_c.write(result[0])
