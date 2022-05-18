# Avlos

Given a tree that represents a remote embedded device, Avlos will generate code (embedded, client) for the remote client to talk to the device, related documentation and more. 

![main lint and test](https://github.com/tinymovr/avlos/actions/workflows/ci.yml/badge.svg)

## Example

Given a device description expressed in a YAML file as follows (the Spec):

    name: toaster
    attributes:
    - name: sn
        dtype: uint32
        c_getter: toaster_get_sn
        summary: The unique device serial number.
    - name: heater
      attributes:
      - name: temperature
          dtype: float
          unit: celsius
          c_getter: toaster_get_heater_temp
          summary: The toaster heater temperature.
    - name: relay
      attributes:
      - name: relay_state
          dtype: bool
          c_getter: toaster_get_relay_state
          c_setter: toaster_set_relay_state
          summary: The toaster heating relay element state.

Avlos can generate the following:

- C implementation of every endpoint included in the Spec, with semantically rich information. The implementation offers data validation, (de-)serialization, getter/setter function calls, and a entry function to call with channel data.

- Python object tree reflecting the functionality of the spec, including data validation, (de-)serialization, units integration and pretty presentation. The root node needs a comms channel to realize communication with a remote device.

- RestructuredText-based documentation for each endpoint.

- CAN DBC file (CAN database), for every endpoint, for use with CAN-based comm channels.

In addition, Avlos will compute a checksum for the spec and add it as a variable so that it can be retrieved by the client for comparing client and device specs. 

The output location, as well as many other attributes of the files are flexible and easily configurable.

Avlos offers:

- A simple straightforward tree structure description, sufficient for most device types out there
- A flexible templating system with several built-in generators, and a simple unassuming system to extend
- Tight integration with physical units through the Pint module.

### Topics

- The Avlos_Command enum is structured so as to be compatible with CAN bus RTR field (i.e. 0 -> write, 1 -> read)