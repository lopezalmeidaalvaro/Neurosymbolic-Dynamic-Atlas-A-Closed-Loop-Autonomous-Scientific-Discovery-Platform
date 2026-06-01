/*
 * ==============================================================================
 * Spacecraft Thermal OS - Deterministic Neural Inference Engine
 * Generated: 2026-05-29
 * Compliance: MISRA-C:2012 Rule Compliant (Dynamic allocation free)
 * ==============================================================================
 */

#include <stdint.h>

#define INPUT_DIM  4
#define HIDDEN_DIM 3
#define OUTPUT_DIM 2

/* Static const neural network weights and biases */
static const float WEIGHTS_FC1[HIDDEN_DIM][INPUT_DIM] = {
    {0.1200f, -0.4500f, 0.8800f, -0.1500f},
    {-0.3400f, 0.2200f, -0.1100f, 0.5600f},
    {0.6700f, -0.8900f, 0.0500f, -0.3100f}
};

static const float BIASES_FC1[HIDDEN_DIM] = {0.1000f, -0.0500f, 0.2500f};

static const float WEIGHTS_FC2[OUTPUT_DIM][HIDDEN_DIM] = {
    {0.9100f, -0.2100f, 0.5400f},
    {-0.1800f, 0.7300f, -0.0900f}
};

static const float BIASES_FC2[OUTPUT_DIM] = {-0.1500f, 0.0800f};

/*
 * Executes one forward propagation step of the surrogate neural network.
 * Satisfies MISRA-C guidelines: No dynamic recursion, fixed loop iterations, zero pointers.
 */
void run_neural_inference(const float input[INPUT_DIM], float output[OUTPUT_DIM]) {
    float hidden[HIDDEN_DIM];
    uint32_t i;
    uint32_t j;

    /* First fully-connected layer (FC1) + ReLU activation */
    for (i = 0U; i < HIDDEN_DIM; i++) {
        float sum = BIASES_FC1[i];
        for (j = 0U; j < INPUT_DIM; j++) {
            sum += WEIGHTS_FC1[i][j] * input[j];
        }
        /* ReLU activation function: max(0.0, sum) */
        if (sum > 0.0f) {
            hidden[i] = sum;
        } else {
            hidden[i] = 0.0f;
        }
    }

    /* Second fully-connected layer (FC2) */
    for (i = 0U; i < OUTPUT_DIM; i++) {
        float sum = BIASES_FC2[i];
        for (j = 0U; j < HIDDEN_DIM; j++) {
            sum += WEIGHTS_FC2[i][j] * hidden[j];
        }
        output[i] = sum;
    }
}
