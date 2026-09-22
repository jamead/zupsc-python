#!/usr/bin/env python3

import time
import epics
import matplotlib.pyplot as plt

channels = [1, 2, 3, 4]
read_order = [1, 2, 3, 4]

# Ramp settings
start = 0.0
stop = 1.0
steps = 300
rate_hz = 10.0

# Hold final value for this long
hold_seconds = 10.0

period = 1.0 / rate_hz


# --------------------------------------------------
# Create EPICS PV connections
# --------------------------------------------------

set_pvs = {}
read_pvs = {}

for ch in channels:

    set_pvs[ch] = epics.PV(
        f"lab{{1}}Chan{ch}:DAC_SetPt-SP"
    )

    read_pvs[ch] = epics.PV(
        f"lab{{1}}Chan{ch}:DAC-I"
    )


# --------------------------------------------------
# Wait for all PVs to connect
# --------------------------------------------------

print("Connecting to PVs...")

for ch in channels:

    if not set_pvs[ch].wait_for_connection(timeout=2.0):
        raise RuntimeError(
            f"Could not connect to {set_pvs[ch].pvname}"
        )

    if not read_pvs[ch].wait_for_connection(timeout=2.0):
        raise RuntimeError(
            f"Could not connect to {read_pvs[ch].pvname}"
        )

print("All PVs connected.")
print(f"Readback order = {read_order}")
print("Starting ramp...")


# --------------------------------------------------
# Storage
# --------------------------------------------------

times = []

setpoints = {
    ch: [] for ch in channels
}

readbacks = {
    ch: [] for ch in channels
}


# --------------------------------------------------
# Helper function to read all channels
# --------------------------------------------------

def read_all_channels():

    values = {}

    for ch in read_order:

        values[ch] = read_pvs[ch].get(
            timeout=0.05,
            use_monitor=False
        )

    return values


# --------------------------------------------------
# Ramp
# --------------------------------------------------

t0 = time.monotonic()

for i in range(steps + 1):

    target_time = t0 + i * period

    sleep_time = target_time - time.monotonic()

    if sleep_time > 0:
        time.sleep(sleep_time)


    setpoint = start + (stop - start) * i / steps


    # Write all four channels
    for ch in channels:
        set_pvs[ch].put(
            setpoint,
            wait=False
        )


    # Allow target/IOC readback to update
    time.sleep(0.03)

    epics.poll(
        evt=0.001,
        iot=0.001
    )


    # Read all four DAC readbacks
    channel_readbacks = read_all_channels()


    elapsed = time.monotonic() - t0

    times.append(elapsed)


    # Print every sample
    print(
        f"\nRAMP  "
        f"Time = {elapsed:7.4f} s   "
        f"Target = {i * period:7.4f} s"
    )

    for ch in channels:

        setpoints[ch].append(setpoint)
        readbacks[ch].append(channel_readbacks[ch])

        print(
            f"Chan{ch}:  "
            f"Setpoint = {setpoint:8.5f}   "
            f"Readback = {channel_readbacks[ch]:8.5f}"
        )


# --------------------------------------------------
# Ramp complete
# --------------------------------------------------

ramp_end_time = time.monotonic() - t0

print()
print("========================================")
print(f"Ramp complete at {ramp_end_time:.3f} s")
print(f"Holding setpoint at {stop:.6f}")
print(f"Hold time = {hold_seconds:.1f} s")
print("========================================")


# --------------------------------------------------
# Explicitly set all channels to final value once
# --------------------------------------------------

for ch in channels:
    set_pvs[ch].put(
        stop,
        wait=False
    )

epics.poll(
    evt=0.001,
    iot=0.001
)


# --------------------------------------------------
# Hold final setpoint and keep reading
# --------------------------------------------------

hold_samples = int(hold_seconds * rate_hz)

hold_t0 = time.monotonic()

for i in range(1, hold_samples + 1):

    target_time = hold_t0 + i * period

    sleep_time = target_time - time.monotonic()

    if sleep_time > 0:
        time.sleep(sleep_time)


    epics.poll(
        evt=0.001,
        iot=0.001
    )


    # Only read during hold
    # Do NOT keep rewriting the setpoint
    channel_readbacks = read_all_channels()


    elapsed = time.monotonic() - t0
    hold_elapsed = time.monotonic() - hold_t0

    times.append(elapsed)


    print(
        f"\nHOLD  "
        f"Time = {elapsed:7.4f} s   "
        f"Hold = {hold_elapsed:7.4f} s"
    )


    for ch in channels:

        setpoints[ch].append(stop)
        readbacks[ch].append(channel_readbacks[ch])

        error = stop - channel_readbacks[ch]

        print(
            f"Chan{ch}:  "
            f"Setpoint = {stop:8.5f}   "
            f"Readback = {channel_readbacks[ch]:8.5f}   "
            f"Error = {error:+9.6f}"
        )


# --------------------------------------------------
# Final results
# --------------------------------------------------

print()
print("========================================")
print("Final Readbacks")
print("========================================")

for ch in channels:

    final_value = readbacks[ch][-1]
    error = stop - final_value

    print(
        f"Chan{ch}:  "
        f"Setpoint = {stop:.6f}   "
        f"Readback = {final_value:.6f}   "
        f"Error = {error:+.6f}"
    )


# --------------------------------------------------
# Plot
# --------------------------------------------------

fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 8),
    sharex=True,
    sharey=True
)

axes = axes.flatten()

for i, ch in enumerate(channels):

    ax = axes[i]

    ax.plot(
        times,
        setpoints[ch],
        "-",
        label="Setpoint"
    )

    ax.plot(
        times,
        readbacks[ch],
        "-",
        label="Readback"
    )

    # Mark beginning of hold
    ax.axvline(
        ramp_end_time,
        linestyle="--",
        label="Hold begins"
    )

    ax.set_title(f"Channel {ch}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("DAC Value")
    ax.grid(True)
    ax.legend()


fig.suptitle(
    "DAC Ramp + Final Setpoint Hold",
    fontsize=14
)

plt.tight_layout()
plt.show()
