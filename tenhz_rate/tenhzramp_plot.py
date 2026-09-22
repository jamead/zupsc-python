#!/usr/bin/env python3

import subprocess
import time
import matplotlib.pyplot as plt

PV_SET = "lab{1}Chan1:DAC_SetPt-SP"
PV_READ = "lab{1}Chan1:DAC-I"

start = 0.0
stop = 5.0
steps = 500
rate_hz = 10.0

period = 1.0 / rate_hz

times = []
setpoints = []
readbacks = []

t0 = time.monotonic()

for i in range(steps + 1):

    # Generate ramp setpoint: 0.0, 0.1, ... 1.0
    setpoint = start + (stop - start) * i / steps

    # Write DAC setpoint
    subprocess.run(
        ["caput", "-t", PV_SET, str(setpoint)],
        check=True
    )

    # Read DAC actual value
    result = subprocess.check_output(
        ["caget", "-t", PV_READ],
        text=True
    )

    readback = float(result.strip())

    elapsed = time.monotonic() - t0

    times.append(elapsed)
    setpoints.append(setpoint)
    readbacks.append(readback)

    print(
        f"{elapsed:6.3f} s   "
        f"Setpoint = {setpoint:8.5f}   "
        f"Readback = {readback:8.5f}"
    )

    # Maintain approximately 10 Hz
    next_time = t0 + (i + 1) * period
    sleep_time = next_time - time.monotonic()

    if sleep_time > 0:
        time.sleep(sleep_time)


# --------------------------------------------------
# Plot
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    times,
    setpoints,
    "o-",
    label="DAC Setpoint"
)

plt.plot(
    times,
    readbacks,
    "o-",
    label="DAC Readback"
)

plt.xlabel("Time (s)")
plt.ylabel("DAC Value")
plt.title("10 Hz DAC Setpoint vs Readback")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()
