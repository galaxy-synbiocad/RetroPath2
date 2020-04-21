"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort, Response
from flask_restful import Resource, Api
import io
import logging
import json
import time

from rq import Connection, Queue
from redis import Redis

import rpTool

from logging.handlers import RotatingFileHandler

#######################################################
############## REST ###################################
#######################################################


app = Flask(__name__)
api = Api(app)


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
        if result[1]==b'timeout':
            app.logger.error('Timeout of RetroPath2.0')
            return Response("Timeout of RetroPath2.0", status=400)
        elif result[1]==b'sourceinsinkerror':
            app.logger.error('Source exists in the sink')
            return Response('Source exists in the sink', status=400)
        elif result[1]==b'sourceinsinknotfounderror':
            app.logger.error('Cannot find the sink-in-source file')
            return Response('Cannot find the sink-in-source file', status=400)
        elif result[1]==b'memoryerror':
            app.logger.error('Memory allocation error')
            return Response("RetroPath2.0 has exceeded its memory limit", status=400)
        elif result[1]==b'oserror':
            app.logger.error('RetroPath2.0 has generated an OS error')
            return Response("RetroPath2.0 returned an OS error", status=400)
        elif result[1]==b'ramerror':
            app.logger.error('Could not setup a RAM limit')
            return Response("RetroPath2.0 has exceeded its memory limit", status=400)
        elif result[1]==b'timeoutwarning' or result[1]==b'memwarning' or result[1]==b'noresultwarning' or result[1]==b'oswarning' or result[1]==b'ramwarning':
            app.logger.warning(result[2])
            app.logger.warning('Returning partial results') 
        if result[0]==b'':
            app.logger.error('Empty results')
            return Response("RetroPath2.0 cannot find any solutions", status=400)
        scope_csv = io.BytesIO()
        scope_csv.write(result[0])
        ###### IMPORTANT ######
        scope_csv.seek(0)
        #######################
        return send_file(scope_csv, as_attachment=True, attachment_filename='rp2_pathways.csv', mimetype='text/csv')


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    handler = RotatingFileHandler('retropath2.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(host="0.0.0.0", port=8888, debug=True, threaded=True)
