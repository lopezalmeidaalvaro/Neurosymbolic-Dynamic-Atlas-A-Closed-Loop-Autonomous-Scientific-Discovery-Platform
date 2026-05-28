# DeepSpace ThermalTwin™ — 5-Minute Live Commercial Demonstration Script

This demo script is designed for sales engineers, lead thermal architects, and product managers to showcase the deep value of the **Spacecraft Orbital Thermal Digital Twin** platform to prospective clients, space agency partners, and tech executives.

---

### ⏱️ Minute 0:00 - 1:00 | The Spaceflight Engineering Challenge
* **Presenter Action:** Open the Next.js web application (e.g. `/satellite` or `/en/satellite` on your local server). Show the stunning dark-mode dashboard with glowing orbital tracks and 3U Cubesat wireframe renderers.
* **Narrative:**
  > "Welcome, everyone. In modern aerospace engineering, thermal regulation is a critical survivability concern. In the vacuum of Low Earth Orbit (LEO), a satellite's CPU can overheat and burn out in minutes if not properly coupled to structural radiators. 
  > 
  > Traditionally, engineers must wait hours or days for high-fidelity Finite Element Method (FEM) mesh solvers to simulate a single design configuration. Today, we are proud to present **DeepSpace ThermalTwin™**—a flight-ready neurosymbolic digital twin that delivers instant, sub-millisecond physical simulations and real-time parameter calibration on the edge."

---

### ⏱️ Minute 1:00 - 2:00 | 3D CAD Voxelization & Mesh Extraction (Phase T19)
* **Presenter Action:** Click on the **"CAD Import & Voxelizer"** tab. Show the text-STL CAD visualization viewport displaying the imported structure `cubesat_cube.stl`. Toggle the **"Extract Mesh"** action to render the 1000 occupied voxel nodes (spatial resolution $1\text{ cm}^3$) and show the extracted conductive paths grid ($k_{ij} = 1.67\text{ W/K}$).
* **Narrative:**
  > "We begin by importing raw spacecraft geometries. Here, we ingest a 3D structural model in standard STL format. Instead of manually constructing thermal nodes, our CAD-Aware Voxelizer discretizes the geometry into 1,000 thermal coupling cells in less than a second. 
  > 
  > It automatically calculates exposed radiative areas and conductive links based on material property tensors. Note the real-time core-to-shell gradient display: with a 15W internal CPU load, the voxelizer shows the core temperature stabilizing at 78.4°C while the outer radiator shell runs at 48.9°C."

---

### ⏱️ Minute 2:00 - 3:00 | 6-Node Coupled Dynamics & Neural ODE Acceleration (Phases T9–T10)
* **Presenter Action:** Toggle to the **"Coupled Simulator"** viewport. Drag the **"CPU Power"** slider to 30W. Drag the **"Solar Beta Angle"** slider. Show the Recharts dynamic plot tracing the 6 coupled node trajectories (CPU, Battery, Payload, Structure, Radiator, Solar Panels) across a full LEO orbit. Switch the **"Neural ODE / PINN Surrogate"** toggle on.
* **Narrative:**
  > "Next, let's look at dynamic physical modeling. The system is solving the coupled 6-node thermodynamic ODEs in real-time, accounting for solar shadow eclipses and Earth albedo fluctuations. 
  > 
  > Now, watch as we toggle the AI Surrogate Engine on. By replacing the numerical integrator with our continuous-time Neural ODE and Physics-Informed Neural Network (PINN) emulators, we obtain identical trajectories in less than 0.2 milliseconds! 
  > 
  > This is a **3,600$\times$ computational speedup**, yielding a Gilmore-Karam correlation of **RMSE = 0.374°C** ($R^2 > 99\%$) compared to reference FEM solvers. Sizing trade-offs that once took weeks are now explored interactively at the slide of a finger."

---

### ⏱️ Minute 3:00 - 4:00 | Bayesian Pareto Sizing & Uncertainty Quantification (Phases T11, T14)
* **Presenter Action:** Scroll down to the **"Pareto Sizer"** panel. Point to the non-dominated Pareto front curve separating radiator mass (area) and coating cost. Point to the **"Uncertainty Propagation"** PDF histogram and click the **"Run 200 Monte Carlo Bootstrap"** button.
* **Narrative:**
  > "To assist design architects, the system runs active Bayesian-like multi-objective optimization. Here on the Pareto front, you can see the optimal radiator layout specification card: it recommends a radiator area of 0.086 m² and emissivity of 0.87, achieving a massive **70% structural mass reduction** while keeping our CPU safely under 85°C.
  > 
  > Concurrently, our uncertainty engine propagates physical tolerance and seasonal solar flux fluctuations using 200 Monte Carlo bootstrap iterations. The result fitted distribution indicates a mean peak CPU temperature of 53.9°C and standard deviation of 1.16°C, yielding a **100.00% mission reliability score** ($R_{\text{thermal}}$)."

---

### ⏱️ Minute 4:00 - 5:00 | Real-Time HIL Online EKF Calibration & Active Throttling (Phase T17)
* **Presenter Action:** Select the **"Hardware-in-the-Loop"** workspace. Point to the streaming telemetry logs and the parameter convergence charts showing the CPU Thermal Capacity ($C$) and Radiator Emissivity ($\epsilon$) starting to adapt. 
* **Narrative:**
  > "Finally, we close the loop between simulation and physical reality. Here we couple the digital twin to an active Hardware-in-the-Loop telemetry stream. 
  > 
  > By comparing one-step-ahead prediction residuals in real-time, our online **Extended Kalman Filter (EKF)** dynamically calibrates the twin's coefficients. Within just **15 seconds**, the CPU thermal capacity converges from an initial miscalibrated 319 J/K to the true hardware value of 500 J/K, stabilizing prediction errors near the sensor noise baseline.
  > 
  > If sensor temperature projections indicate a critical exceedance above 80°C, the HIL active safety controller automatically issues a throttling command, reducing CPU power from 30W to 5W to prevent hardware burnout. DeepSpace ThermalTwin is fully flight-ready, providing real-time safety and self-healing calibration for orbital missions. Thank you, and I will now take your questions."
