import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft, fftfreq
import json
import os

def duffing(t, state):
    x, y = state
    dxdt = y
    # x'' + 0.3x' - x + x^3 = 0.5*cos(1.2*t)
    # y' = -0.3y + x - x^3 + 0.5*cos(1.2*t)
    dydt = x - x**3 - 0.3*y + 0.5*np.cos(1.2*t)
    return [dxdt, dydt]

def main():
    # 1. Integrate and discard transient
    t_span = (0, 2000)
    t_eval = np.linspace(0, 2000, 200000)
    
    # solve_ivp uses RK45 by default
    sol = solve_ivp(duffing, t_span, [0.1, 0.0], t_eval=t_eval, method='RK45')

    # Discard transient (e.g., first 500 time units)
    dt = t_eval[1] - t_eval[0]
    transient_idx = int(500 / dt)
    t_steady = sol.t[transient_idx:]
    x_steady = sol.y[0, transient_idx:]
    y_steady = sol.y[1, transient_idx:]

    # 2. Variance
    variance = np.var(x_steady)

    # 3. Dominant frequency
    N = len(t_steady)
    yf = fft(x_steady)
    xf = fftfreq(N, dt)[:N//2]
    # Exclude the DC component (frequency 0)
    power = np.abs(yf[0:N//2])
    power[0] = 0 # zero out DC component
    dominant_freq = xf[np.argmax(power)]

    # 4. Simple Maximum Lyapunov Exponent
    # Two-trajectories method with renormalization
    t_lyap = np.linspace(500, 2000, 15000)
    dt_lyap = t_lyap[1] - t_lyap[0]
    state = np.array([x_steady[0], y_steady[0]])
    d0 = 1e-8
    pert = np.array([d0, 0.0])
    state_pert = state + pert

    lyap_sum = 0.0
    iters = 0

    for i in range(len(t_lyap)-1):
        t_start = t_lyap[i]
        t_end = t_lyap[i+1]
        
        sol1 = solve_ivp(duffing, (t_start, t_end), state, method='RK45', rtol=1e-8, atol=1e-8)
        sol2 = solve_ivp(duffing, (t_start, t_end), state_pert, method='RK45', rtol=1e-8, atol=1e-8)
        
        state = sol1.y[:, -1]
        state_pert = sol2.y[:, -1]
        
        diff = state_pert - state
        d1 = np.linalg.norm(diff)
        
        if d1 > 0:
            lyap_sum += np.log(d1 / d0)
            state_pert = state + diff * (d0 / d1)
        iters += 1

    lyap_max = lyap_sum / (iters * dt_lyap)

    result = {
        "lyapunov_max": float(lyap_max),
        "dominant_frequency": float(dominant_freq),
        "variance": float(variance)
    }

    # Print to console
    print(json.dumps(result, indent=4))

    # Save to file
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/duffing_signature.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()
