# Retropath2.0

Build a reaction network from a set of source compounds to a set of sink compounds. Docker implementation with Flask REST, RQ and Redis of the KNIME retropath2.0 workflow. 

## Information Flow

### Input

Required information:
    * A list of sink molecules in the form of a CSV file (Can use "sink from SBML" node).
    * A source molecule also in the form of a CSV file (Can use "Make source" node).
    * An integer determining the maximal pathway length. 

Advanced options: 
    * Rules file: (optional) An input CSV file with the collections of reaction rules. The default are the rules from RetroPath2.0
    * TopX: (default 100) The maximal number of pathways to retain for each new iteration
    * Minimum rule diameter: (default: 0) Given a reaction rule, set the lower bound promiscuity
    * Maximaum rule diameter: (default: 1000) Given a reaction rule, set the upper bound promiscuity
    * mwmax source: (default: 1000)
    * mwmax cof: (default: 1000)
    * Server URL: Give the address of the REST service
    * Timemout: (default: 30 min) Limit the execution time of the tool
    * Run in forward direction: (default: No)

### Output

* RetroPath Pathways: describes the heterologous pathways calculated to produce a target molecule of interest (Source) with a complete description of the structures of the product and subtrates as well as the reaction rules applied to it. 

## Installing

Compile the docker image if it hasen't already been done:

```
docker build -t brsynth/retropath2-redis:dev .
```

To run the service on a localhost as the Galaxy interface, after creating the image run the REST service using the following command:

```
docker run -p 8888:8888 brsynth/retropath2
```

## Built With

* Docker - [Install](https://docs.docker.com/v17.09/engine/installation/)
* Base image: [ibisba/knime-base:3.6.2](https://hub.docker.com/r/ibisba/knime-base)

## Contributing

TODO

## Versioning

Version 0.1

## Authors

* **Melchior du Lac**
* Thomas Duigou
* Baudoin Delépine
* Pablo Carbonell

## License

[GPL3](https://github.com/Galaxy-SynBioCAD/RetroPath2/blob/master/LICENSE)

## Acknowledgments

* Joan Hérisson

### How to cite RetroPath2.0?

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
