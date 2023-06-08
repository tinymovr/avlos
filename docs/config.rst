Avlos Configuration
*******************

Device Spec
-----------

The Device Spec is a YAML file that defines how the device is structured. It consists of a tree-like structure. 

Output Config
-------------

The output config defines the output modules that will be used and their options. Example, showing C code generation for embedded devices:

.. code-block::
    
    generators:
        generator_c:
            enabled: true
            paths:
                output_header: outputs/header.h
                output_impl: outputs/header.c
            header_includes:
            - src/header.h
            impl_includes:
            - src/test.h

Usage
-----

Using a Local File
******************

Ensure the device spec and the output config exist in the current folder.

.. code-block:: console

    avlos from file device.yaml

This will generate the outputs according to the configuration in the output config file.


Using a URL
***********

Ensure the output config exists in the current folder.

.. code-block:: console

    avlos from url https://your.url/spec.yaml

This will generate the outputs according to the configuration in the output config file.