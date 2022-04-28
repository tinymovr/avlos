
#pragma once

#include <cstdint>
{%- if 'remote_attributes' in instance %}
    {%- for attr in instance.remote_attributes %}
        {%- if 'remote_attributes' in object %}
#include <{{attr.name}}.hpp>
        {%- endif %}
    {%- endfor %}
{%- endif %}

typedef void (*send_callback)(uint32_t arbitration_id, uint8_t *data, uint8_t dlc, bool rtr);
typedef bool (*recv_callback)(uint32_t arbitration_id, uint8_t *data, uint8_t *dlc);

class Tinymovr
{
    public:

        Tinymovr(uint8_t _can_node_id, send_callback _send_cb, recv_callback _recv_cb):
        can_node_id(_can_node_id), send_cb(_send_cb), recv_cb(_recv_cb) {};

    {%- if 'remote_attributes' in instance %}
        {%- for object in instance.remote_attributes %}
            {%- if 'remote_attributes' in object %}
        {{object.name}} {{object.name}};
            {%- else %}
            
        {{object.type}} get_{{object.name}}(void);
        void set_{{object.name}}({{object.type}} value);
            {%- endif %}
        {%- endfor %}
    {%- endif %}

    private:

        uint8_t can_node_id;
        send_callback send_cb;
        recv_callback recv_cb;
        uint8_t _data[8];
        uint8_t _dlc;

        void send(uint8_t cmd_id, uint8_t *data, uint8_t data_size, bool rtr);
        bool recv(uint8_t cmd_id, uint8_t *data, uint8_t *data_size, uint16_t delay_us);
        uint8_t get_arbitration_id(uint8_t cmd_id);

}