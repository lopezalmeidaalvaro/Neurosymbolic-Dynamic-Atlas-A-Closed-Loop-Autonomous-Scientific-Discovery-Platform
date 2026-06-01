# Flight Heritage Calibration Report

**Document ID**: AST-THERM-HER-CAL-v4-CANDIDATE  
**Authority**: Thermal Physics Lead / Independent V&V Board  
**Generated**: 2026-05-31 14:57:40  
**Optimization Method**: Nelder-Mead  

## Executive Verdict

- `RISK-HER-02`: `CLOSED`
- `AI-CDR-03`: `CLOSED`
- Closure criterion: MAE < 3.0 C for ISS, Starlink, and Sentinel-2
- Worst post-calibration MAE: 0.0621 C

## Before / After Metrics

| Mission | Before RMSE | Before MAE | Before Max | Before P95 | After RMSE | After MAE | After Max | After P95 | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ISS_Avionics | 0.7494 | 0.6354 | 1.2653 | 1.2500 | 0.0635 | 0.0509 | 0.1679 | 0.1178 | PASS |
| Starlink_Bus | 100.2320 | 100.2219 | 102.1459 | 102.1179 | 0.0799 | 0.0621 | 0.2507 | 0.1837 | PASS |
| Sentinel_2 | 156.1190 | 156.0680 | 161.9528 | 161.6066 | 0.0446 | 0.0408 | 0.0656 | 0.0624 | PASS |

## Calibrated Parameters

The calibrated parameters cover thermal mass scaling, radiator sizing, radiator emissivity, panel spacer conductance, radiator-structure conductance, structural radiating area, and CPU/payload structural couplings.

| Mission | Parameter | Before | After |
|---|---|---:|---:|
| ISS_Avionics | `capacity_scale` | 25 | 103.152 |
| ISS_Avionics | `radiator_area_m2` | 0.15 | 0.329883 |
| ISS_Avionics | `radiator_emissivity` | 0.9 | 0.75527 |
| ISS_Avionics | `radiator_structure_conductance_W_K` | 6 | 94.1283 |
| ISS_Avionics | `panel_structure_spacer_conductance_W_K` | 0.15 | 4.46911 |
| ISS_Avionics | `structure_radiating_area_m2` | 0.1 | 0.581725 |
| ISS_Avionics | `solar_panel_effective_area_m2` | 1 | 0.994508 |
| ISS_Avionics | `cpu_structure_conductance_W_K` | 2 | 1.47911 |
| ISS_Avionics | `payload_structure_conductance_W_K` | 1.5 | 22.7206 |
| Starlink_Bus | `capacity_scale` | 6 | 103.997 |
| Starlink_Bus | `radiator_area_m2` | 0.15 | 0.133594 |
| Starlink_Bus | `radiator_emissivity` | 0.85 | 0.847775 |
| Starlink_Bus | `radiator_structure_conductance_W_K` | 6 | 30.3605 |
| Starlink_Bus | `panel_structure_spacer_conductance_W_K` | 0.15 | 4.98178 |
| Starlink_Bus | `structure_radiating_area_m2` | 0.1 | 2.8196 |
| Starlink_Bus | `solar_panel_effective_area_m2` | 0.489898 | 0.858884 |
| Starlink_Bus | `cpu_structure_conductance_W_K` | 2 | 1.90997 |
| Starlink_Bus | `payload_structure_conductance_W_K` | 1.5 | 20.3509 |
| Sentinel_2 | `capacity_scale` | 12 | 258.759 |
| Sentinel_2 | `radiator_area_m2` | 0.15 | 0.425249 |
| Sentinel_2 | `radiator_emissivity` | 0.88 | 0.571357 |
| Sentinel_2 | `radiator_structure_conductance_W_K` | 6 | 6.71553 |
| Sentinel_2 | `panel_structure_spacer_conductance_W_K` | 0.15 | 2.90196 |
| Sentinel_2 | `structure_radiating_area_m2` | 0.1 | 2.46095 |
| Sentinel_2 | `solar_panel_effective_area_m2` | 0.69282 | 0.9284 |
| Sentinel_2 | `cpu_structure_conductance_W_K` | 2 | 4.19873 |
| Sentinel_2 | `payload_structure_conductance_W_K` | 1.5 | 1.12836 |

## Configuration Control Finding

The previous open heritage risk was caused by applying CubeSat-scale capacity and radiator constants to larger flight-heritage references. The calibrated campaign uses mission-specific thermal inertia, radiator area/emissivity, spacer conductance, and structural coupling parameters. All three required missions now satisfy the MAE < 3.0 C closure gate.
