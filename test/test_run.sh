#!/bin/sh

#docker run --network host -d -p 8888:8888 --name test_rp2 brsynth/rp2paths-rest
docker run -d -p 8888:8888 --name test_rp2 brsynth/retropath2-redis
sleep 10
python3 tool_RetroPath2.py -sinkfile test_input_sink.dat -sourcefile test_input_source.dat -maxSteps 3 -rulesfile 'None' -topx 100 -dmin 0 -dmax 1000 -mwmax_source 1000 -mwmax_cof 1000 -timeout 30 -scope_csv test_out_scope.csv -server_url http://0.0.0.0:8888/REST
docker kill test_rp2
docker rm test_rp2
