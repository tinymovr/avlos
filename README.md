<p align="center">
<img src="avlos_logo.png" width="160"/>
</p>

![main lint and test](https://github.com/tinymovr/avlos/actions/workflows/ci.yml/badge.svg)

Given a remote embedded device, a client that wants to control the device, and a YAML file that represents the remote device structure that we want exposed to the client (the spec), Avlos will generate a protocol implementation to help communicate between the client and the remote device, based on the spec. It will also generate documentation and more. 

## Example

Let's make a protocol to control a toaster. First we generate a spec file containing the structure we want the toaster to expose:

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

Given the above, Avlos can generate the following:

- C implementation of the spec, to be included in the device firmware. The implementation offers data validation, (de-)serialization, getter/setter function calls, and a entry function to call with channel data. The actual comms channel implementation is left to the user.

- A Python object reflecting the spec, to be used in the client. The object includes data validation, (de-)serialization, units integration and pretty presentation. The root node needs a comms channel to realize communication with a remote device.

- RestructuredText-based documentation for each endpoint.

- CAN DBC file (CAN database), for every endpoint, for use with CAN-based comm channels.

In addition, Avlos will compute a checksum for the spec and add it as a variable to the implementation so that it can be retrieved by the client for comparing client and device specs. 

The output location, as well as many other attributes of the files are flexible and easily configurable.

#### Avlos offers:

- A simple straightforward tree structure description, sufficient for most device types out there
- A flexible templating system with several built-in generators, and a simple unassuming system to extend
- Tight integration with physical units through the Pint module.

#### Avlos does not offer:

- An implementation of the comms channel, this is left to the user.
- Segmentation of data into packets (this is planned)

### Topics

- The Avlos_Command enum is structured so as to be compatible with CAN bus RTR field (i.e. 0 -> write, 1 -> read)
- Even though Avlos generators generate a protocol hash for both device-side (as a variable) and client-side implementations (as an object attribute), the way the hash is retrieved/checked/enforced is not included. This is due to the fact that each comms channel may implement different means of performing the above.
