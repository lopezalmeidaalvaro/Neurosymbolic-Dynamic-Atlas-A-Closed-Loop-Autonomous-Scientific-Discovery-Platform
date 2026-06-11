# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - OpenMDAO System Group
# File: system.py
# Description: Couples orbital, power, sizing, and thermal components.
# ==============================================================================

try:
    import openmdao.api as om
except ImportError:

    class om:
        Group = object


from .components import (
    ThermalPredictorComponent,
    OrbitThermalCouplingComponent,
    RadiatorSizingComponent,
    PowerThermalCouplingComponent,
)


class SpacecraftThermalGroup(om.Group):
    """
    OpenMDAO Group combining orbital fluxes, electrical power, physical sizing,
    and steady-state thermal solvers into a unified MDO optimization workspace.
    """

    def setup(self):
        # 1. Add individual explicit components
        self.add_subsystem(
            "orbit",
            OrbitThermalCouplingComponent(),
            promotes_inputs=["altitude", "beta_angle"],
        )

        self.add_subsystem(
            "power_gen",
            PowerThermalCouplingComponent(),
            promotes_inputs=["voltage", "payload_current", "heater_current"],
        )

        self.add_subsystem(
            "sizing",
            RadiatorSizingComponent(),
            promotes_inputs=["thickness", "material_density"],
            promotes_outputs=["radiator_mass", "radiator_cost"],
        )

        self.add_subsystem(
            "thermal_solver",
            ThermalPredictorComponent(),
            promotes_inputs=["emissivity"],
            promotes_outputs=["max_temp", "time_to_critical", "thermal_margin"],
        )

        # 2. Connect intermediate variables between subsystems
        # Connect Orbit incident flux to the solver input
        self.connect("orbit.solar_flux", "thermal_solver.solar_flux")

        # Connect Power thermal dissipation to the solver input
        self.connect("power_gen.power", "thermal_solver.power")

        # Area is shared across sizing and solver. We promote it from both or link them
        # Let's connect sizing.area to solver.area and promote sizing.area to the Group level as 'area'
        self.add_design_var("sizing.area", lower=0.01, upper=0.50)
        self.connect("sizing.area", "thermal_solver.area")
