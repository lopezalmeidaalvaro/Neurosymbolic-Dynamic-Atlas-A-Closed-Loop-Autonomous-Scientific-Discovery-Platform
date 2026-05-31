# Theory Autowriter Demo

## Lagrangian

`-g_chi*chi(t) - g_phi*phi(t) - lambda_chi*chi(t)**4/24 - lambda_phi*phi(t)**4/24 - m_chi**2*chi(t)**2/2 - m_phi**2*phi(t)**2/2 + Derivative(chi(t), t)**2/2 + Derivative(phi(t), t)**2/2`

## Equations Of Motion

- `phi`: `-g_phi - lambda_phi*phi(t)**3/6 - m_phi**2*phi(t) - Derivative(phi(t), (t, 2))`
- `chi`: `-g_chi - lambda_chi*chi(t)**3/6 - m_chi**2*chi(t) - Derivative(chi(t), (t, 2))`

## Consistency

```json
{
  "stability": false,
  "symmetry_ok": false,
  "minimum_action_form": true,
  "passed": false
}
```

## Predictions

- Small oscillation residual for phi should remain below 0.1 under normalized perturbation. Falsification: `residual_mse > 0.1`
- Small oscillation residual for chi should remain below 0.1 under normalized perturbation. Falsification: `residual_mse > 0.1`

## Validation

```json
{
  "valid": true,
  "sanity": {
    "hypothesis": "Generated scalar-field MVP theory has falsable small-oscillation predictions.",
    "score": 0.8,
    "accepted": true,
    "checks": {
      "structure": {
        "passed": true,
        "warnings": []
      },
      "math": {
        "passed": true,
        "simplified": "-g_phi - lambda_phi*phi*t**3/6 - m_phi**2*phi*t",
        "warnings": []
      },
      "dimensions": {
        "passed": true,
        "warnings": [
          "no_units_provided"
        ]
      },
      "boundedness": {
        "passed": false,
        "min": null,
        "max": null,
        "warnings": [
          "evaluation_error: Cannot convert expression to float"
        ]
      },
      "conservation": {
        "passed": true,
        "warnings": [
          "unknown_system_type: unknown"
        ],
        "overlap": null
      }
    }
  },
  "claim_level": {
    "level": 1,
    "label": "speculative",
    "text": "Generated scalar-field MVP theory has falsable small-oscillation predictions."
  }
}
```

## Limitations

- MVP only.
- Solo campos escalares.
- Sin cuantización.
- Sin loops.
- No claims beyond simulation-supported symbolic consistency.
