# Experimental Stress Design Report — Phase 4E

Designs physical experiment sweeps that maximize prediction divergence to falsify the RTHEORY model.

| Experiment ID | Theory ID | Physical Domain | Target Gate Error | Target Readout Error | Expected Divergence | Min Shots | Verification Devices |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `EXP_001` | `RTHEORY_001` | `quantum_hardware_noise` | `0.015` | `0.035` | `0.077033` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_002` | `RTHEORY_002` | `calibration_drift` | `0.015` | `0.035` | `0.076467` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_003` | `RTHEORY_003` | `readout_error` | `0.015` | `0.035` | `0.104946` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_004` | `RTHEORY_004` | `gate_error` | `0.015` | `0.035` | `0.064880` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_005` | `RTHEORY_005` | `cross_vendor_transfer` | `0.015` | `0.035` | `0.089252` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_006` | `RTHEORY_006` | `device_aging` | `0.015` | `0.035` | `0.096447` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_007` | `RTHEORY_007` | `hardware_stability` | `0.015` | `0.035` | `0.061632` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_008` | `RTHEORY_008` | `spectator_crosstalk` | `0.015` | `0.035` | `0.071612` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_009` | `RTHEORY_009` | `thermal_relaxation` | `0.015` | `0.035` | `0.094087` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
| `EXP_010` | `RTHEORY_010` | `leakage_rate` | `0.015` | `0.035` | `0.100380` | `10000` | `rigetti_aspen_m3, ionq_aria, quantinuum_h1` |
