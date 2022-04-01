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

, Avlos will generate the following C header(note: there are actually a few more stuff not included here for brevity):

    /*
    * avlos_toaster_get_sn
    *
    * The unique device serial number.
    *
    * @param buffer
    * @param buffer_len
    * @param rtr
    */
    uint8_t avlos_toaster_get_sn(uint8_t * buffer, uint8_t * buffer_len, bool rtr);

    /*
    * avlos_toaster_get_temp
    *
    * The toaster heater temperature.
    *
    * @param buffer
    * @param buffer_len
    * @param rtr
    */
    uint8_t avlos_toaster_get_temp(uint8_t * buffer, uint8_t * buffer_len, bool rtr);

    /*
    * avlos_toaster_get_relay_state
    *
    * The toaster heating relay element state.
    *
    * @param buffer
    * @param buffer_len
    * @param rtr
    */
    uint8_t avlos_toaster_get_relay_state(uint8_t * buffer, uint8_t * buffer_len, bool rtr);

, implementation:

    uint8_t avlos_toaster_get_sn(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
    {
        uint32_t v;
        v = toaster_get_sn();
        *buffer_len = sizeof(uint32_t);
        memcpy(buffer, &v, sizeof(uint32_t));
        return CANRP_Read;
    }

    uint8_t avlos_toaster_get_temp(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
    {
        float v;
        v = toaster_get_temp();
        *buffer_len = sizeof(float);
        memcpy(buffer, &v, sizeof(float));
        return CANRP_Read;
    }

    uint8_t avlos_toaster_get_relay_state(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
    {
        bool v;
        v = toaster_get_relay_state();
        *buffer_len = sizeof(bool);
        memcpy(buffer, &v, sizeof(bool));
        return CANRP_Read;
    }

    uint8_t avlos_toaster_set_relay_state(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
    {
        bool v;
        memcpy(&v, buffer, sizeof(bool));
        toaster_set_relay_state(v);
        return CANRP_Write;
    }

, and the following RestructuredText documentation:

    toaster.sn
    ----------

    - Endpoint ID: 1
    - Data Type: uint32
    - Unit: Not defined

    The unique device serial number.

    toaster.heater.temperature
    --------------------------

    - Endpoint ID: 2
    - Data Type: float
    - Unit: degree_Celsius

    The toaster heater temperature.

    toaster.heater.relay_state
    --------------------------

    - Endpoint ID: 3
    - Data Type: bool
    - Unit: Not defined

    The toaster heating relay element state.


The output location, as well as many other attributes of the files are configurable.