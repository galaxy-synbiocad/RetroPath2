"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort, Response, make_response
from flask_restful import Resource, Api
import io
import json
import time
import sys

import logging
from logging.handlers import RotatingFileHandler

from rq import Connection, Queue
from redis import Redis

import rpTool


#######################################################
############## REST ###################################
#######################################################

app = Flask(__name__)
api = Api(app)

#app.logger.setLevel(logging.WARNING)

## Stamp of rpCofactors
#
#
def stamp(data, status=1):
    appinfo = {'app': 'RetroPath2.0', 'version': '8.0',
               'author': 'Melchior du Lac, Joan Herisson, Thomas Duigou',
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


## REST Query
#
# REST interface that generates the Design.
# Avoid returning numpy or pandas object in
# order to keep the client lighter.
class RestQuery(Resource):
    def post(self):
        sourcefile_bytes = request.files['sourcefile'].read()
        sinkfile_bytes = request.files['sinkfile'].read()
        rulesfile_bytes = request.files['rulesfile'].read()
        params = json.load(request.files['data'])
        ##### REDIS ##############
        conn = Redis()
        q = Queue('default', connection=conn, default_timeout='24h')
        #pass the cache parameters to the rpCofactors object
        if params['partial_retro']=='True' or params['partial_retro']=='T' or params['partial_retro']=='true' or params['partial_retro']==True:
            partial_retro = True
        elif params['partial_retro']=='True' or params['partial_retro']=='F' or params['partial_retro']=='false' or params['partial_retro']==False:
            partial_retro = False
        else:
            app.logger.warning('Cannot interpret partial_retro: '+str(params['partial_retro']))
            app.logger.warning('Setting to False')
            partial_retro = False
        async_results = q.enqueue(rpTool.run_rp2,
                                  sourcefile_bytes,
                                  sinkfile_bytes,
                                  rulesfile_bytes,
                                  int(params['max_steps']),
                                  int(params['topx']),
                                  int(params['dmin']),
                                  int(params['dmax']),
                                  int(params['mwmax_source']),
                                  int(params['mwmax_cof']),
                                  int(params['timeout']),
                                  partial_retro)
        result = None
        while result is None:
            result = async_results.return_value
            if async_results.get_status()=='failed':
                return Response('Job failed \n '+str(result), status=400)
            time.sleep(2.0)
        ###########################
        status_message = 'Successfull execution'
        if result[1]==b'timeouterror' or result[1]==b'timeoutwarning':
            #for debugging
            #app.logger.warning(result[2])
            if not partial_retro:
                app.logger.error('Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool')
                return Response('Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool', status=408)
            else:
                app.logger.warning('Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool')
                app.logger.warning('Returning partial results') 
                status_message = 'WARNING: Timeout of RetroPath2.0 -- Try increasing the timeout limit of the tool -- Returning partial results'
        elif result[1]==b'memwarning' or result[1]==b'memerror':
            #for debugging
            #app.logger.warning(result[2])
            if not partial_retro:
                app.logger.error('RetroPath2.0 has exceeded its memory limit')
                return Response('RetroPath2.0 has exceeded its memory limit', status=403)
            else:
                app.logger.warning('RetroPath2.0 has exceeded its memory limit')
                app.logger.warning('Returning partial results') 
                status_message = 'WARNING: RetroPath2.0 has exceeded its memory limit -- Returning partial results'
        elif result[1]==b'sourceinsinkerror':
            app.logger.error('Source exists in the sink')
            return Response('Source exists in the sink', status=403)
        elif result[1]==b'sourceinsinknotfounderror':
            app.logger.error('Cannot find the sink-in-source file')
            return Response('Cannot find the sink-in-source file', status=500)
        elif result[1]==b'ramerror' or result[1]==b'ramwarning':
            app.logger.error('Memory allocation error')
            return Response('Memory allocation error', status=500)
        elif result[1]==b'oserror' or result[1]==b'oswarning':
            app.logger.error('RetroPath2.0 has generated an OS error')
            return Response('RetroPath2.0 returned an OS error', status=500)
        elif result[1]==b'noresultwarning' or result[1]==b'noresulterror':
            app.logger.error('Empty results')
            return Response('RetroPath2.0 returned an empty file, cannot find any solutions', status=400)
        if result[0]==b'':
            app.logger.error('Empty results')
            return Response('RetroPath2.0 returned an empty file, cannot find any solutions', status=400)
        scope_csv = io.BytesIO()
        #app.logger.error(result[0])
        scope_csv.write(result[0])
        ###### IMPORTANT ######
        scope_csv.seek(0)
        #######################
        response = make_response(send_file(scope_csv, as_attachment=True, attachment_filename='rp2_pathways.csv', mimetype='text/csv'))
        response.headers['status_message'] = status_message
        #app.logger.error('status_message: '+str(status_message))
        return response


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    handler = RotatingFileHandler('retropath2.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(host="0.0.0.0", port=8888, debug=True, threaded=True)
