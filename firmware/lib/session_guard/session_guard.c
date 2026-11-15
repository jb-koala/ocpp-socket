#include "session_guard.h"
#include "limits.h"

void sg_init(sg_t *g, uint32_t now_ms) {
    g->state = SG_STATE_OK;
    g->since_ms = now_ms;
    g->last_temp_c = 0.0f;
    g->trip_count = 0;
}

static void enter(sg_t *g, sg_state_t s, uint32_t now_ms) {
    g->state = s;
    g->since_ms = now_ms;
}

sg_action_t sg_update(sg_t *g, float temp_c, uint32_t now_ms) {
    g->last_temp_c = temp_c;
    uint32_t elapsed = now_ms - g->since_ms;  // wraps correctly on uint32

    switch (g->state) {
    case SG_STATE_OK:
        if (temp_c > SG_TEMP_CUTOFF_C) enter(g, SG_STATE_OVERTEMP, now_ms);
        return SG_ACTION_NONE;

    case SG_STATE_OVERTEMP:
        if (temp_c <= SG_TEMP_CUTOFF_C) {
            enter(g, SG_STATE_OK, now_ms);   // brief spike, back to normal
            return SG_ACTION_NONE;
        }
        if (elapsed >= SG_TEMP_HOLD_MS) {
            g->trip_count++;
            enter(g, SG_STATE_TRIPPED, now_ms);
            return SG_ACTION_STOP_SESSION;
        }
        return SG_ACTION_NONE;

    case SG_STATE_TRIPPED:
        if (temp_c < SG_TEMP_RESUME_C) enter(g, SG_STATE_COOLDOWN, now_ms);
        return SG_ACTION_NONE;

    case SG_STATE_COOLDOWN:
        if (temp_c >= SG_TEMP_RESUME_C) {
            enter(g, SG_STATE_TRIPPED, now_ms);  // went back up: restart cooldown later
            return SG_ACTION_NONE;
        }
        if (elapsed >= SG_TEMP_COOLDOWN_MS) {
            enter(g, SG_STATE_OK, now_ms);
            return SG_ACTION_ALLOW_RESUME;
        }
        return SG_ACTION_NONE;
    }
    return SG_ACTION_NONE;
}

bool sg_charging_allowed(const sg_t *g) {
    return g->state == SG_STATE_OK || g->state == SG_STATE_OVERTEMP;
}

const char *sg_state_name(sg_state_t s) {
    switch (s) {
    case SG_STATE_OK:       return "OK";
    case SG_STATE_OVERTEMP: return "OVERTEMP";
    case SG_STATE_TRIPPED:  return "TRIPPED";
    case SG_STATE_COOLDOWN: return "COOLDOWN";
    }
    return "?";
}
