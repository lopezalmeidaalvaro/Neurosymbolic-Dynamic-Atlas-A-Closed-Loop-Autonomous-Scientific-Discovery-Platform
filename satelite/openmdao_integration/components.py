# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - OpenMDAO Components
# File: components.py
# Description: Defines explicit components with mathematical derivative formulations.
# ==============================================================================

import numpy as np

try:
    import openmdao.api as om
except ImportError:
    # Safe mock implementation if openmdao is not installed in the execution sandbox
    class MOCK_ExplicitComponent:
        def __init__(self, *args, **kwargs):
            pass

        def add_input(self, *args, **kwargs):
            pass

        def add_output(self, *args, **kwargs):
            pass

        def declare_partials(self, *args, **kwargs):
            pass

    class om:
        ExplicitComponent = MOCK_ExplicitComponent
        Group = object


class ThermalPredictorComponent(om.ExplicitComponent):
    """
    Computes steady-state and peak transient temperatures based on radiator size,
    surface emissivity, and CPU electrical power dissipation.
    """

    def setup(self):
        # Inputs
        self.add_input("power", val=15.0, desc="Internal power dissipation in Watts")
        self.add_input("area", val=0.15, desc="Radiator area in m²")
        self.add_input("emissivity", val=0.85, desc="Radiator surface emissivity")
        self.add_input("solar_flux", val=1361.0, desc="Solar flux incident in W/m²")

        # Outputs
        self.add_output(
            "max_temp", val=20.0, desc="Predicted CPU maximum temperature in °C"
        )
        self.add_output(
            "time_to_critical", val=-1.0, desc="Time before CPU limits (seconds)"
        )
        self.add_output("thermal_margin", val=10.0, desc="CPU thermal margin in °C")

        # Finite-difference derivatives for dynamic transient forecasting
        self.declare_partials(
            "max_temp", ["power", "area", "emissivity", "solar_flux"], method="fd"
        )
        self.declare_partials(
            "time_to_critical", ["power", "area", "emissivity"], method="fd"
        )

        # Analytical derivatives for safety margin: margin = 85.0 - max_temp
        self.declare_partials("thermal_margin", "power")
        self.declare_partials("thermal_margin", "area")
        self.declare_partials("thermal_margin", "emissivity")

    def compute(self, inputs, outputs):
        power = float(inputs["power"])
        area = float(inputs["area"])
        emissivity = float(inputs["emissivity"])
        solar_flux = float(inputs["solar_flux"])

        # Stefan-Boltzmann constant
        sigma = 5.67e-8
        T_space = 3.0  # Background cosmic temperature in Kelvin

        # Simplified orbital balance steady-state equation
        # Q_in = power + absorb * solar_flux * area (assumed solar absorption = 0.20)
        q_in = power + 0.20 * solar_flux * area

        # Radiation out = emissivity * sigma * area * (T^4 - T_space^4)
        t_kelvin = (q_in / (emissivity * sigma * area + 1e-12) + T_space**4) ** 0.25
        t_celsius = t_kelvin - 273.15

        # Soft transient scaling for CPU peak forecast
        outputs["max_temp"] = t_celsius

        # Safe thermal limits margin
        cpu_limit = 85.0
        margin = cpu_limit - t_celsius
        outputs["thermal_margin"] = margin

        # Compute time to critical limit
        if t_celsius >= cpu_limit:
            outputs["time_to_critical"] = 0.0
        else:
            # Derived transient heating constant
            heat_capacity = 500.0
            outputs["time_to_critical"] = (heat_capacity * (cpu_limit - t_celsius)) / (
                power + 1e-6
            )

    def compute_partials(self, inputs, partials):
        power = float(inputs["power"])
        area = float(inputs["area"])
        emissivity = float(inputs["emissivity"])
        solar_flux = float(inputs["solar_flux"])

        sigma = 5.67e-8
        T_space = 3.0

        q_in = power + 0.20 * solar_flux * area
        t_kelvin = (q_in / (emissivity * sigma * area + 1e-12) + T_space**4) ** 0.25

        # d(Temp_C)/d(power) = d(Temp_K)/d(power)
        # Temp_K = X^0.25 -> d(Temp_K) = 0.25 * X^-0.75 * dX
        # dX/dPower = 1 / (eps * sigma * Area)
        x_val = q_in / (emissivity * sigma * area) + T_space**4
        dt_dx = 0.25 * (x_val ** (-0.75))

        dx_dpower = 1.0 / (emissivity * sigma * area)
        dt_dpower = dt_dx * dx_dpower

        # dX/dArea = -Power / (eps * sigma * Area^2) + 0.20 * solar_flux / (eps * sigma * Area) (approx)
        # Using exact differential quotients:
        dx_darea = (
            0.20 * solar_flux * (emissivity * sigma * area)
            - q_in * (emissivity * sigma)
        ) / ((emissivity * sigma * area) ** 2)
        dt_darea = dt_dx * dx_darea

        dx_demissivity = -q_in * (sigma * area) / ((emissivity * sigma * area) ** 2)
        dt_demissivity = dt_dx * dx_demissivity

        # Margins derivatives are the negative of temp derivatives: d(margin)/dx = -d(temp)/dx
        partials["thermal_margin", "power"] = -dt_dpower
        partials["thermal_margin", "area"] = -dt_darea
        partials["thermal_margin", "emissivity"] = -dt_demissivity


class OrbitThermalCouplingComponent(om.ExplicitComponent):
    """
    Evaluates incident external solar fluxes based on altitude and shadow eclipse angles.
    """

    def setup(self):
        # Inputs
        self.add_input("altitude", val=500.0, desc="LEO altitude in km")
        self.add_input("beta_angle", val=30.0, desc="Orbit beta angle in degrees")

        # Outputs
        self.add_output(
            "solar_flux", val=1361.0, desc="Net incident solar flux in W/m²"
        )
        self.add_output("eclipse_fraction", val=0.35, desc="Shadow fraction of orbit")

        self.declare_partials("solar_flux", ["altitude", "beta_angle"], method="fd")
        self.declare_partials(
            "eclipse_fraction", ["altitude", "beta_angle"], method="fd"
        )

    def compute(self, inputs, outputs):
        altitude = float(inputs["altitude"])
        beta_angle = float(inputs["beta_angle"])

        # Solar constant
        S0 = 1361.0

        # Approximate shadow fraction based on geometry
        # Earth radius R_e = 6378 km
        Re = 6378.1
        r_orbit = Re + altitude

        # Shadow angle
        arg = Re / r_orbit
        if arg > 1.0:
            arg = 1.0
        shadow_angle_rad = np.arcsin(arg)

        # Scale eclipse fraction with beta angle
        beta_rad = np.radians(beta_angle)
        if np.abs(beta_rad) >= shadow_angle_rad:
            # Orbit is in constant daylight (no eclipse)
            eclipse = 0.0
        else:
            # Shadow fraction decreases as beta angle approaches maximum shadow limit
            eclipse = (2.0 * np.arccos(np.cos(shadow_angle_rad) / np.cos(beta_rad))) / (
                2.0 * np.pi
            )

        outputs["eclipse_fraction"] = eclipse

        # Bounded incident average solar flux
        outputs["solar_flux"] = S0 * (1.0 - eclipse)


class RadiatorSizingComponent(om.ExplicitComponent):
    """
    Calculates physical panel mass and structural manufacturing cost based on thickness
    and material density.
    """

    def setup(self):
        # Inputs
        self.add_input("area", val=0.15, desc="Radiator area in m²")
        self.add_input(
            "thickness", val=0.002, desc="Panel thickness in meters (Nominal: 2mm)"
        )
        self.add_input(
            "material_density",
            val=2700.0,
            desc="Material density in kg/m³ (Aluminium: 2700)",
        )

        # Outputs
        self.add_output(
            "radiator_mass", val=0.81, desc="Computed structural mass in kg"
        )
        self.add_output("radiator_cost", val=2000.0, desc="Manufacturing cost in USD")

        # Analytical derivatives
        self.declare_partials(
            "radiator_mass", ["area", "thickness", "material_density"]
        )
        self.declare_partials("radiator_cost", ["area"])

    def compute(self, inputs, outputs):
        area = float(inputs["area"])
        thickness = float(inputs["thickness"])
        density = float(inputs["material_density"])

        # Mass = Area * Thickness * Density
        outputs["radiator_mass"] = area * thickness * density

        # Cost function: structural base cost + area scaling ($8000 per m²)
        outputs["radiator_cost"] = 500.0 + 8000.0 * area

    def compute_partials(self, inputs, partials):
        area = float(inputs["area"])
        thickness = float(inputs["thickness"])
        density = float(inputs["material_density"])

        # Derivatives for Mass
        partials["radiator_mass", "area"] = thickness * density
        partials["radiator_mass", "thickness"] = area * density
        partials["radiator_mass", "material_density"] = area * thickness

        # Derivatives for Cost
        partials["radiator_cost", "area"] = 8000.0


class PowerThermalCouplingComponent(om.ExplicitComponent):
    """
    Couples spacecraft electrical power management with localized thermal power dissipation.
    """

    def setup(self):
        # Inputs
        self.add_input("voltage", val=28.0, desc="Bus voltage in V")
        self.add_input(
            "payload_current", val=0.5, desc="Optics/payload current in Amperes"
        )
        self.add_input(
            "heater_current", val=0.2, desc="Active heater current in Amperes"
        )

        # Outputs
        self.add_output(
            "power", val=15.0, desc="Total electrical power to dissipate as heat in W"
        )

        # Analytical derivatives
        self.declare_partials("power", ["voltage", "payload_current", "heater_current"])

    def compute(self, inputs, outputs):
        voltage = float(inputs["voltage"])
        payload_c = float(inputs["payload_current"])
        heater_c = float(inputs["heater_current"])

        # Power = Voltage * (Payload_Current + Heater_Current) + CPU baseline (5W)
        outputs["power"] = 5.0 + voltage * (payload_c + heater_c)

    def compute_partials(self, inputs, partials):
        voltage = float(inputs["voltage"])
        payload_c = float(inputs["payload_current"])
        heater_c = float(inputs["heater_current"])

        partials["power", "voltage"] = payload_c + heater_c
        partials["power", "payload_current"] = voltage
        partials["power", "heater_current"] = voltage
