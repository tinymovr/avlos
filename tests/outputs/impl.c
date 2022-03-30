/*
* This file was automatically generated using csnake v0.3.4.
*
* This file should not be edited directly, any changes will be
* overwritten next time the script is run.
*
* Source code for csnake is available at:
* https://gitlab.com/andrejr/csnake
*
* csnake is also available on PyPI, at :
* https://pypi.org/project/csnake
*/

#include "src/common.h"

uint8_t avlos_system_get_sn(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    uint32_t v;
    v = system_get_sn();
    *buffer_len = sizeof(uint32_t);
    memcpy(buffer, &v, sizeof(uint32_t));
    return CANRP_Read;
}

uint8_t avlos_system_get_vbus(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    v = system_get_vbus();
    *buffer_len = sizeof(float);
    memcpy(buffer, &v, sizeof(float));
    return CANRP_Read;
}

uint8_t avlos_motor_get_R(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    v = motor_get_R();
    *buffer_len = sizeof(float);
    memcpy(buffer, &v, sizeof(float));
    return CANRP_Read;
}

uint8_t avlos_motor_set_R(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    memcpy(&v, buffer, sizeof(float));
    motor_set_R(v);
    return CANRP_Write;
}

uint8_t avlos_motor_get_L(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    v = motor_get_L();
    *buffer_len = sizeof(float);
    memcpy(buffer, &v, sizeof(float));
    return CANRP_Read;
}

uint8_t avlos_motor_set_L(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    memcpy(&v, buffer, sizeof(float));
    motor_set_L(v);
    return CANRP_Write;
}

uint8_t avlos_encoder_get_pos_estimate(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    v = encoder_get_pos_estimate();
    *buffer_len = sizeof(float);
    memcpy(buffer, &v, sizeof(float));
    return CANRP_Read;
}

uint8_t avlos_encoder_get_bandwidth(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    v = encoder_get_bandwidth();
    *buffer_len = sizeof(float);
    memcpy(buffer, &v, sizeof(float));
    return CANRP_Read;
}

uint8_t avlos_encoder_set_bandwidth(uint8_t * buffer, uint8_t * buffer_len, bool rtr)
{
    float v;
    memcpy(&v, buffer, sizeof(float));
    encoder_set_bandwidth(v);
    return CANRP_Write;
}

