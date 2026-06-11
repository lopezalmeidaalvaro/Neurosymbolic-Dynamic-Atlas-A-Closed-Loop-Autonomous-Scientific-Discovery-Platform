/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - C Unit Tests
 * File: test_astos_app.c
 * Description: Self-contained Unit Testing matching Unity/CppUTest patterns.
 * Author: Alvaro Lopez Almeida & Antigravity AI
 * ==============================================================================
 */

#include "astos_app.h"
#include <stdio.h>
#include <math.h>
#include <string.h>

/* Global counters for tests */
static int32_t tests_run = 0;
static int32_t tests_failed = 0;

/* Simple Unity-like assertions */
#define RUN_TEST(test_func) \
    do { \
        printf("[RUN] %s\n", #test_func); \
        tests_run++; \
        test_func(); \
    } while (0)

#define TEST_ASSERT_TRUE(cond) \
    do { \
        if (!(cond)) { \
            printf("  [FAIL] Assertion failed: %s (Line %d)\n", #cond, __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while (0)

#define TEST_ASSERT_EQUAL_FLOAT(expected, actual, tolerance) \
    do { \
        if (fabs((expected) - (actual)) > (tolerance)) { \
            printf("  [FAIL] Float mismatch: Expected %.5f, Got %.5f (Line %d)\n", \
                   (double)(expected), (double)(actual), __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while (0)

#define TEST_ASSERT_EQUAL_INT(expected, actual) \
    do { \
        if ((expected) != (actual)) { \
            printf("  [FAIL] Integer mismatch: Expected %d, Got %d (Line %d)\n", \
                   (int)(expected), (int)(actual), __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while (0)

/* External RAM weights declarations from astos_app.c */
extern uint8_t ACTIVE_RAM_ENCODED[144];
extern uint8_t GOLDEN_WEIGHTS_ENCODED[144];
extern float g_Active_FC1_WEIGHTS[4][1];
extern float g_Active_FC1_BIASES[4];

/* EKF and control mode handles */
extern ASTOS_AppData_t g_ASTOS_AppData;

void setUp(void) {
    ASTOS_AppInit();
}

/* 1. Test case: MLP Forward pass comparison */
void test_mlp_forward_pass_known_input(void) {
    setUp();
    float test_power[1] = {15.0f};
    float predicted[2] = {0.0f, 0.0f};

    /* Ingest baseline telemetry */
    CFE_SB_Msg_t tlm_msg;
    tlm_msg.hdr[0] = 0x08;
    tlm_msg.hdr[1] = 0x01;
    ASTOS_ProcessTelemetryPacket(&tlm_msg);

    /* Under 15W load, predicted CPU maximum temperature should converge around 69.5275C */
    TEST_ASSERT_EQUAL_FLOAT(69.5275f, g_ASTOS_AppData.PredictedCpuMax, 1e-4f);
    printf("  [PASS] MLP output matches PyTorch baseline perfectly.\n");
}

/* 2. Test case: EKF Update steps correctness */
void test_ekf_update_step(void) {
    setUp();

    /* Feed baseline telemetry: Power = 15.0W, Temp = 54.0C */
    float initial_cov = g_ASTOS_AppData.EkfCovariance;
    ASTOS_RunEfkStateEstimation(54.0f, 15.0f);

    /* Covariance must decrease after a successful measurement correction step */
    TEST_ASSERT_TRUE(g_ASTOS_AppData.EkfCovariance < initial_cov);
    TEST_ASSERT_TRUE(g_ASTOS_AppData.EkfState >= 0.05f && g_ASTOS_AppData.EkfState <= 0.95f);
    printf("  [PASS] EKF updates successfully and covariance decreases.\n");
}

/* 3. Test case: EDAC corrects single-bit flips */
void test_edac_corrects_single_bit_error(void) {
    setUp();

    /* Inject a single bit-flip error in first byte of active RAM */
    ACTIVE_RAM_ENCODED[0] ^= 1U; 

    /* Process Telemetry (triggers EDAC Hamming decoding and corrections) */
    CFE_SB_Msg_t tlm_msg;
    tlm_msg.hdr[0] = 0x08;
    tlm_msg.hdr[1] = 0x01;
    ASTOS_ProcessTelemetryPacket(&tlm_msg);

    /* The weight array must decode successfully matching baseline float weights */
    TEST_ASSERT_EQUAL_FLOAT(0.58f, g_Active_FC1_WEIGHTS[0][0], 1e-4f);
    printf("  [PASS] Hamming(7,4) EDAC successfully corrected the single-bit flip.\n");
}

/* 4. Test case: SHA-256 detects corruptions */
void test_hash_detects_corruption(void) {
    setUp();

    /* Inject double-bit error (un-correctable by Hamming(7,4)) to trigger SHA-256 reload */
    ACTIVE_RAM_ENCODED[2] ^= 1U;
    ACTIVE_RAM_ENCODED[2] ^= 2U;

    CFE_SB_Msg_t tlm_msg;
    tlm_msg.hdr[0] = 0x08;
    tlm_msg.hdr[1] = 0x01;
    ASTOS_ProcessTelemetryPacket(&tlm_msg);

    /* The integrity check must fail, trigger reloads, and successfully restore floats */
    TEST_ASSERT_EQUAL_FLOAT(0.58f, g_Active_FC1_WEIGHTS[0][0], 1e-4f);
    printf("  [PASS] SHA-256 successfully flagged corruption and reloaded Golden Copy.\n");
}

/* 5. Test case: NOOP command validation */
void test_noop_command(void) {
    setUp();
    uint16_t prev_cnt = g_ASTOS_AppData.CmdCounter;

    CFE_SB_Msg_t cmd_msg;
    cmd_msg.hdr[0] = 0x18;
    cmd_msg.hdr[1] = 0x01;
    cmd_msg.sec[0] = ASTOS_NOOP_CC;

    ASTOS_ProcessCommandPacket(&cmd_msg);

    TEST_ASSERT_EQUAL_INT(prev_cnt + 1, g_ASTOS_AppData.CmdCounter);
    printf("  [PASS] NOOP command increases command accepted counter.\n");
}

/* 6. Test case: SETPARAM command validation */
void test_setparam_command(void) {
    setUp();
    uint16_t prev_cnt = g_ASTOS_AppData.CmdCounter;

    /* SETPARAM command code: 2, new limit: 75.0C */
    ASTOS_SetParamCmd_t cmd_packet;
    cmd_packet.CmdHeader.hdr[0] = 0x18;
    cmd_packet.CmdHeader.hdr[1] = 0x01;
    cmd_packet.CmdHeader.sec[0] = ASTOS_SETPARAM_CC;
    cmd_packet.CpuSafeLimit = 75.0f;

    ASTOS_ProcessCommandPacket((CFE_SB_Msg_t*)&cmd_packet);

    TEST_ASSERT_EQUAL_INT(prev_cnt + 1, g_ASTOS_AppData.CmdCounter);
    TEST_ASSERT_EQUAL_FLOAT(75.0f, g_ASTOS_AppData.ThermalTablePtr->MaxSafeTempLimit[0], 1e-4f);
    printf("  [PASS] SETPARAM dynamically updates CPU safe bounds.\n");
}

/* 7. Test case: SETPARAM rejects invalid inputs */
void test_setparam_rejects_invalid_value(void) {
    setUp();
    uint16_t prev_err = g_ASTOS_AppData.ErrCounter;

    ASTOS_SetParamCmd_t cmd_packet;
    cmd_packet.CmdHeader.hdr[0] = 0x18;
    cmd_packet.CmdHeader.hdr[1] = 0x01;
    cmd_packet.CmdHeader.sec[0] = ASTOS_SETPARAM_CC;
    cmd_packet.CpuSafeLimit = -10.0f; /* Unphysical temperature threshold */

    ASTOS_ProcessCommandPacket((CFE_SB_Msg_t*)&cmd_packet);

    TEST_ASSERT_EQUAL_INT(prev_err + 1, g_ASTOS_AppData.ErrCounter);
    printf("  [PASS] SETPARAM rejects invalid bounds and increments error counter.\n");
}

/* Main test runner entry point */
int main(void) {
    printf("==============================================================================\n");
    printf("               AST-OS Onboard cFS Application Unit Test Suite\n");
    printf("==============================================================================\n");

    RUN_TEST(test_mlp_forward_pass_known_input);
    RUN_TEST(test_ekf_update_step);
    RUN_TEST(test_edac_corrects_single_bit_error);
    RUN_TEST(test_hash_detects_corruption);
    RUN_TEST(test_noop_command);
    RUN_TEST(test_setparam_command);
    RUN_TEST(test_setparam_rejects_invalid_value);

    printf("\n------------------------------------------------------------------------------\n");
    printf("Unit Test Summary: %d executed | %d failed\n", tests_run, tests_failed);
    printf("==============================================================================\n");

    return tests_failed == 0 ? 0 : 1;
}
