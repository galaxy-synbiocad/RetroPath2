# Retropath2.0

* Docker image: [brsynth/retroapth2-standalone](https://hub.docker.com/r/brsynth/retropath2-standalone)

Perform retrosynthesis search of possible metabolic routes between a source molecule and a collection of sink molecules. Docker implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The docker mounts a local folder and expects the following files: rules.csv, sink.csv and source.csv. We only support a single source molecule at this time. 

## Input

Required:
* **-sinkfile**: (string) Path to the sink file
* **-sourcefile**: (string) Path to the source file
* **-max_steps**: (integer) Maximal number of steps 
* **-rulesfile**: (string) Path to the rules file
* **-rulesfile_format**: (string) Valid Options: tar, csv. Format of the rules file

Advanced options:
* **-topx**: (integer, default: 100) For each iteration, number of rules
* **-dmin**: (integer, default: 0)
* **-dmax**: (integer, default: 1000)
* **-mwmax_source**: (integer, default: 1000)
* **-mwmax_cof**: (integer, default: 1000)
* **-timeout**: (integer, default: 30) Timeout in minutes

## Output

* **-scope_csv**: (string) Path to the output scope csv file

## Dependencies

* Base docker image: [ubuntu:18.04](https://hub.docker.com/layers/ubuntu/library/ubuntu/18.04/images/sha256-60a99a670b980963e4a9d882f631cba5d26ba5d14ccba2aa82a4e1f4d084fb1f?context=explore)

## Building the docker

To build the docker, please run the following command in the project root folder:

```
docker build -t brsynth/retropath2-standalone:dev .
```

### Running the test

To test the docker, untar the test.tar.xz file and run the following command:

```
python run.py -sinkfile test/sink.csv -sourcefile test/source.csv -rulesfile test/rules.tar -rulesfile_format tar -max_steps 3 -scope_csv test_scope.csv
```

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Version

v8.0

## Authors

* **Melchior du Lac**
* Joan Hérisson

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thomas Duigou

### How to cite RetroPath2.0?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
