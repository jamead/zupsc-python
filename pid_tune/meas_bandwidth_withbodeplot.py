import cothread
import epics
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

datapts = 100000


def get_waveform(PVs, numpts):
    data = []

    for pv in PVs:
        data.append(pv.get())

    waveform = np.asarray(data, dtype=np.float32)
    waveform = waveform[:, 0:numpts]

    return waveform


def wait_snapshot(trig_pv, wfmrdy_pv):
    # Trigger the snapshot
    trig_pv.put(1)
    print("Triggering Snapshot...")
    time.sleep(1)

    print("Waiting for Snapshot Data...")

    while True:
        val = wfmrdy_pv.get()
        time.sleep(1)

        if val == 0:
            break

    print("Transfer Complete")


def plot_snapshot(snapshot_data, freq, ax):
    dac = snapshot_data[:, 0]
    dcct1 = snapshot_data[:, 1]
    dcct2 = snapshot_data[:, 2]

    label = f"{freq:.0f} Hz"

    ax[0].plot(dac, label=label)
    ax[0].set_ylabel("DAC")
    ax[0].grid(True)

    ax[1].plot(dcct1, label=label)
    ax[1].set_ylabel("DCCT1")
    ax[1].grid(True)

    ax[2].plot(dcct2, label=label)
    ax[2].set_ylabel("DCCT2")
    ax[2].grid(True)


def main():
    parser = argparse.ArgumentParser(
        description="Measure the frequency response of a PSC power supply."
    )

    parser.add_argument(
        "psc_prefix",
        type=str,
        help="PSC prefix string, for example lab{1}"
    )

    parser.add_argument(
        "outfile",
        type=str,
        help="Output filename, for example psc_snapshot.txt"
    )

    args = parser.parse_args()

    psc_prefix = args.psc_prefix
    out_filename = args.outfile

    snapshot_pv = [
        epics.PV(psc_prefix + "Chan1:USR:DAC-Wfm"),
        epics.PV(psc_prefix + "Chan1:USR:DCCT1-Wfm"),
        epics.PV(psc_prefix + "Chan1:USR:DCCT2-Wfm"),
    ]

    # Get PV names
    dds_enb_pv = epics.PV(psc_prefix + "Chan1:DAC-DDS-Enb-SP")
    dds_freq_pv = epics.PV(psc_prefix + "Chan1:DAC-DDS-Freq-SP")
    trig_pv = epics.PV(psc_prefix + "Chan1:SS:Trig:Usr")
    dac_setpt_pv = epics.PV(psc_prefix + "Chan1:DAC_SetPt-SP")
    pid_rst_int_pv = epics.PV(psc_prefix + "Chan1:DPIDResetI-SP")
    kp_pv = epics.PV(psc_prefix + "Chan1:Kp-SP")
    ki_pv = epics.PV(psc_prefix + "Chan1:Ki-SP")
    wfmrdy_pv = epics.PV(psc_prefix + "Chan1:UsrTrigActive-I")

    # Snapshot waveform plots
    fig, ax = plt.subplots(
        3,
        1,
        sharex=True,
        figsize=(12, 8)
    )

    ki = 0.01
    kp = 0.5

    # Initialize DPID
    pid_rst_int_pv.put(1)
    kp_pv.put(kp)
    ki_pv.put(ki)
    dac_setpt_pv.put(0)

    # Store frequency-response measurements
    frequencies = []
    dac_max_values = []
    dcct1_max_values = []
    dcct2_max_values = []
    gain_values = []

    snapshot_data = None

    frequencies_to_test = np.concatenate((
       np.arange(1.0, 20.0, 1.0),    # 1 Hz steps
       np.arange(20.0, 50.0, 2.0),    # 2 Hz steps
       np.arange(50.0, 100.0, 5.0),   # 5 Hz steps
       np.arange(100.0, 500.0, 10.0),  # 10 Hz steps
))

    for freq in frequencies_to_test:
        print(f"\nSetting DDS frequency to {freq:.0f} Hz")

        dds_freq_pv.put(freq)
        time.sleep(1)

        wait_snapshot(trig_pv, wfmrdy_pv)
        time.sleep(1)

        # Read waveform. Initial shape is:
        #     number_of_waveforms x number_of_samples
        snapshot_data = get_waveform(snapshot_pv, datapts)

        # Change shape to:
        #     number_of_samples x number_of_waveforms
        snapshot_data = snapshot_data.T

        # Use all 100,000 samples
        snapshot_data = snapshot_data[0:100000, :]

        dac = snapshot_data[:, 0]
        dcct1 = snapshot_data[:, 1]
        dcct2 = snapshot_data[:, 2]

        # Maximum absolute waveform values
        dac_max = np.max(np.abs(dac))
        dcct1_max = np.max(np.abs(dcct1))
        dcct2_max = np.max(np.abs(dcct2))

        # Requested frequency-response ratio
        if dac_max != 0:
            #gain = dcct2_max / dac_max 
            gain_db = 20.0 * np.log10(dcct2_amplitude / dac_amplitude)
        else:
            gain = np.nan
            print("Warning: DCCT2 maximum is zero.")

        frequencies.append(freq)
        dac_max_values.append(dac_max)
        dcct1_max_values.append(dcct1_max)
        dcct2_max_values.append(dcct2_max)
        gain_values.append(gain)

        print(f"DAC maximum:   {dac_max:.6f}")
        print(f"DCCT1 maximum: {dcct1_max:.6f}")
        print(f"DCCT2 maximum: {dcct2_max:.6f}")
        print(f"DAC/DCCT2:     {gain:.6f}")

        plot_snapshot(snapshot_data, freq, ax)

    # Finish snapshot waveform plot
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()

    ax[0].set_title("PSC Snapshot Waveforms")
    ax[2].set_xlabel("Sample")

    plt.tight_layout()

    # Frequency-response plot
    fig_response, ax_response = plt.subplots(figsize=(10, 6))

    ax_response.plot(
        frequencies,
        gain_values,
        marker="o"
    )

    ax_response.set_title("Power Supply Frequency Response")
    ax_response.set_xlabel("DDS Frequency (Hz)")
    ax_response.set_ylabel("Gain: DCCT / DAC ")
    ax_response.grid(True)

    plt.tight_layout()
    plt.show()

    dac_setpt_pv.put(0)

    # Save the frequency-response measurements rather than only
    # saving the final snapshot.
    response_data = np.column_stack(
        (
            frequencies,
            dac_max_values,
            dcct1_max_values,
            dcct2_max_values,
            gain_values,
        )
    )

    header = (
        "Frequency_Hz "
        "DAC_Max "
        "DCCT1_Max "
        "DCCT2_Max "
        "DAC_Max_div_DCCT2_Max"
    )

    np.savetxt(
        out_filename,
        response_data,
        fmt="%.8f",
        delimiter=" ",
        header=header
    )

    print(f"\nSaved frequency-response data to {out_filename}")


if __name__ == "__main__":
    main()
