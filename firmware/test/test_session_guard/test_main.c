// Native tests for session_guard (REQ004). Run: pio test -e native
#include <unity.h>
#include "session_guard.h"
#include "sg_limits.h"

static sg_t g;

void setUp(void)    { sg_init(&g, 0); }
void tearDown(void) {}

static void test_normal_temperature_keeps_charging(void) {
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, 40.0f, 1000));
    TEST_ASSERT_TRUE(sg_charging_allowed(&g));
    TEST_ASSERT_EQUAL(SG_STATE_OK, g.state);
}

static void test_short_spike_does_not_trip(void) {
    float hot = SG_TEMP_CUTOFF_C + 5.0f;
    sg_update(&g, hot, 1000);
    sg_update(&g, hot, 1000 + SG_TEMP_HOLD_MS / 2);
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, 50.0f, 1000 + SG_TEMP_HOLD_MS / 2 + 100));
    TEST_ASSERT_EQUAL(SG_STATE_OK, g.state);
    TEST_ASSERT_EQUAL(0, g.trip_count);
}

static void test_sustained_overtemp_stops_session(void) {
    float hot = SG_TEMP_CUTOFF_C + 1.0f;
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, hot, 1000));
    TEST_ASSERT_EQUAL(SG_STATE_OVERTEMP, g.state);
    TEST_ASSERT_TRUE(sg_charging_allowed(&g));  // still charging while counting hold
    TEST_ASSERT_EQUAL(SG_ACTION_STOP_SESSION, sg_update(&g, hot, 1000 + SG_TEMP_HOLD_MS));
    TEST_ASSERT_EQUAL(SG_STATE_TRIPPED, g.state);
    TEST_ASSERT_FALSE(sg_charging_allowed(&g));
    TEST_ASSERT_EQUAL(1, g.trip_count);
}

static void test_stays_tripped_until_below_resume(void) {
    float hot = SG_TEMP_CUTOFF_C + 1.0f;
    sg_update(&g, hot, 0);
    sg_update(&g, hot, SG_TEMP_HOLD_MS);
    // between resume and cutoff: still tripped
    float warm = (SG_TEMP_CUTOFF_C + SG_TEMP_RESUME_C) / 2.0f;
    sg_update(&g, warm, SG_TEMP_HOLD_MS + 1000);
    TEST_ASSERT_EQUAL(SG_STATE_TRIPPED, g.state);
    TEST_ASSERT_FALSE(sg_charging_allowed(&g));
}

static void test_resume_only_after_cooldown(void) {
    float hot = SG_TEMP_CUTOFF_C + 1.0f;
    float cool = SG_TEMP_RESUME_C - 5.0f;
    sg_update(&g, hot, 0);
    sg_update(&g, hot, SG_TEMP_HOLD_MS);
    uint32_t t = SG_TEMP_HOLD_MS + 1000;
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, cool, t));
    TEST_ASSERT_EQUAL(SG_STATE_COOLDOWN, g.state);
    TEST_ASSERT_FALSE(sg_charging_allowed(&g));
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, cool, t + SG_TEMP_COOLDOWN_MS - 1));
    TEST_ASSERT_EQUAL(SG_ACTION_ALLOW_RESUME, sg_update(&g, cool, t + SG_TEMP_COOLDOWN_MS));
    TEST_ASSERT_EQUAL(SG_STATE_OK, g.state);
    TEST_ASSERT_TRUE(sg_charging_allowed(&g));
}

static void test_reheat_during_cooldown_restarts(void) {
    float hot = SG_TEMP_CUTOFF_C + 1.0f;
    float cool = SG_TEMP_RESUME_C - 5.0f;
    sg_update(&g, hot, 0);
    sg_update(&g, hot, SG_TEMP_HOLD_MS);
    uint32_t t = SG_TEMP_HOLD_MS + 1000;
    sg_update(&g, cool, t);
    sg_update(&g, SG_TEMP_RESUME_C + 1.0f, t + SG_TEMP_COOLDOWN_MS / 2);
    TEST_ASSERT_EQUAL(SG_STATE_TRIPPED, g.state);
    // cooldown must restart from scratch
    sg_update(&g, cool, t + SG_TEMP_COOLDOWN_MS / 2 + 10);
    TEST_ASSERT_EQUAL(SG_ACTION_NONE, sg_update(&g, cool, t + SG_TEMP_COOLDOWN_MS));
    TEST_ASSERT_EQUAL(SG_STATE_COOLDOWN, g.state);
}

static void test_limits_match_budgets_hysteresis(void) {
    // reqs/budgets.yml must keep resume < cutoff; mirrors tests/test_budgets.py
    TEST_ASSERT_TRUE(SG_TEMP_RESUME_C < SG_TEMP_CUTOFF_C);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_normal_temperature_keeps_charging);
    RUN_TEST(test_short_spike_does_not_trip);
    RUN_TEST(test_sustained_overtemp_stops_session);
    RUN_TEST(test_stays_tripped_until_below_resume);
    RUN_TEST(test_resume_only_after_cooldown);
    RUN_TEST(test_reheat_during_cooldown_restarts);
    RUN_TEST(test_limits_match_budgets_hysteresis);
    return UNITY_END();
}
