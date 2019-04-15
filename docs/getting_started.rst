********************************************************************************
Getting started
********************************************************************************

Installation
============

The recommended way to install **COMPAS FAB** is to use `Anaconda/conda <https://conda.io/docs/>`_:

::

    conda config --add channels conda-forge
    conda install compas_fab


But it can also be installed using ``pip``:

::

    pip install compas_fab


Once installed, you can verify your setup. Start Python from the command prompt and run the following:

.. code-block:: python

    >>> import compas_fab


Environments
============

Just like the main library of **COMPAS**, the core functionality of **COMPAS FAB**
is independent of CAD software and can be used from the command prompt,
in standalone scripts.


Working in Rhino
----------------

*Installing* **COMPAS FAB** for Rhino is very simple. Just open the *command prompt*
and type the following

::

    python -m compas_fab.rhino.install


Optionally, you could provide a Rhino version number (``5.0, 6.0``).
The default is ``6.0``.

::

    python -m compas_fab.rhino.install -v 6.0


Working in Blender
------------------

Once **COMPAS** itself is installed for Blender following the documented procedure,
**COMPAS FAB** will automatically be available as well after installing it.


First Steps
===========

* :ref:`Working with backends <backends>`
* :ref:`Examples <examples>`
* :ref:`API Reference <reference>`
* `COMPAS Examples <https://compas-dev.github.io/main/examples.html>`_
* `COMPAS Tutorials <https://compas-dev.github.io/main/tutorial.html>`_
* `COMPAS API Reference <https://compas-dev.github.io/main/api.html>`_
