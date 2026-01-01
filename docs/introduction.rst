Introduction
************

Avlos makes it easy to create protocol implementations to communicate with remote embedded devices.

Given a remote embedded device, a client that wants to talk with the device, and a YAML file that represents the remote device structure that we want exposed to the client (the spec), Avlos will generate a protocol implementation based on the spec. It will also generate documentation and more. 

.. figure:: diagram.png
  :width: 800
  :align: center
  :alt: Functional diagram of Avlos
  :figclass: align-center

Avlos has been originally developed as a communication layer for `Tinymovr <https://tinymovr.com>`_

Installation
************

.. code-block:: console

    pip install avlos

Development
***********

Versioning
----------

Avlos uses git tags for version management via `setuptools-scm <https://github.com/pypa/setuptools-scm>`_.

To create a new release, tag the commit: ``git tag v0.X.Y``

