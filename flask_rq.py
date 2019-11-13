"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import logging
import json
import time

from rq import Connection, Queue
from redis import Redis

from rp2 import run


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
        conn = Redis()
        q = Queue('default', connection=conn, default_timeout='24h') #essentially infinite
        #q = Queue(default_timeout='24h') #essentially infinite
        sourcefile_bytes = request.files['sourcefile'].read()
        sinkfile_bytes = request.files['sinkfile'].read()
        rulesfile_bytes = request.files['rulesfile'].read()
        app.logger.info(rulesfile_bytes)
        params = json.load(request.files['data'])
        #pass the cache parameters to the rpCofactors object 
        async_results = q.enqueue(run,
                                  sinkfile_bytes,
                                  sourcefile_bytes,
                                  params['maxSteps'],
                                  rulesfile_bytes,
                                  params['topx'],
                                  params['dmin'],
                                  params['dmax'],
                                  params['mwmax_source'],
                                  params['mwmax_cof'],
                                  params['timeout'])
        result = None
        #failed
        while result is None:
            result = async_results.return_value
            if async_results.get_status()=='failed':
                app.logger.error('ERROR: Job failed')
                raise(400)
            time.sleep(2.0)
        if result[0]==b'':
            app.logger.error('ERROR: Empty results')
            logging.error(result[1])
            scopeCSV = io.BytesIO()
            ###### IMPORTANT ######
            scopeCSV.seek(0)
            #######################
            return send_file(scopeCSV, as_attachment=True, attachment_filename='rp2_pathways.csv', mimetype='text/csv')
        elif result[0]==b'timeout':
            app.logger.error.error('ERROR: Timeout of RetroPath2.0')
            raise(400)
        elif result[0]==b'memerror':
            app.logger.error.error('ERROR: Memory allocation error')
            raise(400)
        elif result[0]==b'noresulterror':
            app.logger.error.error('ERROR: Could not find any results by RetroPath2.0')
            raise(400)
        elif result[0]==b'oserror':
            app.logger.error.error('ERROR: RetroPath2.0 has generated an OS error')
            raise(400)
        elif result[0]==b'ramerror':
            app.logger.error.error('ERROR: Could not setup a RAM limit')
            raise(400)
        scopeCSV = io.BytesIO()
        scopeCSV.write(result[0])
        ###### IMPORTANT ######
        scopeCSV.seek(0)
        #######################
        return send_file(scopeCSV, as_attachment=True, attachment_filename='rp2_pathways.csv', mimetype='text/csv')


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    app.run(host="0.0.0.0", port=8991, debug=True, threaded=True)
