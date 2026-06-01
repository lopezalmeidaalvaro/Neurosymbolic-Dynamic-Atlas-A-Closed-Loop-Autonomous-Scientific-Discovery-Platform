#!/usr/bin/env python3
"""
Phase T32: COTS Material Library & Degradation Engine
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Database definition containing 10 COTS aerospace materials
MATERIALS_DB = {
    "Kapton HN": {
        "commercial_name": "DuPont Kapton HN Film",
        "eps_BOL": 0.80,
        "eps_EOL": 0.75,
        "alpha": 0.38,
        "uv_degradation_rate_per_year": 0.010,
        "atox_degradation_rate_per_fluence": 0.005,
        "relative_cost": 4,  # scale 1-10
        "density_kg_m2": 0.070,  # based on standard mil thickness
        "max_use_temp_C": 400.0,
        "min_use_temp_C": -269.0,
        "heritage": [
            "Hubble Space Telescope",
            "ISS",
            "James Webb Space Telescope",
            "Mars Pathfinder",
        ],
    },
    "Teflon FEP": {
        "commercial_name": "Sheldahl Teflon FEP Silvered",
        "eps_BOL": 0.85,
        "eps_EOL": 0.78,
        "alpha": 0.12,
        "uv_degradation_rate_per_year": 0.014,
        "atox_degradation_rate_per_fluence": 0.008,
        "relative_cost": 6,
        "density_kg_m2": 0.120,
        "max_use_temp_C": 200.0,
        "min_use_temp_C": -200.0,
        "heritage": ["ISS Radiators", "GPS Block II", "Voyager 1 & 2"],
    },
    "AZ-93 white paint": {
        "commercial_name": "AZ Technology AZ-93 Thermal Control Paint",
        "eps_BOL": 0.91,
        "eps_EOL": 0.86,
        "alpha": 0.15,
        "uv_degradation_rate_per_year": 0.010,
        "atox_degradation_rate_per_fluence": 0.002,
        "relative_cost": 7,
        "density_kg_m2": 0.250,  # paint dry thickness
        "max_use_temp_C": 150.0,
        "min_use_temp_C": -180.0,
        "heritage": [
            "Space Shuttle",
            "Mars Science Laboratory (Curiosity)",
            "Artemis Orion",
        ],
    },
    "Z306 black paint": {
        "commercial_name": "Aeroglaze Z306 Conductive Black Paint",
        "eps_BOL": 0.89,
        "eps_EOL": 0.89,  # stable
        "alpha": 0.95,
        "uv_degradation_rate_per_year": 0.000,  # highly stable
        "atox_degradation_rate_per_fluence": 0.001,
        "relative_cost": 5,
        "density_kg_m2": 0.180,
        "max_use_temp_C": 180.0,
        "min_use_temp_C": -150.0,
        "heritage": ["Hubble Baffles", "Cassini-Huygens spectrometer", "JWST interior"],
    },
    "Anodized aluminum 6061": {
        "commercial_name": "Anodized Aluminum 6061-T6 Structural Alloy",
        "eps_BOL": 0.70,  # can range 0.55-0.85 depending on thickness
        "eps_EOL": 0.65,
        "alpha": 0.45,
        "uv_degradation_rate_per_year": 0.010,
        "atox_degradation_rate_per_fluence": 0.003,
        "relative_cost": 2,
        "density_kg_m3": 2700.0,  # volumetric density
        "max_use_temp_C": 300.0,
        "min_use_temp_C": -200.0,
        "heritage": ["Cubesat standard structural bus", "Falcon 9 stages", "Skylab"],
    },
    "Germanium-coated Kapton": {
        "commercial_name": "Germanium Coated Kapton film (Intermediate)",
        "eps_BOL": 0.60,
        "eps_EOL": 0.55,
        "alpha": 0.42,
        "uv_degradation_rate_per_year": 0.010,
        "atox_degradation_rate_per_fluence": 0.004,
        "relative_cost": 8,
        "density_kg_m2": 0.075,
        "max_use_temp_C": 350.0,
        "min_use_temp_C": -250.0,
        "heritage": ["Galileo spacecraft", "Rosetta comet lander", "Envisat"],
    },
    "Quartz Mirror": {
        "commercial_name": "Optical Solar Reflector (OSR) Quartz Mirror",
        "eps_BOL": 0.10,  # low IR absorption/emission on front surface
        "eps_EOL": 0.12,
        "alpha": 0.05,
        "uv_degradation_rate_per_year": 0.004,
        "atox_degradation_rate_per_fluence": 0.001,
        "relative_cost": 10,
        "density_kg_m2": 0.450,
        "max_use_temp_C": 250.0,
        "min_use_temp_C": -150.0,
        "heritage": ["Geostationary telecom satellites radiators", "Rosetta"],
    },
    "Beta cloth": {
        "commercial_name": "Beta Cloth woven silica fabric",
        "eps_BOL": 0.90,
        "eps_EOL": 0.82,
        "alpha": 0.22,
        "uv_degradation_rate_per_year": 0.016,
        "atox_degradation_rate_per_fluence": 0.010,
        "relative_cost": 6,
        "density_kg_m2": 0.200,
        "max_use_temp_C": 650.0,  # extremely high thermal protection
        "min_use_temp_C": -200.0,
        "heritage": [
            "Apollo spacesuits",
            "Space Shuttle payload bay",
            "ISS outer covers",
        ],
    },
    "MLI 10-layer stack": {
        "commercial_name": "Multi-Layer Insulation 10-Layer Stack (Effective)",
        "eps_BOL": 0.03,  # eps_effective
        "eps_EOL": 0.05,
        "alpha": 0.14,
        "uv_degradation_rate_per_year": 0.004,
        "atox_degradation_rate_per_fluence": 0.002,
        "relative_cost": 9,
        "density_kg_m2": 0.350,
        "max_use_temp_C": 300.0,
        "min_use_temp_C": -200.0,
        "heritage": [
            "Almost all deep space and LEO missions",
            "James Webb",
            "Mars Rovers",
        ],
    },
    "Graphite epoxy composite": {
        "commercial_name": "High-Modulus Graphite Epoxy Composite Panel",
        "eps_BOL": 0.85,
        "eps_EOL": 0.82,
        "alpha": 0.88,
        "uv_degradation_rate_per_year": 0.006,
        "atox_degradation_rate_per_fluence": 0.002,
        "relative_cost": 8,
        "density_kg_m3": 1600.0,
        "max_use_temp_C": 120.0,  # epoxy limits
        "min_use_temp_C": -100.0,
        "heritage": [
            "Chandra X-ray Observatory structure",
            "Mars Express",
            "Cubesat structures",
        ],
    },
}


def get_material(name):
    """
    Returns the complete physical property dictionary for a given material.
    """
    if name not in MATERIALS_DB:
        raise ValueError(f"Material '{name}' not found in the COTS library.")
    return MATERIALS_DB[name]


def get_material_for_temperature(T_max, T_min):
    """
    Filters and suggests materials that can operate within the requested temperature limits.
    """
    compatible = []
    for name, props in MATERIALS_DB.items():
        if props["max_use_temp_C"] >= T_max and props["min_use_temp_C"] <= T_min:
            compatible.append(name)
    return compatible


def get_material_by_cost(max_cost):
    """
    Filters and returns materials whose relative cost is below or equal to max_cost (1-10).
    """
    return [
        name
        for name, props in MATERIALS_DB.items()
        if props["relative_cost"] <= max_cost
    ]


def apply_material(
    network, node_index, material_name, elapsed_time_years=0.0, atox_fluence=0.0
):
    """
    Applies the material's properties (emissivity and solar absorption) to a specific network node,
    accounting for environmental degradation (UV exposure and atomic oxygen ATOX).
    """
    props = get_material(material_name)

    # Calculate degraded emissivity
    uv_deg = elapsed_time_years * props["uv_degradation_rate_per_year"]
    atox_deg = atox_fluence * props["atox_degradation_rate_per_fluence"]

    # For standard materials, UV and ATOX decrease/increase emissivity.
    # In space, emissivity degrades (usually drops) due to solar radiation.
    # Let's model the drop, bounded by EOL value
    eps_degraded = props["eps_BOL"] - (uv_deg + atox_deg)

    # Bound by EOL
    if props["eps_BOL"] >= props["eps_EOL"]:
        eps_degraded = max(props["eps_EOL"], eps_degraded)
    else:
        eps_degraded = min(props["eps_EOL"], eps_degraded)

    # Apply to network
    network.eps[node_index] = eps_degraded

    # We can also track properties in a custom metadata dict on the network object
    if not hasattr(network, "node_materials"):
        network.node_materials = {}
    network.node_materials[node_index] = {
        "name": material_name,
        "eps_BOL": props["eps_BOL"],
        "eps_degraded": eps_degraded,
        "alpha": props["alpha"],
    }

    return eps_degraded


def compare_materials(material_list, scenario_name="LEO Nominal"):
    """
    Generates a comparative analysis table and exports the comparison report.
    """
    records = []
    for name in material_list:
        p = get_material(name)
        records.append(
            {
                "Material": name,
                "Nombre Comercial": p["commercial_name"],
                "ε BOL": p["eps_BOL"],
                "ε EOL": p["eps_EOL"],
                "α (Solar)": p["alpha"],
                "Deg. UV /año": p["uv_degradation_rate_per_year"],
                "Coste (1-10)": p["relative_cost"],
                "Límite Temp Max": f"{p['max_use_temp_C']}°C",
                "Uso Recomendado": (
                    "Radiadores"
                    if p["alpha"] < 0.2
                    else (
                        "Aislamiento MLI"
                        if p["eps_BOL"] < 0.05
                        else "Estructura/Interior"
                    )
                ),
            }
        )
    df = pd.DataFrame(records)
    return df


def save_database_to_json(filepath):
    """
    Saves the MATERIALS_DB to a beautiful, formatted JSON file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(MATERIALS_DB, f, indent=4)
    print(f"[+] Base de datos de materiales guardada en: {filepath}")


def generate_report():
    """
    Generates the material comparison Markdown report detailing BOL, EOL, and Space Heritage.
    """
    report_path = "satellite/thermal/material_comparison_report.md"

    report_lines = [
        "# Biblioteca de Materiales COTS Aeroespaciales y Envejecimiento (Fase T32)\n\n",
        f"**Generado:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | **Base de Datos:** COTS-MAT-V1.0\n\n",
        "Este informe describe la biblioteca de materiales espaciales comerciales (COTS) desarrollada para sustituir los parámetros abstractos del modelo térmico por recubrimientos físicos reales con perfiles de degradación BOL/EOL por radiación ultravioleta (UV) y oxígeno atómico (ATOX).\n\n",
        "## 1. Biblioteca Completa de Materiales Aeroespaciales\n\n",
        "| Material | Nombre Comercial | ε BOL | ε EOL | α Solar | Deg. UV/año | Coste (1-10) | Heritage Destacado |\n",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n",
    ]

    for name, p in MATERIALS_DB.items():
        heritage_str = ", ".join(p["heritage"][:2]) + "..."
        report_lines.append(
            f"| **{name}** | {p['commercial_name']} | {p['eps_BOL']:.2f} | {p['eps_EOL']:.2f} | {p['alpha']:.2f} | "
            f"{p['uv_degradation_rate_per_year']:.3f} | {p['relative_cost']} | {heritage_str} |\n"
        )

    report_lines.extend(
        [
            "\n## 2. Recomendaciones de Materiales por Región Térmica\n\n",
            "### A. Disipación Activa (Radiadores Externos)\n",
            "- **Recomendado**: **Teflon FEP** o **AZ-93 white paint**.\n",
            "- **Razón**: Poseen una relación solar $\\alpha/\\epsilon$ extremadamente baja (AZ-93: $\\alpha=0.15, \\epsilon=0.91$), lo que minimiza la absorción del calor solar mientras maximiza la emisión de radiación infrarroja hacia el espacio profundo.\n\n",
            "### B. Aislamiento de Instrumentación Sensible (CPU/Batería)\n",
            "- **Recomendado**: **MLI 10-layer stack**.\n",
            "- **Razón**: La emisividad efectiva extremadamente baja ($\\epsilon_{\\text{eff}} = 0.03$) aísla los componentes críticos del frío extremo orbital y las fluctuaciones transitorias.\n\n",
            "### C. Superficies Internas y Blindajes de Acoplamiento\n",
            "- **Recomendado**: **Z306 black paint**.\n",
            "- **Razón**: Posee una alta emisividad estable ($\\epsilon=0.89$) y nula degradación por UV al estar protegido en el interior del chasis. Maximiza la transferencia de calor por radiación entre la CPU y la estructura interna.\n\n",
            "## 3. Modelo de Degradación Espacial Integrado\n\n",
            "> [!IMPORTANT]\n",
            "> **Fórmula de Envejecimiento Dinámico (BOL -> EOL):**\n",
            "> El modelo calcula la emisividad efectiva en órbita en base a la fluencia acumulada de oxígeno atómico y el tiempo de exposición UV:\n",
            "> $$\\epsilon(t) = \\max\\left(\\epsilon_{\\text{EOL}},\\ \\epsilon_{\\text{BOL}} - t \\cdot \\Delta\\epsilon_{\\text{UV}} - F_{\\text{ATOX}} \\cdot \\Delta\\epsilon_{\\text{ATOX}}\\right)$$\n",
            "> Esto permite al Gemelo Digital predecir la pérdida de capacidad de los radiadores en misiones prolongadas (hasta 5 años LEO).\n",
        ]
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("".join(report_lines))
    print(f"[+] Informe de comparación de materiales guardado en: {report_path}")


def main():
    print("======================================================================")
    print("           Phase T32: COTS Material Library & Degradation Engine      ")
    print("======================================================================\n")

    # Save the database
    json_path = "satellite/thermal/material_library.json"
    save_database_to_json(json_path)

    # Generate the Markdown report
    generate_report()


if __name__ == "__main__":
    main()
