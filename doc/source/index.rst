RetroPath2's Documentation
==========================

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
############

.. _MyExperiment: https://www.myexperiment.org/workflows/4987.html
.. _KNIME: https://www.knime.com/

Welcome to RetroPath2's documentation. This project wraps the RetroPath2.0 KNIME_ workflow hosted on MyExperiment_ into a docker that may be called locally. 

First build the docker using the following command:

.. code-block:: bash

   docker build -t brsynth/rpextractsink-standalone:v2 .

To call the docker locally you can use the following command:

.. code-block:: bash

   python run.py -sinkfile /path/to/file -sourcefile /path/to/file -rulesfile /path/to/file -rulesfile_format csv -scope_csv /path/to/output -max_steps 10

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

.. currentmodule:: run

.. autoclass:: main
    :show-inheritance:
    :members:
    :inherited-members:

