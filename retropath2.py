#!/usr/bin/env python3
"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
import glob
import os
import sys
import random
import string
import subprocess
import logging
import shutil
import resource
import json
import libsbml
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import tarfile
import csv


#######################################################
############## REST ###################################
#######################################################


app = Flask(__name__)
api = Api(app)
# local paths TODO: change to Docker
KPATH = '/home/mdulac/knime_3.6.1/knime'
RP_WORK_PATH = '/home/mdulac/Downloads/RetroPath2.0_docker_test/RetroPath2.0/RetroPath2.0.knwf'
#MAX_VIRTUAL_MEMORY = 10 * 1024 * 1024 # 10 MB
MAX_VIRTUAL_MEMORY = 15000 * 1024 * 1024 # 15 GB -- define what is the best


## Stamp of rpCofactors
#
#
def stamp(data, status=1):
    appinfo = {'app': 'RetroPath2.0', 'version': '8.0', 
               'author': 'Melchior du Lac',
               'organization': 'BRS',
               'time': datetime.now().isoformat(), 
               'status': status}
    out = appinfo.copy()
    out['data'] = data
    return out


## REST App.
#
#
class RestApp(Resource):
    def post(self):
        return jsonify(stamp(None))
    def get(self):
        return jsonify(stamp(None))


#rulesfile = "/home/mdulac/Documents/mnx_data/mnx_20190524/nostereo_hs/rule/aroaam_final_rp2/rules_rall_retro.csv"




## REST Query
#
# REST interface that generates the Design.
# Avoid returning numpy or pandas object in
# order to keep the client lighter.
class RestQuery(Resource):
    def post(self):
        sourcefile = request.files['sourcefile']
        sinkfile = request.files['sinkfile']
        rulesfile = request.files['rulesfile']
        params = json.load(request.files['data'])
        #pass the cache parameters to the rpCofactors object
        scopeCSV = io.BytesIO()
        scopeCSV = runRetroPath2(sinkfile, sourcefile, params['maxSteps'], rulesfile, params['topx'], params['dmin'], params['dmax'], params['mwmax_source'], params['mwmax_cof'])
        ###### IMPORTANT ######
        scopeCSV.seek(0)
        #######################
        return send_file(scopeCSV, as_attachment=True, attachment_filename='scope.csv', mimetype='text/csv')


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    app.run(host="0.0.0.0", port=8991, debug=True, threaded=True)
