// session_guard: decides whether a charging session may run, based on the
// power-block temperature (REQ004). Pure logic, no hardware or RTOS deps, so it
// runs identically on the laptop (native tests) and on the ESP32-S3.
//
// Thresholds come from limits.h, generated from reqs/budgets.yml.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SG_STATE_OK = 0,        // charging allowed
    SG_STATE_OVERTEMP,      // above cutoff, counting hold time; charging still allowed
    SG_STATE_TRIPPED,       // session stopped by the guard; relay must be open
    SG_STATE_COOLDOWN,      // temperature back below resume, waiting cooldown
} sg_state_t;

typedef enum {
    SG_ACTION_NONE = 0,
    SG_ACTION_STOP_SESSION,  // caller must open the relay and send StopTransaction
    SG_ACTION_ALLOW_RESUME,  // caller may re-enable charging (new session)
} sg_action_t;

typedef struct {
    sg_state_t state;
    uint32_t   since_ms;     // timestamp of the last state change
    float      last_temp_c;
    uint32_t   trip_count;
} sg_t;

void        sg_init(sg_t *g, uint32_t now_ms);
// Feed one temperature sample. Returns the action the caller must take now.
sg_action_t sg_update(sg_t *g, float temp_c, uint32_t now_ms);
bool        sg_charging_allowed(const sg_t *g);
const char *sg_state_name(sg_state_t s);

#ifdef __cplusplus
}
#endif
