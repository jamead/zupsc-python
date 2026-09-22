#!/usr/bin/env python3

import subprocess
import time

PV = "lab{1}Chan1:DAC_SetPt-SP"

start = 0.0
stop = 1.0
steps = 100
rate_hz = 10.0

delay = 1.0 / rate_hz

for i in range(steps + 1):
    value = start + (stop - start) * i / steps

    print(f"{PV} = {value:.3f}")

    subprocess.run(
        ["caput", PV, f"{value:.3f}"],
        check=True
    )

    if i < steps:
        time.sleep(delay)

print("Ramp complete.")
