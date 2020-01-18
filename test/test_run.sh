#!/bin/sh

#docker run --network host -d -p 8888:8888 --name test_rp2 brsynth/rp2paths-rest
docker run -d -p 8888:8888 --name test_rp2 brsynth/retropath2-rest
sleep 10
python tool_RetroPath2.py -sinkfile input_sink.csv -sourcefile input_source.csv -maxSteps 3 -rulesfile None -topx 100 -dmin 0 -dmax 1000 -mwmax_source 1000 -mwmax_cof 1000 -server_url http://0.0.0.0:8888/REST -scope_csv output_scope.csv -timeout 30
docker kill test_rp2
docker rm test_rp2
