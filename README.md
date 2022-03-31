# Avlos

Given a tree that represents a remote embedded device, Avlos will generate code (embedded, client) for the remote client to talk to the device. 

## Example

Given the description expressed in a YAML file as follows:

    name: toaster
    attributes:
    - name: sn
        dtype: uint32
        c_getter: toaster_get_sn
        description: The unique device serial number.
    - name: heater
      attributes:
      - name: temperature
          dtype: float
          unit: celsius
          c_getter: toaster_get_temp
          description: The toaster heater temperature.
      - name: relay_state
          dtype: bool
          c_getter: toaster_get_relay_state
          c_setter: toaster_set_relay_state
          description: The toaster heating relay element state.

, Avlos will generate the following C header and implementation:



, and the following RestructuredText documentation:



The output location, as well as many other attributes of the files are configurable.