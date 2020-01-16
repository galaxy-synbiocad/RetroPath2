#!/bin/bash

docker run -v ${PWD}/inside_run.sh:/home/src/inside_run.sh -v ${PWD}/tool_RetroPath2.py:/home/src/tool_RetroPath2.py -v ${PWD}/test_input_sink.dat:/home/src/test_input_sink.dat -v ${PWD}/test_input_source.dat:/home/src/test_input_source.dat -v ${PWD}/results/:/home/src/results/ --rm brsynth/retropath2 /bin/sh /home/src/inside_run.sh

cp results/test_out_scope.csv .
