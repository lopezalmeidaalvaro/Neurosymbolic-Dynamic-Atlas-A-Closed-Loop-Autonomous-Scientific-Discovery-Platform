# AST-OS cFS Application Memory Budget

This document presents a rigorous memory footprint analysis of the **AST-OS cFS flight application**, demonstrating strict conformance to resource-constrained onboard aerospace computer systems.

---

## 1. Memory Allocation Strategy

To satisfy strict safety-critical guidelines (such as **NASA Software Safety Standards** and **MISRA-C:2012**), the application implements a strict **no dynamic memory allocation** strategy:
* **Zero heap allocation**: The C files contain no calls to `malloc()`, `calloc()`, or `realloc()`. All dynamic pointers are replaced with statically bounded memory or stack variables.
* **Deterministic stack frame**: Arrays use constant bounds known at compile-time to prevent stack overflows.
* **Statically allocated globals**: Global application state data structures are allocated in the `.bss` and `.data` segments at compile-time.

---

## 2. Dynamic Memory Footprint Breakdown

```text
  AST-OS Memory Layout (Statically Bounded)
  ┌─────────────────────────────────────────────────────────┐
  │ .text (Compiled Flight Code)           ~32.5 KB         │
  ├─────────────────────────────────────────────────────────┤
  │ .rodata (Static Const MLP Weights)     ~0.15 KB         │
  ├─────────────────────────────────────────────────────────┤
  │ .data / .bss (Global Task Context)     ~0.22 KB         │
  ├─────────────────────────────────────────────────────────┤
  │ Stack Frame (Transient Calculations)    ~1.24 KB        │
  ├─────────────────────────────────────────────────────────┤
  │ Heap (Dynamic Allocation)              0.00 KB (FREE)   │
  └─────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Memory Allocations

### A. Read-Only Data (`.rodata` / `.text` Segments)
Statically defined neural weights, biases, and constant EKF coefficients:
* **MLP Hidden Layer Weights (FC1)**: 4 floats $\times$ 1 float = $16 \text{ Bytes}$
* **MLP Hidden Layer Biases (FC1)**: 4 floats = $16 \text{ Bytes}$
* **MLP Output Layer Weights (FC2)**: 2 floats $\times$ 4 floats = $32 \text{ Bytes}$
* **MLP Output Layer Biases (FC2)**: 2 floats = $8 \text{ Bytes}$
* **Event Log Static Format Strings**: $\approx 1024 \text{ Bytes}$
* *Subtotal Read-Only Data*: **$\approx 1.1 \text{ KB}$**

### B. Global Application Context (`.data` / `.bss` Segments)
Dedicated to the global task tracking structure `g_ASTOS_AppData`:
* **State counters**: `CmdCounter`, `ErrCounter` = $4 \text{ Bytes}$
* **Pipe Handles**: `CmdPipeId`, `TlmPipeId`, `TableHandle` = $12 \text{ Bytes}$
* **Active State Arrays**: `NodeTemps[5]`, `CalibratedEmissivity`, `PredictedCpuMax`, `TimeToCritical` = $32 \text{ Bytes}$
* **Boolean status flags**: `FdirActive`, `RedundantEkfActive` = $2 \text{ Bytes}$
* **CCSDS Output packet buffers**: `ASTOS_TlmPacket_t` = $48 \text{ Bytes}$
* **EKF parameter state variables**: `EkfState`, `EkfCovariance`, etc. = $16 \text{ Bytes}$
* *Subtotal Global Context*: **`220 Bytes`**

### C. Stack Frame Segment (`.stack`)
Allocated dynamically during task executions and released on block termination:
* **ASTOS_ProcessTelemetryPacket stack variables**: Local float array copies = $64 \text{ Bytes}$
* **ASTOS_RunThermalInference stack variables**: Hidden neural activations = $16 \text{ Bytes}$
* **ASTOS_RunEfkStateEstimation variables**: Jacobian and gain float coefficients = $32 \text{ Bytes}$
* *Subtotal Stack Consumption*: **`112 Bytes`** (Safe margin against $8.0 \text{ KB}$ stack budget).
