# Galaxy Retropath2.0

Docker implementation with Flask REST, RQ and Redis of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The docker mounts a local folder and expects the following files: rules.csv, sinl.csv and source.csv. 

## Installing

### How to run using Galaxy

```
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart
```

We will cover calling RetroPath2.0 using Galaxy where the docker is installed locally and when the docker is remotely located using the Pulsar package. In both cases one needs to build the docker using the following command:

```
docker build -t brsynth/retropath2-redis .
```

It is recommended that one tests the docker using the following commands. First enter the docker in bash using:

```
docker run -p 8888:8888 brsynth/retropath2
```

The pyKnime.py script will write the output files in the "outDir" as well as locally as named using the NEW keyword. This is required to make the docker compatible with the manner by which Galaxy requires the data to be returned to it.

### Local docker

If one has the docker and the Galaxy services on the same machine, then the following Galaxy configurations are required to make them run. 

##### Add the tool to Galaxy's tool_conf.xml

Create a new section in the Galaxy tool_conf.xml

```
<section id="retro" name="Retro Nodes">
  <tool file="/local/path/retroPath_galaxy.xml" />
</section>
```

##### Modify the job_conf.xml

```
<?xml version="1.0"?>
<job_conf>
  <plugins>
    <plugin id="local" type="runner" load="galaxy.jobs.runners.local:LocalJobRunner" workers="4"/>
  </plugins>
  <destinations default="docker_local">
    <destination id="local" runner="local" />
    <destination id="docker_local" runner="local">
      <param id="docker_enabled">true</param>
      <param id="docker_sudo">false</param>
      <param id="docker_auto_rm">true</param>
      <param id="docker_set_user">root</param>
    </destination>
  </destinations>
</job_conf>
```

It is important to run the docker as root user since we will be calling a script that writes files to a temporary folder inside the docker before sending bask to Galaxy

### Pulsar docker call

To run the tool on a remote server and call it using any Galaxy instance, we need to install and configure Pulsar and the docker of the tool

##### Add the tool your LOCAL Galaxy's tool_conf.xml

```
<section id="retro" name="Retro Nodes">
  <tool file="/local/path/retroPath_galaxy.xml" />
</section>
```

## Running

### Example Input

TODO

### Example Docker Run

Once inside the docker in bash, use the following command to call a KNIME job using the example files provided:

```
pyKnime.py -source "/home/src/tutorial_data/carotene/source.csv" -sink "/home/src/tutorial_data/carotene/sink.csv" -rules "/home/src/tutorial_data/carotene/rules.csv" -dmin 0 -dmax 1000 -maxSteps 5 -outDir "/home/src/data" -results "NEWresults.csv" -sourceinsink "NEWsource-in-sink.csv" -scopeJSON "NEWscope.json" -scopeCSV "NEWscope.csv"
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

### Cite

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
