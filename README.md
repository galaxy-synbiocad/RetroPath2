# Retropath2.0 docker

* Docker image: [brsynth/retroapth2-standalone](https://hub.docker.com/r/brsynth/retropath2-standalone)

Perform retrosynthesis search of possible metabolic routes between a source molecule and a collection of sink molecules. Docker implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The docker mounts a local folder and expects the following files: rules.csv, sink.csv and source.csv. We only support a single source molecule at this time. 

## Building the docker

We will cover calling RetroPath2.0 using Galaxy where the docker is installed locally and when the docker is remotely located using the Pulsar package. In both cases one needs to build the docker using the following command:

```
docker build -t brsynth/retropath2-standalone:dev .
```

### Running the test

To test the docker, untar the test.tar.xz file and run the following command:

```
python run.py -sinkfile test/sink.csv -sourcefile test/source.csv -rulesfile test/rules.tar -rulesfile_format tar -max_steps 3 -scope_csv test_scope.csv
```

## Dependencies

* Base image: [ibisba/knime-base:3.6.2](https://hub.docker.com/r/ibisba/knime-base)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Version

Version 8.0

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
