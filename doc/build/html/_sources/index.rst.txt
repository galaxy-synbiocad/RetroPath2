RetroPath2's Redis Documentation
================================

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
############

.. _MyExperiment: https://www.myexperiment.org/workflows/4987.html
.. _KNIME: https://www.knime.com/

Welcome to RetroPath2's Redis documentation. This project wraps the RetroPath2.0 KNIME_ workflow hosted on MyExperiment_ into a Redis docker that may be called locally. The project is intended to be used to be used as a service that is called by multiple users and allows for limits of the number of users that call RetroPath2.0 simultaneously. 

The Redis service is used as a queuing service that allows for a number of users to wait for the x number of RetroPath2.0 instances. This is controlled by modifying the supervisor.conf file at the following line: numprocs=2.

The limit of RAM usage can also be defined by changing the following line of rpTool.py: MAX_VIRTUAL_MEMORY = 30000*1024*1024 # 30 GB. 

In both cases the docker must be rebuild if changed, using the following command:

.. code-block:: bash

   docker build -t brsynth/retropath2-redis .

The service must be ran, and can be done using the following command:

.. code-block:: bash

   docker run -p 8888:8888 brsynth/retropath2-redis

Where the public port number can be changed by the first instance of the 8888 number above. 

To call the rest service, the easiest way is to use the galaxy/code/tool_RetroPath2.py file in the following fashion:

.. code-block:: bash

   python tool_RetroPath2.py -sinkfile test/sink.csv -sourcefile test/source.csv -rulesfile test/rules.tar -rulesfile_format tar -max_steps 3 -scope_csv test_scope.csv

API
###

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. currentmodule:: rpTool

.. autoclass:: run_rp2
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: rpToolServe

.. autoclass:: RestQuery
    :show-inheritance:
    :members:
    :inherited-members:

